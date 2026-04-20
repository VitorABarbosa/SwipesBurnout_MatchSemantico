---
phase: 02-seed-data-sintetico
plan: "02"
subsystem: testing
tags: [seed-data, pydantic, random, pytest, tdd]

# Dependency graph
requires:
  - phase: 02-01
    provides: suite TDD RED com 5 testes para seed_data (todos falhando com ModuleNotFoundError)
  - phase: 01-02
    provides: Perfil model e gerar_uuid em connect_ai/schema.py
provides:
  - connect_ai/seed_data.py com SEED_FIXA=42, PERFIL_TESTE e gerar_pool_perfis()
  - Pool de 100 perfis sinteticos reproduziveis (seed=42)
  - Garantia matematica de >= 10 perfis compativeis com PERFIL_TESTE
affects:
  - fase-03-agente-perfilador
  - fase-05-pipeline-compatibilidade

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "random.Random(seed) local — instancia isolada, sem side-effects no estado global"
    - "20 perfis alta-compat + 80 diversidade = pool calibrado de 100 perfis"
    - "IDs deterministicos: seed-compat-XXXX e seed-diverso-XXXX"

key-files:
  created:
    - connect_ai/seed_data.py
  modified: []

key-decisions:
  - "random.Random(seed) local em vez de random.seed() global — evita side-effects em testes paralelos e garante reproducibilidade isolada"
  - "20 perfis de alta-compat (garantia SEED-02) + 80 de diversidade (SEED-01) com shuffle ao final para nao ter bias posicional"
  - "Interesses fixos: 3 sorteados de _INTERESSES_ALTA_COMPAT para garantir intersecao >= 3 com PERFIL_TESTE sem hard-code individual"
  - "IDs deterministicos (seed-compat-XXXX, seed-diverso-XXXX) em vez de gerar_uuid() — evita nao-determinismo nos IDs do pool"

patterns-established:
  - "Pool calibrado: separar subconjunto de alta compatibilidade (20%) do subconjunto de diversidade (80%)"
  - "Constantes de modulo para listas de dados sinteticos — nao-aleatorias, sempre legíveis no fonte"

requirements-completed:
  - SEED-01
  - SEED-02
  - SEED-03
  - SEED-04

# Metrics
duration: 5min
completed: 2026-04-20
---

# Phase 2 Plan 02: Seed Data Sintetico Summary

**Pool de 100 perfis sinteticos reproduziveis com seed=42 em connect_ai/seed_data.py — 20 de alta compatibilidade garantem >= 10 matches estruturais com PERFIL_TESTE (Ana Lima, namoro, 27 anos)**

## Performance

- **Duration:** 5 min
- **Started:** 2026-04-20T20:10:00Z
- **Completed:** 2026-04-20T20:15:00Z
- **Tasks:** 1 (TDD GREEN)
- **Files modified:** 1

## Accomplishments

- Implementou connect_ai/seed_data.py com SEED_FIXA=42, PERFIL_TESTE explicito e gerar_pool_perfis()
- 5/5 testes de test_seed_data.py passando: reproducibilidade, perfil_teste, pool_100, 10_compat, diversidade
- 51/51 testes da suite completa passando sem nenhuma regressao
- Pool calibrado: 20 perfis de alta-compatibilidade com PERFIL_TESTE + 80 de diversidade geografica/demografica

## Task Commits

1. **Tarefa 1: Implementar connect_ai/seed_data.py (fase GREEN)** - `4e0430a` (feat)

**Plan metadata:** (pendente — criado junto com SUMMARY.md)

## Files Created/Modified

- `connect_ai/seed_data.py` — Gerador de perfis sinteticos com SEED_FIXA, PERFIL_TESTE e gerar_pool_perfis()

## Decisions Made

- `random.Random(seed)` local em vez de `random.seed()` global: evita side-effects em testes paralelos; cada chamada a `gerar_pool_perfis(seed)` e completamente isolada
- 20 perfis de alta-compat + 80 de diversidade + shuffle ao final: garante SEED-02 (>= 10 compativeis) sem vies posicional no pool
- 3 interesses sorteados de `_INTERESSES_ALTA_COMPAT` por perfil de alta-compat: garante intersecao >= 3 com PERFIL_TESTE de forma robusta sem hard-code excessivo
- IDs deterministicos (`seed-compat-XXXX`, `seed-diverso-XXXX`) em vez de `gerar_uuid()`: manter reproducibilidade total do pool, incluindo os IDs

## Deviations from Plan

None — plano executado exatamente como especificado. Todos os 5 testes passaram na primeira execucao.

## Issues Encountered

None.

## User Setup Required

None — nenhuma configuracao de servico externo necessaria. seed_data.py e completamente offline e deterministico.

## Self-Check

- [x] connect_ai/seed_data.py existe e e importavel
- [x] SEED_FIXA = 42 definida
- [x] PERFIL_TESTE.nome == "Ana Lima", idade == 27, objetivo == "namoro"
- [x] gerar_pool_perfis() retorna >= 100 perfis validos
- [x] Duas chamadas com seed=42 retornam pool identico
- [x] >= 10 perfis compativeis com PERFIL_TESTE (analise estrutural)
- [x] Pool cobre >= 5 cidades, 3 objetivos, idades 18-60+
- [x] 5/5 testes de test_seed_data.py passando
- [x] 51/51 testes da suite completa passando (sem regressoes)
- [x] Commit 4e0430a existe

## Next Phase Readiness

- Fase 3 (Agente Perfilador) pode importar `PERFIL_TESTE` e `gerar_pool_perfis()` diretamente
- Fase 5 (gate critico: score >= 85) tem garantia matematica de >= 10 matches estruturais disponiveis no pool
- Sem bloqueadores conhecidos para avanco as proximas fases

---
*Phase: 02-seed-data-sintetico*
*Completed: 2026-04-20*
