"""Testes RED para swipes_burnout/ingestao.py — Pipeline de Ingestao.

Cobre os 4 requisitos do Pipeline de Ingestao:
  ING-01 — ingerir_perfil executa fluxo completo (retorna dict + persiste no ChromaDB)
  ING-02 — ingerir_lote processa lista de perfis (retorna contagens corretas)
  ING-03 — logs em PT-BR emitidos durante a ingestao (verificado via caplog)
  ING-04 — idempotencia: reinserir o mesmo perfil nao duplica a colecao

Todos os 6 testes DEVEM FALHAR antes da implementacao de swipes_burnout/ingestao.py.
O erro esperado e ModuleNotFoundError ou ImportError ao tentar importar
ingerir_perfil / ingerir_lote de swipes_burnout.ingestao.

Cada funcao de teste importa lazily (dentro do corpo) para que o erro de
ImportError seja gerado individualmente por teste, garantindo RED puro.
"""
from __future__ import annotations

import logging

import pytest


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def colecao_temporaria(tmp_path):
    """Repositorio isolado em diretorio temporario.

    Usa tmp_path do pytest para criar um diretorio de ChromaDB exclusivo
    para este teste, evitando interferencia entre execucoes. Chama
    colecao.resetar() no teardown via yield para garantir limpeza.
    """
    from swipes_burnout.repositorio import Repositorio

    colecao = Repositorio(
        diretorio=str(tmp_path / "chroma_test"),
        nome_colecao="test_ingestao",
    )
    yield colecao
    colecao.resetar()


@pytest.fixture
def perfil_unico():
    """Perfil valido com campos fixos para testes unitarios de ingestao.

    Usa dados completamente deterministicos (sem aleatoriedade) para que
    os testes sejam reproduziveis independentemente da seed ou do pool gerado.
    """
    from swipes_burnout.schema import Perfil

    return Perfil(
        id="test-ing-001",
        nome="Teste Ingestao",
        idade=25,
        cidade="Sao Paulo",
        genero="masculino",
        genero_preferido="feminino",
        faixa_etaria_pref=(22, 32),
        objetivo="namoro",
        bio="Perfil de teste para ingestao unitaria.",
        interesses=["musica", "viagem", "cinema"],
    )


# ── ING-01: ingerir_perfil executa fluxo completo ─────────────────────────────


def test_ingerir_perfil_retorna_dict(colecao_temporaria, perfil_unico):
    """ingerir_perfil deve retornar dict com chaves 'sucesso', 'id' e 'erro' (ING-01)."""
    from swipes_burnout.ingestao import ingerir_perfil

    resultado = ingerir_perfil(perfil_unico, colecao_temporaria)
    assert isinstance(resultado, dict)
    assert "sucesso" in resultado
    assert "id" in resultado
    assert "erro" in resultado


def test_ingerir_perfil_persiste_no_chromadb(colecao_temporaria, perfil_unico):
    """Apos ingerir_perfil, a colecao deve conter exatamente 1 documento (ING-01)."""
    from swipes_burnout.ingestao import ingerir_perfil

    ingerir_perfil(perfil_unico, colecao_temporaria)
    assert colecao_temporaria.contar() == 1


# ── ING-02: ingerir_lote processa lista ───────────────────────────────────────


def test_ingerir_lote_retorna_dict_com_contagens(colecao_temporaria):
    """ingerir_lote deve retornar dict com chaves 'sucesso', 'falha' e 'total' (ING-02)."""
    from swipes_burnout.ingestao import ingerir_lote
    from swipes_burnout.seed_data import gerar_pool_perfis

    perfis = gerar_pool_perfis()[:5]
    resultado = ingerir_lote(perfis, colecao_temporaria)
    assert isinstance(resultado, dict)
    assert "sucesso" in resultado and "falha" in resultado and "total" in resultado
    assert resultado["total"] == 5


def test_ingerir_lote_todos_perfis_inseridos(colecao_temporaria):
    """Apos ingerir_lote com 10 perfis, a colecao deve conter 10 documentos (ING-02)."""
    from swipes_burnout.ingestao import ingerir_lote
    from swipes_burnout.seed_data import gerar_pool_perfis

    perfis = gerar_pool_perfis()[:10]
    ingerir_lote(perfis, colecao_temporaria)
    assert colecao_temporaria.contar() == 10


# ── ING-03: logs em PT-BR ─────────────────────────────────────────────────────


def test_ingerir_perfil_emite_log_ptbr(colecao_temporaria, perfil_unico, caplog):
    """ingerir_perfil deve emitir ao menos um log contendo 'ingeri', 'ingerindo' ou 'perfil' (ING-03)."""
    from swipes_burnout.ingestao import ingerir_perfil

    with caplog.at_level(logging.INFO):
        ingerir_perfil(perfil_unico, colecao_temporaria)

    mensagens = " ".join(r.message for r in caplog.records)
    assert any(
        palavra in mensagens.lower() for palavra in ["ingeri", "ingerindo", "perfil"]
    ), f"Nenhuma palavra PT-BR encontrada nos logs. Mensagens: {mensagens!r}"


# ── ING-04: idempotencia ──────────────────────────────────────────────────────


def test_idempotencia_nao_duplica(colecao_temporaria, perfil_unico):
    """Reinserir o mesmo perfil duas vezes nao deve duplicar a colecao (ING-04)."""
    from swipes_burnout.ingestao import ingerir_perfil

    ingerir_perfil(perfil_unico, colecao_temporaria)
    ingerir_perfil(perfil_unico, colecao_temporaria)  # segunda chamada identica
    assert colecao_temporaria.contar() == 1, (
        "Idempotencia violada: reinserir o mesmo perfil gerou mais de 1 documento na colecao."
    )
