---
phase: 03-agentes-e-grafo-langgraph
plan: "01"
subsystem: testing
tags: [pytest, tdd, langgraph, agentes, red-phase, agentstate]

# Dependency graph
requires:
  - phase: 02-seed-data-sintetico
    provides: PERFIL_TESTE fixture and seed_data module used as test inputs
  - phase: 01-setup-e-schema
    provides: Perfil schema and connect_ai package structure

provides:
  - tests/test_agentes.py with 10 failing RED tests for AgentState and 3 agents
  - tests/test_grafo.py with 5 failing RED tests for LangGraph pipeline and visualization
  - Contracts fixed for AgentState, agente_perfilador, agente_casamenteiro, agente_rag_justificador
  - Contracts fixed for pipeline_consumo (CompiledStateGraph) and salvar_visualizacao_grafo

affects:
  - 03-02 (GREEN implementation of connect_ai/agentes.py)
  - 03-03 (GREEN implementation of connect_ai/grafo.py)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - TDD RED phase — contracts written as tests before implementation
    - AgentState as TypedDict-like dict with keys: perfil, candidatos, matches, justificativas, erro
    - Agent functions accept and return AgentState (dict)
    - LangGraph pipeline exposed as pipeline_consumo (CompiledStateGraph with .invoke)
    - Mermaid export always generated; PNG is optional (graphviz dependency)

key-files:
  created:
    - tests/test_agentes.py
    - tests/test_grafo.py
  modified: []

key-decisions:
  - "03-01: AgentState como dict (TypedDict-style) com 5 campos: perfil, candidatos, matches, justificativas, erro — verificado via 'in' operator nos testes"
  - "03-01: salvar_visualizacao_grafo gera .mmd sempre (Mermaid) e .png opcionalmente — testes validam apenas .mmd para evitar dependencia de graphviz"
  - "03-01: test_grafo.py usa imports lazy (dentro das funcoes de teste) para garantir que cada funcao falha individualmente em vez de falhar na coleta"
  - "03-01: match_mock em state_com_matches usa id='seed-compat-0001' — alinhado com IDs deterministicos do seed_data"

patterns-established:
  - "RED-first: todos os contratos de interface fixados em testes antes de qualquer implementacao"
  - "Testes de agentes: cada agente testado isoladamente (unit) e em sequencia (integration via test_pipeline_acumulacao)"
  - "Imports lazy em test_grafo.py: from connect_ai.grafo import X dentro do corpo da funcao de teste"

requirements-completed: [AGT-01, AGT-02, AGT-03, AGT-04, AGT-05, AGT-06, AGT-07]

# Metrics
duration: 5min
completed: 2026-04-20
---

# Phase 3 Plan 01: Agentes e Grafo LangGraph (RED) Summary

**TDD RED phase: 15 failing tests (10 for agents + 5 for LangGraph graph) fix contracts for AgentState, 3 agents, pipeline_consumo and Mermaid visualization before implementation**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-20T20:41:37Z
- **Completed:** 2026-04-20T20:46:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `tests/test_agentes.py` with 10 test functions covering AGT-01 through AGT-04 and AGT-07
- Created `tests/test_grafo.py` with 5 test functions covering AGT-05 and AGT-06
- Both files fail with `ModuleNotFoundError` (RED confirmed) — implementation modules do not exist
- Existing 51-test suite continues passing (zero regression)

## Task Commits

Each task was committed atomically:

1. **Task 1: Testes RED para AgentState e os tres agentes** - `8441efe` (test)
2. **Task 2: Testes RED para compilacao do grafo e visualizacao** - `1722854` (test)

**Plan metadata:** (docs commit follows)

_Note: TDD tasks use test-only commits for RED phase._

## Files Created/Modified

- `tests/test_agentes.py` — 10 RED tests for AgentState (AGT-01), agente_perfilador (AGT-02), agente_casamenteiro (AGT-03), agente_rag_justificador (AGT-04), pipeline accumulation (AGT-01+AGT-07)
- `tests/test_grafo.py` — 5 RED tests for pipeline_consumo graph compilation (AGT-05) and salvar_visualizacao_grafo Mermaid export (AGT-06)

## Decisions Made

- `AgentState` verified via dict `in` operator (keys: perfil, candidatos, matches, justificativas, erro) — compatible with LangGraph TypedDict approach
- `test_grafo.py` uses lazy imports inside test functions to ensure each test fails individually (instead of all failing at collection time)
- `salvar_visualizacao_grafo` tested with `tmp_path` fixture, Mermaid (.mmd) always required, PNG optional (no graphviz needed for CI)
- `match_mock` in `state_com_matches` uses `id="seed-compat-0001"` — aligns with deterministic IDs from `seed_data.py`

## Deviations from Plan

### Minor Plan Discrepancy

**1. [Documentation] test_agentes.py line count: 160 lines vs plan acceptance criterion of >= 200 lines**
- **Found during:** Task 1 acceptance check
- **Issue:** Plan's `<action>` block provides exact content (160 lines) but acceptance criteria says `>= 200 lines` — contradiction within the plan itself
- **Resolution:** Exact content provided in `<action>` block was used as specified; the content satisfies all behavioral requirements (10 test functions >= 9 required)
- **Impact:** None — all functional acceptance criteria met; line count criterion was inconsistent with the exact content block

---

**Total deviations:** 1 documentation note (plan inconsistency, no code change required)
**Impact on plan:** Zero. All functional criteria satisfied.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- RED phase complete: all test contracts locked for AGT-01 through AGT-07
- Next: Implement `connect_ai/agentes.py` (GREEN for test_agentes.py) — define AgentState TypedDict, agente_perfilador with deterministic personalidade_ia, agente_casamenteiro stub, agente_rag_justificador mock
- After that: Implement `connect_ai/grafo.py` (GREEN for test_grafo.py) — build LangGraph StateGraph with 3 nodes, compile, add Mermaid export

---
*Phase: 03-agentes-e-grafo-langgraph*
*Completed: 2026-04-20*
