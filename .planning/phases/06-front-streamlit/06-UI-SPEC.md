---
phase: 6
slug: front-streamlit
status: draft
shadcn_initialized: false
preset: none
created: 2026-04-22
---

# Phase 6 — UI Design Contract

> Visual and interaction contract para o Front Streamlit do CONNECT.AI (CP5 FIAP).
> Gerado por gsd-ui-researcher. Verificado pelo gsd-ui-checker.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | none — Streamlit nativo |
| Preset | not applicable |
| Component library | Streamlit built-ins (`st.form`, `st.columns`, `st.expander`, `st.metric`, `st.progress`, `st.image`, `st.spinner`) |
| Icon library | none — texto puro em PT-BR (unicode: checkmark ✓ apenas em badges de score) |
| Font | Streamlit default (Source Sans Pro / system-ui fallback) |
| Theming | `st.set_page_config` + bloco `st.markdown` com `<style>` injetado uma vez no topo do app |

> shadcn gate: inaplicável. Stack é Python + Streamlit, sem React/Next.js/Vite.

---

## Spacing Scale

Aplicado via padding/margin no CSS injetado e via argumentos `gap` do `st.columns`.

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Espaço interno de badges (score tag), gap entre label e valor em card |
| sm | 8px | Padding interno de `st.expander`, margem entre campo e helper text |
| md | 16px | Padding de card de match, espaço entre campos do formulário |
| lg | 24px | Separação entre seções na sidebar, margem abaixo de título de página |
| xl | 32px | Espaço entre card e card na grade de matches |
| 2xl | 48px | Separação entre bloco de cadastro e bloco de ação principal |
| 3xl | 64px | Espaço de topo da página (logo / título principal) |

Exceções: nenhuma.

---

## Typography

Implementado via CSS injetado com `st.markdown(..., unsafe_allow_html=True)`.

| Role | Size | Weight | Line Height | Uso |
|------|------|--------|-------------|-----|
| Body | 15px | 400 | 1.5 | Texto de bio, justificativa RAG, helper text de campo |
| Label | 13px | 600 | 1.4 | Rótulos de breakdown (Semântico, Interesses, Objetivo, Idade, Geografia), badges |
| Heading | 20px | 600 | 1.2 | Título de cada card de match (`Nome, Idade — Cidade`) |
| Display | 28px | 700 | 1.15 | Título de página (`st.title`) — "Cadastro de Perfil", "Matches", "Visualização" |

Fonte declarada explicitamente no bloco CSS: `font-family: "Source Sans Pro", system-ui, sans-serif;`

---

## Color

Paleta aplicada via variáveis CSS no bloco `<style>` injetado. Segue o esquema escuro padrão do Streamlit com overrides pontuais.

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#0E1117` | Background geral da página (`stApp`, `main`) |
| Secondary (30%) | `#1A1D27` | Fundo de cada card de match, fundo do formulário, sidebar |
| Accent (10%) | `#FF4B6E` | Exclusivo para: badge de score total, botão CTA primário, barra de progresso do score, nome do app no header |
| Success | `#2ECC71` | Mensagem de confirmação após popular o banco, confirmação de cadastro bem-sucedido |
| Destructive | `#E74C3C` | Mensagem de erro quando pipeline retorna < 10 matches ≥ 85 (APP-07); nunca usada para ações irreversíveis pois o app não tem deleção |

Accent reservado para: badge de score total no card, botão "Encontrar Matches" (CTA primário), barra `st.progress` de score, logotipo "CONNECT.AI" no topo.
Accent NÃO É usado em: rótulos de breakdown, texto de justificativa, campos do formulário, qualquer elemento informativo.

Contraste: accent `#FF4B6E` sobre dominant `#0E1117` atinge ≥ 4.5:1 (WCAG AA). Verificado via cálculo de luminância relativa.

---

## Estrutura de Páginas e Componentes

### Navegação

Implementada com `st.sidebar` + `st.radio` com label "Navegação" e opções:
- `"Cadastro de Perfil"` (padrão ao iniciar)
- `"Matches"`
- `"Visualização"`

### Página 1 — Cadastro de Perfil (APP-01, APP-02)

Estrutura:
1. `st.title("Cadastro de Perfil")` — Display 28px
2. Aviso ético fixo (`st.info`): "Este aplicativo usa dados sintéticos para fins de demonstração acadêmica (CP5 FIAP)." — ETH-03
3. `st.form("form_cadastro")` contendo:
   - `st.text_input("Nome completo")` — placeholder: "Ex: Ana Lima"
   - `st.number_input("Idade", min_value=18, max_value=99, step=1)`
   - `st.text_input("Cidade")` — placeholder: "Ex: São Paulo"
   - `st.selectbox("Gênero", ["feminino", "masculino", "nao_binario", "outro"])`
   - `st.selectbox("Gênero preferido", ["feminino", "masculino", "nao_binario", "outro", "todos"])`
   - `st.selectbox("Objetivo", ["namoro", "casual", "amizade"])`
   - `st.slider("Faixa etária preferida", 18, 99, (22, 35))` — retorna tupla
   - `st.text_area("Bio", max_chars=2000)` — placeholder: "Conte um pouco sobre você..."
   - `st.text_input("Interesses (separados por vírgula)")` — placeholder: "Ex: música, viagem, leitura"
   - `st.form_submit_button("Cadastrar e Ingerir Perfil")` — botão accent

4. Durante ingestão: `st.spinner("Processando perfil e gerando embedding...")` dentro de `with st.spinner(...):`
5. Sucesso: `st.success("Perfil de [Nome] cadastrado com sucesso! Vá para Matches para ver seus resultados.")` — cor success
6. Botão secundário fora do form (abaixo): `st.button("Popular banco com seed data")` — somente se banco vazio (APP-06)
   - Feedback: `st.info("Inserindo 100 perfis sintéticos no ChromaDB...")` + `st.success("Banco populado com 100 perfis. Pronto para buscar matches.")`

### Página 2 — Matches (APP-03, APP-04)

Estrutura:
1. `st.title("Matches")` — Display 28px
2. Seletor de perfil: `st.selectbox("Perfil para buscar matches", [lista de nomes cadastrados + IDs])` — fonte: `st.session_state`
3. Botão CTA: `st.button("Encontrar Matches")` — background accent `#FF4B6E`, texto branco
4. Durante busca: `st.spinner("Executando pipeline de consumo (filtros → busca vetorial → scoring)...")`

Cards de match (renderizados em grid 2 colunas via `st.columns(2)`):
Cada card é um bloco HTML injetado via `st.markdown`:
```
[Nome, Idade — Cidade]  [SCORE: XX/100]   <- Heading 20px + badge accent
[Objetivo: namoro]                         <- Label 13px
────────────────────────────────
Breakdown dos fatores:
  Semântico:   [barra]  XX pts (60%)
  Interesses:  [barra]  XX pts (20%)
  Objetivo:    [barra]  XX pts (10%)
  Idade:       [barra]  XX pts ( 5%)
  Geografia:   [barra]  XX pts ( 5%)
────────────────────────────────
[st.expander "Ver justificativa do RAG"]
  [texto da justificativa — Body 15px]
```

Barras de breakdown: `st.progress(valor / max_valor)` com cor accent para scores ≥ 85, cor padrão para os demais. Cada fator exibe valor numérico (float truncado a 1 decimal) ao lado.

Estado vazio (nenhum match): ver seção Copywriting.
Estado de erro (< 10 matches ≥ 85): ver seção Copywriting.

### Página 3 — Visualização (APP-05)

Estrutura:
1. `st.title("Visualização do Pipeline")` — Display 28px
2. `st.subheader("Grafo LangGraph")` — Heading 20px
   - `st.image("relatorio/grafo_langgraph.png", caption="Grafo LangGraph do CONNECT.AI", use_container_width=True)`
   - Fallback se PNG ausente: `st.code(open("relatorio/grafo_langgraph.mmd").read(), language="mermaid")` + `st.info("PNG não disponível. Instale graphviz para gerar a imagem.")`
3. `st.subheader("Pipeline de Ingestão")` — Heading 20px
   - `st.image("relatorio/pipeline_ingestao.png", use_container_width=True)` — ou diagrama Mermaid inline
4. `st.subheader("Pipeline de Consumo e Scoring")` — Heading 20px
   - `st.image("relatorio/pipeline_consumo.png", use_container_width=True)` — ou diagrama Mermaid inline

---

## Copywriting Contract

Todos os textos em Português do Brasil. Nenhum texto em inglês visível ao usuário.

| Element | Copy |
|---------|------|
| CTA primário (cadastro) | "Cadastrar e Ingerir Perfil" |
| CTA primário (matches) | "Encontrar Matches" |
| CTA seed data | "Popular banco com seed data" |
| Título página cadastro | "Cadastro de Perfil" |
| Título página matches | "Matches" |
| Título página visualização | "Visualização do Pipeline" |
| Aviso ético (ETH-03) | "Este aplicativo usa dados sintéticos para fins de demonstração acadêmica (CP5 FIAP)." |
| Empty state — matches (banco vazio) heading | "Banco de perfis vazio" |
| Empty state — matches (banco vazio) body | "Nenhum perfil encontrado no banco. Clique em 'Popular banco com seed data' na página Cadastro para inserir os perfis sintéticos." |
| Empty state — nenhum perfil selecionado | "Selecione um perfil acima e clique em 'Encontrar Matches' para iniciar a busca." |
| Error state — pipeline < 10 matches ≥ 85 (APP-07) | "O pipeline retornou [N] match(es) com score ≥ 85 (mínimo esperado: 10). Verifique se o banco foi populado com o seed data completo e tente novamente." |
| Error state — banco vazio ao tentar buscar | "Banco de perfis vazio. Popular com seed data antes de buscar matches." |
| Error state — falha de ingestão | "Falha ao processar o perfil: [mensagem de erro]. Verifique os campos e tente novamente." |
| Error state — arquivo de grafo ausente | "Imagem do grafo não encontrada em relatorio/. Execute o pipeline ao menos uma vez para gerar os artefatos." |
| Confirmação de cadastro | "Perfil de [Nome] cadastrado com sucesso! Vá para Matches para ver seus resultados." |
| Confirmação de seed data | "Banco populado com 100 perfis sintéticos. Pronto para buscar matches." |
| Spinner — ingestão | "Processando perfil e gerando embedding..." |
| Spinner — busca de matches | "Executando pipeline de consumo (filtros → busca vetorial → scoring)..." |
| Label de score total no card | "SCORE: [N]/100" |
| Expander de justificativa | "Ver justificativa do RAG" |
| Seção breakdown no card | "Fatores de compatibilidade:" |
| Rótulos de breakdown | "Semântico (60%)", "Interesses (20%)", "Objetivo (10%)", "Idade (5%)", "Geografia (5%)" |

Ações destrutivas: não existem nesta fase. O app não oferece deleção de perfis ou reset do banco via UI (essas operações existem apenas programaticamente via `Repositorio.resetar()`). Portanto, confirmação de ação destrutiva: não aplicável.

---

## Estado de Sessão (`st.session_state`)

| Chave | Tipo | Descrição |
|-------|------|-----------|
| `perfil_cadastrado` | `Perfil \| None` | Último perfil cadastrado via formulário |
| `matches` | `list[dict]` | Resultado do último `buscar_matches()` |
| `justificativas` | `dict[str, str]` | Justificativas RAG keyed por id do match |
| `banco_populado` | `bool` | True após seed data ter sido inserido nesta sessão |
| `perfis_disponiveis` | `list[str]` | Nomes + IDs para o seletor de perfil na página Matches |

---

## CSS Injetado (Bloco Único)

Injetado uma única vez no topo de `streamlit_app.py` via:

```python
st.markdown("""
<style>
/* === Tokens === */
:root {
    --color-bg: #0E1117;
    --color-card: #1A1D27;
    --color-accent: #FF4B6E;
    --color-success: #2ECC71;
    --color-error: #E74C3C;
    --font-body: 15px;
    --font-label: 13px;
    --font-heading: 20px;
    --font-display: 28px;
}

/* === Card de match === */
.match-card {
    background-color: var(--color-card);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    border-left: 3px solid var(--color-accent);
}

/* === Badge de score === */
.score-badge {
    background-color: var(--color-accent);
    color: white;
    font-size: var(--font-label);
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
    float: right;
}

/* === Título do card === */
.match-heading {
    font-size: var(--font-heading);
    font-weight: 600;
    line-height: 1.2;
    margin: 0 0 8px 0;
}

/* === Rótulos de breakdown === */
.factor-label {
    font-size: var(--font-label);
    font-weight: 600;
    line-height: 1.4;
    color: #AAAAAA;
}
</style>
""", unsafe_allow_html=True)
```

---

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | nenhum — não aplicável (Streamlit, não React) | não aplicável |
| Terceiros | nenhum declarado | não aplicável |

Dependências de UI desta fase: apenas `streamlit` (já em `requirements.txt`). Nenhum pacote adicional de componente Streamlit (ex: `streamlit-aggrid`, `streamlit-echarts`) é necessário. As visualizações de grafo usam `st.image` sobre PNG/Mermaid já gerados pelas fases anteriores.

---

## Interações e Estados por Componente

| Componente | Estado normal | Estado carregando | Estado erro |
|-----------|--------------|------------------|-------------|
| Botão "Cadastrar e Ingerir Perfil" | Habilitado | `st.spinner` ativo, botão desabilitado pelo form | `st.error` com mensagem de falha |
| Botão "Encontrar Matches" | Habilitado se perfil selecionado | `st.spinner` ativo | `st.warning` se < 10 matches |
| Botão "Popular banco com seed data" | Visível se `banco_populado == False` | `st.info` + `st.spinner` | `st.error` se ingestão falhar |
| Card de match | Renderizado após busca | — | — |
| `st.expander` de justificativa | Fechado por padrão | — | Texto de fallback se justificativa vazia |
| Imagem do grafo | Exibe PNG | — | `st.info` com fallback Mermaid |

---

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS

**Approval:** pending
