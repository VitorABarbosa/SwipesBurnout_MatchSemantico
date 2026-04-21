---
phase: 05-pipeline-de-consumo-e-scoring
plan: 01
subsystem: testing
tags: [pytest, tdd, scoring, chromadb, embedding, seed-data]

# Dependency graph
requires:
  - phase: 04-pipeline-de-ingestao
    provides: ingerir_perfil, ingerir_lote, Repositorio — usados nas fixtures de integracao
  - phase: 02-seed-data
    provides: PERFIL_TESTE, gerar_pool_perfis — usados como fixtures de integracao
  - phase: 03-agentes-e-grafo-langgraph
    provides: AgentState, agente_casamenteiro — buscar_matches sera adicionado em agentes.py

provides:
  - tests/test_scoring.py com 20 testes RED cobrindo SCR-01..SCR-05 e TEST-01
  - tests/test_consumo.py com 10 testes RED cobrindo CONS-01..CONS-03, TEST-02, TEST-03
  - Contratos verificaveis de calcular_score, score_semantico, score_interesses, score_objetivo, score_idade, score_geografia e buscar_matches

affects:
  - 05-02-PLAN (Wave 2 — implementacao de scoring.py e buscar_matches — governada por estes testes)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Imports lazy dentro de funcoes de teste (ModuleNotFoundError individual por teste RED)"
    - "Fixture colecao_com_seed com ingerir_lote(gerar_pool_perfis()) para integracao realista"
    - "Gate critico TEST-02 com mensagem de erro diagnostica caso falhe na Wave 2"

key-files:
  created:
    - tests/test_scoring.py
    - tests/test_consumo.py
  modified: []

key-decisions:
  - "05-01: Imports lazy (dentro das funcoes) em test_scoring.py — cada teste falha individualmente com ModuleNotFoundError, nao ha ImportError no nivel de coleta do pytest"
  - "05-01: Fixtures colecao_temp e colecao_com_seed com tmp_path — isolamento total por teste sem polucao de chroma_db/ real"
  - "05-01: test_gate_critico_dez_matches_acima_85 inclui mensagem diagnostica com scores obtidos — facilita debug da Wave 2 se gate falhar"
  - "05-01: test_calcular_score_gate_85_com_cinco_interesses confirma score_final=84 (nao 85) — gate 85 e atingido pela similaridade semantica real dos embeddings, nao por valores literais no teste unitario"

patterns-established:
  - "Lazy imports em testes RED: from connect_ai.scoring import X DENTRO da funcao, nao no topo"
  - "Fixture colecao_com_seed: cria Repositorio real + ingere lote completo — padrao para testes de integracao de consumo"

requirements-completed: [SCR-01, SCR-02, SCR-03, SCR-04, SCR-05, CONS-01, CONS-02, CONS-03, TEST-01, TEST-02, TEST-03]

# Metrics
duration: 4min
completed: 2026-04-21
---

# Phase 5 Plan 01: Pipeline de Consumo e Scoring — Testes RED Summary

**20 testes RED de scoring (5 fatores, formula 60/20/10/5/5) + 10 testes RED do pipeline end-to-end (buscar_matches) com gate critico TEST-02 (>= 10 matches, score >= 85)**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-21T22:14:11Z
- **Completed:** 2026-04-21T22:18:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Criados 20 testes RED para connect_ai/scoring.py cobrindo os 5 fatores (score_semantico, score_interesses, score_objetivo, score_idade, score_geografia) e a composicao ponderada calcular_score com pesos 60/20/10/5/5
- Criados 10 testes RED para o pipeline de consumo end-to-end cobrindo buscar_matches (CONS-01..CONS-03), gate critico TEST-02 (>= 10 matches com score >= 85), filtros hard de genero/objetivo e filtros ChromaDB (TEST-03)
- Suite existente (test_agentes, test_repositorio, test_ingestao) permanece 100% green (27/27 passando)

## Task Commits

Cada tarefa foi commitada atomicamente:

1. **Tarefa 1: Testes RED para connect_ai/scoring.py** - `1ee5e3b` (test)
2. **Tarefa 2: Testes RED para pipeline de consumo** - `6e0d6e2` (test)

## Files Created/Modified

- `tests/test_scoring.py` — 20 testes RED dos 5 fatores de scoring e calcular_score; todos falham com ModuleNotFoundError (connect_ai.scoring nao existe)
- `tests/test_consumo.py` — 10 testes RED do pipeline de consumo: 8 falham com ImportError (buscar_matches), 2 passam (testes de repositorio TEST-03 ja funcionais)

## Decisions Made

- Imports lazy dentro de cada funcao de teste em test_scoring.py: garante que cada teste falhe individualmente com ModuleNotFoundError sem bloquear a coleta do pytest
- Fixtures `colecao_temp` e `colecao_com_seed` com `tmp_path`: isolamento total por teste, sem estado compartilhado nem poluicao do `chroma_db/` real
- `test_gate_critico_dez_matches_acima_85` inclui mensagem de erro diagnostica com os scores obtidos ordenados em ordem decrescente — facilita debugging da Wave 2 se o gate falhar
- `test_calcular_score_gate_85_com_cinco_interesses` confirma que score_final=84 com valores literais (nao 85): o gate 85 e atingido pela similaridade semantica real dos embeddings, nao por interesses em comum (cap em 20)

## Deviations from Plan

None — plano executado exatamente como especificado.

## Issues Encountered

None.

## User Setup Required

None — nenhuma configuracao de servico externo necessaria.

## Next Phase Readiness

- Contratos verificaveis estabelecidos para toda a Fase 5
- Wave 2 (05-02) pode iniciar: implementar connect_ai/scoring.py e adicionar buscar_matches em connect_ai/agentes.py governado pelos 30 testes RED desta Wave 1
- Gate critico TEST-02 esta documentado com mensagem diagnostica para facilitar calibracao do scoring se necessario

---
*Phase: 05-pipeline-de-consumo-e-scoring*
*Completed: 2026-04-21*
