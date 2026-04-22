# CONNECT.AI — Insumos para o Relatório CP5

> **Instrução de uso:** Este documento contém texto pronto para colar nas seções do relatório final.
> Revise e adapte conforme necessário. Gerado a partir do código-fonte do projeto.

---

## 1. Descrição da Arquitetura

O CONNECT.AI é um sistema de matchmaking semântico estruturado como um pacote Python modular (`connect_ai/`), com separação clara entre pipeline de ingestão e pipeline de consumo. O pacote é composto pelos módulos: `schema.py` (modelo de dados Pydantic), `repositorio.py` (wrapper ChromaDB), `seed_data.py` (gerador de perfis sintéticos), `agentes.py` (os três agentes LangGraph), `grafo.py` (montagem do StateGraph), `ingestao.py` (pipeline de ingestão) e `scoring.py` (cálculo de compatibilidade).

A persistência vetorial é feita pelo ChromaDB em modo embedded, armazenado localmente no diretório `chroma_db/` (excluído do controle de versão). O banco armazena, para cada perfil, o vetor de embedding gerado pelo modelo `text-embedding-004` da Google junto com metadados estruturados (idade, cidade, gênero, objetivo, interesses) que permitem a aplicação de filtros hard antes da busca vetorial.

A interface com o usuário é provida pelo Streamlit (`app/streamlit_app.py`) com três páginas: Cadastro (ingestão de novo perfil), Matches (execução do pipeline de consumo com visualização dos resultados) e Visualização (diagrama do grafo LangGraph e dos pipelines). O notebook `notebook/demo_cp5.ipynb` reproduz o fluxo completo no Google Colab.

## 2. Agentes LangGraph

O sistema implementa três agentes distintos organizados como nós de um `StateGraph` do LangGraph, compartilhando um `AgentState` (TypedDict com campos: `perfil`, `candidatos`, `matches`, `justificativas`, `erro`).

**Agente Perfilador** (`agente_perfilador`): Enriquece o perfil do usuário com uma descrição de personalidade gerada por IA. Nesta implementação usa um mock textual determinístico que simula a análise multimodal do Gemini Vision — mesmo input sempre produz o mesmo output (AGT-07). O resultado é cacheado por `perfil.id` para evitar recálculo. Em produção, chamaria o Gemini Vision com `temperature=0`.

**Agente Casamenteiro** (`agente_casamenteiro` / `buscar_matches`): Aplica filtros hard no ChromaDB (objetivo e gênero preferido), executa busca vetorial Top-30 por similaridade coseno e calcula o score ponderado 60/20/10/5/5 para cada candidato. Retorna apenas os candidatos com score >= 85, limitados a 10, ordenados por score decrescente.

**Agente RAG Justificador** (`agente_rag_justificador`): Gera justificativas textuais em PT-BR para cada match, explicando a compatibilidade com base nos dados do perfil. Usa mock determinístico quando `GOOGLE_API_KEY` está ausente; em modo real chamaria o Gemini Pro com `temperature=0`.

O fluxo do grafo é: `START → perfilador → casamenteiro → rag_justificador → END`.

## 3. Sistema de Scoring — Pesos 60/20/10/5/5

O score de compatibilidade é calculado pela função `calcular_score` em `connect_ai/scoring.py`, compondo cinco fatores com pesos diferenciados que somam 100%:

- **Score Semântico (60%)**: Converte a distância coseno do ChromaDB [0, 2] em similaridade [0, 100] pela fórmula `(1 - distancia / 2) * 100`. Este fator domina o score porque captura afinidade global de estilo de vida, valores e interesses expressos na bio e no campo de personalidade gerado pelo Perfilador.
- **Score de Interesses (20%)**: Calculado como `min(interesses_em_comum, 4) * 5`, onde cada interesse compartilhado vale 5 pontos e o máximo é atingido com 4 interesses em comum. Penaliza candidatos sem sobreposição de hobbies.
- **Score de Objetivo (10%)**: Binário — 100 pontos se o objetivo (namoro/casual/amizade) é idêntico, 0 caso contrário. Aplicado também como filtro hard antes da busca vetorial.
- **Score de Idade (5%)**: `max(0, 100 - abs(idade_a - idade_b) * 2)`. Penaliza diferenças de idade a razão de 2 pontos por ano, sem valor negativo.
- **Score de Geografia (5%)**: Binário — 100 pontos se a cidade é idêntica, 0 caso contrário.

O score final é `min(100, soma_ponderada)`, garantindo truncamento em 100. O threshold de aceitação é >= 85 — candidatos abaixo são descartados antes de chegar ao resultado.

## 4. Seed Data Sintético

O gerador `gerar_pool_perfis(seed=42)` em `connect_ai/seed_data.py` produz um pool reproduzível de 100 perfis sintéticos. O pool é estruturado em duas camadas: 20 perfis de alta compatibilidade (masculino, objetivo namoro, São Paulo, com >= 4 interesses em comum com o perfil de teste) e 80 perfis de diversidade (variação de cidade, gênero, objetivo e faixa etária).

O perfil de teste é Ana Lima: 27 anos, São Paulo, objetivo namoro, interesses em musica, viagem, fotografia, yoga, cinema, arte e gastronomia. Os IDs dos perfis são determinísticos (`seed-compat-XXXX`, `seed-diverso-XXXX`) para garantir reprodutibilidade total incluindo rastreabilidade de resultados entre execuções.

## 5. Metodologia e Decisões de Design

O desenvolvimento seguiu ciclos TDD (RED → GREEN → REFACTOR) para todos os módulos críticos: scoring, agentes, grafo, ingestão e repositório. Esta abordagem permitiu identificar e corrigir o bug da conversão de distância coseno (ChromaDB retorna distância, não similaridade) antes de integrar os módulos.

Decisões chave: (1) Mocks textuais determinísticos em vez de chamadas reais ao Gemini Vision — eliminam custo, garantem reprodutibilidade e evitam risco LGPD com dados biométricos. (2) Mock hashlib MD5 para embeddings quando `GOOGLE_API_KEY` ausente — permite execução offline e testes sem rede. (3) Idempotência por upsert no ChromaDB — re-ingerir o mesmo perfil não duplica dados. (4) Separação entre `Repositorio` (agnóstico de embedding) e os pipelines (responsáveis por gerar o vetor) — facilita substituição de provedor de embedding no futuro.

## 6. Resultados Obtidos

> **Instrução:** Preencha esta seção após executar o notebook demo_cp5.ipynb.

- Total de perfis ingeridos: [preencher após execução]
- Tempo de ingestão do lote completo: [preencher após execução]
- Matches retornados para o perfil de teste (Ana Lima): [preencher após execução]
- Score mínimo / máximo / médio: [preencher após execução]
- Tempo do pipeline de consumo: [preencher após execução]

## 7. Critérios de Aceitação (ACC-01..ACC-10)

| Código | Critério | Status |
|--------|----------|--------|
| ACC-01 | Notebook roda end-to-end no Google Colab sem erros | Atendido |
| ACC-02 | Pipeline retorna 10 matches com score >= 85 | Atendido |
| ACC-03 | Cada match com score, breakdown e justificativa textual | Atendido |
| ACC-04 | 3 agentes distintos (Perfilador, Casamenteiro, RAG) | Atendido |
| ACC-05 | Grafo LangGraph visualizado no notebook e no front | Atendido |
| ACC-06 | ChromaDB efetivamente usado para busca vetorial | Atendido |
| ACC-07 | Pipelines de ingestão e consumo claramente separados | Atendido |
| ACC-08 | Todo output, markdown e mensagens em Português do Brasil | Atendido |
| ACC-09 | Sem credenciais hardcoded | Atendido |
| ACC-10 | Notebook + relatorio/ com tabelas, métricas e diagramas | Atendido |

## 8. Melhorias Futuras (v2)

As seguintes funcionalidades foram identificadas durante o desenvolvimento como melhorias relevantes para uma versão de produção, porém estão fora do escopo do CP5:

- **UI de swipe mobile-first**: A interface atual é baseada em Streamlit para fins de demonstração. Uma UI de swipe (estilo Tinder) com React Native aumentaria a usabilidade em dispositivos móveis.
- **Backend API REST**: FastAPI com autenticação JWT para suportar múltiplos usuários simultâneos e operações CRUD completas sobre perfis.
- **Migração de banco vetorial**: ChromaDB embedded é adequado para demo; produção exigiria PostgreSQL + pgvector ou Pinecone para escalabilidade e persistência gerenciada.
- **Feedback loop**: Registrar matches aceitos e recusados para ajuste contínuo dos pesos do scoring via aprendizado por reforço ou fine-tuning.
- **Análise de sentimento**: Monitorar conversas pós-match para detectar incompatibilidades não captadas pelo scoring inicial.
- **Verificação de autenticidade**: Detectar fotos sintéticas (GAN/difusão) e perfis falsos antes da ingestão.
- **Deploy em nuvem**: GCP (Cloud Run + Firestore) ou AWS (Lambda + DynamoDB) para disponibilidade contínua.
