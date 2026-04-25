"""Aplicação principal do CONNECT.AI — interface Streamlit.

Fase 6 — Front Streamlit (CP5 FIAP).
Estrutura:
  - CSS injetado (design system da UI-SPEC)
  - Navegação sidebar com 3 páginas
  - Página 1: Cadastro de Perfil (formulário + ingestão + seed data)
  - Página 2: Matches (stub — implementação no plano 02)
  - Página 3: Visualização do Pipeline (stub — implementação no plano 02)
"""

from __future__ import annotations

import os

import streamlit as st
from swipes_burnout.repositorio import Repositorio
from swipes_burnout.schema import Perfil, gerar_uuid
from swipes_burnout.ingestao import ingerir_perfil, ingerir_lote
from swipes_burnout.seed_data import gerar_pool_perfis
from swipes_burnout.agentes import buscar_matches, agente_rag_justificador, AgentState
from swipes_burnout.grafo import salvar_visualizacao_grafo

# ── Page config (deve ser a primeira chamada st do arquivo) ──────────────────
st.set_page_config(
    page_title="CONNECT.AI",
    page_icon="💞",
    layout="wide",
)

# ── CSS injetado (bloco único — design system UI-SPEC) ───────────────────────
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

# ── Session state — inicialização de todas as chaves necessárias ─────────────
if "repositorio" not in st.session_state:
    st.session_state["repositorio"] = Repositorio()
if "perfil_cadastrado" not in st.session_state:
    st.session_state["perfil_cadastrado"] = None
if "matches" not in st.session_state:
    st.session_state["matches"] = []
if "justificativas" not in st.session_state:
    st.session_state["justificativas"] = {}
if "banco_populado" not in st.session_state:
    st.session_state["banco_populado"] = False
if "perfis_disponiveis" not in st.session_state:
    st.session_state["perfis_disponiveis"] = []
# Dict label → Perfil para lookup rápido na página Matches
if "perfis_por_label" not in st.session_state:
    st.session_state["perfis_por_label"] = {}

# ── Carregar perfis existentes do ChromaDB ao iniciar (resolve reload da página)
if not st.session_state["perfis_disponiveis"]:
    colecao_init = st.session_state["repositorio"]
    for entrada in colecao_init.listar_todos():
        meta = entrada["metadata"]
        pid = entrada["id"]
        nome = meta.get("nome", "?")
        label = f"{nome} ({pid[:8]})"
        if label not in st.session_state["perfis_por_label"]:
            st.session_state["perfis_disponiveis"].append(label)
            st.session_state["perfis_por_label"][label] = Perfil(
                id=pid,
                nome=nome,
                idade=int(meta.get("idade", 18)),
                cidade=str(meta.get("cidade", "")),
                genero=meta.get("genero", "outro"),
                genero_preferido=meta.get("genero_preferido", "todos"),
                faixa_etaria_pref=(
                    int(meta.get("faixa_etaria_min", 18)),
                    int(meta.get("faixa_etaria_max", 99)),
                ),
                objetivo=meta.get("objetivo", "namoro"),
                bio=meta.get("bio", "") or "Perfil sintético.",
                interesses=[
                    i.strip()
                    for i in meta.get("interesses_csv", "").split(",")
                    if i.strip()
                ],
            )

# ── Sidebar — navegação principal ────────────────────────────────────────────
with st.sidebar:
    st.markdown("## CONNECT.AI")
    pagina = st.radio(
        "Navegação",
        ["Cadastro de Perfil", "Matches", "Visualização"],
    )


# ── Páginas ──────────────────────────────────────────────────────────────────

def _pagina_cadastro() -> None:
    """Página 1 — Cadastro de Perfil com formulário completo e seed data."""
    st.title("Cadastro de Perfil")
    st.info("Este aplicativo usa dados sintéticos para fins de demonstração acadêmica (CP5 FIAP).")

    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo", placeholder="Ex: Ana Lima")
        idade = st.number_input("Idade", min_value=18, max_value=99, step=1, value=25)
        cidade = st.text_input("Cidade", placeholder="Ex: São Paulo")
        genero = st.selectbox("Gênero", ["feminino", "masculino", "nao_binario", "outro"])
        genero_preferido = st.selectbox(
            "Gênero preferido",
            ["feminino", "masculino", "nao_binario", "outro", "todos"],
        )
        objetivo = st.selectbox("Objetivo", ["namoro", "casual", "amizade"])
        faixa_etaria = st.slider("Faixa etária preferida", 18, 99, (22, 35))
        bio = st.text_area("Bio", max_chars=2000, placeholder="Conte um pouco sobre você...")
        interesses_str = st.text_input(
            "Interesses (separados por vírgula)",
            placeholder="Ex: música, viagem, leitura",
        )
        submitted = st.form_submit_button("Cadastrar e Ingerir Perfil")

    if submitted:
        # Validação dos campos obrigatórios
        if not nome.strip() or not cidade.strip() or not bio.strip():
            st.error("Preencha todos os campos obrigatórios.")
            return

        # Parsear lista de interesses
        interesses = [i.strip() for i in interesses_str.split(",") if i.strip()]

        # Construir instância do Perfil
        perfil = Perfil(
            id=gerar_uuid(),
            nome=nome,
            idade=int(idade),
            cidade=cidade,
            genero=genero,
            genero_preferido=genero_preferido,
            faixa_etaria_pref=(int(faixa_etaria[0]), int(faixa_etaria[1])),
            objetivo=objetivo,
            bio=bio,
            interesses=interesses,
        )

        with st.spinner("Processando perfil e gerando embedding..."):
            try:
                resultado = ingerir_perfil(perfil, st.session_state["repositorio"])
                if resultado.get("sucesso"):
                    st.success(
                        f"Perfil de {nome} cadastrado com sucesso! "
                        "Vá para Matches para ver seus resultados."
                    )
                    st.session_state["perfil_cadastrado"] = perfil
                    label = f"{nome} ({perfil.id[:8]})"
                    if label not in st.session_state["perfis_por_label"]:
                        st.session_state["perfis_disponiveis"].append(label)
                        st.session_state["perfis_por_label"][label] = perfil
                else:
                    mensagem = resultado.get("erro") or "erro desconhecido"
                    st.error(
                        f"Falha ao processar o perfil: {mensagem}. "
                        "Verifique os campos e tente novamente."
                    )
            except Exception as e:
                st.error(
                    f"Falha ao processar o perfil: {e}. "
                    "Verifique os campos e tente novamente."
                )

    # ── Seed data (fora do form) ─────────────────────────────────────────────
    colecao = st.session_state["repositorio"]
    total = colecao.contar()
    st.metric("Perfis no banco", total)

    if not st.session_state["banco_populado"] or total == 0:
        if st.button("Popular banco com seed data"):
            st.info("Inserindo perfis sintéticos no ChromaDB...")
            with st.spinner("Aguarde..."):
                try:
                    perfis = gerar_pool_perfis()
                    ingerir_lote(perfis, colecao)
                    st.session_state["banco_populado"] = True
                    st.success(
                        f"Banco populado com {len(perfis)} perfis sintéticos. "
                        "Pronto para buscar matches."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao popular banco: {e}")


def _renderizar_card(match: dict, justificativas: dict) -> None:
    """Renderiza um card de match com score badge, breakdown e justificativa RAG."""
    nome = match["nome"]
    idade = match["idade"]
    cidade = match["cidade"]
    score = match["score"]
    objetivo = match.get("objetivo", "")
    mid = match["id"]

    # Card container com HTML + CSS da UI-SPEC
    st.markdown(
        f"""<div class="match-card">
        <span class="score-badge">SCORE: {score:.0f}/100</span>
        <div class="match-heading">{nome}, {idade} — {cidade}</div>
        <div class="factor-label">Objetivo: {objetivo}</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # Breakdown dos fatores com st.progress
    st.markdown("**Fatores de compatibilidade:**")

    fatores = [
        ("Semântico (60%)",    match.get("score_semantico", 0),    60.0),
        ("Interesses (20%)",   match.get("score_interesses", 0),   20.0),
        ("Objetivo (10%)",     match.get("score_objetivo", 0),     10.0),
        ("Idade (5%)",         match.get("score_idade", 0),        5.0),
        ("Geografia (5%)",     match.get("score_geografia", 0),    5.0),
    ]

    for rotulo, valor, maximo in fatores:
        proporcao = min(valor / maximo, 1.0) if maximo > 0 else 0.0
        st.markdown(f'<span class="factor-label">{rotulo}</span>', unsafe_allow_html=True)
        col_bar, col_val = st.columns([4, 1])
        with col_bar:
            st.progress(proporcao)
        with col_val:
            st.markdown(f"**{valor:.1f}**")

    # Justificativa RAG em expander
    justificativa = justificativas.get(mid, "")
    with st.expander("Ver justificativa do RAG"):
        if justificativa:
            st.markdown(justificativa)
        else:
            st.markdown("_Justificativa não disponível._")

    st.markdown("---")


def _pagina_matches() -> None:
    """Página 2 — Matches com pipeline de consumo, cards e tratamento de erro."""
    st.title("Matches")

    colecao = st.session_state["repositorio"]

    # Verificar se banco tem perfis
    if colecao.contar() == 0:
        st.warning("Banco de perfis vazio. Popular com seed data antes de buscar matches.")
        return

    # Seletor de perfil
    opcoes = st.session_state.get("perfis_disponiveis", [])
    if not opcoes:
        st.info("Selecione um perfil acima e clique em 'Encontrar Matches' para iniciar a busca.")
        st.info("Nenhum perfil cadastrado ainda. Vá para Cadastro de Perfil e cadastre um perfil primeiro.")
        return

    perfil_selecionado_label = st.selectbox("Perfil para buscar matches", opcoes)

    if st.button("Encontrar Matches"):
        # Buscar o perfil pelo label selecionado no dropdown
        perfil = st.session_state["perfis_por_label"].get(perfil_selecionado_label)
        if perfil is None:
            st.error("Perfil não encontrado. Recarregue a página e tente novamente.")
            return

        with st.spinner("Executando pipeline de consumo (filtros → busca vetorial → scoring)..."):
            try:
                matches = buscar_matches(perfil, colecao)
            except Exception as e:
                st.error(f"Erro ao executar pipeline: {e}")
                return

        # Gerar justificativas via agente_rag_justificador
        if matches:
            state_rag: AgentState = {
                "perfil": perfil,
                "candidatos": [],
                "matches": matches,
                "justificativas": {},
                "erro": None,
            }
            try:
                state_resultado = agente_rag_justificador(state_rag)
                justificativas = state_resultado.get("justificativas", {})
            except Exception:
                justificativas = {}
        else:
            justificativas = {}

        st.session_state["matches"] = matches
        st.session_state["justificativas"] = justificativas

    # Renderizar matches do session_state
    matches = st.session_state.get("matches", [])
    justificativas = st.session_state.get("justificativas", {})

    if not matches:
        return

    # Verificar gate >= 10 matches (APP-07)
    if len(matches) < 10:
        n = len(matches)
        st.warning(
            f"O pipeline retornou {n} match(es) com score ≥ 85 "
            f"(mínimo esperado: 10). Verifique se o banco foi populado "
            f"com o seed data completo e tente novamente."
        )

    st.markdown(f"### {len(matches)} match(es) encontrado(s)")

    # Grid 2 colunas
    cols = st.columns(2)
    for i, match in enumerate(matches):
        col = cols[i % 2]
        with col:
            _renderizar_card(match, justificativas)


def _pagina_visualizacao() -> None:
    """Página 3 — Visualização do Pipeline com grafo e diagramas."""
    st.title("Visualização do Pipeline")

    # ── Seção 1: Grafo LangGraph ─────────────────────────────────────────
    st.subheader("Grafo LangGraph")

    png_grafo = "relatorio/grafo_pipeline.png"
    mmd_grafo = "relatorio/grafo_pipeline.mmd"

    if os.path.exists(png_grafo):
        st.image(png_grafo, caption="Grafo LangGraph do CONNECT.AI", use_container_width=True)
    elif os.path.exists(mmd_grafo):
        st.code(open(mmd_grafo).read(), language="mermaid")
        st.info("PNG não disponível. Instale graphviz para gerar a imagem.")
    else:
        st.info("Imagem do grafo não encontrada em relatorio/. Execute o pipeline ao menos uma vez para gerar os artefatos.")
        if st.button("Gerar artefatos do grafo"):
            with st.spinner("Gerando visualização do grafo..."):
                try:
                    salvar_visualizacao_grafo("relatorio/grafo_pipeline.png")
                    st.success("Artefatos gerados. Recarregue a página.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao gerar grafo: {e}")

    # ── Seção 2: Pipeline de Ingestão ───────────────────────────────────
    st.subheader("Pipeline de Ingestão")

    png_ingestao = "relatorio/pipeline_ingestao.png"
    mmd_ingestao = "relatorio/pipeline_ingestao.mmd"

    if os.path.exists(png_ingestao):
        st.image(png_ingestao, use_container_width=True)
    elif os.path.exists(mmd_ingestao):
        st.code(open(mmd_ingestao).read(), language="mermaid")
        st.info("PNG não disponível. Instale graphviz para gerar a imagem.")
    else:
        # Diagrama Mermaid inline do pipeline de ingestão
        mermaid_ingestao = """graph TD
    A[Perfil submetido] --> B[Validação Pydantic]
    B --> C[Agente Perfilador]
    C --> D[Gerar embedding text-embedding-004]
    D --> E[ChromaDB upsert]
    E --> F[Confirmação PT-BR]"""
        st.code(mermaid_ingestao, language="mermaid")
        st.info("Diagrama inline do pipeline de ingestão (PNG em relatorio/ ausente).")

    # ── Seção 3: Pipeline de Consumo e Scoring ───────────────────────────
    st.subheader("Pipeline de Consumo e Scoring")

    png_consumo = "relatorio/pipeline_consumo.png"
    mmd_consumo = "relatorio/pipeline_consumo.mmd"

    if os.path.exists(png_consumo):
        st.image(png_consumo, use_container_width=True)
    elif os.path.exists(mmd_consumo):
        st.code(open(mmd_consumo).read(), language="mermaid")
        st.info("PNG não disponível. Instale graphviz para gerar a imagem.")
    else:
        mermaid_consumo = """graph TD
    A[Perfil solicitante] --> B[Filtros hard: objetivo + gênero]
    B --> C[Busca vetorial Top-30 ChromaDB]
    C --> D[Scoring ponderado 60/20/10/5/5]
    D --> E{score ≥ 85?}
    E -->|Sim| F[Top-10 matches]
    E -->|Não| G[Descartado]
    F --> H[Agente RAG Justificador]
    H --> I[10 matches com justificativa]"""
        st.code(mermaid_consumo, language="mermaid")
        st.info("Diagrama inline do pipeline de consumo (PNG em relatorio/ ausente).")


# ── Roteamento ───────────────────────────────────────────────────────────────
if pagina == "Cadastro de Perfil":
    _pagina_cadastro()
elif pagina == "Matches":
    _pagina_matches()
else:
    _pagina_visualizacao()
