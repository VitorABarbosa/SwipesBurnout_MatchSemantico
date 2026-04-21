---
phase: 04-pipeline-de-ingestao
plan: "01"
subsystem: testing
tags: [pytest, tdd, chromadb, pydantic, ingestao]

# Dependency graph
requires:
  - phase: 01-fundacao
    provides: Repositorio, Perfil, schema, seed_data (gerar_pool_perfis, PERFIL_TESTE)
  - phase: 03-agentes-e-grafo-langgraph
    provides: Padrao de imports lazy em testes RED (conforme 03-01)
provides:
  - Suite RED de 6 testes cobrindo ING-01..ING-04 para connect_ai/ingestao.py
  - Fixture colecao_temporaria com tmp_path isolado e teardown idempotente
  - Contrato publico de ingerir_perfil e ingerir_lote definido pelos testes
affects: [04-02-pipeline-de-ingestao, 05-scoring-e-consumo]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Imports lazy dentro do corpo dos testes (cada teste falha com ImportError individual)"
    - "Fixture colecao_temporaria com yield + resetar() para isolamento total entre testes"
    - "Perfil de teste com campos fixos (sem aleatoriedade) para reproducibilidade"

key-files:
  created:
    - tests/test_ingestao.py
  modified: []

key-decisions:
  - "Imports lazy em test_ingestao.py (dentro das funcoes de teste) — replica padrao do 03-01 para garantir RED individual por teste"
  - "perfil_unico com campos fixos (nao usa PERFIL_TESTE) — evita acoplamento entre suites de teste"
  - "colecao_temporaria usa tmp_path + nome_colecao='test_ingestao' — isolamento total sem conflito com outros testes"

patterns-established:
  - "Fixture com yield e teardown via resetar() para testes de repositorio"
  - "Perfil deterministico com id='test-ing-...' para testes unitarios de ingestao"

requirements-completed: [ING-01, ING-02, ING-03, ING-04]

# Metrics
duration: 4min
completed: 2026-04-21
---

# Phase 4 Plan 01: Pipeline de Ingestao RED Summary

**Suite TDD RED de 6 testes cobrindo ING-01..ING-04 — todos falhando com ModuleNotFoundError antes da implementacao de connect_ai/ingestao.py**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-21T21:28:02Z
- **Completed:** 2026-04-21T21:32:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Criado tests/test_ingestao.py com 141 linhas e 6 testes RED confirmados
- Contrato publico de ingerir_perfil (retorna dict com sucesso/id/erro) e ingerir_lote (retorna dict com sucesso/falha/total) definido pelos testes
- Imports lazy garantem ModuleNotFoundError individual por teste (padrao 03-01)
- Fixture colecao_temporaria isola ChromaDB em tmp_path com teardown automatico via yield

## Task Commits

1. **Task 1: Escrever tests/test_ingestao.py com todos os testes falhando** - `b869e5a` (test)

**Plan metadata:** (docs commit abaixo)

## Testes Criados — Nomes Exatos

| Teste | Requisito | Descricao |
|-------|-----------|-----------|
| `test_ingerir_perfil_retorna_dict` | ING-01 | Verifica dict com chaves sucesso/id/erro |
| `test_ingerir_perfil_persiste_no_chromadb` | ING-01 | Verifica colecao.contar() == 1 apos ingestao |
| `test_ingerir_lote_retorna_dict_com_contagens` | ING-02 | Verifica dict com sucesso/falha/total e total==5 |
| `test_ingerir_lote_todos_perfis_inseridos` | ING-02 | Verifica colecao.contar() == 10 apos lote de 10 |
| `test_ingerir_perfil_emite_log_ptbr` | ING-03 | Verifica log com "ingeri"/"ingerindo"/"perfil" via caplog |
| `test_idempotencia_nao_duplica` | ING-04 | Verifica colecao.contar() == 1 apos 2 insercoes identicas |

## Confirmacao do Estado RED

```
FAILED tests/test_ingestao.py::test_ingerir_perfil_retorna_dict - ModuleNotFoundError
FAILED tests/test_ingestao.py::test_ingerir_perfil_persiste_no_chromadb - ModuleNotFoundError
FAILED tests/test_ingestao.py::test_ingerir_lote_retorna_dict_com_contagens - ModuleNotFoundError
FAILED tests/test_ingestao.py::test_ingerir_lote_todos_perfis_inseridos - ModuleNotFoundError
FAILED tests/test_ingestao.py::test_ingerir_perfil_emite_log_ptbr - ModuleNotFoundError
FAILED tests/test_ingestao.py::test_idempotencia_nao_duplica - ModuleNotFoundError
========================= 6 failed, 0 passed =================================
```

Erro: `ModuleNotFoundError: No module named 'connect_ai.ingestao'`

## Files Created/Modified

- `tests/test_ingestao.py` — Suite RED com 6 testes, 141 linhas, importando lazily de connect_ai.ingestao

## Decisions Made

- Imports lazy dentro de cada funcao de teste (replica padrao do plano 03-01) — garante que cada teste falha individualmente com ImportError ao inves de erro de coleta global
- `perfil_unico` como fixture separada (nao reutiliza PERFIL_TESTE de seed_data) — evita acoplamento entre a suite de ingestao e a suite de seed data; campos fixos garantem reproducibilidade
- `colecao_temporaria` com `nome_colecao="test_ingestao"` — previne conflito de nome com outros testes que usam colecoes ChromaDB diferentes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## Next Phase Readiness

- Suite RED completa e pronta para guiar a implementacao de connect_ai/ingestao.py (Plano 04-02)
- Contrato de ingerir_perfil e ingerir_lote definido pelos testes: retornos tipados, idempotencia garantida, logs PT-BR obrigatorios

---
*Phase: 04-pipeline-de-ingestao*
*Completed: 2026-04-21*
