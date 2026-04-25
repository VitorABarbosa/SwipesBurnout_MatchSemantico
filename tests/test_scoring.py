"""Testes TDD RED para swipes_burnout/scoring.py.

Cobre os requisitos SCR-01 a SCR-05 (cinco fatores de scoring) e TEST-01
(contrato verificavel da composicao ponderada 60/20/10/5/5).

Todos os testes DEVEM FALHAR antes da implementacao de swipes_burnout/scoring.py.
O modulo swipes_burnout.scoring ainda nao existe — cada import dentro das funcoes
provocara ImportError individual, tornando cada teste independentemente RED.

Fatores cobertos:
  SCR-01 — score_semantico: distancia coseno [0,2] -> score [0,100]
  SCR-02 — score_interesses: interseccao de listas -> score [0,20]
  SCR-03 — score_objetivo: igualdade de objetivos -> 100 ou 0
  SCR-04 — score_idade: diferenca de idade penalizada -> score [0,100]
  SCR-05 — score_geografia: igualdade de cidade -> 100 ou 0
  TEST-01 — calcular_score: composicao ponderada 60/20/10/5/5
"""

import pytest


# ── FATOR 1: score_semantico (SCR-01) ─────────────────────────────────────────


def test_score_semantico_distancia_zero():
    """Distancia coseno 0.0 (perfil identico) deve retornar score 100.0."""
    from swipes_burnout.scoring import score_semantico
    assert score_semantico(0.0) == pytest.approx(100.0)


def test_score_semantico_distancia_um():
    """Distancia coseno 1.0 (perfil ortogonal) deve retornar score 50.0."""
    from swipes_burnout.scoring import score_semantico
    assert score_semantico(1.0) == pytest.approx(50.0)


def test_score_semantico_distancia_dois():
    """Distancia coseno 2.0 (perfil oposto) deve retornar score 0.0."""
    from swipes_burnout.scoring import score_semantico
    assert score_semantico(2.0) == pytest.approx(0.0)


def test_score_semantico_distancia_meio():
    """Distancia coseno 0.5 deve retornar score 75.0."""
    from swipes_burnout.scoring import score_semantico
    assert score_semantico(0.5) == pytest.approx(75.0)


# ── FATOR 2: score_interesses (SCR-02) ────────────────────────────────────────


def test_score_interesses_zero_comum():
    """Sem interesses em comum deve retornar 0.0."""
    from swipes_burnout.scoring import score_interesses
    assert score_interesses(["musica"], ["viagem"]) == pytest.approx(0.0)


def test_score_interesses_um_comum():
    """1 interesse em comum deve retornar 5.0."""
    from swipes_burnout.scoring import score_interesses
    assert score_interesses(["musica", "viagem"], ["musica", "leitura"]) == pytest.approx(5.0)


def test_score_interesses_quatro_comum():
    """4 interesses em comum deve retornar 20.0 (maximo)."""
    from swipes_burnout.scoring import score_interesses
    a = ["musica", "viagem", "leitura", "cinema"]
    b = ["musica", "viagem", "leitura", "cinema", "esportes"]
    assert score_interesses(a, b) == pytest.approx(20.0)


def test_score_interesses_truncado_em_vinte():
    """5 interesses em comum: min(5*5, 20) = 20, nao 25 (truncado)."""
    from swipes_burnout.scoring import score_interesses
    # 5 em comum -> min(5*5, 20) = 20, nao 25
    a = ["a", "b", "c", "d", "e"]
    b = ["a", "b", "c", "d", "e", "f"]
    assert score_interesses(a, b) == pytest.approx(20.0)


# ── FATOR 3: score_objetivo (SCR-03) ──────────────────────────────────────────


def test_score_objetivo_iguais():
    """Mesmo objetivo deve retornar 100.0."""
    from swipes_burnout.scoring import score_objetivo
    assert score_objetivo("namoro", "namoro") == pytest.approx(100.0)


def test_score_objetivo_diferentes():
    """Objetivos diferentes devem retornar 0.0."""
    from swipes_burnout.scoring import score_objetivo
    assert score_objetivo("namoro", "amizade") == pytest.approx(0.0)


# ── FATOR 4: score_idade (SCR-04) ─────────────────────────────────────────────


def test_score_idade_iguais():
    """Mesma idade deve retornar 100.0."""
    from swipes_burnout.scoring import score_idade
    assert score_idade(27, 27) == pytest.approx(100.0)


def test_score_idade_cinco_anos():
    """Diferenca de 5 anos: 100 - 5*2 = 90.0."""
    from swipes_burnout.scoring import score_idade
    assert score_idade(27, 32) == pytest.approx(90.0)


def test_score_idade_truncado_zero():
    """Diferenca de 50 anos: 100 - 50*2 = 0, nao negativo (truncado)."""
    from swipes_burnout.scoring import score_idade
    # 100 - 50*2 = 0, nao negativo
    assert score_idade(20, 70) == pytest.approx(0.0)


def test_score_idade_quarenta_e_nove_anos():
    """Diferenca de 49 anos: 100 - 49*2 = 2.0."""
    from swipes_burnout.scoring import score_idade
    # 100 - 49*2 = 2
    assert score_idade(20, 69) == pytest.approx(2.0)


# ── FATOR 5: score_geografia (SCR-05) ─────────────────────────────────────────


def test_score_geografia_mesma_cidade():
    """Mesma cidade deve retornar 100.0."""
    from swipes_burnout.scoring import score_geografia
    assert score_geografia("Sao Paulo", "Sao Paulo") == pytest.approx(100.0)


def test_score_geografia_cidades_diferentes():
    """Cidades diferentes devem retornar 0.0."""
    from swipes_burnout.scoring import score_geografia
    assert score_geografia("Sao Paulo", "Rio de Janeiro") == pytest.approx(0.0)


# ── COMPOSICAO PONDERADA: calcular_score (TEST-01) ────────────────────────────


def test_calcular_score_retorna_dict_com_chaves():
    """calcular_score deve retornar dict com as 6 chaves esperadas."""
    from swipes_burnout.scoring import calcular_score
    resultado = calcular_score(
        distancia_coseno=0.0,
        interesses_a=["musica"],
        interesses_b=["musica"],
        objetivo_a="namoro",
        objetivo_b="namoro",
        idade_a=27,
        idade_b=27,
        cidade_a="Sao Paulo",
        cidade_b="Sao Paulo",
    )
    assert isinstance(resultado, dict)
    for chave in ["score_final", "score_semantico", "score_interesses",
                  "score_objetivo", "score_idade", "score_geografia"]:
        assert chave in resultado, f"Chave '{chave}' ausente no resultado"


def test_calcular_score_composicao_pesos():
    """Caso controlado: semantico=100, interesses=20 (4 em comum), objetivo=100, idade=100, geo=100.

    score_final = 100*0.60 + 20*1.0 + 100*0.10 + 100*0.05 + 100*0.05
               = 60 + 20 + 10 + 5 + 5 = 100.0
    """
    from swipes_burnout.scoring import calcular_score
    # Caso controlado: semantico=100, interesses=20 (4 em comum), objetivo=100, idade=100, geo=100
    # score_final = 100*0.60 + 20*1.0 + 100*0.10 + 100*0.05 + 100*0.05
    #             = 60 + 20 + 10 + 5 + 5 = 100.0
    resultado = calcular_score(
        distancia_coseno=0.0,
        interesses_a=["a", "b", "c", "d"],
        interesses_b=["a", "b", "c", "d"],
        objetivo_a="namoro",
        objetivo_b="namoro",
        idade_a=27,
        idade_b=27,
        cidade_a="SP",
        cidade_b="SP",
    )
    assert resultado["score_final"] == pytest.approx(100.0)
    assert resultado["score_semantico"] == pytest.approx(100.0)
    assert resultado["score_interesses"] == pytest.approx(20.0)


def test_calcular_score_gate_85_com_cinco_interesses():
    """5+ interesses em comum: interesses truncado em 20, score_final = 100.0.

    Com multiplicador correto (1.0) para score_interesses em [0,20]:
    score_final = 60 + 20 + 10 + 5 + 5 = 100.0 (teto maximo).
    O gate >= 85 e viavel em contextos reais com boa similaridade semantica.
    """
    from swipes_burnout.scoring import calcular_score
    # 5+ interesses em comum: interesses=20, semantico=100, objetivo=100, idade=100, geo=100
    # score_final = 60 + 20 + 10 + 5 + 5 = 100.0
    resultado = calcular_score(
        distancia_coseno=0.0,
        interesses_a=["a", "b", "c", "d", "e"],
        interesses_b=["a", "b", "c", "d", "e"],
        objetivo_a="namoro",
        objetivo_b="namoro",
        idade_a=27,
        idade_b=27,
        cidade_a="SP",
        cidade_b="SP",
    )
    # interesses truncado em 20, semantico=100 -> score_final=100
    assert resultado["score_final"] == pytest.approx(100.0)


def test_calcular_score_final_nao_negativo():
    """score_final nao pode ser negativo mesmo com pior caso (dist=2, sem comum, obj diff)."""
    from swipes_burnout.scoring import calcular_score
    resultado = calcular_score(
        distancia_coseno=2.0,
        interesses_a=[],
        interesses_b=["a"],
        objetivo_a="namoro",
        objetivo_b="amizade",
        idade_a=18,
        idade_b=99,
        cidade_a="A",
        cidade_b="B",
    )
    assert resultado["score_final"] >= 0.0
