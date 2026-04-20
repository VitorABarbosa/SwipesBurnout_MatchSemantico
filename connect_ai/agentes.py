"""Agentes LangGraph do CONNECT.AI.

Define AgentState (TypedDict compartilhado) e os tres nos do grafo:
  - agente_perfilador: mock deterministico do Gemini Vision (AGT-02, AGT-07)
  - agente_casamenteiro: stub com scoring fixo, substituivel na Fase 5 (AGT-03)
  - agente_rag_justificador: mock do Gemini Pro, modo real quando API disponivel (AGT-04)

Todos os agentes recebem e devolvem AgentState — contrato exigido pelo LangGraph.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from typing_extensions import TypedDict

from connect_ai.schema import Perfil


class AgentState(TypedDict):
    """Estado compartilhado entre os nos do grafo LangGraph.

    Campos acumulados ao longo do pipeline:
      perfil: Perfil processado (personalidade_ia preenchida pelo Perfilador).
      candidatos: Top-30 da busca vetorial (populado pelo Casamenteiro, Fase 5).
      matches: Top-10 com score >= 85 (populado pelo Casamenteiro).
      justificativas: Texto PT-BR do RAG para cada match, keyed por id.
      erro: Mensagem de erro se qualquer no falhar; None em execucao normal.
    """

    perfil: Perfil
    candidatos: List[Dict[str, Any]]
    matches: List[Dict[str, Any]]
    justificativas: Dict[str, str]
    erro: Optional[str]


# ── Cache interno do Perfilador (AGT-07: determinismo via cache) ───────────────
_cache_personalidade: Dict[str, str] = {}


def _gerar_personalidade_mock(perfil: Perfil) -> str:
    """Gera descricao de personalidade deterministica baseada nos dados do Perfil.

    Mock textual determinístico: mesmo input -> mesmo output, sem chamar Gemini.
    O texto e suficientemente rico para ser util como entrada do embedding na Fase 4.
    """
    interesses_str = ", ".join(perfil.interesses[:5])
    return (
        f"Perfil de personalidade gerado pelo Perfilador IA (modo mock): "
        f"{perfil.nome} e uma pessoa de {perfil.idade} anos, residente em {perfil.cidade}, "
        f"com objetivo de {perfil.objetivo}. "
        f"Demonstra interesse ativo em: {interesses_str}. "
        f"Bio pessoal: {perfil.bio[:120].strip()}. "
        f"Tracos predominantes: sociavel, comunicativo e orientado a conexoes autenticas."
    )


def agente_perfilador(state: AgentState) -> AgentState:
    """No Perfilador: enriquece o Perfil com descricao de personalidade gerada por IA.

    Usa cache por perfil.id (AGT-07) para garantir determinismo entre chamadas.
    Em producao (Fase futura), chamaria Gemini Vision com temperature=0.
    Nesta implementacao, usa mock textual deterministico.

    Args:
        state: AgentState com campo 'perfil' preenchido.

    Returns:
        AgentState com state['perfil'].personalidade_ia preenchido.
    """
    perfil = state["perfil"]
    id_perfil = perfil.id

    if id_perfil not in _cache_personalidade:
        _cache_personalidade[id_perfil] = _gerar_personalidade_mock(perfil)

    perfil_atualizado = perfil.model_copy(
        update={"personalidade_ia": _cache_personalidade[id_perfil]}
    )
    return {**state, "perfil": perfil_atualizado}


# ── Stub de scoring (substituido na Fase 5 por connect_ai.scoring) ─────────────


def _calcular_score_stub(candidato: Dict[str, Any], perfil_ref: Perfil) -> float:
    """Stub: retorna 90.0 para todos os candidatos.

    FASE 3 APENAS. A Fase 5 substitui por connect_ai.scoring.calcular_score
    com pesos 60/20/10/5/5 (semantico/interesses/objetivo/idade/geografia).
    """
    return 90.0


def agente_casamenteiro(state: AgentState) -> AgentState:
    """No Casamenteiro: aplica filtros e scoring para selecionar Top-10 matches.

    Fase 3 (stub): usa gerar_pool_perfis() como candidatos mock e _calcular_score_stub.
    Fase 5 substituira a busca vetorial real via Repositorio e scoring ponderado.

    Popula state['matches'] com dicts contendo pelo menos 'id', 'score' e 'nome'.
    Retorna apenas candidatos com score >= 85.0.

    Args:
        state: AgentState com 'perfil' preenchido (apos Perfilador).

    Returns:
        AgentState com 'matches' populado.
    """
    from connect_ai.seed_data import gerar_pool_perfis

    perfil_ref = state["perfil"]
    pool = gerar_pool_perfis()

    matches = []
    for candidato in pool:
        # Filtro hard basico: nao incluir o proprio perfil
        if candidato.id == perfil_ref.id:
            continue
        score = _calcular_score_stub({"id": candidato.id, "nome": candidato.nome}, perfil_ref)
        if score >= 85.0:
            matches.append(
                {
                    "id": candidato.id,
                    "score": float(score),
                    "nome": candidato.nome,
                    "cidade": candidato.cidade,
                    "idade": candidato.idade,
                }
            )

    # Limitar a 10 matches (Top-10 do BRIEFING)
    matches_top10 = matches[:10]
    return {**state, "matches": matches_top10}


def _justificativa_mock(match: Dict[str, Any], perfil_ref: Perfil) -> str:
    """Gera justificativa de compatibilidade deterministica em PT-BR.

    Usado quando GOOGLE_API_KEY nao esta disponivel ou em testes.
    """
    nome_match = match.get("nome", "Candidato")
    score = match.get("score", 90.0)
    return (
        f"{nome_match} apresenta alta compatibilidade com {perfil_ref.nome} "
        f"(score {score:.1f}/100). Compartilham objetivos semelhantes e "
        f"demonstram afinidade semantica elevada baseada em interesses, "
        f"bio e estilo de vida descritos nos perfis."
    )


def agente_rag_justificador(state: AgentState) -> AgentState:
    """No RAG Justificador: gera justificativa textual PT-BR para cada match.

    Modo mock (sem GOOGLE_API_KEY): usa _justificativa_mock deterministico.
    Modo real (com GOOGLE_API_KEY): chamaria Gemini Pro com temperature=0.

    Args:
        state: AgentState com 'matches' preenchido (apos Casamenteiro).

    Returns:
        AgentState com 'justificativas' populado.
    """
    perfil_ref = state["perfil"]
    matches = state["matches"]
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    usar_mock = not api_key

    justificativas: Dict[str, str] = {}

    for match in matches:
        id_match = match["id"]
        if usar_mock:
            justificativas[id_match] = _justificativa_mock(match, perfil_ref)
        else:
            # Modo real: Gemini Pro com temperature=0 (AGT-07)
            # Implementacao completa na Fase futura (RAG com contexto real)
            justificativas[id_match] = _justificativa_mock(match, perfil_ref)

    return {**state, "justificativas": justificativas}
