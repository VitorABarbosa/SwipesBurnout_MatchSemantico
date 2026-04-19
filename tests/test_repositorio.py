"""Testes de integracao do wrapper Repositorio (ChromaDB local).

Roda o ChromaDB real (PersistentClient) em diretorios temporarios isolados
por teste -- nao mocka o cliente. Embeddings sao vetores sinteticos curtos
(16 dimensoes) ja que o ChromaDB aceita qualquer dimensionalidade desde que
seja consistente dentro da colecao. Em producao serao 768d (text-embedding-004).

Cada teste usa `tmp_path` do pytest para garantir isolamento total: nenhum
teste polui `./chroma_db` real e nenhum teste depende de estado de outro.
"""

from typing import List, Optional

import pytest

from connect_ai.repositorio import Repositorio, ResultadoBusca
from connect_ai.schema import Perfil


# Embedding sintetico curto (16 dimensoes) -- ChromaDB aceita qualquer
# dimensionalidade desde que seja consistente dentro da colecao.
DIM = 16


def _embedding_constante(valor: float) -> List[float]:
    """Cria um vetor de DIM dimensoes com valor constante.

    Vetores constantes diferentes (ex: [0.1]*16 vs [0.7]*16) ficam ate
    perfeitamente alinhados em direcao (mesma direcao do vetor (1,1,...,1)),
    o que da distancia coseno proxima de 0. Para criar vetores realmente
    distantes nos testes de busca, usamos outras direcoes.
    """
    return [valor] * DIM


def _embedding_direcao(indice: int) -> List[float]:
    """Cria um vetor unitario na direcao do `indice`-esimo eixo canonico.

    Vetores em eixos diferentes sao ortogonais entre si (distancia coseno = 1).
    Util para testes que precisam de candidatos distantes do alvo.
    """
    v = [0.0] * DIM
    v[indice % DIM] = 1.0
    return v


def _perfil(
    idade: int = 28,
    cidade: str = "Sao Paulo",
    objetivo: str = "namoro",
    id_: Optional[str] = None,
) -> Perfil:
    """Helper que monta um Perfil valido com defaults razoaveis.

    Sobrescreve apenas os campos relevantes para cada teste; o resto
    fica fixo para reduzir ruido nos asserts.
    """
    kwargs = dict(
        nome=f"Perfil {idade}",
        idade=idade,
        cidade=cidade,
        genero="feminino",
        genero_preferido="masculino",
        faixa_etaria_pref=(20, 40),
        objetivo=objetivo,
        bio="Bio sintetica de teste.",
        interesses=["musica", "leitura"],
        foto_perfil=None,
        fotos_extras=[],
        personalidade_ia="Personalidade fake.",
    )
    if id_:
        kwargs["id"] = id_
    return Perfil(**kwargs)


@pytest.fixture()
def repo(tmp_path):
    """Cria um Repositorio isolado em diretorio temporario do pytest.

    Cada teste recebe um diretorio fresco -- nao ha vazamento de estado
    entre testes nem poluicao do `chroma_db/` real.
    """
    return Repositorio(
        diretorio=str(tmp_path / "chroma_test"),
        nome_colecao="perfis_test",
    )


def test_inserir_e_contar(repo):
    """Inserir 3 perfis -> contar() retorna 3."""
    repo.inserir(_perfil(id_="a"), _embedding_constante(0.1))
    repo.inserir(_perfil(id_="b"), _embedding_constante(0.2))
    repo.inserir(_perfil(id_="c"), _embedding_constante(0.3))
    assert repo.contar() == 3


def test_inserir_lote_conta_correto(repo):
    """inserir_lote retorna a quantidade inserida e atualiza contar()."""
    perfis = [_perfil(id_=f"p{i}") for i in range(5)]
    embeddings = [_embedding_constante(i * 0.1 + 0.05) for i in range(5)]
    inseridos = repo.inserir_lote(perfis, embeddings)
    assert inseridos == 5
    assert repo.contar() == 5


def test_inserir_lote_lista_desbalanceada_levanta(repo):
    """Sequencias de tamanhos diferentes -> ValueError com mensagem PT-BR."""
    with pytest.raises(ValueError):
        repo.inserir_lote(
            [_perfil(id_="a")],
            [_embedding_constante(0.1), _embedding_constante(0.2)],
        )


def test_idempotencia_upsert(repo):
    """Inserir 3x o mesmo id -> contar() retorna 1 (upsert nao duplica)."""
    p = _perfil(id_="mesmo-id")
    repo.inserir(p, _embedding_constante(0.5))
    repo.inserir(p, _embedding_constante(0.5))
    repo.inserir(p, _embedding_constante(0.5))
    assert repo.contar() == 1


def test_busca_retorna_proprio_perfil_em_primeiro(repo):
    """Buscar com query == embedding inserido -> esse perfil em 1o lugar com d ~ 0."""
    emb = _embedding_direcao(0)
    repo.inserir(_perfil(id_="alvo"), emb)
    repo.inserir(_perfil(id_="outro"), _embedding_direcao(1))

    resultados = repo.buscar(embedding_query=emb, n_resultados=2)
    assert len(resultados) >= 1
    assert resultados[0].id == "alvo"
    # Distancia para si mesmo deve ser muito proxima de zero (vetores identicos).
    assert resultados[0].distancia < 0.01


def test_busca_retorna_resultado_busca_dataclass(repo):
    """O retorno de buscar() e uma lista de ResultadoBusca tipados."""
    repo.inserir(_perfil(id_="a"), _embedding_constante(0.5))
    resultados = repo.buscar(embedding_query=_embedding_constante(0.5), n_resultados=1)
    assert len(resultados) == 1
    assert isinstance(resultados[0], ResultadoBusca)
    assert resultados[0].id == "a"
    assert isinstance(resultados[0].metadata, dict)
    assert isinstance(resultados[0].distancia, float)


def test_metadados_gravam_chaves_esperadas(repo):
    """O metadata gravado contem todas as chaves filtraveis (REPO-03)."""
    repo.inserir(
        _perfil(id_="x", idade=33, cidade="Rio", objetivo="amizade"),
        _embedding_constante(0.4),
    )
    resultados = repo.buscar(embedding_query=_embedding_constante(0.4), n_resultados=1)
    meta = resultados[0].metadata
    for chave in [
        "idade",
        "cidade",
        "genero",
        "genero_preferido",
        "faixa_etaria_min",
        "faixa_etaria_max",
        "objetivo",
        "nome",
    ]:
        assert chave in meta, f"Metadado '{chave}' ausente"
    assert meta["idade"] == 33
    assert meta["cidade"] == "Rio"
    assert meta["objetivo"] == "amizade"


def test_filtro_hard_objetivo(repo):
    """where={'objetivo': 'namoro'} retorna apenas perfis com objetivo='namoro'."""
    repo.inserir(_perfil(id_="namoro1", objetivo="namoro"), _embedding_constante(0.5))
    repo.inserir(_perfil(id_="amizade1", objetivo="amizade"), _embedding_constante(0.5))
    repo.inserir(_perfil(id_="namoro2", objetivo="namoro"), _embedding_constante(0.5))

    resultados = repo.buscar(
        embedding_query=_embedding_constante(0.5),
        n_resultados=10,
        filtros={"objetivo": "namoro"},
    )
    ids = {r.id for r in resultados}
    assert ids == {"namoro1", "namoro2"}
    assert "amizade1" not in ids


def test_existe(repo):
    """existe() retorna True para id presente, False para id ausente."""
    repo.inserir(_perfil(id_="presente"), _embedding_constante(0.1))
    assert repo.existe("presente") is True
    assert repo.existe("ausente") is False


def test_resetar_zera_colecao(repo):
    """Apos resetar(), contar() retorna 0."""
    repo.inserir(_perfil(id_="a"), _embedding_constante(0.1))
    repo.inserir(_perfil(id_="b"), _embedding_constante(0.2))
    assert repo.contar() == 2
    repo.resetar()
    assert repo.contar() == 0


def test_repositorio_persiste_entre_instancias(tmp_path):
    """Inserir com uma instancia, ler com outra apontando ao mesmo diretorio.

    Confirma que PersistentClient grava em disco e que dados sobrevivem
    a re-abertura do client (caso de uso: rodar ingestao em um script
    e consumir os matches em outro).
    """
    diretorio = str(tmp_path / "chroma_persistent")
    nome = "perfis_persist_test"

    repo1 = Repositorio(diretorio=diretorio, nome_colecao=nome)
    repo1.inserir(_perfil(id_="persistente"), _embedding_constante(0.5))
    assert repo1.contar() == 1

    repo2 = Repositorio(diretorio=diretorio, nome_colecao=nome)
    assert repo2.contar() == 1
    assert repo2.existe("persistente") is True
