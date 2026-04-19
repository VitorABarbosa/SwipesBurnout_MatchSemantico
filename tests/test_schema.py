"""Testes do schema de dados do CONNECT.AI (Perfil).

Cobre validacoes Pydantic dos 3 grupos de campos definidos no BRIEFING secao 6
(estruturados, semanticos, multimodais) + o campo gerado `personalidade_ia`.
"""

import pytest
from pydantic import ValidationError

from connect_ai.schema import Perfil


def _perfil_valido_kwargs(**overrides):
    """Helper: retorna um dict de kwargs validos para instanciar Perfil.

    Permite sobrescrever campos individuais via kwargs para construir variantes
    invalidas em cada teste sem repetir o dicionario base.
    """
    base = dict(
        nome="Maria Silva",
        idade=28,
        cidade="Sao Paulo",
        genero="feminino",
        genero_preferido="masculino",
        faixa_etaria_pref=(25, 35),
        objetivo="namoro",
        bio="Adoro caminhadas, jazz e culinaria italiana.",
        interesses=["caminhada", "jazz", "culinaria"],
        foto_perfil=None,
        fotos_extras=[],
    )
    base.update(overrides)
    return base


def test_perfil_valido_e_instanciado():
    """Perfil com todos os campos validos deve ser instanciado sem erro."""
    perfil = Perfil(**_perfil_valido_kwargs())
    assert perfil.nome == "Maria Silva"
    assert perfil.idade == 28
    assert perfil.objetivo == "namoro"
    assert perfil.id  # gerado automaticamente


def test_perfil_aceita_id_explicito():
    """Quando um id explicito e fornecido, deve ser preservado."""
    perfil = Perfil(**_perfil_valido_kwargs(id="id-fixo-123"))
    assert perfil.id == "id-fixo-123"


def test_idade_minima_18():
    """Idade abaixo de 18 deve ser rejeitada (sem cadastro de menores)."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(idade=17))


def test_idade_maxima_99():
    """Idade acima de 99 deve ser rejeitada (limite superior do dominio)."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(idade=100))


def test_genero_invalido_rejeitado():
    """Valor de genero fora do conjunto aceito deve levantar ValidationError."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(genero="invalido"))


def test_genero_preferido_aceita_todos():
    """genero_preferido deve aceitar 'todos' alem dos valores de genero."""
    perfil = Perfil(**_perfil_valido_kwargs(genero_preferido="todos"))
    assert perfil.genero_preferido == "todos"


def test_objetivo_invalido_rejeitado():
    """Objetivo fora de {namoro, casual, amizade} deve ser rejeitado."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(objetivo="trabalho"))


def test_objetivos_validos_aceitos():
    """Os 3 objetivos definidos pelo BRIEFING sao todos aceitos."""
    for obj in ["namoro", "casual", "amizade"]:
        perfil = Perfil(**_perfil_valido_kwargs(objetivo=obj))
        assert perfil.objetivo == obj


def test_faixa_etaria_invertida_rejeitada():
    """Faixa com limite inferior maior que o superior deve ser rejeitada."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(faixa_etaria_pref=(40, 25)))


def test_faixa_etaria_fora_de_18_99_rejeitada():
    """Faixa fora do intervalo [18, 99] deve ser rejeitada."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(faixa_etaria_pref=(15, 30)))


def test_interesses_vazio_rejeitado():
    """Lista de interesses vazia deve ser rejeitada (nao ha o que embedar)."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(interesses=[]))


def test_bio_vazia_rejeitada():
    """Bio vazia deve ser rejeitada (nao ha texto para embedding)."""
    with pytest.raises(ValidationError):
        Perfil(**_perfil_valido_kwargs(bio=""))


def test_personalidade_ia_opcional():
    """personalidade_ia e opcional: ainda nao processado pelo Perfilador."""
    perfil = Perfil(**_perfil_valido_kwargs())
    # Aceita None ou string vazia como "ainda nao processado pelo Perfilador"
    assert perfil.personalidade_ia in (None, "")


def test_personalidade_ia_pode_ser_preenchida():
    """Apos passagem pelo Perfilador, personalidade_ia carrega o traco inferido."""
    perfil = Perfil(
        **_perfil_valido_kwargs(personalidade_ia="Introvertida com forte interesse cultural.")
    )
    assert "Introvertida" in perfil.personalidade_ia


# ===================================================================
# Testes da funcao construir_documento_semantico
# ===================================================================

from connect_ai.schema import construir_documento_semantico


def test_documento_inclui_bio_interesses_objetivo():
    """O documento deve concatenar bio + interesses + objetivo de forma legivel."""
    perfil = Perfil(**_perfil_valido_kwargs(
        bio="Adoro jazz",
        interesses=["musica", "leitura"],
        objetivo="namoro",
    ))
    doc = construir_documento_semantico(perfil)
    assert "Adoro jazz" in doc
    assert "musica" in doc
    assert "leitura" in doc
    assert "namoro" in doc


def test_documento_inclui_personalidade_quando_preenchida():
    """Quando personalidade_ia esta preenchida, deve aparecer no documento com marcador."""
    perfil = Perfil(**_perfil_valido_kwargs(
        personalidade_ia="Introvertida e cultural"
    ))
    doc = construir_documento_semantico(perfil)
    assert "Introvertida e cultural" in doc
    assert "Personalidade" in doc


def test_documento_omite_personalidade_quando_ausente():
    """Sem personalidade_ia, NAO deve vazar 'None'/'null' nem emitir a secao."""
    perfil = Perfil(**_perfil_valido_kwargs(personalidade_ia=None))
    doc = construir_documento_semantico(perfil)
    # Nao deve vazar tokens "None" / "null" no texto enviado ao embedding
    assert "None" not in doc
    assert "null" not in doc
    assert "Personalidade" not in doc


def test_documento_e_estavel():
    """Determinismo: chamar 2x com o mesmo perfil retorna a mesma string."""
    perfil = Perfil(**_perfil_valido_kwargs())
    assert construir_documento_semantico(perfil) == construir_documento_semantico(perfil)


def test_documento_contem_marcadores_ptbr():
    """Documento deve usar marcadores PT-BR human-readable."""
    perfil = Perfil(**_perfil_valido_kwargs())
    doc = construir_documento_semantico(perfil)
    assert "Bio:" in doc
    assert "Interesses:" in doc
    assert "Objetivo:" in doc
