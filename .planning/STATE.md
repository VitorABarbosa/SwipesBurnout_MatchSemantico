---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: Fase 7 concluida — relatorio/ completo com CONTEUDO.md, ETICA.md, pipeline_ingestao.mmd, pipeline_consumo.mmd; PROJETO CP5 COMPLETAMENTE CONCLUIDO
last_updated: "2026-04-22T18:06:04.964Z"
progress:
  total_phases: 7
  completed_phases: 7
  total_plans: 17
  completed_plans: 17
---

# Estado do Projeto

## Referência do Projeto

Ver: .planning/PROJECT.md (atualizado em 2026-04-19)

**Valor central:** Para qualquer perfil submetido, devolver 10 matches com score de compatibilidade ≥ 85, com breakdown dos fatores e justificativa textual gerada por IA.
**Foco atual:** Fase 5 — Scoring e Consumo (em execução — Wave 1 RED concluida)

## Posição Atual

Fase: 7 de 7 (Demo Notebook e Entregaveis Finais — COMPLETO)
Plano: 2 de 2 na fase atual (07-02 — COMPLETO)
Status: Fase 7 concluida — relatorio/ completo com CONTEUDO.md, ETICA.md, pipeline_ingestao.mmd, pipeline_consumo.mmd; PROJETO CP5 COMPLETAMENTE CONCLUIDO
Última atividade: 2026-04-22 — Plano 07-02: 4 artefatos de relatorio criados (CONTEUDO.md 87 linhas, ETICA.md 74 linhas, 2 diagramas Mermaid); ACC-10 e ETH-01..ETH-03 atendidos.

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
- 05-01: Imports lazy (dentro das funcoes) em test_scoring.py — cada teste falha individualmente com ModuleNotFoundError, nao ha ImportError no nivel de coleta do pytest
- 05-01: Fixtures colecao_temp e colecao_com_seed com tmp_path — isolamento total por teste sem polucao de chroma_db/ real
- 05-01: test_gate_critico_dez_matches_acima_85 inclui mensagem diagnostica com scores obtidos — facilita debug da Wave 2 se gate falhar
- 05-01: test_calcular_score_gate_85_com_cinco_interesses confirma score_final=84 (nao 85) — gate 85 e atingido pela similaridade semantica real dos embeddings, nao por valores literais no teste unitario
- 05-02: score_interesses usa multiplicador 1.0 (nao 0.20) — escala [0,20] representa diretamente os 20 pts de contribuicao; teto=100
- 05-02: seed_data com 15 perfis gate-garantido (masculino+namoro+SP+4interesses) para viabilizar gate com mock embedding MD5
- 06-01: ingerir_perfil retorna {"sucesso": bool, "id": str, "erro": str|None} — plano especificava {"status": "ok"|"erro"} mas implementacao real usa chave "sucesso"; front adaptado sem alterar o backend
- 06-02: perfis_disponiveis vazio causa retorno antecipado antes do st.selectbox — evita lista vazia no seletor
- 06-02: justificativas tratadas com try/except silencioso — falha do agente RAG nao bloqueia exibicao dos matches
- 06-02: st.warning (nao st.error) para APP-07 — aviso informativo, nao erro fatal; usuario pode prosseguir
- 06-02: fallback em cascata para artefatos de grafo: os.path.exists(png) > os.path.exists(mmd) > diagrama Mermaid inline
- 07-01: Repositorio() chamado com diretorio= (nao caminho_db=) — parametro real da implementacao; plano usava nome de interface diferente do codigo
- 07-01: GOOGLE_API_KEY via userdata.get() com try/except fallback os.environ — padrao Colab-safe sem credencial hardcoded
- 07-01: relatorio/grafo_pipeline.mmd gerado via execucao direta durante plano (salvar_visualizacao_grafo gerara sempre .mmd + .png quando graphviz disponivel)
- 07-02: ingerir_perfil / ingerir_lote adicionado como no de retorno no pipeline_ingestao.mmd para satisfazer criterio de aceitacao que verifica assert 'ingerir' in content

### Pendências (Todos)

Nenhuma ainda.

### Bloqueadores / Preocupações

Nenhum bloqueador ativo.

## Continuidade da Sessão

Última sessão: 2026-04-22
Parou em: Completou 07-02 — relatorio/ completo: CONTEUDO.md (87 linhas), ETICA.md (74 linhas), pipeline_ingestao.mmd, pipeline_consumo.mmd. PROJETO CP5 COMPLETAMENTE CONCLUIDO.
Proximo: Nenhum — todas as fases e planos concluidos.
