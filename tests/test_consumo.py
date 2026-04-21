"""Testes TDD RED para o pipeline de consumo end-to-end do CONNECT.AI.

Cobre os requisitos CONS-01 a CONS-03 (buscar_matches) e TEST-02 e TEST-03
(integracao com ChromaDB real e filtros de repositorio).

Os testes do GRUPO A (buscar_matches) falham com ImportError pois
connect_ai.agentes.buscar_matches ainda nao existe.

Os testes do GRUPO C (repositorio) podem passar parcialmente, pois
connect_ai.repositorio ja esta implementado — mas sao incluidos aqui
para documentar o contrato de TEST-03 de forma completa.

Grupos de testes:
  GRUPO A — Testes unitarios de buscar_matches (CONS-01..CONS-03, SCR-04..SCR-05)
  GRUPO B — Teste de integracao end-to-end (TEST-02 — GATE CRITICO)
  GRUPO C — Testes de repositorio com filtros (TEST-03)
"""

import pytest

from connect_ai.seed_data import PERFIL_TESTE, gerar_pool_perfis


# ── Fixtures ───────────────────────────────────────────────────────────────────


@pytest.fixture
def colecao_temp(tmp_path):
    """Cria Repositorio isolado em diretorio temporario do pytest.

    Padrao identico ao de test_repositorio.py: cada teste recebe colecao
    fresca sem poluir chroma_db/ real.
    """
    from connect_ai.repositorio import Repositorio
    return Repositorio(
        diretorio=str(tmp_path / "chroma_consumo_test"),
        nome_colecao="test_consumo",
    )


@pytest.fixture
def colecao_com_seed(tmp_path):
    """Cria Repositorio com seed data completo ingerido (para TEST-02).

    Insere os 100 perfis de gerar_pool_perfis() via ingerir_lote.
    Permite testar buscar_matches em condicoes realistas.
    """
    from connect_ai.repositorio import Repositorio
    from connect_ai.ingestao import ingerir_lote
    repo = Repositorio(
        diretorio=str(tmp_path / "chroma_seed_test"),
        nome_colecao="test_seed_completo",
    )
    perfis = gerar_pool_perfis()
    ingerir_lote(perfis, repo)
    return repo


# ── GRUPO A: Testes unitarios de buscar_matches (CONS-01..CONS-03) ─────────────


def test_buscar_matches_existe(colecao_temp):
    """buscar_matches deve ser importavel de connect_ai.agentes (CONS-01)."""
    from connect_ai.agentes import buscar_matches  # RED: ImportError
    assert callable(buscar_matches)


def test_buscar_matches_retorna_lista(colecao_temp):
    """buscar_matches deve retornar lista (CONS-01)."""
    from connect_ai.agentes import buscar_matches
    resultado = buscar_matches(PERFIL_TESTE, colecao_temp)
    assert isinstance(resultado, list)


def test_buscar_matches_estrutura_dict(colecao_com_seed):
    """Cada match deve conter as chaves de exibicao e breakdown (CONS-02)."""
    from connect_ai.agentes import buscar_matches
    matches = buscar_matches(PERFIL_TESTE, colecao_com_seed)
    chaves_esperadas = {
        "id", "score", "nome", "cidade", "idade",
        "score_semantico", "score_interesses",
        "score_objetivo", "score_idade", "score_geografia",
    }
    for m in matches:
        for chave in chaves_esperadas:
            assert chave in m, f"Chave '{chave}' ausente no match {m.get('id')}"


def test_buscar_matches_score_minimo_85(colecao_com_seed):
    """Todos os matches retornados devem ter score >= 85.0 (CONS-03)."""
    from connect_ai.agentes import buscar_matches
    matches = buscar_matches(PERFIL_TESTE, colecao_com_seed)
    for m in matches:
        assert m["score"] >= 85.0, (
            f"Match id={m['id']} tem score={m['score']:.2f} abaixo de 85"
        )


def test_buscar_matches_maximo_dez(colecao_com_seed):
    """buscar_matches deve retornar no maximo 10 matches (CONS-03)."""
    from connect_ai.agentes import buscar_matches
    matches = buscar_matches(PERFIL_TESTE, colecao_com_seed)
    assert len(matches) <= 10, f"Retornou {len(matches)} matches, esperado <= 10"


# ── GRUPO B: Gate critico de integracao end-to-end (TEST-02) ──────────────────


def test_gate_critico_dez_matches_acima_85(colecao_com_seed):
    """GATE CRITICO (TEST-02): pipeline retorna >= 10 matches com score >= 85 para PERFIL_TESTE.

    Este e o teste de integracao mais importante da Fase 5. Valida que o pipeline
    completo (filtros hard -> busca vetorial Top-30 -> scoring ponderado -> corte >= 85)
    entrega pelo menos 10 matches validos para o PERFIL_TESTE.

    Se falhar apos a implementacao da Wave 2, o procedimento e:
      1. Verificar seed data (gerar_pool_perfis) — precisa de >= 10 perfis estruturalmente
         compativeis com PERFIL_TESTE (mesmo objetivo, faixa etaria e interesses em comum).
      2. Verificar formula de scoring (pesos 60/20/10/5/5) — distancia coseno dos
         embeddings mock (hashlib.md5) pode nao gerar similaridade semantica suficiente.
    """
    from connect_ai.agentes import buscar_matches
    matches = buscar_matches(PERFIL_TESTE, colecao_com_seed)
    acima_85 = [m for m in matches if m["score"] >= 85.0]
    assert len(acima_85) >= 10, (
        f"Gate critico FALHOU: apenas {len(acima_85)} matches com score >= 85 "
        f"(esperado >= 10). Verificar seed data e formula de scoring. "
        f"Scores obtidos: {sorted([m['score'] for m in matches], reverse=True)}"
    )


# ── GRUPO A continuacao: Filtros hard (CONS-01) ────────────────────────────────


def test_filtro_hard_genero(colecao_com_seed):
    """Candidatos com genero incompativel com genero_preferido do solicitante nao aparecem.

    PERFIL_TESTE tem genero_preferido='masculino', portanto candidatos com
    genero='feminino' nao devem constar nos matches retornados.
    """
    from connect_ai.agentes import buscar_matches
    # PERFIL_TESTE tem genero_preferido="masculino"
    # logo candidatos feminino nao devem aparecer
    matches = buscar_matches(PERFIL_TESTE, colecao_com_seed)
    for m in matches:
        # metadata do candidato deve ter genero="masculino"
        assert m.get("genero", "masculino") == "masculino", (
            f"Match id={m['id']} tem genero errado: {m.get('genero')}"
        )


def test_filtro_hard_objetivo(colecao_com_seed):
    """Candidatos com objetivo diferente do solicitante nao aparecem nos matches.

    PERFIL_TESTE tem objetivo='namoro', portanto candidatos com objetivo
    diferente nao devem constar nos matches retornados.
    """
    from connect_ai.agentes import buscar_matches
    # PERFIL_TESTE tem objetivo="namoro"
    matches = buscar_matches(PERFIL_TESTE, colecao_com_seed)
    for m in matches:
        assert m.get("objetivo", "namoro") == "namoro", (
            f"Match id={m['id']} tem objetivo errado: {m.get('objetivo')}"
        )


# ── GRUPO C: Testes de repositorio com filtros (TEST-03) ──────────────────────


def test_repositorio_busca_filtrada_por_genero(colecao_temp):
    """TEST-03: where com genero filtra corretamente no ChromaDB."""
    from connect_ai.repositorio import Repositorio
    from connect_ai.ingestao import ingerir_perfil
    from connect_ai.schema import Perfil
    # Inserir 1 masculino e 1 feminino
    perfil_m = Perfil(
        id="test-masc-001",
        nome="Carlos Teste",
        idade=28,
        cidade="Sao Paulo",
        genero="masculino",
        genero_preferido="feminino",
        faixa_etaria_pref=(20, 35),
        objetivo="namoro",
        bio="Bio masculino teste consumo.",
        interesses=["musica", "esportes"],
    )
    perfil_f = Perfil(
        id="test-fem-001",
        nome="Carla Teste",
        idade=26,
        cidade="Sao Paulo",
        genero="feminino",
        genero_preferido="masculino",
        faixa_etaria_pref=(20, 35),
        objetivo="namoro",
        bio="Bio feminino teste consumo.",
        interesses=["musica", "viagem"],
    )
    ingerir_perfil(perfil_m, colecao_temp)
    ingerir_perfil(perfil_f, colecao_temp)
    assert colecao_temp.contar() == 2

    # Buscar apenas masculinos
    from connect_ai.repositorio import ResultadoBusca
    resultados = colecao_temp.buscar(
        embedding_query=[0.5] * 768,
        n_resultados=10,
        filtros={"genero": "masculino"},
    )
    ids_encontrados = {r.id for r in resultados}
    assert "test-masc-001" in ids_encontrados
    assert "test-fem-001" not in ids_encontrados


def test_repositorio_busca_top30(colecao_com_seed):
    """TEST-03: buscar com n_resultados=30 retorna ate 30 resultados do seed."""
    resultados = colecao_com_seed.buscar(
        embedding_query=[0.5] * 768,
        n_resultados=30,
    )
    assert len(resultados) <= 30
    assert len(resultados) > 0
