"""Wrapper de repositorio do ChromaDB para o CONNECT.AI.

Encapsula o cliente nativo do ChromaDB, expondo apenas a API necessaria
pelos pipelines de ingestao (Fase 4) e consumo (Fase 5). Mantem o ChromaDB
como detalhe de implementacao -- substituir por outro vector DB no futuro
afeta apenas este arquivo.

Decisoes de design:
  - **Embeddings sao fornecidos pre-calculados**: o construtor NAO recebe
    um embedding function nem chama o Gemini. Os pipelines (Fases 4 e 5)
    calcularao o embedding via `text-embedding-004` e o passarao pronto ao
    `inserir`. Isso mantem o repositorio agnostico ao provedor de embedding
    e testavel sem rede.
  - **PersistentClient (modo embedded com persistencia em disco)**: NAO o
    `Client` em memoria (perderia dados entre runs) nem o `HttpClient`
    (requer servidor). O diretorio e gitignored (`chroma_db/`).
  - **Distancia coseno explicita** via `metadata={"hnsw:space": "cosine"}`
    na criacao da colecao -- explicito e melhor que implicito; documenta
    a escolha que sustenta a conversao em `scoring_utils.distancia_cosseno_para_score`.
  - **upsert (nao add)**: re-inserir o mesmo `id` substitui o registro
    sem duplicar -- suporta ingestao idempotente (re-rodar o pipeline
    nao polui a colecao).
  - **API minima**: `inserir`, `inserir_lote`, `buscar`, `contar`, `existe`,
    `resetar`. Nada de scoring, nada de chamadas a LLMs -- isso pertence
    aos agentes (Fase 5).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence

import chromadb
from chromadb.config import Settings

from connect_ai.config import obter_diretorio_chroma, obter_nome_colecao
from connect_ai.schema import Perfil, construir_documento_semantico


@dataclass
class ResultadoBusca:
    """Item retornado por `Repositorio.buscar`.

    Encapsula em uma estrutura tipada o que o ChromaDB devolve em listas
    paralelas (ids, documents, metadatas, distances). Facilita o consumo
    no Casamenteiro (Fase 5) sem depender da forma exata da resposta nativa.

    Attributes:
        id: Identificador do perfil (chave primaria no ChromaDB).
        documento: Texto que foi embedado (resultado de
            `construir_documento_semantico`). Util para o RAG.
        metadata: Metadados estruturados gravados (idade, cidade, genero,
            genero_preferido, faixa_etaria_min, faixa_etaria_max, objetivo, nome).
            Usados para filtros hard e exibicao no front.
        distancia: Distancia coseno retornada pelo ChromaDB (0 = identico,
            2 = oposto). Convertida para score 0-100 via
            `scoring_utils.distancia_cosseno_para_score`.
    """

    id: str
    documento: str
    metadata: Dict[str, Any]
    distancia: float


class Repositorio:
    """Wrapper do ChromaDB para perfis do CONNECT.AI.

    Encapsula criacao/abertura da colecao, insercao (com upsert idempotente),
    busca vetorial Top-K com filtros hard via metadata, contagem, verificacao
    de presenca por id e reset (limpeza completa).

    O construtor le configuracao via `connect_ai.config` se nao receber
    overrides explicitos -- centraliza a fonte da verdade dos caminhos
    (env var `CHROMA_PERSIST_DIR`) e evita literais espalhados.
    """

    def __init__(
        self,
        diretorio: Optional[str] = None,
        nome_colecao: Optional[str] = None,
    ) -> None:
        """Cria/abre a colecao de perfis.

        Args:
            diretorio: Diretorio de persistencia em disco. Default: lido de
                `CHROMA_PERSIST_DIR` (env) ou "./chroma_db" (decisao de
                PROJECT.md, gitignored).
            nome_colecao: Nome da colecao dentro do banco. Default: lido de
                `CHROMA_COLLECTION` (env) ou "perfis_connect_ai".

        A flag `allow_reset=True` em Settings habilita o metodo `resetar`
        em ambientes de teste e no botao "Repopular banco" do front (Fase 6).
        `anonymized_telemetry=False` evita envios silenciosos para o
        endpoint de telemetria do ChromaDB.
        """
        self._diretorio = diretorio or obter_diretorio_chroma()
        self._nome_colecao = nome_colecao or obter_nome_colecao()
        self._cliente = chromadb.PersistentClient(
            path=self._diretorio,
            settings=Settings(anonymized_telemetry=False, allow_reset=True),
        )
        self._colecao = self._cliente.get_or_create_collection(
            name=self._nome_colecao,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------ #
    # Construcao de metadados
    # ------------------------------------------------------------------ #

    @staticmethod
    def _metadata_de_perfil(perfil: Perfil) -> Dict[str, Any]:
        """Extrai metadados estruturados (REPO-03) do `Perfil`.

        Apenas tipos primitivos (str, int) -- restricao do ChromaDB para
        campos de metadata (nao aceita listas, tuplas, None ou objetos
        aninhados). A tupla `faixa_etaria_pref` e desempacotada em
        `faixa_etaria_min` e `faixa_etaria_max` para permitir filtros
        numericos `$gte`/`$lte` no `where` da Fase 5.

        Args:
            perfil: Instancia validada de `Perfil`.

        Returns:
            Dict com chaves: idade, cidade, genero, genero_preferido,
            faixa_etaria_min, faixa_etaria_max, objetivo, nome.
        """
        faixa_min, faixa_max = perfil.faixa_etaria_pref
        return {
            "idade": int(perfil.idade),
            "cidade": str(perfil.cidade),
            "genero": str(perfil.genero),
            "genero_preferido": str(perfil.genero_preferido),
            "faixa_etaria_min": int(faixa_min),
            "faixa_etaria_max": int(faixa_max),
            "objetivo": str(perfil.objetivo),
            "nome": str(perfil.nome),  # util para exibicao no front
            "interesses_csv": ",".join(perfil.interesses),  # ex: "musica,viagem,leitura"
        }

    # ------------------------------------------------------------------ #
    # API publica
    # ------------------------------------------------------------------ #

    def inserir(
        self,
        perfil: Perfil,
        embedding: Sequence[float],
    ) -> None:
        """Insere (ou atualiza por upsert) um perfil ja embedado.

        Idempotente: re-inserir o mesmo `perfil.id` substitui o registro
        existente sem duplicar (suporte a ING-04 da Fase 4). Isso permite
        reexecutar o pipeline de ingestao varias vezes sem inflar a colecao.

        Args:
            perfil: Instancia validada de `Perfil`.
            embedding: Vetor pre-calculado pelo `text-embedding-004` (768d
                esperado em producao; testes usam dimensionalidades menores).
        """
        documento = construir_documento_semantico(perfil)
        metadata = self._metadata_de_perfil(perfil)
        self._colecao.upsert(
            ids=[perfil.id],
            embeddings=[list(embedding)],
            metadatas=[metadata],
            documents=[documento],
        )

    def inserir_lote(
        self,
        perfis: Sequence[Perfil],
        embeddings: Sequence[Sequence[float]],
    ) -> int:
        """Insere multiplos perfis em uma chamada.

        Mais eficiente que chamar `inserir` em loop quando o pipeline ja
        possui os embeddings em batch (caso da Fase 4 que processa N perfis
        do seed data de uma so vez).

        Args:
            perfis: Sequencia de `Perfil`.
            embeddings: Sequencia de vetores na mesma ordem dos perfis.

        Returns:
            Quantidade de perfis efetivamente inseridos.

        Raises:
            ValueError: Se as duas sequencias tiverem tamanhos diferentes
                (erro grave -- indica bug no chamador, nao input invalido).
        """
        if len(perfis) != len(embeddings):
            raise ValueError(
                f"Numero de perfis ({len(perfis)}) difere do numero de "
                f"embeddings ({len(embeddings)})."
            )
        if not perfis:
            return 0
        ids = [p.id for p in perfis]
        documentos = [construir_documento_semantico(p) for p in perfis]
        metadatas = [self._metadata_de_perfil(p) for p in perfis]
        self._colecao.upsert(
            ids=ids,
            embeddings=[list(e) for e in embeddings],
            metadatas=metadatas,
            documents=documentos,
        )
        return len(perfis)

    def buscar(
        self,
        embedding_query: Sequence[float],
        n_resultados: int = 30,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> List[ResultadoBusca]:
        """Busca vetorial Top-K com filtros hard opcionais via metadados.

        A Fase 5 usa K=30 por padrao (BRIEFING secao 8.2 passo 3): traz mais
        candidatos do que os 10 finais para que o re-ranking ponderado tenha
        margem para descartar e ainda atingir o threshold >= 85.

        Args:
            embedding_query: Vetor da query (mesma dimensionalidade dos
                vetores da colecao).
            n_resultados: Quantos vizinhos retornar.
            filtros: Dict no formato `where` do ChromaDB (ex:
                `{"objetivo": "namoro", "cidade": {"$eq": "Sao Paulo"}}`).
                None = sem filtros (busca puramente semantica).

        Returns:
            Lista de `ResultadoBusca` ordenada por distancia crescente
            (mais similar primeiro). Pode ter menos itens que `n_resultados`
            se a colecao for menor ou se os filtros restringirem demais.
        """
        kwargs: Dict[str, Any] = {
            "query_embeddings": [list(embedding_query)],
            "n_results": n_resultados,
        }
        if filtros:
            kwargs["where"] = filtros
        resposta = self._colecao.query(**kwargs)

        ids = (resposta.get("ids") or [[]])[0]
        documentos = (resposta.get("documents") or [[]])[0]
        metadatas = (resposta.get("metadatas") or [[]])[0]
        distancias = (resposta.get("distances") or [[]])[0]

        return [
            ResultadoBusca(
                id=ids[i],
                documento=documentos[i] if i < len(documentos) else "",
                metadata=dict(metadatas[i]) if i < len(metadatas) and metadatas[i] else {},
                distancia=float(distancias[i]),
            )
            for i in range(len(ids))
        ]

    def contar(self) -> int:
        """Retorna o numero de documentos na colecao.

        Util para sanity-check apos a ingestao e para exibir no front
        ("Banco contem N perfis").
        """
        return int(self._colecao.count())

    def existe(self, id_perfil: str) -> bool:
        """Verifica se um perfil esta presente na colecao por id.

        Args:
            id_perfil: ID do perfil a verificar.

        Returns:
            True se o id existir, False caso contrario.
        """
        resultado = self._colecao.get(ids=[id_perfil])
        ids = resultado.get("ids") or []
        return id_perfil in ids

    def resetar(self) -> None:
        """Apaga todos os documentos da colecao (recria do zero).

        Util para testes (cada teste comeca com colecao limpa) e para o
        botao "Repopular banco" do front (Fase 6) que zera o estado e
        re-roda a ingestao do seed data.

        Implementacao: deleta a colecao inteira e recria com a mesma
        configuracao (`hnsw:space=cosine`). E mais simples e rapido que
        deletar documento por documento.
        """
        try:
            self._cliente.delete_collection(name=self._nome_colecao)
        except Exception:
            # Se a colecao nao existir (ex: ja deletada por outro processo),
            # segue para recria-la sem propagar erro.
            pass
        self._colecao = self._cliente.get_or_create_collection(
            name=self._nome_colecao,
            metadata={"hnsw:space": "cosine"},
        )
