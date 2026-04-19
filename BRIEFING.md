# BRIEFING — CONNECT.AI (CP5)

> Documento de contexto único para desenvolvimento autônomo do Checkpoint 5 da disciplina de Sistemas Multi-Agentes e IA Generativa (NLP) — FIAP.
> Toda a comunicação, código, comentários, outputs, mensagens de erro e documentação devem estar em **Português do Brasil**.

---

## 1. Identificação

- **Projeto:** CONNECT.AI — Dating powered by AI
- **Equipe:** Matheus Barbosa (RM 561085) · Guilherme Henrique (RM 559977) · Vitor Adauto (RM 560247)
- **Curso:** Tecnologia em Inteligência Artificial — FIAP
- **Disciplina:** Sistemas Multi-Agentes e IA Generativa (NLP)
- **Entrega:** Checkpoint 5 (CP5)
- **Precedente:** CP4 já entregue (planejamento/pitch do aplicativo). CP5 é a execução técnica do que foi planejado.

---

## 2. Enunciado oficial do professor

> "Em nossa última CP de número 4 vocês foram desafiados a elaborar um projeto de aplicativo de namoro e apresentar um pitch sobre a ferramenta, agora chegou o momento de por mãos a obra. Utilizando as capacidades atuais de vibe coding das LLM's, os conceitos de engenharia de prompt e de contexto, IA Agêntica, etc, vocês deverão elaborar seu aplicativo. Ele deverá ser capaz de registrar os dados mais importantes do usuário e suas preferências de modo a poder cruzar os dados e encontrar os melhores parceiros. Os dados deverão ser armazenados em um banco de dados relacional ou vetorial, serem acessados durante a etapa de cruzamento de dados e ingeridos por agentes de IA responsáveis por fazer a seleção dos melhores casais. O uso dos agentes deverá estar claro em sua ferramenta, assim como o pipeline adotado no processamento dos dados desde a ingestão até o uso. Espera-se como saída, que para cada perfil de usuário este possua 10 outros perfis que correspondam a suas preferências e tenham um índice de proximidade acima de 85 pontos."

### Entregáveis e pesos

1. **Notebook contendo os códigos do app** — 50%
2. **Relatório** contendo a descrição dos dados coletados e usados na análise, uma explicação da escolha destes dados para o cruzamento, diagramas dos pipelines de ingestão e de consumo, e futuras melhorias do app — 25%
3. **Vídeo** mostrando o cadastro de perfis e a saída contendo os 10 perfis mais afinados para o perfil em estudo — 25%

---

## 3. Restrição crítica (hard requirement)

Para cada perfil de usuário submetido ao pipeline, o sistema **deve retornar 10 perfis** com **índice de compatibilidade ≥ 85 (em escala 0–100)**. Essa é a métrica de avaliação principal. A demonstração desse resultado, de forma inequívoca, é obrigatória no notebook e no vídeo.

---

## 4. Visão do produto

O CONNECT.AI é um aplicativo de relacionamento que substitui os filtros rígidos dos apps tradicionais por uma análise semântica multimodal. Cada perfil é convertido em um vetor de alta dimensão que representa simultaneamente:

- Dados estruturados (idade, localização, gênero, objetivo)
- Traços de personalidade inferidos de texto livre (bio) e imagens (fotos)

A engine é orquestrada por um pipeline multi-agente que garante precisão objetiva (filtros determinísticos) e subjetiva (similaridade semântica). O diferencial declarado é capturar afinidades implícitas — valores, estilo de vida, contextos visuais — que filtros tradicionais não conseguem identificar.

---

## 5. Stack tecnológica definida

| Camada | Tecnologia | Função |
|---|---|---|
| Orquestração | **LangGraph** | Grafo de agentes com gerenciamento de estado |
| Modelo LLM | **Gemini Pro / Gemini Vision** | Análise semântica e multimodal dos perfis |
| Banco Vetorial | **ChromaDB** | Armazenamento e busca por similaridade (cosine) |
| Filtros relacionais | **Metadados do ChromaDB** (ou SQLite/Pandas) | Filtros hard: idade, cidade, gênero preferido, objetivo |
| Embeddings | **Google `text-embedding-004`** | Vetorização de bios, interesses e personalidade inferida |
| Ambiente | **Google Colab / Vertex AI** | Execução e APIs Google Cloud |
| Linguagem | **Python 3.10+** | Toda a lógica de agentes e dados |

Chaves de API devem ser lidas via `google.colab.userdata` ou variáveis de ambiente. **Nunca hardcoded no notebook.**

---

## 6. Schema de dados do usuário

O perfil combina três categorias de dados:

### 6.1. Campos estruturados (usados como filtros hard)

| Campo | Tipo | Uso |
|---|---|---|
| `id` | UUID | Chave primária |
| `nome` | str | Display na interface |
| `idade` | int | Filtro hard — compatibilidade etária |
| `cidade` | str | Filtro hard — proximidade geográfica |
| `genero` | str | Filtro de preferência |
| `genero_preferido` | str | Filtro de busca |
| `faixa_etaria_pref` | tuple[int, int] | Restrição de faixa |
| `objetivo` | str | Agrupamento semântico: `namoro` / `casual` / `amizade` |

### 6.2. Campos semânticos (compõem o embedding)

| Campo | Tipo | Uso |
|---|---|---|
| `bio` | str (texto livre) | Embedding + RAG — personalidade em texto livre |
| `interesses` | list[str] | Embedding + scoring — afinidades comportamentais |

### 6.3. Campos multimodais

| Campo | Tipo | Uso |
|---|---|---|
| `foto_perfil` | base64 ou URL | Inferência visual de traços via Gemini Vision |
| `fotos_extras` | list[URL] | Contexto de estilo de vida |

### 6.4. Campo gerado (não preenchido pelo usuário)

| Campo | Tipo | Uso |
|---|---|---|
| `personalidade_ia` | str | Output do **Agente Perfilador** após análise multimodal. Compõe o documento final que será embedado no ChromaDB, enriquecendo o vetor com traços inferidos. |

---

## 7. Arquitetura de agentes (LangGraph)

O grafo possui **3 nós de agentes** compartilhando um `AgentState` que é enriquecido a cada etapa.

### 7.1. Agente Perfilador (Análise)

- **Quando atua:** na ingestão de cada perfil.
- **Input:** dados brutos do usuário + fotos.
- **Output:** `perfil_enriquecido` com o campo `personalidade_ia` preenchido.
- **Modelo:** Gemini Vision (multimodal).
- **Responsabilidade:** extrair traços de personalidade implícitos (ex: "introvertido com interesse cultural profundo") a partir da bio e das fotos. Identificar contextos visuais (locais, atividades, estilo de vida) que enriquecem o perfil além do que foi declarado explicitamente.

### 7.2. Agente Casamenteiro (Busca + Ranking)

- **Quando atua:** no consumo, quando um usuário solicita matches.
- **Input:** vetor de query do usuário + ChromaDB.
- **Output:** lista Top-30 → filtrada para candidatos com score ≥ 85.
- **Modelo:** Gemini Pro + ChromaDB.
- **Responsabilidade:** executar busca vetorial filtrada pelos metadados hard, aplicar re-ranking com o sistema de scoring ponderado (ver seção 9), e retornar a lista ordenada.

### 7.3. Agente RAG Justificador (Geração)

- **Quando atua:** após o Casamenteiro, para cada um dos Top-10 matches.
- **Input:** Top-10 matches + perfis completos.
- **Output:** justificativas textuais em linguagem natural.
- **Modelo:** Gemini Pro + RAG.
- **Responsabilidade:** gerar explicações do tipo "Vocês têm em comum X e Y, e seus perfis apresentam complementaridade em Z." Aumenta a confiança do usuário no sistema.

### 7.4. Estado compartilhado (AgentState)

O `AgentState` flui entre os nós e acumula:
- Dados do usuário solicitante
- Perfil enriquecido (após o Perfilador)
- Lista de candidatos com scores (após o Casamenteiro)
- Justificativas (após o RAG)

---

## 8. Pipelines de dados

### 8.1. Pipeline de Ingestão (cadastro de um perfil)

1. **Cadastro do usuário** — formulário com dados estruturados, semânticos e fotos.
2. **Agente Perfilador** — invocado como primeiro nó do grafo; roda análise multimodal e gera `personalidade_ia`.
3. **Análise multimodal Gemini Vision** — identifica contextos visuais a partir das fotos.
4. **Concatenação do documento semântico** — `bio + interesses (joined) + objetivo + personalidade_ia` em um único texto.
5. **Geração de embedding** — documento semântico → `text-embedding-004` → vetor de alta dimensão (768d).
6. **Armazenamento no ChromaDB** — vetor + metadados estruturados (idade, cidade, gênero, objetivo) usados posteriormente como filtros hard.

### 8.2. Pipeline de Consumo (geração de matches para um usuário)

1. **Construção do vetor de query** — perfil do solicitante é re-embedado ou recuperado do cache; vira o ponto de referência para busca por similaridade.
2. **Filtros hard (pré-filtragem relacional)** — aplicados via metadados do ChromaDB: faixa etária compatível, cidade/região, gênero preferido, objetivo alinhado. Reduz o espaço de busca antes da fase vetorial.
3. **Busca vetorial Top-K (ChromaDB)** — `K=30`, retorna os 30 perfis mais próximos semanticamente por distância coseno.
4. **Agente Casamenteiro** — aplica o sistema de scoring completo (ver seção 9), normaliza scores 0–100, filtra apenas os candidatos com score final ≥ 85.
5. **Agente RAG Justificador** — para cada um dos Top-10, gera justificativa textual via RAG.
6. **Saída: Top-10 com score ≥ 85** — estrutura final contendo ID do perfil, score de compatibilidade, breakdown dos fatores, e justificativa.

---

## 9. Sistema de scoring (0–100)

| Fator | Peso | Método de cálculo |
|---|---|---|
| Similaridade semântica | **60%** | Cosine similarity entre embeddings (a partir da distância retornada pelo ChromaDB) |
| Interesses em comum | **20%** | +5 pontos por interesse compartilhado (máx 20) |
| Alinhamento de objetivo | **10%** | Match exato do campo `objetivo` (namoro/casual/amizade) |
| Compatibilidade etária | **5%** | Escala linear dentro da faixa preferida |
| Compatibilidade geográfica | **5%** | Mesma cidade = 5pts · mesma região = 2pts |
| **Total** | **100** | |
| **Threshold mínimo para match** | **≥ 85** | Hard cutoff definido pelo enunciado do professor |

---

## 10. Dados semente (seed data)

O notebook precisa popular o ChromaDB com um conjunto de perfis sintéticos diversificados que viabilize a demonstração do hard requirement (10 matches ≥ 85 para o usuário de teste).

O dimensionamento e a distribuição desse pool — quantidade de perfis, distribuição de interesses, cidades, objetivos, idades — são decisões de projeto que devem ser tomadas considerando a restrição de ≥85 pontos. Os perfis de teste usados na demonstração também precisam ser construídos para garantir a viabilidade da saída exigida.

---

## 11. Considerações críticas (pitfalls conhecidos)

### 11.1. Normalização da similaridade coseno
O ChromaDB retorna **distância** coseno, não similaridade. A conversão correta e a normalização para a escala 0–100 precisam ser tratadas explicitamente no Agente Casamenteiro.

### 11.2. Viabilidade matemática do threshold de 85
Atingir score ≥ 85 para 10 perfis depende da combinação de alta similaridade semântica com interesses compartilhados, objetivo igual, idade na faixa e proximidade geográfica. Essa combinação precisa ser validada empiricamente no próprio notebook, com fallback claro caso o resultado não seja alcançado (mensagem explícita, não falha silenciosa).

### 11.3. Determinismo dos LLMs
Execuções sucessivas do Perfilador ou do RAG podem gerar outputs ligeiramente diferentes, o que afeta os embeddings e, por consequência, os matches. Recomenda-se `temperature=0` onde aplicável, e/ou cache do output do Perfilador, para garantir que o notebook entregue resultados consistentes quando re-executado (importante para gravação do vídeo).

### 11.4. Tratamento das fotos
- **Privacidade/LGPD:** não usar fotos de pessoas reais sem consentimento.
- **Custo:** análises do Gemini Vision em 30+ perfis com múltiplas fotos podem ter custo relevante.
- **Reprodutibilidade:** Vision pode variar entre execuções.

Fotos sintéticas, avatares livres de licença ou mocks textuais simulando output do Vision são opções aceitáveis — a decisão deve ser justificada no relatório.

### 11.5. Chaves de API
Nunca hardcoded. Sempre via `google.colab.userdata` ou variáveis de ambiente. O notebook deve falhar com mensagem clara se as chaves não estiverem presentes.

### 11.6. LGPD e ética
O relatório deve conter uma seção tratando: consentimento do usuário, minimização de dados, riscos de viés no Agente Perfilador (ex: estereótipos inferidos a partir de imagens), e considerações éticas específicas para apps de relacionamento.

---

## 12. Ambiente de execução

- **Plataforma principal:** Google Colab (o notebook deve rodar nativamente no Colab, com instalação das dependências na primeira célula).
- **Python:** 3.10+
- **Dependências principais esperadas:** `langgraph`, `chromadb`, `google-generativeai` (ou equivalente Vertex), `pandas`, bibliotecas de visualização padrão.
- **Reprodutibilidade:** o notebook deve poder ser rodado do zero por um avaliador, incluindo setup, seed data, ingestão, consumo e visualizações, sem intervenção manual além do fornecimento das chaves de API.

---

## 13. Saídas esperadas do notebook

O notebook deve demonstrar, de forma autossuficiente:

1. Setup completo do ambiente e dependências.
2. Schema de dados definido.
3. ChromaDB criado e configurado.
4. Seed data sintético gerado e inserido no banco vetorial via pipeline de ingestão completo (passando pelo Agente Perfilador).
5. Visualização do grafo LangGraph.
6. Demo end-to-end: cadastro de um usuário de teste + execução do pipeline de consumo + geração dos 10 matches ≥ 85 com scores, breakdown dos fatores e justificativas.
7. Análises e visualizações: tabela Top-10, distribuição de scores, tempo de execução, cobertura.
8. Seção final de conclusão e próximos passos (alinhada ao que vai no relatório).

---

## 14. Material de apoio para o relatório

O notebook deve produzir, ao longo da execução, material utilizável no relatório:

- Diagramas dos pipelines de ingestão e consumo (podem ser gerados programaticamente ou referenciados como imagens).
- Descrição dos dados coletados e justificativa da escolha.
- Métricas reais do experimento (scores, tempos, distribuição).
- Seção de futuras melhorias (já esboçada no plano do CP4: UI de swipe, feedback loop, PostgreSQL + PostGIS, chat com IA mediadora, análise de sentimento, verificação de autenticidade, API REST, testes A/B).

---

## 15. Material de apoio para o vídeo

O vídeo (25% da nota) será gravado manualmente pela equipe, mas o notebook precisa estar preparado para uma demo limpa:

- Execução sequencial sem erros
- Outputs visualmente claros
- Tempo total de execução razoável
- Resultados determinísticos entre re-execuções (para permitir múltiplos takes)
- Células de cadastro do perfil de teste destacadas
- Apresentação dos 10 matches de forma visualmente compreensível

---

## 16. Critérios de aceitação

A entrega está pronta quando:

- [ ] Notebook roda end-to-end no Google Colab sem erros.
- [ ] Para o perfil de teste, o pipeline retorna **10 matches com score ≥ 85**.
- [ ] Cada match vem com score, breakdown dos fatores e justificativa textual.
- [ ] Os 3 agentes (Perfilador, Casamenteiro, RAG) são visivelmente distintos no código e no grafo.
- [ ] O grafo LangGraph é visualizado no notebook.
- [ ] ChromaDB está sendo efetivamente usado para busca vetorial (não apenas armazenamento).
- [ ] Os pipelines de ingestão e consumo estão claramente separados e documentados no notebook.
- [ ] Todo output, markdown, docstring e mensagem está em Português do Brasil.
- [ ] Não há credenciais hardcoded.
- [ ] O notebook gera material suficiente (tabelas, métricas, diagramas) para sustentar o relatório.

---

## 17. Fora do escopo desta entrega

- Frontend web/mobile (é um notebook, não um app em produção).
- Autenticação, contas de usuário, persistência além do ChromaDB local.
- Deploy em servidor remoto.
- Banco relacional externo (PostgreSQL etc. ficam como "futuras melhorias").
- Gravação do vídeo (tarefa manual da equipe).
- Redação final do relatório em formato de documento (o notebook produz insumos, mas o documento final é escrito separadamente).

---

**Fim do briefing.**