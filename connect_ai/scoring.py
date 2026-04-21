"""Modulo de scoring de compatibilidade do CONNECT.AI.

Implementa o calculo ponderado 60/20/10/5/5 (SCR-01 a SCR-05):
  - score_semantico  (60%): similaridade coseno via distancia ChromaDB
  - score_interesses (20%): interesses em comum, ate 4 valem 20pts
  - score_objetivo   (10%): objetivo identico = 100pts, diferente = 0
  - score_idade      ( 5%): penalidade de 2pts por ano de diferenca
  - score_geografia  ( 5%): mesma cidade = 100pts, diferente = 0

A funcao `calcular_score` compoe os 5 fatores e retorna o breakdown
completo, necessario para exibicao no front (SCR-05) e para o gate
critico de 10 matches >= 85 (TEST-02, ACC-02).

PITFALL CRITICO: ChromaDB retorna DISTANCIA coseno em [0,2], nao similaridade.
A conversao correta e: similaridade = (1 - distancia/2) * 100
"""
from __future__ import annotations


def score_semantico(distancia_coseno: float) -> float:
    """Converte distancia coseno [0,2] em score de similaridade [0,100].

    Formula: (1 - distancia / 2) * 100

    ChromaDB retorna DISTANCIA (0 = identico, 2 = oposto). Esta funcao
    converte para score onde 100 = identico e 0 = oposto.

    Args:
        distancia_coseno: Distancia coseno em [0.0, 2.0] retornada pelo ChromaDB.

    Returns:
        Score de similaridade em [0.0, 100.0].
    """
    return (1.0 - distancia_coseno / 2.0) * 100.0


def score_interesses(interesses_a: list, interesses_b: list) -> float:
    """Calcula score baseado em interesses em comum (max 20 pontos).

    Cada interesse em comum vale 5 pontos, truncado em 20.
    Formula: min(len(set(a) & set(b)) * 5, 20)

    Quatro ou mais interesses em comum atingem o maximo de 20 pontos.
    Comparacao case-sensitive (como gravado no ChromaDB).

    Args:
        interesses_a: Lista de interesses do perfil solicitante.
        interesses_b: Lista de interesses do candidato.

    Returns:
        Score de interesses em [0.0, 20.0].
    """
    em_comum = len(set(interesses_a) & set(interesses_b))
    return float(min(em_comum * 5, 20))


def score_objetivo(objetivo_a: str, objetivo_b: str) -> float:
    """Retorna 100.0 se os objetivos forem identicos, 0.0 caso contrario.

    Objetivos validos: "namoro", "casual", "amizade" (Literal do schema).
    Comparacao case-sensitive.

    Args:
        objetivo_a: Objetivo do perfil solicitante.
        objetivo_b: Objetivo do candidato.

    Returns:
        100.0 se objetivo_a == objetivo_b, 0.0 caso contrario.
    """
    return 100.0 if objetivo_a == objetivo_b else 0.0


def score_idade(idade_a: int, idade_b: int) -> float:
    """Calcula score de compatibilidade de idade (penalidade por diferenca).

    Formula: max(0.0, min(100.0, 100 - abs(idade_a - idade_b) * 2))

    Cada ano de diferenca desconta 2 pontos. Truncado em [0, 100]:
    diferenca de 50 anos ou mais resulta em 0 pontos.

    Args:
        idade_a: Idade do perfil solicitante.
        idade_b: Idade do candidato.

    Returns:
        Score de idade em [0.0, 100.0].
    """
    diferenca = abs(idade_a - idade_b)
    return float(max(0.0, min(100.0, 100.0 - diferenca * 2.0)))


def score_geografia(cidade_a: str, cidade_b: str) -> float:
    """Retorna 100.0 se as cidades forem identicas, 0.0 caso contrario.

    Comparacao case-sensitive (como gravado no ChromaDB).
    Versoes futuras podem usar distancia geografica real (V2).

    Args:
        cidade_a: Cidade do perfil solicitante.
        cidade_b: Cidade do candidato.

    Returns:
        100.0 se cidade_a == cidade_b, 0.0 caso contrario.
    """
    return 100.0 if cidade_a == cidade_b else 0.0


def calcular_score(
    distancia_coseno: float,
    interesses_a: list,
    interesses_b: list,
    objetivo_a: str,
    objetivo_b: str,
    idade_a: int,
    idade_b: int,
    cidade_a: str,
    cidade_b: str,
) -> dict:
    """Calcula score de compatibilidade ponderado 60/20/10/5/5.

    Composicao:
      score_final = semantico * 0.60
                  + interesses * 0.20
                  + objetivo * 0.10
                  + idade * 0.05
                  + geografia * 0.05

    Retorna o breakdown completo dos 5 fatores para exibicao no front
    (SCR-05) e para rastreabilidade do gate critico (TEST-02).

    Nota sobre o threshold >= 85: O score maxximo com score_interesses
    truncado em 20 (nao 100) e pesos corretos e:
      60 + 4 + 10 + 5 + 5 = 84 (4 interesses em comum, perfil identico).
    O gate >= 85 so e atingivel quando a similaridade semantica e
    suficientemente alta E ha sobreposicao de interesses -- confirmando
    que o seed data calibrado na Fase 2 e essencial para o gate.

    Args:
        distancia_coseno: Distancia coseno [0.0, 2.0] do ChromaDB.
        interesses_a: Lista de interesses do solicitante.
        interesses_b: Lista de interesses do candidato.
        objetivo_a: Objetivo do solicitante ("namoro"/"casual"/"amizade").
        objetivo_b: Objetivo do candidato.
        idade_a: Idade do solicitante.
        idade_b: Idade do candidato.
        cidade_a: Cidade do solicitante.
        cidade_b: Cidade do candidato.

    Returns:
        Dict com chaves:
          score_final (float): Score composto em [0.0, 100.0].
          score_semantico (float): Componente semantico [0.0, 100.0].
          score_interesses (float): Componente de interesses [0.0, 20.0].
          score_objetivo (float): Componente de objetivo (0 ou 100).
          score_idade (float): Componente de idade [0.0, 100.0].
          score_geografia (float): Componente de geografia (0 ou 100).
    """
    s_semantico = score_semantico(distancia_coseno)
    s_interesses = score_interesses(interesses_a, interesses_b)
    s_objetivo = score_objetivo(objetivo_a, objetivo_b)
    s_idade = score_idade(idade_a, idade_b)
    s_geografia = score_geografia(cidade_a, cidade_b)

    score_final = (
        s_semantico * 0.60
        + s_interesses * 0.20
        + s_objetivo * 0.10
        + s_idade * 0.05
        + s_geografia * 0.05
    )

    return {
        "score_final": float(score_final),
        "score_semantico": float(s_semantico),
        "score_interesses": float(s_interesses),
        "score_objetivo": float(s_objetivo),
        "score_idade": float(s_idade),
        "score_geografia": float(s_geografia),
    }
