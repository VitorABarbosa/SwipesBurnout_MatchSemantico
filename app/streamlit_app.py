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

import streamlit as st
from connect_ai.repositorio import Repositorio
from connect_ai.schema import Perfil, gerar_uuid
from connect_ai.ingestao import ingerir_perfil, ingerir_lote
from connect_ai.seed_data import gerar_pool_perfis

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
                    st.session_state["perfis_disponiveis"].append(
                        f"{nome} ({perfil.id[:8]})"
                    )
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


def _pagina_matches() -> None:
    """Página 2 — Matches (stub para o plano 02)."""
    st.title("Matches")
    st.info("Página de matches — implementação no plano 02.")


def _pagina_visualizacao() -> None:
    """Página 3 — Visualização do Pipeline (stub para o plano 02)."""
    st.title("Visualização do Pipeline")
    st.info("Página de visualização — implementação no plano 02.")


# ── Roteamento ───────────────────────────────────────────────────────────────
if pagina == "Cadastro de Perfil":
    _pagina_cadastro()
elif pagina == "Matches":
    _pagina_matches()
else:
    _pagina_visualizacao()
