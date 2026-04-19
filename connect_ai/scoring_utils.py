"""Utilitarios numericos compartilhados entre os pipelines do CONNECT.AI.

Concentra a conversao distancia coseno -> score 0-100, citada como
pitfall 11.1 do BRIEFING (ChromaDB retorna distancia, nao similaridade).

Manter a conversao em UM unico lugar evita o bug classico de cada nova chamada
ao ChromaDB inventar sua propria formula e gerar scores inconsistentes entre
o Casamenteiro (Fase 5), os testes e os relatorios.
"""

from __future__ import annotations


def distancia_cosseno_para_score(distancia: float) -> float:
    """Converte distancia coseno (0..2) em score de similaridade (100..0).

    Formula:
      similaridade = 1 - distancia / 2     # mapeia [0, 2] -> [1, 0]
      score        = similaridade * 100    # escala 0-100

    Equivalente a: score = (2 - distancia) / 2 * 100  =  100 - distancia * 50.

    Resultado e sempre truncado em [0.0, 100.0] para tolerar pequenos
    overshoots numericos do ChromaDB (ex: distancia ligeiramente
    negativa por arredondamento de ponto flutuante apos um produto interno
    com vetores quase identicos).

    Args:
        distancia: Distancia coseno retornada pelo ChromaDB (esperado em [0, 2]).
            Aceita `int` ou `float`; conversao interna via `float()`.

    Returns:
        Score em [0.0, 100.0] -- 100 quando distancia=0 (vetores identicos),
        50 quando distancia=1 (vetores ortogonais), 0 quando distancia=2
        (vetores opostos). Valores fora do intervalo esperado sao truncados
        sem levantar excecao.

    Examples:
        >>> distancia_cosseno_para_score(0.0)
        100.0
        >>> distancia_cosseno_para_score(1.0)
        50.0
        >>> distancia_cosseno_para_score(2.0)
        0.0
        >>> distancia_cosseno_para_score(-0.1)  # overshoot negativo
        100.0
        >>> distancia_cosseno_para_score(2.5)   # overshoot positivo
        0.0
    """
    similaridade = 1.0 - (float(distancia) / 2.0)
    score = similaridade * 100.0
    if score < 0.0:
        return 0.0
    if score > 100.0:
        return 100.0
    return score
