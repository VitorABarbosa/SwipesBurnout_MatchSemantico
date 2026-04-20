# Roadmap: CONNECT.AI (CP5)

## Visão Geral

O projeto parte do zero (greenfield) e entrega, em 7 fases sequenciais, um pipeline multi-agente completo que devolve 10 matches com score ≥ 85 para qualquer perfil submetido. As fases foram derivadas das categorias naturais de requisitos: fundação técnica → seed calibrado → agentes LangGraph → ingestão → consumo+scoring (gate crítico) → front Streamlit → demo e entregáveis finais. Cada fase entrega uma capacidade coerente e verificável.

> **Gate crítico:** Fase 5 — Pipeline de Consumo e Scoring. Se o threshold de 10 matches ≥ 85 não for atingido empiricamente, o procedimento é retornar à Fase 2 para recalibrar o seed data antes de avançar para as Fases 6 e 7.

---

## Fases

- [ ] **Fase 1: Fundação** - Estrutura do pacote, ambiente, schema de dados e repositório ChromaDB prontos para uso
- [ ] **Fase 2: Seed Data Sintético** - Pool de perfis sintéticos calibrado matematicamente para garantir ≥ 10 matches com score ≥ 85 para o perfil de teste
- [ ] **Fase 3: Agentes e Grafo LangGraph** - Três agentes distintos (Perfilador, Casamenteiro, RAG Justificador) montados no grafo com AgentState compartilhado
- [ ] **Fase 4: Pipeline de Ingestão** - Fluxo completo de cadastro: validação → Perfilador → embedding → ChromaDB
- [ ] **Fase 5: Pipeline de Consumo e Scoring** ⚠️ GATE CRÍTICO - Filtros hard → busca vetorial Top-30 → scoring ponderado → threshold ≥ 85 → 10 matches verificados empiricamente
- [ ] **Fase 6: Front Streamlit** - Interface de cadastro, visualização de matches e grafo acessível via `streamlit run`
- [ ] **Fase 7: Demo, Notebook e Entregáveis Finais** - Notebook Colab end-to-end, visualizações, insumos para relatório, ética e LGPD

---

## Detalhes das Fases

### Phase 1: Fundação
**Objetivo**: Toda a infraestrutura base está pronta — pacote Python instalável, ambiente reproduzível, schema de dados validado e repositório ChromaDB encapsulado — de forma que qualquer fase seguinte possa importar `connect_ai/` e começar a trabalhar.
**Depende de**: Nada (primeira fase)
**Requisitos**: ENV-01, ENV-02, ENV-03, ENV-04, ENV-05, ENV-06, ENV-07, DATA-01, DATA-02, DATA-03, DATA-04, REPO-01, REPO-02, REPO-03, REPO-04
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. `pip install -e .` instala o pacote `connect_ai` sem erros e os módulos são importáveis no Colab
  2. A leitura de chave de API ausente produz mensagem de erro clara em PT-BR (nunca `KeyError` ou traceback cru)
  3. Um perfil sintético pode ser instanciado, validado e seu "documento semântico" gerado sem erros
  4. O wrapper ChromaDB insere um perfil, recupera por busca e a conversão distância coseno → score 0–100 devolve valor correto para um exemplo conhecido
  5. README.md em PT-BR lista os passos de setup, execução do front e do notebook e pode ser seguido do zero
**Plans:** 3/4 plans executed
Plans:
- [x] 01-01-PLAN.md — Estrutura do pacote, dependências, pyproject.toml, .env.example, .gitignore e módulo de configuração com leitura segura de chaves (ENV-01..06)
- [x] 01-02-PLAN.md — Schema Pydantic `Perfil`, gerador de UUID e função `construir_documento_semantico` (DATA-01..04)
- [ ] 01-03-PLAN.md — Função `distancia_cosseno_para_score` + wrapper `Repositorio` do ChromaDB com filtros hard via metadados (REPO-01..04)
- [x] 01-04-PLAN.md — README.md em PT-BR com instruções completas de setup, execução do front e do notebook (ENV-07)

### Phase 2: Seed Data Sintético
**Objetivo**: Existir um gerador de perfis sintéticos com seed fixa que produz um pool matematicamente garantido de conter ≥ 10 perfis compatíveis com o perfil de teste (score ≥ 85), de forma reproduzível entre execuções.
**Depende de**: Fase 1
**Requisitos**: SEED-01, SEED-02, SEED-03, SEED-04
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. O gerador roda com seed fixa e produz o mesmo conjunto de perfis em execuções consecutivas
  2. O perfil de teste está documentado no código (campos explícitos, não aleatórios)
  3. Análise estática do pool mostra ≥ 10 perfis com sobreposição de interesses, objetivo e faixa etária compatíveis com o perfil de teste (validação matemática antes da ingestão real)
  4. Os perfis gerados cobrem diversidade de cidade, faixa etária, gênero e objetivo sem viés óbvio
**Plans:** 2/2 plans complete
Plans:
- [ ] 02-01-PLAN.md — Testes TDD (fase RED): tests/test_seed_data.py com 5 testes cobrindo SEED-01..04, todos falhando antes da implementacao (SEED-01, SEED-02, SEED-03, SEED-04)
- [ ] 02-02-PLAN.md — Implementacao: connect_ai/seed_data.py com SEED_FIXA=42, PERFIL_TESTE explicito e gerar_pool_perfis() ate 5 passed (SEED-01, SEED-02, SEED-03, SEED-04)

### Phase 3: Agentes e Grafo LangGraph
**Objetivo**: Os três agentes (Perfilador, Casamenteiro, RAG Justificador) estão implementados como nós distintos de um grafo LangGraph com AgentState compartilhado, e o grafo pode ser visualizado como artefato.
**Depende de**: Fase 1
**Requisitos**: AGT-01, AGT-02, AGT-03, AGT-04, AGT-05, AGT-06, AGT-07
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. O grafo LangGraph é compilado sem erros e a visualização (Mermaid/PNG) é gerada e salva em `relatorio/`
  2. O Agente Perfilador executa o mock textual determinístico e sempre devolve o mesmo `personalidade_ia` para o mesmo input
  3. Os três agentes são identificáveis como nós distintos no grafo exportado — não como uma função única
  4. O AgentState acumula dados de forma correta ao transitar do Perfilador → Casamenteiro → RAG (verificado por asserção de campos em teste manual)
**Plans:** 1/3 plans executed
Plans:
- [ ] 03-01-PLAN.md — TDD RED: tests/test_agentes.py e tests/test_grafo.py com todos os testes falhando (AGT-01..07)
- [ ] 03-02-PLAN.md — Implementacao: connect_ai/agentes.py com AgentState TypedDict + 3 funcoes de agente (GREEN para test_agentes.py) (AGT-01, AGT-02, AGT-03, AGT-04, AGT-07)
- [ ] 03-03-PLAN.md — Implementacao: connect_ai/grafo.py com StateGraph compilado + salvar_visualizacao_grafo + artefato relatorio/ (GREEN para test_grafo.py) (AGT-05, AGT-06, AGT-07)

### Phase 4: Pipeline de Ingestão
**Objetivo**: Dado um perfil válido (ou um lote), o pipeline de ingestão executa o fluxo completo — validação → Perfilador → embedding via `text-embedding-004` → persistência no ChromaDB — com logs claros e sem duplicação.
**Depende de**: Fase 2 e Fase 3
**Requisitos**: ING-01, ING-02, ING-03, ING-04
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. `ingerir_lote(perfis_seed)` insere todos os perfis sintéticos no ChromaDB e os logs em PT-BR mostram contagem correta de sucesso/falha
  2. Re-ingerir o mesmo perfil não aumenta o total de documentos no ChromaDB (idempotência verificável por contagem antes/depois)
  3. Após a ingestão do lote completo, uma query de busca vetorial no ChromaDB retorna resultados (banco não está vazio)
**Planos**: TBD

### Phase 5: Pipeline de Consumo e Scoring
**Objetivo**: Para o perfil de teste, o pipeline de consumo end-to-end — filtros hard → busca vetorial Top-30 → scoring ponderado 60/20/10/5/5 → corte ≥ 85 — devolve 10 matches com score ≥ 85, com breakdown dos 5 fatores. Este é o gate crítico da entrega.

> **Procedimento de fallback:** Se esta fase não produzir 10 matches ≥ 85, PARE e retorne à Fase 2 para recalibrar a distribuição do seed data (mais sobreposição de interesses, perfil de teste mais "central" no espaço semântico). Não avance para Fase 6 ou 7 sem passar este gate.

**Depende de**: Fase 4 (e transitivamente Fase 2 e Fase 3)
**Requisitos**: CONS-01, CONS-02, CONS-03, SCR-01, SCR-02, SCR-03, SCR-04, SCR-05, TEST-01, TEST-02, TEST-03
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. **Para o perfil de teste, o pipeline retorna exatamente 10 matches com score ≥ 85** (validado pelo teste de integração TEST-02)
  2. Os testes unitários de `scoring.py` passam para todos os 5 fatores individualmente e para a composição final (TEST-01)
  3. O score de cada match inclui breakdown explícito dos 5 fatores (semântico, interesses, objetivo, idade, geografia) visível no output estruturado
  4. O teste do wrapper de repositório (insert, busca filtrada, reset) passa sem erros (TEST-03)
  5. A aplicação dos filtros hard antes da busca vetorial é verificável — candidatos incompatíveis por gênero/objetivo/faixa etária não aparecem no Top-30
**Planos**: TBD

### Phase 6: Front Streamlit
**Objetivo**: A interface Streamlit está funcional e permite, sem intervenção no terminal, cadastrar um perfil, popular o banco com seed data, executar o pipeline de consumo e visualizar os 10 matches em cards com breakdown e justificativa do RAG.
**Depende de**: Fase 5
**Requisitos**: APP-01, APP-02, APP-03, APP-04, APP-05, APP-06, APP-07
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. `streamlit run app/streamlit_app.py` sobe a interface sem erros com o ambiente configurado
  2. O botão "Popular banco com seed data" insere os perfis sintéticos e exibe confirmação sem necessidade de linha de comando
  3. Após cadastrar o perfil de teste via formulário, a página de matches exibe 10 cards com nome, idade, cidade, score total, breakdown dos fatores e justificativa textual do RAG
  4. A página de visualização exibe o grafo LangGraph (imagem) e os diagramas dos pipelines
  5. Quando o pipeline não retorna 10 matches ≥ 85, uma mensagem de erro clara em PT-BR é exibida (não uma tela branca ou traceback)
**Planos**: TBD

### Phase 7: Demo, Notebook e Entregáveis Finais
**Objetivo**: Todos os entregáveis do CP5 estão prontos — notebook Colab roda end-to-end sem erros, visualizações e métricas estão em `relatorio/`, documentação de ética e LGPD está completa, e os critérios de aceitação oficiais do enunciado são todos atendidos.
**Depende de**: Fase 5 e Fase 6
**Requisitos**: NB-01, NB-02, NB-03, NB-04, OUT-01, OUT-02, OUT-03, OUT-04, OUT-05, OUT-06, OUT-07, ETH-01, ETH-02, ETH-03, ACC-01, ACC-02, ACC-03, ACC-04, ACC-05, ACC-06, ACC-07, ACC-08, ACC-09, ACC-10
**Critérios de Sucesso** (o que deve ser VERDADE ao final):
  1. `notebook/demo_cp5.ipynb` roda do zero no Google Colab (célula de setup instala deps, célula final mostra os 10 matches ≥ 85) sem nenhum erro
  2. O diretório `relatorio/` contém: diagrama do pipeline de ingestão, diagrama do pipeline de consumo, grafo LangGraph (PNG), tabela Top-10 com scores e breakdowns, e `CONTEUDO.md` com texto para colar no relatório
  3. `relatorio/ETICA.md` cobre consentimento, minimização de dados, riscos de viés do Perfilador e justificativa do uso de mocks em vez de fotos reais
  4. Nenhum arquivo do projeto contém credenciais hardcoded (verificável por `grep -r "AIza\|api_key\s*=" .` sem hits)
  5. Todo texto visível no notebook, front e arquivos markdown está em Português do Brasil
**Planos**: TBD

---

## Progresso

**Ordem de execução:** Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 (GATE) → Fase 6 → Fase 7

> Se a Fase 5 falhar no threshold: Fase 5 → Fase 2 (recalibrar) → Fase 4 (re-ingerir) → Fase 5 (re-validar) → Fase 6 → Fase 7

| Fase | Planos Concluídos | Status | Concluída em |
|------|-------------------|--------|--------------|
| 1. Fundação | 3/4 | In Progress |  |
| 2. Seed Data Sintético | 2/2 | Complete   | 2026-04-20 |
| 3. Agentes e Grafo LangGraph | 1/3 | In Progress|  |
| 4. Pipeline de Ingestão | 0/? | Não iniciada | - |
| 5. Pipeline de Consumo e Scoring | 0/? | Não iniciada | - |
| 6. Front Streamlit | 0/? | Não iniciada | - |
| 7. Demo, Notebook e Entregáveis Finais | 0/? | Não iniciada | - |
