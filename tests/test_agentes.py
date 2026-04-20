"""Testes RED para connect_ai/agentes.py.

Cobre AgentState (AGT-01), Agente Perfilador (AGT-02),
Agente Casamenteiro stub (AGT-03) e Agente RAG mock (AGT-04).

Todos os testes DEVEM FALHAR antes da implementacao de connect_ai/agentes.py.
"""
from __future__ import annotations

import pytest

from connect_ai.agentes import (
    AgentState,
    agente_casamenteiro,
    agente_perfilador,
    agente_rag_justificador,
)
from connect_ai.seed_data import PERFIL_TESTE


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def state_inicial() -> AgentState:
    """AgentState com PERFIL_TESTE e demais campos em branco."""
    return AgentState(
        perfil=PERFIL_TESTE,
        candidatos=[],
        matches=[],
        justificativas={},
        erro=None,
    )


@pytest.fixture
def state_com_matches() -> AgentState:
    """AgentState com 1 match pre-populado para testar o RAG isolado."""
    match_mock = {"id": "seed-compat-0001", "score": 90.0, "nome": "Joao Silva"}
    return AgentState(
        perfil=PERFIL_TESTE,
        candidatos=[],
        matches=[match_mock],
        justificativas={},
        erro=None,
    )


# ── AgentState (AGT-01) ───────────────────────────────────────────────────────


def test_agent_state_campos(state_inicial: AgentState) -> None:
    """AgentState deve ter os cinco campos obrigatorios com valores corretos."""
    assert "perfil" in state_inicial
    assert "candidatos" in state_inicial
    assert "matches" in state_inicial
    assert "justificativas" in state_inicial
    assert "erro" in state_inicial
    assert state_inicial["candidatos"] == []
    assert state_inicial["matches"] == []
    assert state_inicial["justificativas"] == {}
    assert state_inicial["erro"] is None


# ── Agente Perfilador (AGT-02) ────────────────────────────────────────────────


def test_perfilador_retorna_state(state_inicial: AgentState) -> None:
    """agente_perfilador deve retornar um AgentState (dict)."""
    resultado = agente_perfilador(state_inicial)
    assert isinstance(resultado, dict)
    assert "perfil" in resultado


def test_perfilador_nao_nulo(state_inicial: AgentState) -> None:
    """personalidade_ia deve ser string nao-vazia apos o Perfilador."""
    resultado = agente_perfilador(state_inicial)
    personalidade = resultado["perfil"].personalidade_ia
    assert personalidade is not None
    assert isinstance(personalidade, str)
    assert len(personalidade) > 10


def test_perfilador_determinismo(state_inicial: AgentState) -> None:
    """Mesmo input deve produzir exatamente o mesmo personalidade_ia (AGT-07)."""
    resultado_1 = agente_perfilador(state_inicial)
    resultado_2 = agente_perfilador(state_inicial)
    assert resultado_1["perfil"].personalidade_ia == resultado_2["perfil"].personalidade_ia


# ── Agente Casamenteiro stub (AGT-03) ─────────────────────────────────────────


def test_casamenteiro_retorna_state(state_inicial: AgentState) -> None:
    """agente_casamenteiro deve retornar um AgentState (dict)."""
    resultado = agente_casamenteiro(state_inicial)
    assert isinstance(resultado, dict)
    assert "matches" in resultado


def test_casamenteiro_popula_matches(state_inicial: AgentState) -> None:
    """matches deve ser lista de dicts com 'id' (str) e 'score' (float)."""
    resultado = agente_casamenteiro(state_inicial)
    matches = resultado["matches"]
    assert isinstance(matches, list)
    assert len(matches) > 0
    for m in matches:
        assert "id" in m and isinstance(m["id"], str)
        assert "score" in m and isinstance(m["score"], float)


def test_casamenteiro_score_minimo(state_inicial: AgentState) -> None:
    """Todos os matches devem ter score >= 85.0 (threshold do BRIEFING)."""
    resultado = agente_casamenteiro(state_inicial)
    for m in resultado["matches"]:
        assert m["score"] >= 85.0, f"Score {m['score']} abaixo de 85 para id={m['id']}"


# ── Agente RAG Justificador mock (AGT-04) ─────────────────────────────────────


def test_rag_retorna_state(state_com_matches: AgentState) -> None:
    """agente_rag_justificador deve retornar um AgentState (dict)."""
    resultado = agente_rag_justificador(state_com_matches)
    assert isinstance(resultado, dict)
    assert "justificativas" in resultado


def test_rag_popula_justificativas(state_com_matches: AgentState) -> None:
    """justificativas deve ser dict keyed por id do match com valor str."""
    resultado = agente_rag_justificador(state_com_matches)
    justificativas = resultado["justificativas"]
    assert isinstance(justificativas, dict)
    assert len(justificativas) > 0
    for id_match, texto in justificativas.items():
        assert isinstance(id_match, str)
        assert isinstance(texto, str)
        assert len(texto) > 10


# ── Acumulacao do AgentState (AGT-01) ─────────────────────────────────────────


def test_pipeline_acumulacao(state_inicial: AgentState) -> None:
    """Perfilador -> Casamenteiro -> RAG deve acumular todos os campos."""
    state = agente_perfilador(state_inicial)
    state = agente_casamenteiro(state)
    state = agente_rag_justificador(state)

    # Perfilador preencheu personalidade_ia
    assert state["perfil"].personalidade_ia is not None
    assert len(state["perfil"].personalidade_ia) > 10

    # Casamenteiro preencheu matches
    assert len(state["matches"]) > 0

    # RAG preencheu justificativas para cada match
    assert len(state["justificativas"]) == len(state["matches"])
    for m in state["matches"]:
        assert m["id"] in state["justificativas"]
