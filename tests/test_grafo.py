"""Testes RED para swipes_burnout/grafo.py.

Cobre compilacao do grafo LangGraph (AGT-05) e visualizacao (AGT-06).

Todos os testes DEVEM FALHAR antes da implementacao de swipes_burnout/grafo.py.
"""
from __future__ import annotations

import os
import pytest

from swipes_burnout.seed_data import PERFIL_TESTE


# ── Grafo LangGraph (AGT-05) ──────────────────────────────────────────────────


def test_grafo_compila() -> None:
    """pipeline_consumo deve ser um grafo LangGraph compilado (tem .invoke)."""
    from swipes_burnout.grafo import pipeline_consumo

    assert hasattr(pipeline_consumo, "invoke"), (
        "pipeline_consumo deve ser um CompiledStateGraph com metodo .invoke"
    )


def test_grafo_tem_tres_nos() -> None:
    """Grafo deve ter exatamente os nos 'perfilador', 'casamenteiro', 'rag_justificador'."""
    from swipes_burnout.grafo import pipeline_consumo

    # LangGraph expoe nos via get_graph()
    nos = set(pipeline_consumo.get_graph().nodes.keys())
    assert "perfilador" in nos, f"No 'perfilador' ausente. Nos encontrados: {nos}"
    assert "casamenteiro" in nos, f"No 'casamenteiro' ausente. Nos encontrados: {nos}"
    assert "rag_justificador" in nos, f"No 'rag_justificador' ausente. Nos encontrados: {nos}"


def test_grafo_invoke_com_perfil_teste() -> None:
    """Invocar o grafo com PERFIL_TESTE deve retornar state com matches preenchido."""
    from swipes_burnout.grafo import pipeline_consumo

    state_entrada = {
        "perfil": PERFIL_TESTE,
        "candidatos": [],
        "matches": [],
        "justificativas": {},
        "erro": None,
    }
    resultado = pipeline_consumo.invoke(state_entrada)

    assert "matches" in resultado, "Campo 'matches' ausente no resultado"
    assert isinstance(resultado["matches"], list)
    assert len(resultado["matches"]) > 0, "pipeline deve retornar pelo menos 1 match"
    assert "justificativas" in resultado
    assert isinstance(resultado["justificativas"], dict)


# ── Visualizacao (AGT-06) ─────────────────────────────────────────────────────


def test_mermaid_exportado(tmp_path: "pytest.fixture") -> None:
    """salvar_visualizacao_grafo deve gerar arquivo .mmd com texto Mermaid."""
    from swipes_burnout.grafo import salvar_visualizacao_grafo

    caminho_mmd = str(tmp_path / "grafo_pipeline.mmd")
    # A funcao salva PNG no caminho informado e MMD substituindo extensao
    # Testar apenas o MMD (nao precisa de graphviz instalado)
    salvar_visualizacao_grafo(caminho=str(tmp_path / "grafo_pipeline.png"))

    assert os.path.exists(caminho_mmd), (
        f"Arquivo Mermaid nao foi gerado em {caminho_mmd}"
    )
    with open(caminho_mmd, encoding="utf-8") as f:
        conteudo = f.read()
    assert "perfilador" in conteudo, "Texto Mermaid deve conter no 'perfilador'"
    assert "casamenteiro" in conteudo, "Texto Mermaid deve conter no 'casamenteiro'"
    assert "rag_justificador" in conteudo, "Texto Mermaid deve conter no 'rag_justificador'"


def test_visualizacao_cria_diretorio(tmp_path: "pytest.fixture") -> None:
    """salvar_visualizacao_grafo deve criar o diretorio de destino se nao existir."""
    from swipes_burnout.grafo import salvar_visualizacao_grafo

    subdir = tmp_path / "novo_relatorio"
    assert not subdir.exists()
    salvar_visualizacao_grafo(caminho=str(subdir / "grafo.png"))
    assert subdir.exists(), "Diretorio deve ser criado automaticamente"
