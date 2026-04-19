# CONNECT.AI — Dating powered by AI (CP5)

## What This Is

Aplicação Python modular com front em Streamlit que implementa o motor de matchmaking semântico do app de relacionamento **CONNECT.AI**. É a entrega técnica do Checkpoint 5 da disciplina de Sistemas Multi-Agentes e IA Generativa (NLP) da FIAP, executando o que foi planejado no CP4. Substitui filtros rígidos por análise semântica multimodal orquestrada por um pipeline multi-agente (LangGraph + Gemini + ChromaDB), retornando para cada usuário 10 perfis afins com índice de compatibilidade ≥ 85.

## Core Value

Para qualquer perfil submetido ao pipeline, devolver **10 perfis com score de compatibilidade ≥ 85 (escala 0–100)**, com breakdown dos fatores e justificativa textual gerada por IA. Sem isso, a entrega não atende o enunciado e perde a nota principal.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

(Nenhum ainda — projeto greenfield.)

### Active

<!-- Construindo em direção a estes requisitos. -->

- [ ] Aplicação Python modular (pacote `connect_ai/`) que isola schema, agentes, pipelines, scoring, repositório e seed data
- [ ] Front Streamlit (`app/`) para cadastro de perfil, execução do pipeline de consumo e visualização dos matches
- [ ] Notebook fino (`notebook/demo_cp5.ipynb`) que importa `connect_ai/` e demonstra o pipeline end-to-end (atende item de 50% da nota)
- [ ] 3 agentes LangGraph distintos no código e no grafo: Perfilador, Casamenteiro, RAG Justificador
- [ ] Pipeline de Ingestão funcional: cadastro → Perfilador → embedding `text-embedding-004` → ChromaDB
- [ ] Pipeline de Consumo funcional: filtros hard → busca vetorial Top-30 → scoring ponderado 60/20/10/5/5 → threshold ≥85 → RAG
- [ ] Sistema de scoring 0–100 com normalização correta da distância coseno do ChromaDB
- [ ] Seed data sintético calibrado para garantir 10 matches ≥ 85 para o(s) perfil(s) de teste
- [ ] Mocks textuais simulando output do Gemini Vision (sem custo, determinístico, justificado no relatório)
- [ ] Visualização do grafo LangGraph
- [ ] Tabelas, métricas e diagramas que sirvam de insumo direto para o relatório
- [ ] Seção/documentação de ética e LGPD (consentimento, viés, fotos)
- [ ] Reprodutibilidade total: setup limpo, sem credenciais hardcoded, leitura via `.env`/userdata
- [ ] README em PT-BR com instruções de execução do front e do notebook

### Out of Scope

<!-- Limites explícitos com motivo, para não voltarem mais tarde. -->

- Frontend web/mobile em produção — Streamlit é o front da entrega; nada além disso
- Autenticação real, contas de usuário ou multi-tenant — fora do escopo do CP5
- Persistência além do ChromaDB local — sem PostgreSQL/PostGIS nesta entrega (vai como melhoria futura)
- Deploy em servidor remoto — execução é local
- Gravação do vídeo de demo — tarefa manual da equipe
- Redação final do relatório em formato de documento — o código produz insumos; o documento é escrito separadamente
- Uso de fotos reais de pessoas — risco LGPD; serão mocks/avatares sintéticos
- Chat com IA mediadora, feedback loop, análise de sentimento, testes A/B — todos listados como melhorias futuras

## Context

- **Disciplina e equipe:** Sistemas Multi-Agentes e IA Generativa (NLP) — FIAP. Equipe: Matheus Barbosa (RM 561085), Guilherme Henrique (RM 559977), Vitor Adauto (RM 560247).
- **Precedente:** CP4 já entregue com o planejamento e pitch do app. CP5 é a execução técnica do que foi planejado.
- **Idioma:** Toda a entrega — código, comentários, docstrings, mensagens de erro, outputs, markdown, README — em **Português do Brasil**.
- **Schema do perfil:** 3 categorias — estruturados (idade, cidade, gênero, objetivo), semânticos (bio, interesses) e multimodais (fotos). O Perfilador gera um campo extra `personalidade_ia` que enriquece o documento embedado.
- **Arquitetura de agentes:** LangGraph com 3 nós e `AgentState` compartilhado. Perfilador atua na ingestão; Casamenteiro + RAG atuam no consumo.
- **Sistema de scoring:** 60% similaridade semântica, 20% interesses em comum (+5/interesse, máx 20), 10% objetivo, 5% idade, 5% geografia. Threshold ≥ 85.
- **Pitfalls conhecidos:** ChromaDB retorna distância coseno (não similaridade); viabilidade matemática do threshold 85 precisa ser validada empiricamente; LLMs não são determinísticos por padrão (`temperature=0` + cache do Perfilador); fotos exigem cuidado LGPD; chaves de API jamais hardcoded.
- **Material para relatório:** O código deve produzir tabelas, métricas, gráficos de distribuição de scores e diagramas dos pipelines, prontos para colar no documento final.

## Constraints

- **Stack obrigatória**: LangGraph (orquestração) + Gemini Pro/Vision (LLM) + ChromaDB (banco vetorial) + `text-embedding-004` (embeddings) + Python 3.10+ — definido no BRIEFING §5.
- **Front**: Streamlit (decisão tomada na inicialização, justificada por ser Python-nativo, leve e ideal para demo).
- **Threshold**: 10 matches ≥ 85 é hard requirement do enunciado oficial. Não negociável.
- **Idioma**: Português do Brasil em 100% dos artefatos.
- **Segurança**: Sem credenciais hardcoded — apenas `.env` ou `google.colab.userdata`.
- **Reprodutibilidade**: Notebook e front devem rodar sem intervenção manual além das chaves de API; resultados consistentes entre re-execuções (importante para gravação do vídeo).
- **Custo**: Mocks textuais para o Gemini Vision para reduzir custo e garantir determinismo (decisão tomada na inicialização).
- **Privacidade/LGPD**: Sem fotos de pessoas reais. Avatares sintéticos ou mocks.

## Key Decisions

| Decisão | Justificativa | Resultado |
|---|---|---|
| Aplicação Python modular ao invés de notebook monolítico | Usuário pediu app organizado, modular e testável; notebook fino só importa os módulos para entregar o item de 50% da nota | — Pendente |
| Front em Streamlit | Python-nativo, sem JS/HTML, pronto para demo em vídeo, baixo custo de desenvolvimento | — Pendente |
| Notebook híbrido (`notebook/demo_cp5.ipynb` fino que importa `connect_ai/*`) | Atende o entregável de notebook (50% da nota) sem duplicar lógica nem virar Jupyter monolítico | — Pendente |
| Mocks textuais para Gemini Vision | Custo zero em chamadas Vision em 30+ perfis, determinismo total para regravação do vídeo, justificável na seção de ética/LGPD do relatório | — Pendente |
| Sem pesquisa de domínio (`Skip research` no GSD) | BRIEFING.md já é prescritivo: stack, schema, arquitetura, scoring, pitfalls e critérios de aceitação estão fechados | ✓ Boa |
| Modo YOLO + granularidade Standard + execução sequencial | Fluxo linear (notebook + app único), poucos pontos de paralelização real; YOLO acelera sem perder os checkpoints naturais entre fases | — Pendente |
| Verifier e Plan Check ativados | Hard requirement de 10 matches ≥ 85 é não-trivial; verificação por fase reduz risco de chegar no final sem atingir o threshold | — Pendente |
| Equipe brasileira + curso brasileiro = tudo em PT-BR | Requisito explícito do BRIEFING; nenhuma exceção em código, docs ou outputs | — Pendente |

---
*Última atualização: 2026-04-19, na inicialização do projeto.*
