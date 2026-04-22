# Requisitos: CONNECT.AI (CP5)

**Definidos em:** 2026-04-19
**Core Value:** Para qualquer perfil submetido, devolver 10 matches com score de compatibilidade ≥ 85, com breakdown e justificativa textual.

## Requisitos da v1 (Entrega CP5)

Cada requisito mapeia para exatamente uma fase do roadmap.

### Setup e Ambiente

- [x] **ENV-01**: Estrutura de pacote Python (`connect_ai/`, `app/`, `notebook/`, `relatorio/`, `tests/`) criada
- [x] **ENV-02**: `requirements.txt` com todas as dependências obrigatórias (`langgraph`, `chromadb`, `google-generativeai`, `streamlit`, `pandas`, `python-dotenv`, etc.)
- [x] **ENV-03**: `pyproject.toml` configurado para instalação em modo editável (`pip install -e .`)
- [x] **ENV-04**: Leitura de chaves de API exclusivamente via `.env` ou variável de ambiente; nunca hardcoded
- [x] **ENV-05**: `.env.example` documentando todas as variáveis necessárias
- [x] **ENV-06**: Mensagem de erro clara e em PT-BR quando uma chave de API estiver ausente
- [x] **ENV-07**: README.md em PT-BR com instruções de setup, execução do front e do notebook

### Schema e Modelo de Dados

- [x] **DATA-01**: Dataclass/Pydantic do perfil contemplando os 3 grupos de campos (estruturados, semânticos, multimodais) e o campo gerado `personalidade_ia`
- [x] **DATA-02**: Validação dos campos estruturados (tipos, faixa etária, gêneros aceitos, objetivos válidos: namoro/casual/amizade)
- [x] **DATA-03**: Função utilitária para gerar UUID dos perfis
- [x] **DATA-04**: Função para construir o "documento semântico" a ser embedado: `bio + interesses + objetivo + personalidade_ia`

### ChromaDB e Repositório

- [x] **REPO-01**: Wrapper de repositório ChromaDB encapsulando criação, inserção, busca filtrada e reset da coleção
- [x] **REPO-02**: Persistência local do ChromaDB em diretório dedicado e `.gitignore`-ado
- [x] **REPO-03**: Metadados estruturados (idade, cidade, gênero, gênero preferido, faixa etária preferida, objetivo) gravados junto ao vetor para suportar filtros hard
- [x] **REPO-04**: Conversão correta de distância coseno → similaridade → escala 0–100, encapsulada em função única e testada

### Seed Data Sintético

- [x] **SEED-01**: Gerador de perfis sintéticos diversificados (cidade, idade, gênero, objetivo, interesses, bio)
- [x] **SEED-02**: Pool calibrado matematicamente para garantir que existem ≥ 10 perfis compatíveis com cada perfil de teste (score ≥ 85)
- [x] **SEED-03**: Pelo menos 1 perfil de teste pré-definido e documentado no código (não-aleatório), usado nas demos e testes
- [x] **SEED-04**: Reprodutibilidade — geração com seed fixa para resultados estáveis entre execuções

### Agentes (LangGraph)

- [x] **AGT-01**: `AgentState` (TypedDict) com todos os campos compartilhados entre os 3 nós
- [x] **AGT-02**: Agente Perfilador implementado com mock textual do Gemini Vision (output determinístico que simula análise multimodal)
- [x] **AGT-03**: Agente Casamenteiro implementado, executando filtros hard + busca vetorial Top-30 + scoring + corte ≥ 85
- [x] **AGT-04**: Agente RAG Justificador implementado, gerando justificativas textuais em PT-BR para cada um dos Top-10
- [x] **AGT-05**: Grafo LangGraph montado com os 3 nós e estado fluindo corretamente entre eles
- [x] **AGT-06**: Função para visualização do grafo (Mermaid/PNG) salva como artefato e exibida no front e no notebook
- [x] **AGT-07**: Determinismo dos LLMs garantido onde aplicável (`temperature=0` ou cache do output do Perfilador)

### Pipeline de Ingestão

- [x] **ING-01**: Função `ingerir_perfil(perfil)` que executa o fluxo completo: validação → Perfilador → embedding → persistência
- [x] **ING-02**: Função `ingerir_lote(perfis)` para processar a base inicial de seed data
- [x] **ING-03**: Logs claros em PT-BR de cada etapa da ingestão (perfis processados, falhas, tempo)
- [x] **ING-04**: Idempotência — re-ingerir o mesmo perfil não duplica registros

### Pipeline de Consumo e Scoring

- [x] **CONS-01**: Função `buscar_matches(perfil_solicitante)` que orquestra o pipeline de consumo end-to-end
- [x] **CONS-02**: Aplicação dos filtros hard (faixa etária, cidade/região, gênero preferido, objetivo) via metadados do ChromaDB antes da busca vetorial
- [x] **CONS-03**: Busca vetorial Top-K (`K=30`) com cosine distance no ChromaDB
- [x] **SCR-01**: Cálculo do score ponderado 60/20/10/5/5 implementado em módulo `scoring.py` testável isoladamente
- [x] **SCR-02**: Cada componente do score (semântico, interesses, objetivo, idade, geografia) com função própria, testada
- [x] **SCR-03**: Score final normalizado em escala 0–100 com truncamento explícito
- [x] **SCR-04**: Filtro final ≥ 85, retornando até 10 candidatos
- [x] **SCR-05**: Output estruturado contendo: id, score total, breakdown dos 5 fatores, dados de exibição do match

### Front Streamlit

- [x] **APP-01**: `app/streamlit_app.py` com navegação entre páginas (cadastro, matches, visualização do grafo)
- [x] **APP-02**: Página de cadastro permitindo criar um perfil e disparar a ingestão (com loader/feedback)
- [x] **APP-03**: Página de matches recebendo um perfil (existente ou recém-cadastrado), executando o pipeline de consumo e exibindo os 10 matches em cards
- [x] **APP-04**: Cada card de match exibe: nome, idade, cidade, score total, breakdown dos fatores e justificativa do RAG
- [x] **APP-05**: Página de visualização exibindo o grafo LangGraph + diagramas dos pipelines de ingestão e consumo
- [x] **APP-06**: Botão para popular o ChromaDB com o seed data caso o banco esteja vazio
- [x] **APP-07**: Mensagens de erro claras em PT-BR quando o pipeline não retorna 10 matches ≥ 85

### Saídas, Visualizações e Insumos para o Relatório

- [x] **OUT-01**: Função para gerar tabela Top-10 (Pandas DataFrame) com scores e breakdown
- [x] **OUT-02**: Gráfico de distribuição de scores entre os Top-30 candidatos
- [x] **OUT-03**: Métrica de tempo de execução do pipeline de consumo
- [x] **OUT-04**: Diagrama do pipeline de ingestão exportado como imagem para `relatorio/`
- [x] **OUT-05**: Diagrama do pipeline de consumo exportado como imagem para `relatorio/`
- [x] **OUT-06**: Visualização do grafo LangGraph exportada como imagem para `relatorio/`
- [x] **OUT-07**: Documento `relatorio/CONTEUDO.md` em PT-BR com texto pronto para colar no relatório (descrição dos dados, escolhas, métricas, futuras melhorias)

### Notebook (Demo)

- [x] **NB-01**: `notebook/demo_cp5.ipynb` rodando do zero sem erros, importando exclusivamente de `connect_ai/`
- [x] **NB-02**: Notebook contém células de: setup, schema, ChromaDB, seed data, ingestão, visualização do grafo, demo do pipeline de consumo, Top-10 com breakdown e justificativas, análises e visualizações, conclusão
- [x] **NB-03**: Notebook compatível com Google Colab (instala dependências na primeira célula via `pip install`)
- [x] **NB-04**: Outputs em PT-BR, células de cadastro do perfil de teste destacadas, resultados visualmente claros

### Ética e LGPD

- [x] **ETH-01**: Documento `relatorio/ETICA.md` em PT-BR cobrindo: consentimento, minimização de dados, riscos de viés do Perfilador, considerações para apps de relacionamento
- [x] **ETH-02**: Justificativa explícita da decisão de usar mocks textuais ao invés de fotos reais (privacidade + custo + reprodutibilidade)
- [x] **ETH-03**: Aviso visível no front sobre uso de dados sintéticos para fins de demonstração

### Testes

- [x] **TEST-01**: Testes unitários do `scoring.py` cobrindo cada um dos 5 fatores e a composição final
- [x] **TEST-02**: Teste de integração do pipeline de consumo garantindo que para o perfil de teste retornam 10 matches ≥ 85
- [x] **TEST-03**: Teste do wrapper de repositório (insert, search filtrado, reset)

### Critérios de Aceitação (auditoria final)

- [x] **ACC-01**: Notebook `demo_cp5.ipynb` roda end-to-end no Google Colab sem erros
- [x] **ACC-02**: Para o perfil de teste, o pipeline retorna **10 matches com score ≥ 85**
- [x] **ACC-03**: Cada match vem com score, breakdown dos fatores e justificativa textual
- [x] **ACC-04**: Os 3 agentes (Perfilador, Casamenteiro, RAG) são visivelmente distintos no código e no grafo
- [x] **ACC-05**: O grafo LangGraph é visualizado no notebook e no front
- [x] **ACC-06**: ChromaDB é efetivamente usado para busca vetorial (não apenas armazenamento)
- [x] **ACC-07**: Pipelines de ingestão e consumo claramente separados e documentados
- [x] **ACC-08**: Todo output, markdown, docstring e mensagem em Português do Brasil
- [x] **ACC-09**: Não há credenciais hardcoded
- [x] **ACC-10**: O notebook + `relatorio/` geram material suficiente (tabelas, métricas, diagramas) para sustentar o relatório

## Requisitos da v2 (Diferidos — fora do CP5)

Listados como "futuras melhorias" no relatório.

### Plataforma

- **V2-PLAT-01**: UI de swipe (mobile-first)
- **V2-PLAT-02**: Backend API REST (FastAPI) com autenticação real
- **V2-PLAT-03**: Migração de ChromaDB para PostgreSQL + PostGIS + pgvector
- **V2-PLAT-04**: Deploy em ambiente cloud

### Inteligência

- **V2-IA-01**: Chat com IA mediadora pós-match
- **V2-IA-02**: Análise de sentimento das conversas
- **V2-IA-03**: Verificação de autenticidade de perfis
- **V2-IA-04**: Feedback loop com aprendizado contínuo

### Validação

- **V2-VAL-01**: Testes A/B do algoritmo de scoring
- **V2-VAL-02**: Métricas reais de retenção e satisfação

## Fora do Escopo (explicitamente excluídos)

| Feature | Razão |
|---|---|
| Frontend mobile/web em produção | CP5 é demo técnica; Streamlit cobre o front da entrega |
| Autenticação e contas de usuário reais | Fora do escopo do CP5 |
| Deploy remoto | Execução é local |
| Banco relacional externo (PostgreSQL etc.) | Listado como melhoria futura, não esta entrega |
| Gravação do vídeo de demo | Tarefa manual da equipe |
| Redação final do relatório como documento | O código produz insumos; o documento é escrito separadamente |
| Fotos reais de pessoas | Risco LGPD; usaremos mocks/avatares sintéticos |
| Chamadas reais ao Gemini Vision | Custo + não-determinismo; usaremos mocks textuais (decisão registrada em PROJECT.md) |

## Rastreabilidade

Mapeamento requisito → fase. Atualizado durante a criação do roadmap em 2026-04-19.

| Requisito | Fase | Status |
|---|---|---|
| ENV-01 | Fase 1 — Fundação | Concluído |
| ENV-02 | Fase 1 — Fundação | Concluído |
| ENV-03 | Fase 1 — Fundação | Concluído |
| ENV-04 | Fase 1 — Fundação | Concluído |
| ENV-05 | Fase 1 — Fundação | Concluído |
| ENV-06 | Fase 1 — Fundação | Concluído |
| ENV-07 | Fase 1 — Fundação | Pendente |
| DATA-01 | Fase 1 — Fundação | Pendente |
| DATA-02 | Fase 1 — Fundação | Pendente |
| DATA-03 | Fase 1 — Fundação | Pendente |
| DATA-04 | Fase 1 — Fundação | Pendente |
| REPO-01 | Fase 1 — Fundação | Concluído |
| REPO-02 | Fase 1 — Fundação | Concluído |
| REPO-03 | Fase 1 — Fundação | Concluído |
| REPO-04 | Fase 1 — Fundação | Concluído |
| SEED-01 | Fase 2 — Seed Data Sintético | Concluído |
| SEED-02 | Fase 2 — Seed Data Sintético | Concluído |
| SEED-03 | Fase 2 — Seed Data Sintético | Concluído |
| SEED-04 | Fase 2 — Seed Data Sintético | Concluído |
| AGT-01 | Fase 3 — Agentes e Grafo LangGraph | Concluído |
| AGT-02 | Fase 3 — Agentes e Grafo LangGraph | Concluído |
| AGT-03 | Fase 3 — Agentes e Grafo LangGraph | Concluído |
| AGT-04 | Fase 3 — Agentes e Grafo LangGraph | Concluído |
| AGT-05 | Fase 3 — Agentes e Grafo LangGraph | Pendente |
| AGT-06 | Fase 3 — Agentes e Grafo LangGraph | Pendente |
| AGT-07 | Fase 3 — Agentes e Grafo LangGraph | Concluído |
| ING-01 | Fase 4 — Pipeline de Ingestão | Pendente |
| ING-02 | Fase 4 — Pipeline de Ingestão | Pendente |
| ING-03 | Fase 4 — Pipeline de Ingestão | Pendente |
| ING-04 | Fase 4 — Pipeline de Ingestão | Pendente |
| CONS-01 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| CONS-02 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| CONS-03 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| SCR-01 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| SCR-02 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| SCR-03 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| SCR-04 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| SCR-05 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| TEST-01 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| TEST-02 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| TEST-03 | Fase 5 — Pipeline de Consumo e Scoring | Pendente |
| APP-01 | Fase 6 — Front Streamlit | Pendente |
| APP-02 | Fase 6 — Front Streamlit | Pendente |
| APP-03 | Fase 6 — Front Streamlit | Pendente |
| APP-04 | Fase 6 — Front Streamlit | Pendente |
| APP-05 | Fase 6 — Front Streamlit | Pendente |
| APP-06 | Fase 6 — Front Streamlit | Pendente |
| APP-07 | Fase 6 — Front Streamlit | Pendente |
| NB-01 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| NB-02 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| NB-03 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| NB-04 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-01 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-02 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-03 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-04 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-05 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-06 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| OUT-07 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ETH-01 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ETH-02 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ETH-03 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-01 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-02 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-03 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-04 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-05 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-06 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-07 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-08 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-09 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |
| ACC-10 | Fase 7 — Demo, Notebook e Entregáveis Finais | Pendente |

**Cobertura:**
- Requisitos v1: 72
- Mapeados para fases: 72
- Não mapeados: 0 (cobertura 100%)

---
*Requisitos definidos em: 2026-04-19*
*Última atualização: 2026-04-19 — rastreabilidade preenchida pelo roadmapper*
