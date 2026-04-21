---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Em execução
last_updated: "2026-04-21T21:38:57.769Z"
progress:
  total_phases: 7
  completed_phases: 4
  total_plans: 11
  completed_plans: 11
---

# Estado do Projeto

## Referência do Projeto

Ver: .planning/PROJECT.md (atualizado em 2026-04-19)

**Valor central:** Para qualquer perfil submetido, devolver 10 matches com score de compatibilidade ≥ 85, com breakdown dos fatores e justificativa textual gerada por IA.
**Foco atual:** Fase 5 — Scoring e Consumo (proxima fase)

## Posição Atual

Fase: 4 de 7 (Pipeline de Ingestao — CONCLUIDA)
Plano: 2 de 2 na fase atual (04-02 concluído — GREEN para connect_ai/ingestao.py)
Status: Em execução
Última atividade: 2026-04-21 — Plano 04-02 concluído (connect_ai/ingestao.py implementado com ingerir_perfil e ingerir_lote; 6/6 testes GREEN, 72 testes da suite completa passando)

Progresso: [██████████] 100%

## Métricas de Desempenho

**Velocidade:**
- Total de planos concluídos: 7
- Duração média: ~2.5 min
- Tempo total de execução: 20 min

**Por Fase:**

| Fase | Planos | Total | Média/Plano |
|------|--------|-------|-------------|
| 1    | 3      | 9 min | 3 min       |
| 2    | 2      | 6 min | 3 min       |
| 3    | 3      | 13 min | 4.3 min     |

**Tendência Recente:**
- Últimos 5 planos: 02-02 (5 min), 03-01 (5 min), 03-02 (3 min), 03-03 (5 min)
- Tendência: estável (~1-5 min por plano)

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
- 01-04: README como arquivo único (em vez de docs/ multi-arquivo) — escopo de CP5 não justifica fragmentação
- 01-04: Forward references explícitas para `app/streamlit_app.py` e `notebook/demo_cp5.ipynb` com nota "(criado nas fases seguintes)" — evita reescrever README a cada fase
- 01-04: Instruções de venv para 3 plataformas (Linux/macOS, Windows PowerShell, Windows Git Bash) — equipe usa Windows mas avaliador pode usar Mac/Linux
- 01-04: Troubleshooting cita erros reais já codificados (`ConfigError` do 01-01, `get_or_create_collection` do 01-03) — alinha doc com mensagens reais do código
- 02-01: Análise estatica pura (sem ChromaDB) para test_pool_tem_10_compativeis — criterios: interesses_em_comum >= 3 + objetivo == "namoro" + faixa_etaria_pref cobre idade 27
- 02-01: PERFIL_TESTE campos fixos documentados: nome="Ana Lima", objetivo="namoro", idade=27, >= 5 interesses incluindo musica e viagem
- 02-02: `random.Random(seed)` local em vez de `random.seed()` global — reproducibilidade isolada sem side-effects em testes paralelos
- 02-02: 20 perfis alta-compat + 80 diversidade + shuffle — garante SEED-02 (>= 10 compativeis) sem vies posicional no pool
- 02-02: IDs deterministicos (`seed-compat-XXXX`, `seed-diverso-XXXX`) em vez de `gerar_uuid()` — reproducibilidade total incluindo IDs
- 03-01: AgentState como dict TypedDict-style com 5 campos (perfil, candidatos, matches, justificativas, erro) verificado via operador `in` nos testes
- 03-01: `salvar_visualizacao_grafo` gera .mmd (Mermaid) sempre; .png opcional — testes validam apenas .mmd para evitar dependencia de graphviz
- 03-01: Imports lazy em test_grafo.py (dentro das funcoes de teste) para garantir que cada teste falha individualmente em RED
- 03-02: _cache_personalidade como dict global em vez de functools.lru_cache — Pydantic BaseModel nao e hashavel; dict keyed por perfil.id e mais simples e igualmente deterministico
- 03-02: _calcular_score_stub retorna 90.0 hardcoded para todos os candidatos — substituido na Fase 5 por scoring ponderado com pesos 60/20/10/5/5
- 03-02: agente_casamenteiro importa gerar_pool_perfis lazily (dentro da funcao) — evita dependencia circular no nivel de modulo
- 03-03: pipeline_consumo compilado no nivel de modulo — importado diretamente pelo Streamlit (Fase 6) e notebook (Fase 7)
- 03-03: salvar_visualizacao_grafo silencia excecao do PNG — .mmd e o artefato confiavel; .png e bonus quando graphviz presente
- 04-01: Imports lazy em test_ingestao.py (dentro das funcoes de teste) — replica padrao do 03-01 para garantir RED individual por teste
- 04-01: perfil_unico com campos fixos (id="test-ing-001") em vez de PERFIL_TESTE — evita acoplamento entre suites de teste
- 04-01: colecao_temporaria usa tmp_path + nome_colecao="test_ingestao" — isolamento total sem conflito com outros testes
- 04-02: Mock de embedding via hashlib.md5 (deterministico, 768d) — fallback gracioso quando GOOGLE_API_KEY ausente sem quebrar reproducibilidade
- 04-02: ingerir_lote itera ingerir_perfil individualmente — cada perfil gera seu embedding separado; falhas individuais nao abortam lote
- 04-02: genai.configure() chamado dentro de _gerar_embedding (nao no nivel de modulo) — evita efeito colateral global ao importar sem GOOGLE_API_KEY
- 04-02: obter_chave_api("GOOGLE_API_KEY", padrao="") em vez de os.environ.get() — centraliza leitura de env no config e carrega .env automaticamente

### Pendências (Todos)

Nenhuma ainda.

### Bloqueadores / Preocupações

- **Fase 5 (gate crítico):** A viabilidade do threshold ≥ 85 precisa ser validada empiricamente. Se falhar, o procedimento é retornar à Fase 2 para recalibrar o seed data antes de avançar.
- **Fase 2 RESOLVIDA:** Pool calibrado entregue — 20 perfis de alta-compat garantem >= 10 matches estruturais com PERFIL_TESTE. Gate da Fase 5 tem base matematica.

## Continuidade da Sessão

Última sessão: 2026-04-21
Parou em: Concluído 04-02-PLAN.md — connect_ai/ingestao.py implementado com ingerir_perfil e ingerir_lote; ING-01..ING-04 fechados com 6/6 testes GREEN; 72 testes da suite completa passando. Proxima fase: 05 — Scoring e Consumo.
Arquivo de retomada: Nenhum
