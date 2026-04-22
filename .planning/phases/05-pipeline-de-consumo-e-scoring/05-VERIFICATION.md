---
phase: 05-pipeline-de-consumo-e-scoring
verified: 2026-04-21T22:55:00Z
status: passed
score: 7/7 must-haves verified
re_verification: false
gaps: []
human_verification: []
---

# Phase 5: Pipeline de Consumo e Scoring — Verification Report

**Phase Goal:** Para o perfil de teste, o pipeline de consumo end-to-end — filtros hard -> busca vetorial Top-30 -> scoring ponderado 60/20/10/5/5 -> corte >= 85 — devolve 10 matches com score >= 85, com breakdown dos 5 fatores. Este e o gate critico da entrega.
**Verified:** 2026-04-21T22:55:00Z
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | connect_ai/scoring.py existe com as 6 funcoes publicas (5 fatores + calcular_score) | VERIFIED | Arquivo em disco, 179 linhas. grep retorna def em linhas 20, 37, 57, 73, 92, 108 |
| 2 | connect_ai/agentes.py exporta buscar_matches que orquestra o pipeline end-to-end | VERIFIED | `def buscar_matches` em linha 115; `from connect_ai.agentes import buscar_matches; print('OK')` imprime OK |
| 3 | _calcular_score_stub em agentes.py e substituido por chamada a calcular_score de scoring.py | VERIFIED | Linha 99 de agentes.py: `from connect_ai.scoring import calcular_score` dentro do stub |
| 4 | connect_ai/repositorio.py _metadata_de_perfil grava campo interesses_csv como string CSV | VERIFIED | Linha 139: `"interesses_csv": ",".join(perfil.interesses)` |
| 5 | python -m pytest tests/test_scoring.py retorna 20 passed | VERIFIED | `20 passed in 0.02s` confirmado |
| 6 | python -m pytest tests/test_consumo.py retorna 10 passed incluindo test_gate_critico_dez_matches_acima_85 | VERIFIED | `10 passed in 17.80s`; test_gate_critico_dez_matches_acima_85 PASSED confirmado |
| 7 | Suite completa (102 testes) continua 100% green | VERIFIED | `102 passed, 3 warnings in 22.88s` |

**Score: 7/7 truths verified**

---

### Required Artifacts

| Artifact | Expected | Level 1: Exists | Level 2: Substantive | Level 3: Wired | Status |
|----------|----------|-----------------|----------------------|----------------|--------|
| `connect_ai/scoring.py` | Modulo de scoring ponderado 60/20/10/5/5 com os 5 fatores | YES | 179 linhas, 6 funcoes publicas, formulas implementadas | Importado em agentes.py e test_scoring.py | VERIFIED |
| `connect_ai/agentes.py` | buscar_matches orquestrando pipeline completo de consumo | YES (modificado) | `def buscar_matches` em linha 115 com 72+ linhas de corpo | Importado em test_consumo.py; chamado com colecao real | VERIFIED |
| `connect_ai/repositorio.py` | Campo interesses_csv no metadata de cada perfil | YES (modificado) | `interesses_csv` na linha 139 do _metadata_de_perfil | Parseado em agentes.py linha 190: `meta.get("interesses_csv", "")` | VERIFIED |
| `tests/test_scoring.py` | 20 testes dos 5 fatores de scoring e composicao ponderada | YES | 229 linhas, 20 funcoes de teste com imports lazy | Referencia connect_ai.scoring, 20 lazy imports confirmados | VERIFIED |
| `tests/test_consumo.py` | 10 testes do pipeline de consumo end-to-end | YES | 224 linhas, 10 funcoes de teste + 2 fixtures | Referencia connect_ai.agentes.buscar_matches e repositorio | VERIFIED |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| connect_ai/agentes.py | connect_ai/scoring.py | `from connect_ai.scoring import calcular_score` | WIRED | Linhas 99 e 148 de agentes.py — import lazy dentro de _calcular_score_stub e buscar_matches |
| connect_ai/agentes.py | connect_ai/repositorio.py | `colecao.buscar(embedding_query, n_resultados=30, filtros=where)` | WIRED | Linha 177 de agentes.py: `candidatos = colecao.buscar(...)` |
| connect_ai/agentes.py | connect_ai/ingestao.py | `_gerar_embedding(construir_documento_semantico(perfil))` | WIRED | Linhas 149 e 164: `from connect_ai.ingestao import _gerar_embedding` + chamada |
| tests/test_scoring.py | connect_ai/scoring.py | `from connect_ai.scoring import ...` | WIRED | 20 lazy imports confirmados via grep -c |
| tests/test_consumo.py | connect_ai/agentes.py | `from connect_ai.agentes import buscar_matches` | WIRED | 8 lazy imports em funcoes de teste |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| CONS-01 | 05-01, 05-02 | Funcao buscar_matches que orquestra pipeline end-to-end | SATISFIED | `def buscar_matches` em agentes.py; test_buscar_matches_existe PASSED |
| CONS-02 | 05-01, 05-02 | Filtros hard via metadados ChromaDB (genero, objetivo) | SATISFIED | Filtros `$and` em agentes.py linhas 171-177; test_filtro_hard_genero e test_filtro_hard_objetivo PASSED |
| CONS-03 | 05-01, 05-02 | Busca vetorial Top-K (K=30) com cosine distance | SATISFIED | `colecao.buscar(..., n_resultados=30, ...)` linha 177; test_repositorio_busca_top30 PASSED |
| SCR-01 | 05-01, 05-02 | Score ponderado 60/20/10/5/5 em modulo scoring.py testavel isoladamente | SATISFIED | scoring.py com calcular_score; 20 testes unitarios passando |
| SCR-02 | 05-01, 05-02 | Cada componente do score com funcao propria, testada | SATISFIED | 5 funcoes individuais em scoring.py; 16 testes unitarios por fator passando |
| SCR-03 | 05-01, 05-02 | Score final normalizado 0-100 com truncamento explicito | SATISFIED | score_final em [0,100]; test_calcular_score_final_nao_negativo PASSED |
| SCR-04 | 05-01, 05-02 | Filtro final >= 85, retornando ate 10 candidatos | SATISFIED | `if breakdown["score_final"] >= 85.0` + `matches[:10]` em agentes.py; test_buscar_matches_maximo_dez PASSED |
| SCR-05 | 05-01, 05-02 | Output com id, score total, breakdown dos 5 fatores, dados de exibicao | SATISFIED | Dict com 11 chaves incluindo breakdown; test_buscar_matches_estrutura_dict PASSED |
| TEST-01 | 05-01, 05-02 | Testes unitarios do scoring.py cobrindo cada fator e composicao final | SATISFIED | 20 testes em test_scoring.py, todos PASSED |
| TEST-02 | 05-01, 05-02 | Teste de integracao garantindo 10 matches >= 85 para perfil de teste | SATISFIED | test_gate_critico_dez_matches_acima_85 PASSED |
| TEST-03 | 05-01, 05-02 | Teste do wrapper de repositorio (insert, search filtrado, reset) | SATISFIED | test_repositorio_busca_filtrada_por_genero e test_repositorio_busca_top30 PASSED |

**All 11 requirements satisfied. No orphaned requirements.**

---

### Anti-Patterns Found

No anti-patterns detected (TODO/FIXME/PLACEHOLDER/return null/return []) in any of the key files:
- connect_ai/scoring.py
- connect_ai/agentes.py
- connect_ai/repositorio.py
- tests/test_scoring.py
- tests/test_consumo.py

---

### Authorized Deviation: Formula Multiplier for score_interesses

The PLAN specifies the formula as `semantico*0.60 + interesses*0.20 + objetivo*0.10 + idade*0.05 + geografia*0.05` where all components are in `[0,100]`.

The implementation uses `s_interesses * 1.0` because `score_interesses` returns values in `[0,20]` (not `[0,100]`). These are mathematically equivalent for the weighted contribution (20 points max). This deviation was:

1. Discovered during Task 3 of Plan 02 (gate was mathematically impossible with 0.20 on a [0,20] scale)
2. Explicitly approved by the user
3. Documented in 05-02-SUMMARY.md under "Deviations from Plan"
4. All 20 scoring tests updated to reflect the corrected formula and pass

**Verdict: Authorized, documented, functionally correct.**

---

### Human Verification Required

None — all observable truths were verified programmatically. The gate critical test (`test_gate_critico_dez_matches_acima_85`) serves as the integration proof for the end-to-end pipeline behavior.

---

## Summary

Phase 5 goal is fully achieved. The end-to-end pipeline for PERFIL_TESTE delivers:

- Hard filters on gender and objective applied via ChromaDB metadata (CONS-02)
- Vectorial search Top-30 (CONS-03)
- Weighted scoring 60/20/10/5/5 with breakdown of all 5 factors (SCR-01 to SCR-05)
- Score cutoff >= 85 returning up to 10 matches (SCR-04)
- The critical gate test confirms >= 10 matches with score >= 85 (TEST-02)

Full test suite: **102/102 tests passing, zero regressions**.

---

_Verified: 2026-04-21T22:55:00Z_
_Verifier: Claude (gsd-verifier)_
