# CONNECT.AI — Dating powered by AI

> Motor de matchmaking semântico multi-agente desenvolvido para o **Checkpoint 5** da disciplina **Sistemas Multi-Agentes e IA Generativa (NLP)** da FIAP.

Para qualquer perfil submetido, o pipeline retorna **10 perfis com score de compatibilidade ≥ 85** (escala 0–100), com breakdown dos fatores e justificativa textual gerada por IA.

---

## Equipe

| Nome                | RM     |
|---------------------|--------|
| Matheus Barbosa     | 561085 |
| Guilherme Henrique  | 559977 |
| Vitor Adauto        | 560247 |

Curso: Tecnologia em Inteligência Artificial — FIAP
Disciplina: Sistemas Multi-Agentes e IA Generativa (NLP)

---

## Visão Geral

CONNECT.AI substitui filtros rígidos de apps de relacionamento por uma análise semântica multimodal orquestrada por três agentes:

- **Perfilador** — gera traços de personalidade a partir do perfil bruto (mock textual do Gemini Vision).
- **Casamenteiro** — aplica filtros hard, busca vetorial Top-30 no ChromaDB e scoring ponderado.
- **RAG Justificador** — gera justificativas em linguagem natural para cada match.

Os três agentes são nós distintos de um grafo **LangGraph** com `AgentState` compartilhado.

### Stack

- Python 3.10+
- LangGraph (orquestração)
- Google `google-generativeai` (Gemini Pro + `text-embedding-004`)
- ChromaDB (banco vetorial local)
- Streamlit (front)
- Pandas (insumos do relatório)

---

## Requisitos do Sistema

- Python **3.10 ou superior** (`python --version`)
- `pip` atualizado (`python -m pip install --upgrade pip`)
- Acesso à internet para baixar dependências e chamar a API do Gemini
- Chave de API do **Google AI Studio** (gratuita) — instruções abaixo

---

## Instalação

1. **Clone o repositório**

   ```bash
   git clone <url-do-repositorio>
   cd CP5_PLN
   ```

2. **(Recomendado) Crie e ative um ambiente virtual**

   ```bash
   python -m venv .venv

   # Linux / macOS
   source .venv/bin/activate

   # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1

   # Windows (Git Bash)
   source .venv/Scripts/activate
   ```

3. **Instale o pacote em modo editável**

   ```bash
   pip install -e .
   ```

   Isso instala o pacote `swipes_burnout` e todas as dependências listadas em `pyproject.toml`.

   Para incluir as dependências de teste:

   ```bash
   pip install -e ".[dev]"
   ```

4. **Verifique a instalação**

   ```bash
   python -c "import swipes_burnout; print(swipes_burnout.__version__)"
   ```

   Deve imprimir: `0.1.0`

---

## Configuração de Chaves de API

> **Atenção:** Nenhuma chave fica hardcoded no código. Elas são lidas via arquivo `.env` (que está no `.gitignore`) ou variáveis de ambiente do sistema.

1. **Obtenha sua chave do Google AI Studio**

   Acesse [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey), faça login com uma conta Google e clique em **"Create API key"**. A chave começa com `AIza...`.

2. **Crie o arquivo `.env`**

   Copie o template:

   ```bash
   # Linux / macOS / Git Bash
   cp .env.example .env

   # Windows (PowerShell)
   Copy-Item .env.example .env
   ```

3. **Preencha o `.env`** com sua chave:

   ```
   GOOGLE_API_KEY=AIza...sua-chave-real-aqui
   CHROMA_PERSIST_DIR=./chroma_db
   CHROMA_COLLECTION=perfis_swipes_burnout
   ```

   Se a chave não for configurada, a aplicação falhará com mensagem clara em PT-BR (não com `KeyError`).

---

## Execução do Front (Streamlit)

Após a instalação e a configuração do `.env`:

```bash
streamlit run app/streamlit_app.py
```

O Streamlit abrirá o navegador em `http://localhost:8501`. As páginas disponíveis são:

- **Cadastro** — formulário para criar um novo perfil e dispará-lo no pipeline de ingestão.
- **Matches** — executa o pipeline de consumo para o perfil selecionado e mostra os 10 matches em cards com score, breakdown e justificativa.
- **Visualização** — exibe o grafo LangGraph e os diagramas dos pipelines de ingestão e consumo.

> **Primeira execução:** use o botão "Popular banco com seed data" na barra lateral antes de buscar matches — o ChromaDB começa vazio.

---

## Execução do Notebook (Google Colab)

O notebook `notebook/demo_cp5.ipynb` é a entrega principal (50% da nota) e roda nativamente no Google Colab.

1. Acesse [https://colab.research.google.com](https://colab.research.google.com)
2. Faça **File → Upload notebook** e envie `notebook/demo_cp5.ipynb`
3. Configure a chave da API em **Tools → Secrets** com o nome `GOOGLE_API_KEY`
4. Execute todas as células sequencialmente (`Runtime → Run all`)

A primeira célula instala as dependências automaticamente. As células seguintes mostram, em ordem: setup, schema, ChromaDB, seed data, ingestão, grafo LangGraph, demo do pipeline de consumo, Top-10 com breakdown e justificativas, e visualizações.

### Execução local do notebook (alternativa)

Caso prefira rodar localmente com Jupyter:

```bash
pip install jupyter
jupyter notebook notebook/demo_cp5.ipynb
```

A célula de instalação no topo do notebook é segura para rodar mesmo após `pip install -e .` (é idempotente).

---

## Estrutura do Projeto

```
CP5_PLN/
├── swipes_burnout/           # Pacote Python (schema, agentes, pipelines, scoring, repositório)
│   ├── __init__.py
│   ├── config.py         # Leitura de .env e chaves de API
│   ├── schema.py         # Modelo Pydantic Perfil + utilitários
│   ├── repositorio.py    # Wrapper ChromaDB
│   └── scoring_utils.py  # Conversão distância coseno → score 0-100
├── app/                  # Front Streamlit
│   └── streamlit_app.py  # (criado nas fases seguintes)
├── notebook/             # Notebook Colab fino que importa swipes_burnout
│   └── demo_cp5.ipynb    # (criado na Fase 7)
├── relatorio/            # Insumos para o relatório (diagramas, tabelas, ETICA.md)
├── tests/                # Testes pytest
├── chroma_db/            # Persistência local do ChromaDB (gitignored)
├── .env.example          # Template das variáveis de ambiente
├── .env                  # Suas chaves locais (gitignored — NÃO commitar)
├── pyproject.toml        # Configuração do pacote Python
├── requirements.txt      # Dependências (espelho do pyproject.toml)
└── README.md
```

---

## Testes

```bash
# Rodar todos os testes
pytest

# Rodar testes de um módulo específico
pytest tests/test_schema.py -v

# Rodar com saída detalhada
pytest -v --tb=short
```

Os testes cobrem o schema, o módulo de configuração, o wrapper do ChromaDB, a função de scoring e (a partir da Fase 5) o pipeline de consumo end-to-end.

---

## Decisões de Projeto

- **Mocks textuais para o Gemini Vision** — eliminam custo, garantem determinismo na regravação do vídeo de demo e respeitam LGPD (não usamos fotos reais). Decisão registrada em `.planning/PROJECT.md`.
- **Persistência local do ChromaDB** — em `./chroma_db/` (gitignored). Para resetar o banco, basta apagar o diretório.
- **Seed data sintético calibrado** — gerado com seed fixa para garantir reprodutibilidade entre execuções (importante para o vídeo).
- **Idioma Português do Brasil** — 100% do código, comentários, docstrings, mensagens de erro, outputs e documentação. Sem exceções.

---

## Solução de Problemas

### "ConfigError: A variável de ambiente 'GOOGLE_API_KEY' não está definida"

O arquivo `.env` não foi criado ou não contém a chave. Volte para a seção [Configuração de Chaves de API](#configuração-de-chaves-de-api).

### "ModuleNotFoundError: No module named 'swipes_burnout'"

O pacote não foi instalado em modo editável. Execute:

```bash
pip install -e .
```

### Erro de SSL/TLS ao chamar a API do Google

Verifique sua conexão com a internet e o relógio do sistema. Em redes corporativas, pode ser necessário configurar o certificado raiz da empresa.

### "ChromaDB collection already exists" ao re-rodar o notebook

Comportamento esperado — o ChromaDB usa `get_or_create_collection`. Para começar do zero, apague o diretório `./chroma_db/` ou use o botão "Resetar banco" no front.

---

## Licença e Uso

Este projeto é entregue como atividade acadêmica do CP5 da FIAP. Os perfis utilizados são **100% sintéticos** — nenhum dado real de pessoas é coletado, processado ou armazenado.

---

*CONNECT.AI — Checkpoint 5 — FIAP — 2026*
