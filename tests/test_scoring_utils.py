"""Testes da conversao distancia coseno -> score 0-100.

Cobre o pitfall 11.1 do BRIEFING: ChromaDB retorna distancia coseno (em [0, 2]),
NAO similaridade. A funcao `distancia_cosseno_para_score` mapeia 0 -> 100 (vetores
identicos), 1 -> 50 (ortogonais), 2 -> 0 (opostos), e tolera overshoots numericos.
"""

import pytest

from swipes_burnout.scoring_utils import distancia_cosseno_para_score


def test_distancia_zero_retorna_score_maximo():
    """Vetores identicos (distancia = 0) -> score 100."""
    assert distancia_cosseno_para_score(0.0) == 100.0


def test_distancia_um_retorna_score_meio():
    """Vetores ortogonais (distancia = 1) -> score 50."""
    assert distancia_cosseno_para_score(1.0) == 50.0


def test_distancia_dois_retorna_score_zero():
    """Vetores opostos (distancia = 2) -> score 0."""
    assert distancia_cosseno_para_score(2.0) == 0.0


def test_overshoot_negativo_e_truncado_para_100():
    """Overshoot numerico negativo (ex: -0.05) deve ser truncado para 100."""
    assert distancia_cosseno_para_score(-0.05) == 100.0


def test_overshoot_positivo_e_truncado_para_0():
    """Overshoot numerico positivo (ex: 2.3) deve ser truncado para 0."""
    assert distancia_cosseno_para_score(2.3) == 0.0


def test_resultado_e_sempre_float_no_intervalo():
    """Para qualquer distancia em [0, 2], o resultado e float em [0, 100]."""
    for d in [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]:
        score = distancia_cosseno_para_score(d)
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0


def test_e_funcao_pura_estavel():
    """Funcao pura: mesmo input sempre retorna mesmo output."""
    assert distancia_cosseno_para_score(0.7) == distancia_cosseno_para_score(0.7)


def test_monotonicamente_decrescente():
    """Distancia maior -> score menor (ou igual nas saturacoes)."""
    valores = [distancia_cosseno_para_score(d) for d in [0.0, 0.5, 1.0, 1.5, 2.0]]
    for anterior, atual in zip(valores, valores[1:]):
        assert anterior >= atual
