---
phase: 01-fundacao
plan: 04
subsystem: docs
tags: [readme, documentation, ptbr, onboarding, setup-guide]

requires:
  - phase: 01-fundacao
    provides: "Pacote connect_ai instalavel via pip install -e ., .env.example, requirements.txt e pyproject.toml — tudo o que precisa ser referenciado nas instrucoes de setup"
provides:
  - "README.md em PT-BR (256 linhas, 12 secoes nivel-2) cobrindo setup completo do projeto do zero"
  - "Documentacao da equipe (Matheus Barbosa RM561085, Guilherme Henrique RM559977, Vitor Adauto RM560247) e do contexto da disciplina"
  - "Passo a passo de instalacao: clone -> venv -> pip install -e . -> verificacao"
  - "Documentacao da configuracao de GOOGLE_API_KEY via .env (com link para Google AI Studio)"
  - "Comandos de execucao do front Streamlit (streamlit run app/streamlit_app.py) e do notebook Colab (notebook/demo_cp5.ipynb)"
  - "Estrutura completa de diretorios do projeto e secao de troubleshooting com 4 erros mais provaveis"
affects:
  - 02-* (avaliadores e novos membros podem clonar e rodar antes mesmo dos seed data existirem)
  - 06-* (front Streamlit ja referenciado por antecipacao em app/streamlit_app.py)
  - 07-* (notebook Colab ja referenciado em notebook/demo_cp5.ipynb)
  - relatorio (README serve de base para a secao de execucao do relatorio final)
  - video de demo (instrucoes do README sao a fonte para a sequencia gravada)

tech-stack:
  added: []  # README e documentacao pura — nenhuma dependencia nova
  patterns:
    - "README como ponto unico de entrada — tudo o que um avaliador precisa esta em um arquivo"
    - "Forward references explicitas e marcadas — citar app/streamlit_app.py e notebook/demo_cp5.ipynb mesmo antes de existirem (com nota '(criado nas fases seguintes)')"
    - "Comandos exatos copiaveis — cada bloco de codigo e literal, sem placeholders ambiguos"
    - "Instrucoes multiplataforma — Linux/macOS, Windows PowerShell e Windows Git Bash documentados separadamente"
    - "Secao de troubleshooting alinhada com erros reais ja codificados (ex: ConfigError do plano 01-01)"

key-files:
  created: []
  modified:
    - "README.md — substituido placeholder de 5 linhas (criado em 01-01) por documentacao completa de 256 linhas em PT-BR"

key-decisions:
  - "README como arquivo unico (em vez de docs/ multi-arquivo) — escopo de CP5 nao justifica fragmentacao; um avaliador deve achar tudo em um lugar"
  - "Forward references para app/streamlit_app.py e notebook/demo_cp5.ipynb com nota explicita '(criado nas fases seguintes)' — evita refazer o README a cada fase"
  - "Instrucoes de venv para 3 plataformas (Linux/macOS, Windows PowerShell, Windows Git Bash) — equipe usa Windows; avaliador pode usar Mac/Linux"
  - "Troubleshooting cita ConfigError textual (do plano 01-01) e ChromaDB get_or_create_collection (do plano 01-03) — alinha o README com mensagens de erro reais do codigo"
  - "Sem badges de CI/coverage — nao temos esses fluxos configurados; badges falsos quebrariam a confianca no documento"
  - "Sem emojis — convencao do projeto definida em 01-01 (PROJECT.md citacao explicita)"

patterns-established:
  - "Padrao de README do projeto: visao geral -> equipe -> stack -> requisitos -> instalacao -> chaves -> execucao (front + notebook) -> estrutura -> testes -> decisoes -> troubleshooting -> licenca"
  - "Padrao de instrucao multiplataforma: bloco unico com comentarios separadores '# Linux / macOS' e '# Windows (PowerShell)'"
  - "Padrao de comando exato: o usuario pode copiar e colar literalmente sem editar (nada de <PLACEHOLDER>)"

requirements-completed: [ENV-07]

duration: 2 min
completed: 2026-04-19
---

# Phase 1 Plano 04: README em Português do Brasil — Resumo

**README.md de 256 linhas em PT-BR com instruções completas de setup, configuração de chave do Google AI Studio, execução do front Streamlit, execução do notebook Colab, estrutura do projeto e troubleshooting — substituindo o placeholder mínimo criado pelo plano 01-01 e fechando o requisito ENV-07.**

## Performance

- **Duração:** 2 min
- **Início:** 2026-04-19T18:54:11Z
- **Conclusão:** 2026-04-19T18:55:52Z
- **Tasks:** 1/1 concluída
- **Arquivos criados:** 0
- **Arquivos modificados:** 1 (README.md)
- **Commits:** 1 (task) + 1 (metadata final)

## Realizações

- README expandido de 5 linhas (placeholder de 01-01) para 256 linhas de documentação completa em PT-BR
- 12 seções nível-2 cobrindo: visão geral, equipe, stack, requisitos do sistema, instalação, configuração de chaves de API, execução do front, execução do notebook, estrutura do projeto, testes, decisões de projeto, solução de problemas e licença
- Equipe completa documentada com RMs (Matheus Barbosa 561085, Guilherme Henrique 559977, Vitor Adauto 560247) e contexto da disciplina (FIAP, Tecnologia em IA, NLP, CP5)
- Visão geral cita os 3 agentes (Perfilador, Casamenteiro, RAG Justificador) e a stack completa (LangGraph, Gemini, ChromaDB, Streamlit, Pandas)
- Passo a passo de instalação multiplataforma (Linux/macOS, Windows PowerShell, Windows Git Bash) com comandos exatos copiáveis
- Configuração de `GOOGLE_API_KEY` documentada com link direto para Google AI Studio e exemplo do conteúdo do `.env`
- Comandos exatos para rodar front (`streamlit run app/streamlit_app.py`) e notebook (Colab e local com `jupyter notebook notebook/demo_cp5.ipynb`)
- Árvore de diretórios completa com comentários do propósito de cada subpasta
- Seção de troubleshooting com os 4 erros mais prováveis: `ConfigError`, `ModuleNotFoundError`, erro SSL/TLS, `ChromaDB collection already exists`
- Decisões de projeto centralizadas (mocks textuais, persistência local, seed data sintético, idioma PT-BR)
- Nenhum emoji, nenhuma chave hardcoded — apenas placeholder `AIza...sua-chave-real-aqui`

## Commits por Task

1. **Task 1: Escrever README.md em PT-BR com instruções completas de setup** — `4e707a3` (docs)

**Plan metadata:** *(adicionado pelo commit final de docs)*

## Arquivos Criados/Modificados

### Criados
*(nenhum — plano puramente substitutivo)*

### Modificados
- `README.md` — substituído placeholder de 5 linhas por documentação completa de 256 linhas em PT-BR

## Comandos Exatos Documentados (referência rápida)

| Categoria | Comando |
|---|---|
| Clone | `git clone <url-do-repositorio> && cd CP5_PLN` |
| Venv (Linux/macOS) | `python -m venv .venv && source .venv/bin/activate` |
| Venv (Windows PS) | `python -m venv .venv && .\.venv\Scripts\Activate.ps1` |
| Venv (Git Bash) | `python -m venv .venv && source .venv/Scripts/activate` |
| Instalar pacote | `pip install -e .` |
| Instalar com dev deps | `pip install -e ".[dev]"` |
| Verificar versão | `python -c "import connect_ai; print(connect_ai.__version__)"` |
| Copiar .env (Unix) | `cp .env.example .env` |
| Copiar .env (Windows PS) | `Copy-Item .env.example .env` |
| Front Streamlit | `streamlit run app/streamlit_app.py` |
| Notebook local | `pip install jupyter && jupyter notebook notebook/demo_cp5.ipynb` |
| Testes | `pytest` |
| Testes verbose | `pytest -v --tb=short` |

## Forward References (arquivos citados que ainda não existem)

| Arquivo citado | Fase prevista | Justificativa |
|---|---|---|
| `app/streamlit_app.py` | Fase 6 | Front Streamlit; o README ancora o comando de execução para evitar reescrita futura |
| `notebook/demo_cp5.ipynb` | Fase 7 | Notebook Colab que importa `connect_ai`; entrega principal (50% da nota) |
| `connect_ai/repositorio.py` | Plano 01-03 | Wrapper ChromaDB; já planejado, será criado a seguir |
| `connect_ai/scoring_utils.py` | Fase 5 | Conversão distância coseno → score 0-100 |
| `relatorio/ETICA.md` | Fase 7 ou 8 | Seção de ética/LGPD do relatório |

Cada forward reference é marcada na árvore de diretórios com `# (criado nas fases seguintes)` ou similar, deixando claro ao avaliador que o arquivo existirá oportunamente.

## Notas de Manutenção (o que precisa ser atualizado em fases futuras)

- **Fase 01-03:** quando `connect_ai/repositorio.py` for criado, validar que o exemplo da seção "Estrutura do Projeto" continua coerente (a função `get_or_create_collection` já é citada no troubleshooting).
- **Fase 2 (seed data):** se o nome do gerador ou o caminho mudar, atualizar a menção a "Popular banco com seed data" na seção "Execução do Front".
- **Fase 6 (Streamlit):** se o nome do arquivo do front for diferente de `app/streamlit_app.py`, atualizar todas as 3 menções no README (instalação, execução do front, estrutura).
- **Fase 7 (notebook):** se o notebook for renomeado de `notebook/demo_cp5.ipynb`, atualizar todas as 4 menções (execução notebook, execução local, estrutura, forward reference table acima).
- **Antes da entrega final:** trocar `<url-do-repositorio>` na seção "Instalação" pela URL real do repositório no GitHub.

## Decisões Tomadas

| Decisão | Justificativa |
|---|---|
| README como arquivo único | Escopo do CP5 não justifica fragmentação em `docs/`; um avaliador deve achar tudo em um lugar |
| Forward references com nota explícita | Evita reescrever o README a cada fase nova; o leitor entende que `app/streamlit_app.py` ainda não existe |
| Instruções de venv para 3 plataformas | A equipe usa Windows mas o avaliador pode estar em Mac/Linux; a documentação cobre os 3 cenários |
| Troubleshooting alinhado com erros reais | Cita `ConfigError` (mensagem definida em 01-01) e `get_or_create_collection` (definido em 01-03), não erros genéricos |
| Sem badges de CI/coverage | Não temos esses fluxos configurados; badges falsos minariam a credibilidade do documento |
| Sem emojis | Convenção definida no PROJECT.md desde a inicialização do projeto |
| Comandos exatos copiáveis | Avaliador deve poder copiar-colar sem editar nada além de `<url-do-repositorio>` e da chave da API |

## Deviations from Plan

None - plan executed exactly as written.

O plano foi seguido tarefa por tarefa. Não houve descobertas de bugs, dependências faltantes nem decisões arquiteturais novas durante a execução. O conteúdo do README especificado no `<action>` da Task 1 cobriu todos os critérios de aceitação sem necessidade de fixes ou adições.

**Total deviations:** 0
**Impact on plan:** Plano executado conforme escrito. Sem scope creep.

## Issues Encountered

Nenhum problema durante a execução. O `git commit` emitiu apenas um warning informativo sobre conversão de line-endings LF/CRLF (esperado em Windows), sem afetar o resultado.

## User Setup Required

Nenhum — README é documentação pura. O usuário só precisa segui-lo (ver a si mesmo seguindo as instruções é o teste final, mas isso é tarefa do avaliador, não setup).

## Next Phase Readiness

- **Pronto para 01-03 (Repositório ChromaDB):** o README já documenta o wrapper `connect_ai/repositorio.py` na árvore de diretórios e cita `get_or_create_collection` no troubleshooting; quando o módulo for criado, o README continua coerente.
- **Pronto para encerrar a Fase 1:** todos os 4 planos (estrutura, schema, README) cobrem as fundações; o plano 01-03 (repositório ChromaDB) é o último da fase.
- **Pronto para Fases 2-7:** o README serve de porta de entrada; conforme novos artefatos forem adicionados (seed data, agentes, pipelines, front, notebook), basta validar que os caminhos citados continuam corretos.
- **Sem bloqueadores.**

## Self-Check

Verificação dos artefatos antes de finalizar:

- `README.md` — FOUND (256 linhas, 12 seções nível-2)
- Commit `4e707a3` (Task 1: docs) — FOUND
- Conteúdo `CONNECT.AI` — FOUND
- Conteúdo `pip install -e .` — FOUND
- Conteúdo `streamlit run app/streamlit_app.py` — FOUND
- Conteúdo `demo_cp5.ipynb` — FOUND
- Conteúdo `GOOGLE_API_KEY` — FOUND
- Conteúdo `.env.example` — FOUND
- Conteúdo `Matheus Barbosa` — FOUND
- Conteúdo `Guilherme Henrique` — FOUND
- Conteúdo `Vitor Adauto` — FOUND
- Conteúdo `Python **3.10` — FOUND
- Seções obrigatórias (Equipe, Visão Geral, Stack, Requisitos do Sistema, Instalação, Configuração de Chaves de API, Execução do Front, Execução do Notebook, Estrutura do Projeto, Testes, Solução de Problemas) — TODAS FOUND
- `grep` por emojis (faixas U+1F300–U+1FAFF e U+2600–U+27BF) — sem matches
- Únicas ocorrências de `AIza` são placeholders explícitos (`AIza...` e `AIza...sua-chave-real-aqui`) — sem chaves reais

## Self-Check: PASSED

---
*Phase: 01-fundacao*
*Completed: 2026-04-19*
