# Estado do Projeto

## Referência do Projeto

Ver: .planning/PROJECT.md (atualizado em 2026-04-19)

**Valor central:** Para qualquer perfil submetido, devolver 10 matches com score de compatibilidade ≥ 85, com breakdown dos fatores e justificativa textual gerada por IA.
**Foco atual:** Fase 1 — Fundação

## Posição Atual

Fase: 1 de 7 (Fundação)
Plano: 2 de 4 na fase atual
Status: Em execução
Última atividade: 2026-04-19 — Plano 01-02 concluído (schema Pydantic `Perfil` + `construir_documento_semantico` com 19 testes passando)

Progresso: [██░░░░░░░░] 8%

## Métricas de Desempenho

**Velocidade:**
- Total de planos concluídos: 2
- Duração média: 3.5 min
- Tempo total de execução: 7 min

**Por Fase:**

| Fase | Planos | Total | Média/Plano |
|------|--------|-------|-------------|
| 1    | 2      | 7 min | 3.5 min     |

**Tendência Recente:**
- Últimos 5 planos: 01-01 (4 min), 01-02 (3 min)
- Tendência: estável (~3-4 min por plano)

*Atualizado após cada conclusão de plano*

## Contexto Acumulado

### Decisões

Decisões registradas em PROJECT.md — tabela "Key Decisions".
Decisões relevantes para o trabalho atual:

- Inicialização: Mocks textuais para Gemini Vision (custo zero, determinístico)
- Inicialização: Estrutura modular `connect_ai/` + Streamlit + notebook fino
- Inicialização: Modo YOLO + granularidade Standard + execução sequencial
- 01-01: Build-backend `setuptools` (em vez de hatch/poetry) — mais simples e estável para `pip install -e .`
- 01-01: Lower bounds nas dependências (sem upper) — facilita reprodutibilidade no Colab
- 01-01: `app/` excluído do pacote `connect_ai` — Streamlit roda via `streamlit run app/streamlit_app.py`
- 01-01: ChromaDB em modo embedded (sem `chromadb-client`)
- 01-01: `ConfigError` subclasse de `RuntimeError` — captura específica + mensagem PT-BR substitui `KeyError` cru
- 01-02: `Literal` (em vez de `Enum`) para `Genero`/`GeneroPreferido`/`Objetivo` — Pydantic-nativo, serializa string limpa para metadata
- 01-02: `personalidade_ia` opcional (default `None`) — Perfilador (Fase 3) preenche; separa "ainda não processado" de "processado e vazio"
- 01-02: `genero_preferido` aceita `"todos"` — modela "sem preferência" explicitamente para o filtro hard
- 01-02: `construir_documento_semantico` é a fonte ÚNICA da verdade do texto enviado ao `text-embedding-004` — divergência entre ingestão e consumo invalida o threshold ≥ 85
- 01-02: Função omite seção `"Personalidade"` quando vazia — defesa contra vazamento de `"None"` no embedding

### Pendências (Todos)

Nenhuma ainda.

### Bloqueadores / Preocupações

- **Fase 5 (gate crítico):** A viabilidade do threshold ≥ 85 precisa ser validada empiricamente. Se falhar, o procedimento é retornar à Fase 2 para recalibrar o seed data antes de avançar.
- **Fase 2:** A calibragem do seed data (distribuição de interesses, cidades, objetivos) é decisão crítica que impacta diretamente o gate da Fase 5.

## Continuidade da Sessão

Última sessão: 2026-04-19
Parou em: Concluído 01-02-PLAN.md — schema Pydantic `Perfil` + função canônica `construir_documento_semantico` com 19 testes passando (27 ao todo na suíte). Próximo: 01-03 (repositório ChromaDB).
Arquivo de retomada: Nenhum
