---
phase: 04-pipeline-de-ingestao
plan: "02"
subsystem: ingestao
tags: [python, chromadb, pydantic, google-generativeai, hashlib, logging, tdd-green]

# Dependency graph
requires:
  - phase: 04-01
    provides: Suite RED de 6 testes cobrindo ING-01..ING-04 (test_ingestao.py)
  - phase: 03-agentes-e-grafo-langgraph
    provides: agente_perfilador, AgentState
  - phase: 01-fundacao
    provides: Repositorio (upsert idempotente), Perfil, construir_documento_semantico, obter_chave_api
provides:
  - connect_ai/ingestao.py com ingerir_perfil e ingerir_lote implementados
  - Pipeline de ingestao completo cobrindo ING-01..ING-04 (6/6 testes GREEN)
  - Embedding deterministico via hashlib.md5 quando GOOGLE_API_KEY ausente
  - Idempotencia garantida via colecao.inserir (upsert do Repositorio)
affects: [05-scoring-e-consumo, 06-front-streamlit, 07-notebook]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mock de embedding via hashlib.md5 (vetor 768d deterministico) quando API ausente"
    - "obter_chave_api com padrao='' para fallback gracioso sem levantar ConfigError"
    - "try/except Exception em ingerir_perfil para captura de falhas individuais no lote"
    - "Logger de modulo com mensagens PT-BR; nenhum print()"

key-files:
  created:
    - connect_ai/ingestao.py
  modified: []

key-decisions:
  - "Mock de embedding via hashlib.md5 (deterministico, reproducivel) em vez de vetor zero — vetor zero causaria colisao semantica entre todos os perfis no ChromaDB"
  - "obter_chave_api('GOOGLE_API_KEY', padrao='') em vez de os.environ.get() — centraliza leitura de env no modulo config e carrega .env automaticamente"
  - "ingerir_lote itera ingerir_perfil individualmente (nao usa Repositorio.inserir_lote) — cada perfil tem seu proprio embedding calculado; tratamento de falha individual"
  - "genai.configure() chamado dentro de _gerar_embedding (nao no nivel de modulo) — evita efeito colateral global ao importar o modulo sem GOOGLE_API_KEY"

patterns-established:
  - "Pipeline de ingestao: Perfilador → construir_documento_semantico → embedding → upsert"
  - "Fallback de embedding: checar api_key vazia antes de chamar genai.configure()"

requirements-completed: [ING-01, ING-02, ING-03, ING-04]

# Metrics
duration: 8min
completed: 2026-04-21
---

# Phase 4 Plan 02: Pipeline de Ingestao GREEN Summary

**Pipeline de ingestao implementado em connect_ai/ingestao.py com embedding via google.generativeai (text-embedding-004) e fallback deterministico hashlib.md5 — 6/6 testes TDD GREEN, 72 testes da suite completa passando**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-21T21:35:00Z
- **Completed:** 2026-04-21T21:43:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Criado connect_ai/ingestao.py com 171 linhas cobrindo ING-01..ING-04 completamente
- 6/6 testes de tests/test_ingestao.py passam GREEN (ModuleNotFoundError -> 6 passed)
- Suite completa com 72 testes passa sem regressoes
- Idempotencia confirmada: re-ingerir mesmo lote nao altera contagem (colecao.contar() estavel)
- Banco nao vazio confirmado: colecao.buscar([0.1]*768, n_resultados=1) retorna resultado

## Estrutura de connect_ai/ingestao.py

| Elemento | Linhas aprox. | Descricao |
|----------|--------------|-----------|
| Docstring de modulo | 1-23 | PT-BR descrevendo ING-01..ING-04 |
| Imports | 25-37 | google.generativeai, agentes, config, repositorio, schema |
| `logger` | 40 | Logger de modulo via logging.getLogger(__name__) |
| `_gerar_embedding(texto)` | 43-85 | Mock hashlib.md5 (768d) ou API Google text-embedding-004 |
| `ingerir_perfil(perfil, colecao)` | 88-131 | Perfilador → embedding → upsert; retorna {sucesso, id, erro} |
| `ingerir_lote(perfis, colecao)` | 134-171 | Itera ingerir_perfil; retorna {sucesso, falha, total} |

## Resultado Final do pytest

```
tests/test_ingestao.py::test_ingerir_perfil_retorna_dict PASSED
tests/test_ingestao.py::test_ingerir_perfil_persiste_no_chromadb PASSED
tests/test_ingestao.py::test_ingerir_lote_retorna_dict_com_contagens PASSED
tests/test_ingestao.py::test_ingerir_lote_todos_perfis_inseridos PASSED
tests/test_ingestao.py::test_ingerir_perfil_emite_log_ptbr PASSED
tests/test_ingestao.py::test_idempotencia_nao_duplica PASSED
========================= 6 passed, 2 warnings in 4.17s =========================

========================= 72 passed, 3 warnings in 6.30s ======================== (suite completa)
```

## Task Commits

1. **Task 1: Implementar connect_ai/ingestao.py (GREEN)** - `6a95809` (feat)

**Plan metadata:** (docs commit abaixo)

## Files Created/Modified

- `connect_ai/ingestao.py` — Pipeline de ingestao com ingerir_perfil, ingerir_lote, _gerar_embedding (171 linhas)

## Decisions Made

- Mock de embedding via hashlib.md5 (deterministico, reproducivel) em vez de vetor zero ou random — vetor zero causaria colisao semantica no ChromaDB; vetor random quebraria reproducibilidade dos testes
- `obter_chave_api("GOOGLE_API_KEY", padrao="")` em vez de `os.environ.get()` — centraliza leitura de env e carrega .env automaticamente via dotenv
- `ingerir_lote` itera `ingerir_perfil` individualmente (nao usa `Repositorio.inserir_lote`) — cada perfil precisa do seu proprio embedding calculado sequencialmente; tratamento de falha individual preserva lote parcial
- `genai.configure()` chamado apenas dentro de `_gerar_embedding` — evita efeito colateral global ao importar o modulo sem GOOGLE_API_KEY

## Confirmacao dos 3 Criterios de Sucesso da Fase 4

| Criterio | Status | Evidencia |
|----------|--------|-----------|
| ING-01..ING-04: 6/6 testes GREEN | CONFIRMADO | `6 passed, 0 failed` |
| Idempotencia: re-ingestao nao duplica | CONFIRMADO | `Idempotencia OK: 5 documentos antes e depois` |
| Banco nao vazio apos lote | CONFIRMADO | `Banco nao vazio: 5 perfis, busca retornou 1 resultado(s)` |

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- FutureWarning sobre `google.generativeai` deprecado (migracao para `google.genai` recomendada) — apenas warning, nao afeta funcionamento; a migracao esta fora do escopo desta fase.
- PermissionError do Windows ao deletar diretorio temporario com ChromaDB aberto — comportamento esperado do Windows (lock de arquivo); nao afeta resultados dos testes; todos os criteiros foram confirmados antes do cleanup.

## Next Phase Readiness

- connect_ai/ingestao.py pronto para ser chamado pela Fase 5 (pipeline de consumo)
- Fase 4 concluida: ING-01..ING-04 fechados, suite RED->GREEN completa
- Proximo: Fase 5 — Scoring e Consumo (substituir _calcular_score_stub por scoring ponderado 60/20/10/5/5)

---
*Phase: 04-pipeline-de-ingestao*
*Completed: 2026-04-21*
