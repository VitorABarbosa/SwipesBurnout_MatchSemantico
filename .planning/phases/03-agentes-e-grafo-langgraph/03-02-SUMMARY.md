---
phase: 03-agentes-e-grafo-langgraph
plan: "02"
subsystem: agentes
tags: [langgraph, agentstate, typeddict, mock, deterministic, tdd-green, pydantic]

# Dependency graph
requires:
  - phase: 03-01
    provides: RED test contracts (tests/test_agentes.py with 10 failing tests for AgentState and 3 agents)
  - phase: 02-seed-data-sintetico
    provides: PERFIL_TESTE fixture, gerar_pool_perfis() returning 100 synthetic profiles
  - phase: 01-setup-e-schema
    provides: Perfil schema with model_copy(), connect_ai package structure

provides:
  - connect_ai/agentes.py with AgentState TypedDict + 3 agent functions (181 lines)
  - agente_perfilador: deterministic mock with dict-based LRU cache keyed by perfil.id
  - agente_casamenteiro: stub using fixed 90.0 score, top-10 filter, excludes self
  - agente_rag_justificador: deterministic PT-BR mock justification per match id

affects:
  - 03-03 (grafo.py imports AgentState and all 3 agent functions as LangGraph nodes)
  - 05-scoring (replaces _calcular_score_stub with real weighted scoring)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - GREEN phase TDD — implementation written to satisfy pre-existing RED tests
    - AgentState TypedDict as shared mutable pipeline state (dict-compatible)
    - Dict-based cache (_cache_personalidade) for determinism without functools overhead
    - Immutable state updates via {**state, field: new_value} pattern
    - Lazy import of gerar_pool_perfis inside agente_casamenteiro to avoid circular imports

key-files:
  created:
    - connect_ai/agentes.py
  modified: []

key-decisions:
  - "03-02: _cache_personalidade como dict global em vez de functools.lru_cache — lru_cache nao suporta Pydantic BaseModel como argumento (nao-hashavel); dict keyed por perfil.id e mais simples e igualmente deterministico"
  - "03-02: _calcular_score_stub retorna 90.0 hardcoded para TODOS os candidatos — substituido na Fase 5 por connect_ai.scoring.calcular_score com pesos 60/20/10/5/5 (semantico/interesses/objetivo/idade/geografia)"
  - "03-02: agente_casamenteiro importa gerar_pool_perfis lazily (dentro da funcao) — evita dependencia circular no nivel de modulo e alinha com pratica LangGraph de nós autocontidos"
  - "03-02: agente_rag_justificador usa mesmo mock em modo real e mock (GOOGLE_API_KEY) — modo real sera implementado na Fase futura com RAG real; estrutura if/else ja preparada para substituicao"

patterns-established:
  - "GREEN-TDD: arquivo de implementacao criado somente apos testes RED — zero over-engineering, contrato ditado pelos testes"
  - "Imutabilidade de estado: {**state, campo: novo_valor} preserva todos os outros campos sem mutacao"
  - "Stub substituivel: _calcular_score_stub tem docstring explicita marcando substituicao na Fase 5"

requirements-completed: [AGT-01, AGT-02, AGT-03, AGT-04, AGT-07]

# Metrics
duration: 3min
completed: 2026-04-20
---

# Phase 3 Plan 02: Agentes e Grafo LangGraph (GREEN Agentes) Summary

**AgentState TypedDict + 3 agentes LangGraph (Perfilador mock deterministico, Casamenteiro stub 90.0, RAG Justificador PT-BR) com 10/10 testes passando em connect_ai/agentes.py (181 linhas)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-20T20:46:16Z
- **Completed:** 2026-04-20T20:49:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `connect_ai/agentes.py` (181 lines) with AgentState TypedDict and 3 agent functions
- 10/10 tests in `tests/test_agentes.py` passing GREEN (was RED in 03-01)
- 61-test full suite passing with zero regressions (previously 51 tests)
- No external API calls required — module fully testable offline

## Task Commits

1. **Task 1: Implementar connect_ai/agentes.py (GREEN)** - `1ae25fb` (feat)

**Plan metadata:** (docs commit follows)

_Note: TDD GREEN phase — single implementation file commit._

## Files Created/Modified

- `connect_ai/agentes.py` — AgentState TypedDict (5 campos), agente_perfilador (cache+mock), agente_casamenteiro (stub 90.0, top-10), agente_rag_justificador (mock PT-BR); 181 linhas

## Decisions Made

- **Dict-based cache vs. functools.lru_cache:** `_cache_personalidade` implementado como `Dict[str, str]` global em vez de `@lru_cache` porque `Perfil` (Pydantic BaseModel) nao e hashavel. Cache por `perfil.id` (str) e igualmente deterministico e mais direto.

- **_calcular_score_stub retorna 90.0 fixo:** Decisao deliberada de Fase 3 — todos os 100 perfis do pool recebem score 90.0, resultando em 99 matches elegíveis (exceto o proprio perfil). Top-10 limita o resultado. Fase 5 substitui por scoring ponderado real.

- **Import lazy de gerar_pool_perfis:** `from connect_ai.seed_data import gerar_pool_perfis` foi colocado dentro do corpo de `agente_casamenteiro` em vez de no topo do modulo para evitar dependencia circular no carregamento do modulo e alinhar com o padrao LangGraph de nos autocontidos.

## Deviations from Plan

None — plan executed exactly as written. O codigo foi copiado diretamente das secoes `<action>` do plano com ajustes menores de formatacao (ordem de imports, spacing).

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. Modulo autocontido, testavel offline sem Gemini ou ChromaDB.

## Next Phase Readiness

- `connect_ai/agentes.py` entregue: AgentState + 3 agentes prontos para consumo pelo LangGraph
- Proximo: 03-03 GREEN — implementar `connect_ai/grafo.py` fazendo `tests/test_grafo.py` passar (5 testes: compilacao do StateGraph + exportacao Mermaid)
- Gate: `connect_ai/grafo.py` nao deve existir ainda (confirmado — arquivo nao criado)

---
*Phase: 03-agentes-e-grafo-langgraph*
*Completed: 2026-04-20*
