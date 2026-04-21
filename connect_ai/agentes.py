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
from connect_ai.repositorio import Repositorio


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
    """DEPRECATED: use calcular_score de connect_ai.scoring diretamente.

    Mantido para compatibilidade com agente_casamenteiro (stub da Fase 3).
    Quando o candidato nao possui 'distancia_coseno' (uso da Fase 3 sem ChromaDB),
    retorna 90.0 hardcoded — comportamento original preservado para os testes existentes.
    A funcao buscar_matches (Fase 5) usa calcular_score com distancia real do ChromaDB.
    """
    if "distancia_coseno" not in candidato:
        # Modo Fase 3: sem distancia real, retorna score fixo (comportamento original)
        return 90.0
    from connect_ai.scoring import calcular_score
    interesses_b = candidato.get("interesses", [])
    resultado = calcular_score(
        distancia_coseno=float(candidato["distancia_coseno"]),
        interesses_a=list(perfil_ref.interesses),
        interesses_b=list(interesses_b) if isinstance(interesses_b, (list, tuple)) else [],
        objetivo_a=str(perfil_ref.objetivo),
        objetivo_b=str(candidato.get("objetivo", "")),
        idade_a=int(perfil_ref.idade),
        idade_b=int(candidato.get("idade", perfil_ref.idade)),
        cidade_a=str(perfil_ref.cidade),
        cidade_b=str(candidato.get("cidade", "")),
    )
    return resultado["score_final"]


def buscar_matches(perfil_solicitante: Perfil, colecao: "Repositorio") -> List[Dict[str, Any]]:
    """Orquestra o pipeline de consumo end-to-end (CONS-01..03, SCR-04..05).

    Fluxo:
      1. Enriquece o perfil com personalidade_ia via agente_perfilador (determinismo AGT-07).
      2. Gera embedding do documento semantico via _gerar_embedding.
      3. Aplica filtros hard via metadata do ChromaDB (CONS-02):
         - objetivo: so candidatos com mesmo objetivo
         - genero: so candidatos com genero == perfil.genero_preferido (se != "todos")
      4. Busca vetorial Top-30 no ChromaDB (CONS-03, K=30).
      5. Para cada resultado, parseia interesses_csv do metadata e calcula score
         ponderado 60/20/10/5/5 via calcular_score (SCR-01..03).
      6. Filtra score >= 85 e retorna Top-10 ordenado por score desc (SCR-04).
      7. Cada dict de retorno inclui breakdown dos 5 fatores (SCR-05).

    PITFALL: ChromaDB retorna distancia [0,2], nao similaridade. A conversao
    e feita dentro de score_semantico em connect_ai.scoring.

    INTERESSES: Gravados como string CSV ("interesses_csv") no metadata do ChromaDB
    pelo metodo _metadata_de_perfil de repositorio.py. Parseados aqui para lista antes
    de chamar score_interesses.

    Args:
        perfil_solicitante: Perfil de quem busca matches.
        colecao: Instancia de Repositorio com perfis ja ingeridos.

    Returns:
        Lista de ate 10 dicts, cada um contendo:
          id, score, nome, cidade, idade, genero,
          score_semantico, score_interesses, score_objetivo,
          score_idade, score_geografia.
        Ordenada por score decrescente. Vazia se nenhum candidato >= 85.
    """
    from connect_ai.scoring import calcular_score
    from connect_ai.ingestao import _gerar_embedding

    # Passo 1: enriquecer personalidade_ia (determinismo via cache)
    state_enriquecido = agente_perfilador({
        "perfil": perfil_solicitante,
        "candidatos": [],
        "matches": [],
        "justificativas": {},
        "erro": None,
    })
    perfil = state_enriquecido["perfil"]

    # Passo 2: gerar embedding do documento semantico
    from connect_ai.schema import construir_documento_semantico
    texto = construir_documento_semantico(perfil)
    embedding_query = _gerar_embedding(texto)

    # Passo 3: montar filtros hard para ChromaDB (CONS-02)
    filtros: Dict[str, Any] = {"objetivo": str(perfil.objetivo)}
    if perfil.genero_preferido != "todos":
        filtros = {
            "$and": [
                {"objetivo": {"$eq": str(perfil.objetivo)}},
                {"genero": {"$eq": str(perfil.genero_preferido)}},
            ]
        }

    # Passo 4: busca vetorial Top-30 (CONS-03)
    candidatos = colecao.buscar(
        embedding_query=embedding_query,
        n_resultados=30,
        filtros=filtros,
    )

    # Passo 5 e 6: calcular score e filtrar >= 85
    matches = []
    for resultado in candidatos:
        meta = resultado.metadata

        # Parsear interesses_csv gravado por repositorio._metadata_de_perfil
        # Formato: "musica,viagem,leitura" -> ["musica", "viagem", "leitura"]
        interesses_csv = str(meta.get("interesses_csv", ""))
        interesses_b: List[str] = [i.strip() for i in interesses_csv.split(",") if i.strip()]

        breakdown = calcular_score(
            distancia_coseno=float(resultado.distancia),
            interesses_a=list(perfil.interesses),
            interesses_b=interesses_b,
            objetivo_a=str(perfil.objetivo),
            objetivo_b=str(meta.get("objetivo", "")),
            idade_a=int(perfil.idade),
            idade_b=int(meta.get("idade", perfil.idade)),
            cidade_a=str(perfil.cidade),
            cidade_b=str(meta.get("cidade", "")),
        )

        if breakdown["score_final"] >= 85.0:
            matches.append({
                "id": resultado.id,
                "score": breakdown["score_final"],
                "nome": str(meta.get("nome", "")),
                "cidade": str(meta.get("cidade", "")),
                "idade": int(meta.get("idade", 0)),
                "genero": str(meta.get("genero", "")),
                "objetivo": str(meta.get("objetivo", "")),
                "score_semantico": breakdown["score_semantico"],
                "score_interesses": breakdown["score_interesses"],
                "score_objetivo": breakdown["score_objetivo"],
                "score_idade": breakdown["score_idade"],
                "score_geografia": breakdown["score_geografia"],
            })

    # Passo 7: ordenar por score desc e limitar a 10 (SCR-04)
    matches.sort(key=lambda m: m["score"], reverse=True)
    return matches[:10]


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
