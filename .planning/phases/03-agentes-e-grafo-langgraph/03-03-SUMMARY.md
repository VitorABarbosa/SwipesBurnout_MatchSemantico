---
phase: 03-agentes-e-grafo-langgraph
plan: "03"
subsystem: agents
tags: [langgraph, stategraph, mermaid, pipeline, agentes, grafo]

# Dependency graph
requires:
  - phase: 03-02
    provides: AgentState TypedDict + agente_perfilador + agente_casamenteiro + agente_rag_justificador
  - phase: 03-01
    provides: test contracts (tests/test_grafo.py) defining pipeline_consumo and salvar_visualizacao_grafo contracts
provides:
  - connect_ai/grafo.py with pipeline_consumo (CompiledStateGraph) and salvar_visualizacao_grafo()
  - relatorio/grafo_pipeline.mmd — Mermaid diagram of the 3-node pipeline
  - relatorio/grafo_pipeline.png — PNG render of pipeline (graphviz available in environment)
affects: [04-pipeline-ingestao, 05-scoring, 06-streamlit, 07-entregaveis]

# Tech tracking
tech-stack:
  added: [langgraph.graph.StateGraph, langgraph.graph.START, langgraph.graph.END]
  patterns:
    - StateGraph compiled to pipeline_consumo at module level (importable directly)
    - salvar_visualizacao_grafo silences PNG exceptions — .mmd always generated, .png optional
    - Lazy imports in test functions (test_grafo.py) to isolate per-test failures in RED phase

key-files:
  created:
    - connect_ai/grafo.py
    - relatorio/grafo_pipeline.mmd
    - relatorio/grafo_pipeline.png
  modified: []

key-decisions:
  - "pipeline_consumo compiled at module import time — allows direct import by Streamlit (Fase 6) and notebook (Fase 7)"
  - "salvar_visualizacao_grafo silences PNG exception — .mmd is always the reliable artefact; .png is bonus when graphviz present"
  - "graphviz was available in the environment — both .mmd and .png generated successfully"

patterns-established:
  - "Module-level compiled graph: pipeline_consumo = _grafo.compile() at module top — no factory function needed"
  - "Visualization: .mmd (text, no deps) + .png (optional, silenced exception) — always at least one artifact"

requirements-completed: [AGT-05, AGT-06, AGT-07]

# Metrics
duration: 5min
completed: 2026-04-20
---

# Phase 3 Plan 03: Grafo LangGraph Summary

**StateGraph LangGraph compilado com 3 nos (perfilador -> casamenteiro -> rag_justificador), pipeline_consumo exportado e artefato Mermaid gerado em relatorio/**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-04-20T21:00:00Z
- **Completed:** 2026-04-20T21:05:00Z
- **Tasks:** 2
- **Files modified:** 3 (created: connect_ai/grafo.py, relatorio/grafo_pipeline.mmd, relatorio/grafo_pipeline.png)

## Accomplishments

- connect_ai/grafo.py implementado (83 linhas) com StateGraph LangGraph: 3 nos em sequencia START -> perfilador -> casamenteiro -> rag_justificador -> END
- pipeline_consumo compilado e verificado: .invoke() funcional, .get_graph().nodes.keys() contem os 3 nos
- salvar_visualizacao_grafo() cria diretorio automaticamente, salva .mmd sempre, tenta .png silenciando excecao se graphviz ausente
- relatorio/grafo_pipeline.mmd gerado com texto Mermaid valido contendo os 3 nos
- relatorio/grafo_pipeline.png tambem gerado (graphviz disponivel no ambiente de execucao)
- Suite completa: 66/66 testes passando sem regressoes (51 anteriores + 10 test_agentes + 5 test_grafo)

## Task Commits

Cada tarefa foi commitada atomicamente:

1. **Tarefa 1: Implementar connect_ai/grafo.py (GREEN para test_grafo.py)** - `8bd97e8` (feat)
2. **Tarefa 2: Gerar artefato de visualizacao em relatorio/ e validar suite completa** - `106fb80` (feat)

**Plan metadata:** (a ser gerado apos state update)

## Files Created/Modified

- `connect_ai/grafo.py` (83 linhas) — StateGraph com 3 nos, pipeline_consumo compilado, salvar_visualizacao_grafo()
- `relatorio/grafo_pipeline.mmd` (18 linhas) — Diagrama Mermaid do pipeline (AGT-06)
- `relatorio/grafo_pipeline.png` — Render PNG do pipeline (graphviz disponivel)

## Conteudo relatorio/grafo_pipeline.mmd (primeiras 10 linhas)

```
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	perfilador(perfilador)
	casamenteiro(casamenteiro)
	rag_justificador(rag_justificador)
```

## Decisions Made

- pipeline_consumo compilado no nivel de modulo (nao em funcao factory) — facilita importacao direta pelo Streamlit e notebook sem necessidade de instanciar
- salvar_visualizacao_grafo silencia excecao do PNG — .mmd e o artefato confiavel; .png e bonus quando graphviz presente
- graphviz estava disponivel no ambiente — ambos .mmd e .png gerados com sucesso

## Nota sobre dependencias para PNG (Fase 7 — Entregaveis)

- `.mmd` (Mermaid text): sem dependencias extras, sempre gerado
- `.png`: requer `graphviz` instalado no sistema OU `pillow` + cliente Mermaid online
- Para garantir PNG na Fase 7, verificar `pip install Pillow` e graphviz no PATH
- Se indisponivel, o .mmd e suficiente para visualizacao no GitHub e no relatorio PDF

## Decisoes que afetam a Fase 4 (Pipeline de Ingestao) e Fase 5 (Scoring)

- **AgentState fica estavel**: os 5 campos (perfil, candidatos, matches, justificativas, erro) sao o contrato publico do grafo. Fase 4 nao modifica AgentState.
- **stub do Casamenteiro sera substituido na Fase 5**: _calcular_score_stub retorna 90.0 hardcoded. Fase 5 implementa connect_ai.scoring com pesos 60/20/10/5/5.
- **agente_casamenteiro importa gerar_pool_perfis lazily**: a Fase 4 substitui por busca vetorial real via Repositorio — o import lazy facilita a substituicao sem dependencia circular.
- **pipeline_consumo e o ponto de entrada do Streamlit (Fase 6)**: importado diretamente como `from connect_ai.grafo import pipeline_consumo`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - todos os testes passaram na primeira execucao. graphviz disponivel no ambiente permitiu gerar tambem o PNG (alem do .mmd obrigatorio).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Fase 3 completamente concluida: AgentState + 3 agentes + grafo compilado + visualizacao gerada
- Fase 4 (Pipeline de Ingestao) pode comecar: connect_ai/agentes.py e connect_ai/grafo.py estao estaveis
- connect_ai/repositorio.py (criado na Fase 1) e o proximo ponto de integracao
- Gate da Fase 5: validar threshold >= 85 empiricamente apos ingestao real

---
*Phase: 03-agentes-e-grafo-langgraph*
*Completed: 2026-04-20*
