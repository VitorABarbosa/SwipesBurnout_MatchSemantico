---
phase: 01-fundacao
plan: 02
subsystem: database
tags: [pydantic, schema, validation, uuid, embedding-document, ptbr]

requires:
  - phase: 01-fundacao
    provides: "Pacote `connect_ai` instalavel + pydantic>=2.6.0 declarado em requirements.txt + suite pytest configurada"
provides:
  - "Modelo Pydantic v2 `Perfil` (3 grupos de campos do BRIEFING §6 + `personalidade_ia` gerado)"
  - "Tipos Literal `Genero`, `GeneroPreferido` (com 'todos'), `Objetivo` (namoro/casual/amizade)"
  - "Funcao `gerar_uuid()` -> str (UUIDv4, usada como default_factory de `Perfil.id`)"
  - "Funcao `construir_documento_semantico(perfil)` -> str (fonte unica do texto enviado ao text-embedding-004)"
  - "Validacoes Pydantic: idade [18,99], genero/objetivo conjunto fechado, faixa_etaria_pref ordem+dominio, interesses nao vazio, bio nao vazia"
affects:
  - 01-03 (repositorio ChromaDB usa `Perfil` para metadata e `construir_documento_semantico` para embedding)
  - 01-04 (README documenta o schema)
  - 02-* (seed data instancia `Perfil`)
  - 03-* (Perfilador preenche `personalidade_ia`)
  - 04-* (pipeline de ingestao usa `construir_documento_semantico` antes de embedar)
  - 05-* (pipeline de consumo usa `construir_documento_semantico` para a query e `Perfil` para filtros hard)
  - 06-* (front Streamlit constroi `Perfil` a partir do formulario)
  - 07-* (notebook importa `Perfil` para a demo end-to-end)

tech-stack:
  added: []  # Nenhuma dependencia nova — pydantic ja foi adicionado no plano 01-01
  patterns:
    - "Schema Pydantic v2 com `Literal` + `Field(ge=, le=, min_length=)` para constraints declarativas"
    - "field_validator que normaliza (strip + filtro) antes de validar — interesses sem strings vazias"
    - "model_validator(mode='after') para validacoes que envolvem multiplos campos (ordem + dominio da tupla)"
    - "default_factory para id (UUIDv4) — perfis podem ser instanciados sem id explicito"
    - "Funcao canonica de construcao do documento semantico — fonte unica da verdade entre ingestao e consumo"
    - "Defesa contra vazamento de tokens Python ('None'/'null') no texto enviado ao embedding"

key-files:
  created:
    - "connect_ai/schema.py — modelo `Perfil`, helpers `gerar_uuid` e `construir_documento_semantico`, tipos Literal exportados"
    - "tests/test_schema.py — 19 testes (14 do schema + 5 do documento semantico)"
  modified: []

key-decisions:
  - "Pydantic Literal (em vez de Enum) para `Genero`/`Objetivo` — nativo do Pydantic, gera ValidationError sem boilerplate, serializa como string limpa para o ChromaDB metadata"
  - "`personalidade_ia` opcional (default None) — o Perfilador (Fase 3) e quem preenche; manter None ate la evita que perfis sem perfilamento sejam inseridos no ChromaDB com placeholder textual"
  - "`genero_preferido` aceita 'todos' alem dos valores de `genero` — modela a opcao 'sem preferencia' explicitamente, em vez de obrigar string vazia ou None que confundiria o filtro hard"
  - "`construir_documento_semantico` OMITE a secao 'Personalidade' quando vazia — vazar o token literal 'None' no embedding distorceria a representacao vetorial e prejudicaria os scores"
  - "model_validator em vez de field_validator para `faixa_etaria_pref` — precisa comparar os 2 elementos entre si, e `mode='after'` garante que ja foram convertidos para int"
  - "Funcao `construir_documento_semantico` como fonte UNICA da verdade — qualquer divergencia entre o texto embedado na ingestao e o texto da query no consumo invalida o threshold >=85"

patterns-established:
  - "Schema central modular: tipos primitivos (Literal) + modelo (BaseModel) + helpers (gerar_uuid, construir_documento_semantico) no mesmo modulo"
  - "Testes TDD com helper `_perfil_valido_kwargs(**overrides)` — base imutavel + sobrescrita pontual para cada caso"
  - "Cobertura simetrica: para cada validador, ao menos 1 teste positivo + 1 teste negativo"

requirements-completed: [DATA-01, DATA-02, DATA-03, DATA-04]

duration: 3min
completed: 2026-04-19
---

# Phase 1 Plano 02: Schema de Dados (`Perfil` Pydantic) — Resumo

**Modelo Pydantic v2 `Perfil` com 3 grupos de campos (estruturados, semanticos, multimodais) + `personalidade_ia`, validacao declarativa, gerador UUIDv4 e funcao canonica `construir_documento_semantico` que define o texto unico enviado ao `text-embedding-004`.**

## Performance

- **Duração:** 3 min
- **Início:** 2026-04-19T18:45:55Z
- **Conclusão:** 2026-04-19T18:49:11Z
- **Tasks:** 2/2 concluídas (ambas TDD)
- **Arquivos criados:** 2
- **Arquivos modificados:** 0
- **Commits:** 4 (TDD: RED + GREEN para cada uma das 2 tasks) + 1 metadata final

## Realizações

- Modelo `Perfil` (Pydantic v2) implementado com os 3 grupos do BRIEFING §6 (estruturados/semânticos/multimodais) + o campo `personalidade_ia` gerado pelo Perfilador
- Tipos `Literal` para `Genero` (4 valores), `GeneroPreferido` (5 valores, inclui `"todos"`) e `Objetivo` (`namoro`/`casual`/`amizade`) — Pydantic gera `ValidationError` automaticamente para qualquer valor fora dos conjuntos
- Constraints declarativas via `Field`: `idade` em `[18, 99]`, `nome`/`cidade` `min_length=1`, `bio` `min_length=1 max_length=2000`, `interesses` `min_length=1`
- `field_validator` em `interesses` faz `strip` e remove strings vazias antes de validar — protege contra `["", "  "]` que passaria pelo `min_length`
- `model_validator(mode="after")` em `faixa_etaria_pref` garante ordem (mín ≤ máx) + domínio (`[18, 99]`) — o que `field_validator` sobre tupla não oferece de forma natural
- `gerar_uuid()` produz UUIDv4 únicos — usado como `default_factory` de `Perfil.id`
- `construir_documento_semantico(perfil)` é a **fonte única da verdade** do texto enviado ao `text-embedding-004`: concatena `bio + interesses + objetivo + personalidade_ia` em PT-BR e omite a seção `"Personalidade"` quando vazia (defesa contra vazamento de `"None"`/`"null"` no embedding)
- Cobertura: 19 testes em `tests/test_schema.py` cobrem casos positivos (instanciação, aceitação dos 3 objetivos, `genero_preferido="todos"`, `personalidade_ia` opcional/preenchida) **e** negativos (idade fora da faixa, gênero inválido, objetivo inválido, faixa invertida, faixa fora do domínio, interesses vazio, bio vazia)

## Commits por Task

Cada task TDD produziu 2 commits (RED → GREEN). Sem refactor — código já está limpo.

1. **Task 1 RED:** Testes falhando do schema `Perfil` — `0a048ff` (test)
2. **Task 1 GREEN:** Schema `Perfil` com validação Pydantic — `6908d1c` (feat)
3. **Task 2 RED:** Testes falhando do documento semântico — `28de35f` (test)
4. **Task 2 GREEN:** Implementação de `construir_documento_semantico` — `4b2d504` (feat)

**Plan metadata:** *(adicionado pelo commit final de docs)*

## Arquivos Criados/Modificados

### Criados
- `connect_ai/schema.py` (143 linhas) — modelo `Perfil`, tipos `Genero`/`GeneroPreferido`/`Objetivo`, `gerar_uuid()`, `construir_documento_semantico()`
- `tests/test_schema.py` (180 linhas) — 19 testes cobrindo schema + documento

### Modificados
*(nenhum — plano puramente aditivo sobre o pacote `connect_ai`)*

## Definição final do schema

| Grupo | Campo | Tipo | Constraint |
|---|---|---|---|
| Estruturado | `id` | `str` | UUIDv4 (default_factory=`gerar_uuid`) |
| Estruturado | `nome` | `str` | `min_length=1`, `max_length=120` |
| Estruturado | `idade` | `int` | `ge=18`, `le=99` |
| Estruturado | `cidade` | `str` | `min_length=1`, `max_length=120` |
| Estruturado | `genero` | `Literal["feminino","masculino","nao_binario","outro"]` | conjunto fechado |
| Estruturado | `genero_preferido` | `Literal[...4 valores + "todos"]` | conjunto fechado |
| Estruturado | `faixa_etaria_pref` | `Tuple[int, int]` | ambos em `[18,99]` e `min ≤ max` (model_validator) |
| Estruturado | `objetivo` | `Literal["namoro","casual","amizade"]` | conjunto fechado |
| Semântico | `bio` | `str` | `min_length=1`, `max_length=2000` |
| Semântico | `interesses` | `List[str]` | `min_length=1` (após strip+filtro de vazios) |
| Multimodal | `foto_perfil` | `Optional[str]` | default `None` (mock textual nesta entrega) |
| Multimodal | `fotos_extras` | `List[str]` | default `[]` |
| Gerado | `personalidade_ia` | `Optional[str]` | default `None` (preenchido pelo Perfilador) |

## Formato exato do documento semântico

Template usado por `construir_documento_semantico(perfil)`:

```
Bio: <perfil.bio strip>. Interesses: <i1, i2, ...>. Objetivo: <perfil.objetivo>. Personalidade: <perfil.personalidade_ia strip>.
```

A seção `"Personalidade: ..."` é **omitida** quando `perfil.personalidade_ia` é `None`, string vazia ou apenas whitespace. Isso evita inserir os tokens literais `"None"` ou `"null"` no texto enviado ao `text-embedding-004`, o que distorceria o vetor de representação e prejudicaria os scores de similaridade.

**Exemplo (perfil sem personalidade_ia):**
```
Bio: hello. Interesses: a. Objetivo: namoro.
```

**Exemplo (perfil com personalidade_ia):**
```
Bio: Adoro caminhadas. Interesses: caminhada, jazz, culinaria. Objetivo: namoro. Personalidade: Introvertida com forte interesse cultural.
```

## Lista de Exports (`connect_ai.schema`)

| Símbolo | Tipo | Uso |
|---|---|---|
| `Perfil` | `class(BaseModel)` | Modelo de dados do usuário |
| `Genero` | `Literal[...]` | Type alias para `genero` |
| `GeneroPreferido` | `Literal[...]` | Type alias para `genero_preferido` (inclui `"todos"`) |
| `Objetivo` | `Literal[...]` | Type alias para `objetivo` |
| `gerar_uuid` | `() -> str` | Gera UUIDv4 (`default_factory` de `Perfil.id`) |
| `construir_documento_semantico` | `(Perfil) -> str` | Monta o texto enviado ao `text-embedding-004` |

## Decisões Tomadas

| Decisão | Justificativa |
|---|---|
| `Literal` em vez de `Enum` para os campos categóricos | Nativo do Pydantic, gera `ValidationError` sem boilerplate, serializa como string limpa nos metadados do ChromaDB (sem `Genero.feminino` no JSON) |
| `personalidade_ia` opcional (default `None`) | O Perfilador (Fase 3) é quem preenche; manter `None` até lá evita inserir perfis com placeholder textual no ChromaDB e separa claramente "ainda não processado" de "processado e vazio" |
| `genero_preferido` aceita `"todos"` além dos 4 valores de `genero` | Modela explicitamente a opção "sem preferência" do front em vez de exigir `None` ou string vazia, que confundiria o filtro hard do ChromaDB |
| `construir_documento_semantico` **omite** a seção `"Personalidade"` quando vazia | Vazar o token literal `"None"` no embedding distorce a representação vetorial e prejudica os scores; melhor degradar graciosamente |
| `model_validator(mode="after")` para `faixa_etaria_pref` | Precisa comparar os 2 elementos da tupla entre si; `mode="after"` garante que já estão convertidos para `int` e que os outros campos também já passaram pela validação |
| `field_validator` em `interesses` com `strip` antes de checar vazio | `min_length=1` sozinho aceitaria `[""]` ou `["  "]`, que passariam adiante e quebrariam o documento embedado; o validator normaliza primeiro |
| Função canônica de construção do documento (não inline) | Garante consistência entre o vetor armazenado na ingestão e o vetor de query no consumo; qualquer divergência invalida o threshold ≥ 85 |

## Deviations from Plan

None - plan executed exactly as written.

O plano foi seguido tarefa por tarefa, ciclo TDD por ciclo TDD. Não houve descobertas de bugs, dependências faltantes nem decisões arquiteturais novas durante a execução. Todos os 19 testes foram cobertos pelo código fornecido no `<action>` de cada task; nenhum desvio das Regras 1-4 foi acionado.

**Total deviations:** 0
**Impact on plan:** Plano executado conforme escrito. Sem scope creep.

## Issues Encountered

Nenhum problema durante a execução. A suíte completa (`tests/test_config.py` + `tests/test_schema.py`) reporta 27 testes passando em 0.04s, sem regressões no módulo de configuração da Fase 1 Plano 01.

## User Setup Required

Nenhum — o schema é puramente Python e não requer configuração externa. As chaves Google Gemini só serão necessárias quando começarmos a usar `text-embedding-004` de fato (Fase 4 — Pipeline de Ingestão).

## Next Phase Readiness

- **Pronto para 01-03 (Repositório ChromaDB):** o `Perfil` é instanciável, `construir_documento_semantico` define o texto a ser embedado, e os filtros hard (idade, cidade, gênero, objetivo) já estão tipados como `Literal` — perfeitos para serem usados como `metadata` no ChromaDB.
- **Pronto para 01-04 (README):** o schema está estável e pode ser documentado.
- **Pronto para a Fase 2 (Seed Data):** geradores sintéticos podem instanciar `Perfil` diretamente, e `gerar_uuid()` resolve a chave primária sem colisão.
- **Pronto para a Fase 3 (Agentes):** o Perfilador tem o campo `personalidade_ia` disponível para preencher; o Casamenteiro tem todos os campos estruturados como filtros hard; o RAG tem `bio`, `interesses` e `personalidade_ia` para construir justificativas.
- **Sem bloqueadores.**

## Self-Check

Verificação dos artefatos antes de finalizar:

- `connect_ai/schema.py` — FOUND (143 linhas, exporta `Perfil`, `Genero`, `GeneroPreferido`, `Objetivo`, `gerar_uuid`, `construir_documento_semantico`)
- `tests/test_schema.py` — FOUND (180 linhas, 19 testes)
- Commit `0a048ff` (Task 1 RED) — FOUND
- Commit `6908d1c` (Task 1 GREEN) — FOUND
- Commit `28de35f` (Task 2 RED) — FOUND
- Commit `4b2d504` (Task 2 GREEN) — FOUND
- `pytest tests/test_schema.py -v` — 19 passed
- `pytest tests/ -v` — 27 passed (sem regressao no test_config.py)
- `python -c "from pydantic import BaseModel; from connect_ai.schema import Perfil; assert issubclass(Perfil, BaseModel)"` — OK
- `python -c "from connect_ai.schema import gerar_uuid; import uuid; uuid.UUID(gerar_uuid())"` — OK
- 100 chamadas de `gerar_uuid()` produziram 100 strings distintas (sem colisão)
- `Perfil(idade=15, ...)` levanta `pydantic.ValidationError` — confirmado pelo `test_idade_minima_18`
- Documento gerado para perfil sem `personalidade_ia` NÃO contém `"None"` nem `"null"` — confirmado pelo `test_documento_omite_personalidade_quando_ausente`

## Self-Check: PASSED

---
*Phase: 01-fundacao*
*Completed: 2026-04-19*
