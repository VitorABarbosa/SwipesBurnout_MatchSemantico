"""Grafo LangGraph do pipeline de consumo do CONNECT.AI.

Monta os tres agentes como nos distintos de um StateGraph:
  - perfilador    -> agente_perfilador   (AGT-02)
  - casamenteiro  -> agente_casamenteiro (AGT-03)
  - rag_justificador -> agente_rag_justificador (AGT-04)

Fluxo: START -> perfilador -> casamenteiro -> rag_justificador -> END

`pipeline_consumo` e o grafo compilado, pronto para .invoke() e para
ser importado pelo front Streamlit (Fase 6) e pelo notebook (Fase 7).

`salvar_visualizacao_grafo` exporta o diagrama em Mermaid (.mmd) e,
quando as dependencias grafico estao presentes, tambem em PNG.
"""
from __future__ import annotations

import os
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from connect_ai.agentes import (
    AgentState,
    agente_casamenteiro,
    agente_perfilador,
    agente_rag_justificador,
)

# ── Construcao do grafo ───────────────────────────────────────────────────────

_grafo = StateGraph(AgentState)

_grafo.add_node("perfilador", agente_perfilador)
_grafo.add_node("casamenteiro", agente_casamenteiro)
_grafo.add_node("rag_justificador", agente_rag_justificador)

_grafo.add_edge(START, "perfilador")
_grafo.add_edge("perfilador", "casamenteiro")
_grafo.add_edge("casamenteiro", "rag_justificador")
_grafo.add_edge("rag_justificador", END)

# Grafo compilado — importado diretamente pelo front e notebook
pipeline_consumo = _grafo.compile()


# ── Visualizacao ─────────────────────────────────────────────────────────────


def salvar_visualizacao_grafo(caminho: str = "relatorio/grafo_pipeline.png") -> None:
    """Exporta o diagrama do grafo em Mermaid (.mmd) e, se possivel, em PNG.

    O arquivo .mmd e sempre gerado (nao depende de graphviz/pillow).
    O arquivo .png e gerado apenas se as dependencias de renderizacao
    estiverem disponiveis; caso contrario, uma aviso e impresso e a
    funcao retorna normalmente sem lancar excecao.

    O diretorio de destino e criado automaticamente se nao existir.

    Args:
        caminho: Caminho do arquivo PNG de saida.
            Default: "relatorio/grafo_pipeline.png".
            O arquivo .mmd e salvo no mesmo diretorio com extensao trocada.
    """
    caminho_path = Path(caminho)
    caminho_path.parent.mkdir(parents=True, exist_ok=True)

    # Exportar texto Mermaid (sempre disponivel, sem dependencias extras)
    caminho_mmd = caminho_path.with_suffix(".mmd")
    texto_mermaid = pipeline_consumo.get_graph().draw_mermaid()
    caminho_mmd.write_text(texto_mermaid, encoding="utf-8")
    print(f"[grafo] Diagrama Mermaid salvo em: {caminho_mmd}")

    # Tentar exportar PNG (requer graphviz ou pillow instalados)
    try:
        png_bytes = pipeline_consumo.get_graph().draw_mermaid_png()
        caminho_path.write_bytes(png_bytes)
        print(f"[grafo] Diagrama PNG salvo em: {caminho_path}")
    except Exception as excecao:
        print(
            f"[grafo] Aviso: nao foi possivel gerar o PNG ({type(excecao).__name__}: {excecao}). "
            f"O arquivo .mmd foi salvo com sucesso."
        )
