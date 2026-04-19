---
phase: 01-fundacao
plan: 01
subsystem: infra
tags: [setuptools, pyproject, python-dotenv, pytest, env-config, ptbr]

requires: []
provides:
  - "Pacote `connect_ai` instalavel via `pip install -e .`"
  - "Estrutura de diretorios `connect_ai/`, `app/`, `notebook/`, `relatorio/`, `tests/`"
  - "`requirements.txt` com lower bounds das 8 dependencias obrigatorias"
  - "`.env.example` documentando GOOGLE_API_KEY, CHROMA_PERSIST_DIR, CHROMA_COLLECTION"
  - "`.gitignore` cobrindo `.env`, `chroma_db/`, caches Python e checkpoints de notebook"
  - "`connect_ai.config` com `obter_chave_api`, `carregar_env`, `obter_diretorio_chroma`, `obter_nome_colecao`"
  - "`ConfigError` (subclasse de `RuntimeError`) com mensagem PT-BR para chaves ausentes"
  - "Suite pytest configurada com `tests/conftest.py` injetando a raiz no `sys.path`"
affects:
  - 01-02 (schema Pydantic — depende do pacote instalavel)
  - 01-03 (repositorio ChromaDB — usa `obter_diretorio_chroma` e `obter_nome_colecao`)
  - 01-04 (README — substitui placeholder)
  - todos os planos das fases 2-7 (precisam importar `connect_ai`)

tech-stack:
  added:
    - "setuptools>=68 (build-backend)"
    - "python-dotenv>=1.0.0 (carregamento de .env)"
    - "pytest>=8.0.0 (suite de testes)"
    - "langgraph>=0.2.0 (orquestracao multi-agente)"
    - "chromadb>=0.5.0 (banco vetorial)"
    - "google-generativeai>=0.8.0 (Gemini Pro/Vision + text-embedding-004)"
    - "streamlit>=1.36.0 (front)"
    - "pandas>=2.2.0 (tabelas para relatorio)"
    - "pydantic>=2.6.0 (validacao de schema, usado em 01-02)"
  patterns:
    - "Mensagens de erro em PT-BR via excecao customizada (`ConfigError`) ao inves de tracebacks crus"
    - "Configuracao centralizada — todo acesso a variaveis de ambiente passa por `obter_chave_api`"
    - "Idempotencia explicita em `carregar_env()` via flag de modulo `_ENV_CARREGADO`"
    - "TDD para o modulo de configuracao (RED → GREEN — refactor nao necessario)"
    - "Build-backend setuptools com `[tool.setuptools.packages.find]` excluindo subpastas nao-pacote (`app/`, `tests/`, `notebook/`, `relatorio/`)"

key-files:
  created:
    - "connect_ai/__init__.py — marcador do pacote, expoe `__version__ = '0.1.0'`"
    - "connect_ai/config.py — modulo de configuracao com leitura segura de chaves"
    - "app/__init__.py — marcador (Streamlit nao precisa importar como pacote)"
    - "tests/__init__.py — marcador"
    - "tests/conftest.py — injeta a raiz no sys.path para testes"
    - "tests/test_config.py — 8 testes do modulo de configuracao"
    - "notebook/.gitkeep, relatorio/.gitkeep — preservam diretorios vazios"
    - "requirements.txt — dependencias com lower bounds"
    - "pyproject.toml — build-backend setuptools, pacote `connect_ai`"
    - ".env.example — documentacao das variaveis de ambiente"
    - "README.md — placeholder minimo (sera expandido em 01-04)"
  modified:
    - ".gitignore — consolidado com entradas do plano (Python, ChromaDB, Streamlit, notebook checkpoints)"

key-decisions:
  - "Build-backend setuptools (em vez de hatch/poetry) — mais simples para o escopo de aluno e mais estavel para `pip install -e .`"
  - "Lower bounds nas dependencias (sem upper bounds) — facilita reprodutibilidade no Colab sem amarrar a versoes que possam quebrar"
  - "`app/` excluido do pacote `connect_ai` — Streamlit roda via `streamlit run app/streamlit_app.py`, sem import como pacote"
  - "ChromaDB usado em modo embedded (sem `chromadb-client`) — nao ha servidor remoto nesta entrega"
  - "`ConfigError` subclasse de `RuntimeError` — preserva semantica de erro de execucao mas permite captura especifica"
  - "Mensagem de erro instrui o usuario a copiar `.env.example` para `.env` — guia o caminho de correcao em PT-BR"

patterns-established:
  - "Padrao de modulo de config: funcao unica de leitura (`obter_chave_api`) com erro customizado em PT-BR; helpers especificos (diretorio_chroma, nome_colecao) reutilizam essa funcao"
  - "Padrao de teste: monkeypatch em variaveis de ambiente, sem manipulacao de arquivos `.env` reais"

requirements-completed: [ENV-01, ENV-02, ENV-03, ENV-04, ENV-05, ENV-06]

duration: 4min
completed: 2026-04-19
---

# Phase 1 Plano 01: Estrutura do Pacote e Configuração Segura — Resumo

**Pacote `connect_ai` instalável em modo editável via setuptools, com módulo de configuração que lê chaves de API do `.env` e levanta `ConfigError` com mensagem PT-BR quando ausentes.**

## Performance

- **Duração:** 4 min
- **Início:** 2026-04-19T18:37:18Z
- **Conclusão:** 2026-04-19T18:40:55Z
- **Tasks:** 3/3 concluídas
- **Arquivos criados:** 11
- **Arquivos modificados:** 1
- **Commits:** 4 (1 estrutura + 1 deps/install + 2 TDD: RED + GREEN)

## Realizações

- Estrutura completa do projeto criada (`connect_ai/`, `app/`, `notebook/`, `relatorio/`, `tests/`)
- Pacote `connect_ai` instalável via `pip install -e .` (verificado: `Successfully installed connect_ai-0.1.0`)
- Todas as 8 dependências obrigatórias do BRIEFING §5 declaradas em `requirements.txt` e `pyproject.toml`
- `.env.example` documenta `GOOGLE_API_KEY`, `CHROMA_PERSIST_DIR`, `CHROMA_COLLECTION` em PT-BR
- `.gitignore` previne commit acidental de `.env`, `chroma_db/`, caches Python e checkpoints de notebook
- Módulo `connect_ai.config` implementado via TDD com 8 testes passando
- `ConfigError` custom (subclasse de `RuntimeError`) substitui `KeyError` cru por mensagem PT-BR clara e acionável

## Commits por Task

Cada task foi commitada atomicamente. A Task 3 produziu 2 commits (TDD RED → GREEN).

1. **Task 1: Estrutura de diretórios e arquivos sentinela** — `785ea09` (feat)
2. **Task 2: Dependências e instalação editável** — `e1bea40` (feat)
3. **Task 3 RED: Testes falhando do módulo de configuração** — `dbd6612` (test)
4. **Task 3 GREEN: Implementação do módulo de configuração** — `ba83157` (feat)

**Plan metadata:** _(será adicionado pelo commit final de docs)_

## Arquivos Criados/Modificados

### Criados
- `connect_ai/__init__.py` — marcador do pacote, expõe `__version__ = "0.1.0"`
- `connect_ai/config.py` — módulo de configuração (`ConfigError`, `carregar_env`, `obter_chave_api`, `obter_diretorio_chroma`, `obter_nome_colecao`)
- `app/__init__.py` — marcador vazio
- `tests/__init__.py` — marcador vazio
- `tests/conftest.py` — injeta a raiz do projeto no `sys.path`
- `tests/test_config.py` — 8 testes do módulo de configuração
- `notebook/.gitkeep` — preserva diretório vazio no git
- `relatorio/.gitkeep` — preserva diretório vazio no git
- `requirements.txt` — 8 dependências com lower bounds
- `pyproject.toml` — build-backend setuptools, declaração do pacote `connect_ai`
- `.env.example` — documentação PT-BR das variáveis de ambiente
- `README.md` — placeholder mínimo (será expandido no plano 01-04)

### Modificados
- `.gitignore` — consolidado com entradas do plano (Python, ChromaDB, Streamlit, notebook checkpoints)

## Decisões Tomadas

| Decisão | Justificativa |
|---|---|
| Build-backend `setuptools` (em vez de `hatch`/`poetry`) | Mais simples e estável para o escopo do CP5; ampla compatibilidade com `pip install -e .` no Colab |
| Lower bounds nas dependências (sem upper bounds) | Facilita reprodutibilidade no Colab sem amarrar a versões que podem quebrar; permite `pip install -U` futuro |
| `app/` excluído do pacote `connect_ai` | Streamlit é executado via `streamlit run app/streamlit_app.py`, sem necessidade de import como pacote |
| `ChromaDB` em modo embedded (sem `chromadb-client`) | Não há servidor remoto nesta entrega; modo embedded é o padrão e suficiente |
| `ConfigError` subclasse de `RuntimeError` | Preserva a semântica de erro de execução mas permite captura específica em testes e callers |
| Mensagem de erro instrui a copiar `.env.example` para `.env` | Guia o caminho de correção em PT-BR sem exigir leitura de docs externas |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] README.md placeholder criado**
- **Encontrado durante:** Task 2 (instalação editável)
- **Issue:** O `pyproject.toml` declara `readme = "README.md"`, mas o arquivo não existia. `pip install -e .` falharia ao tentar ler o arquivo de readme inexistente. O README é responsabilidade do plano 01-04, mas a instalação editável é critério de aceitação **deste** plano (Task 2).
- **Fix:** Criado `README.md` placeholder mínimo com nota explícita de que será expandido no plano 01-04.
- **Files modified:** `README.md` (novo arquivo, ~5 linhas)
- **Verification:** `pip install -e . --no-deps` retornou `Successfully installed connect_ai-0.1.0`. Ao executar 01-04, o README mínimo será substituído por documentação completa.
- **Committed in:** `e1bea40` (commit de Task 2)

**2. [Rule 2 - Missing Critical] `.gitignore` consolidado com entradas pré-existentes**
- **Encontrado durante:** Task 1
- **Issue:** Já existia um `.gitignore` no repositório (criado fora deste plano) com entradas úteis adicionais (`*.so`, `.streamlit/secrets.toml`, `*.log`, `outputs/`, `.mypy_cache/`, `.ruff_cache/`) que o template do plano não cobria. Sobrescrever com o template puro perderia cobertura legítima.
- **Fix:** Consolidado o conteúdo: mantidas todas as entradas do plano (`.env`, `chroma_db/`, `__pycache__/`, `.venv/`, `*.egg-info/`, `.pytest_cache/`, `.ipynb_checkpoints/`) + entradas extras pré-existentes que reforçam segurança (`*.key`, `.streamlit/secrets.toml`) e higiene (`*.log`, `outputs/`).
- **Files modified:** `.gitignore`
- **Verification:** Todos os requisitos do `<verify>` da Task 1 passaram (`grep -q "chroma_db/"` e `grep -q "\.env"`).
- **Committed in:** `785ea09` (commit de Task 1)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Ambos os desvios essenciais — o README placeholder destrava o critério de aceitação do `pip install -e .`, e a consolidação do `.gitignore` preserva proteções legítimas. Sem scope creep.

## Issues Encountered

- **Python 3.14 instalado no ambiente:** o plano alvo é Python 3.10+, então 3.14 é compatível. Algumas dependências pesadas (chromadb, langgraph) podem não ter wheels para 3.14 — verificado apenas o instalador do pacote `connect_ai` em si (que funciona). A instalação completa de `requirements.txt` será revalidada no plano 01-03 (que importa o ChromaDB de fato).
- **Pytest detectado configfile=`pyproject.toml`:** pytest usa `pyproject.toml` como marcador de raiz do projeto mesmo sem `[tool.pytest.ini_options]`. Comportamento esperado, sem impacto.

## User Setup Required

Nenhum — o pacote pode ser instalado e os testes podem ser executados sem configuração externa. O usuário precisará configurar `GOOGLE_API_KEY` no `.env` apenas quando começarmos a usar o Gemini de fato (planos da Fase 3 em diante). O `.env.example` já documenta o passo a passo.

## Next Phase Readiness

- **Pronto para 01-02 (Schema Pydantic `Perfil`):** o pacote `connect_ai` é importável, `pydantic>=2.6.0` está em `requirements.txt` e `pyproject.toml`, e a infraestrutura de testes (`tests/conftest.py` + pytest) está pronta.
- **Pronto para 01-03 (Wrapper ChromaDB):** `obter_diretorio_chroma()` e `obter_nome_colecao()` já estão disponíveis para o repositório consumir.
- **Pronto para 01-04 (README expandido):** placeholder mínimo já existe, basta expandir.
- **Sem bloqueadores.**

## Self-Check

Verificação manual dos artefatos antes de finalizar:

- `connect_ai/__init__.py` — FOUND (10 linhas)
- `connect_ai/config.py` — FOUND (78 linhas)
- `app/__init__.py` — FOUND (vazio)
- `tests/__init__.py` — FOUND (vazio)
- `tests/conftest.py` — FOUND (10 linhas)
- `tests/test_config.py` — FOUND (8 testes)
- `requirements.txt` — FOUND (8 dependências)
- `pyproject.toml` — FOUND (build-system + project + setuptools.packages.find)
- `.env.example` — FOUND (3 variáveis)
- `.gitignore` — FOUND (consolidado)
- `README.md` — FOUND (placeholder)
- `notebook/.gitkeep`, `relatorio/.gitkeep` — FOUND
- Commit `785ea09` — FOUND
- Commit `e1bea40` — FOUND
- Commit `dbd6612` — FOUND
- Commit `ba83157` — FOUND
- `pytest tests/test_config.py` — 8 passed
- `pip install -e .` — Successfully installed connect_ai-0.1.0
- `grep -r "AIza" connect_ai/ app/ tests/` — no hits (zero credenciais hardcoded)

## Self-Check: PASSED

---
*Phase: 01-fundacao*
*Completed: 2026-04-19*
