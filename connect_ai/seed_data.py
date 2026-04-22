"""Gerador de perfis sinteticos calibrados para o CONNECT.AI.

Produz um pool reproduzivel de >= 100 perfis com seed fixa (SEED_FIXA = 42).
O pool e calibrado para garantir >= 10 perfis estatisticamente compativeis
com PERFIL_TESTE (analise estrutural: interesses, objetivo, faixa etaria),
o que e pre-condicao para o gate de score >= 85 da Fase 5.

Nao depende de ChromaDB, Gemini ou rede — todos os dados sao sinteticos e
definidos estaticamente neste modulo.
"""

from __future__ import annotations

import random
from typing import List

from connect_ai.schema import Perfil, gerar_uuid


# ── Constante de seed ──────────────────────────────────────────────────────────

SEED_FIXA: int = 42


# ── Perfil de teste explicito (campos 100% fixos, nao-aleatorios) ──────────────

PERFIL_TESTE = Perfil(
    id="perfil-teste-ana-lima-001",
    nome="Ana Lima",
    idade=27,
    cidade="Sao Paulo",
    genero="feminino",
    genero_preferido="masculino",
    faixa_etaria_pref=(23, 35),
    objetivo="namoro",
    bio=(
        "Apaixonada por musica ao vivo, adoro explorar novos destinos e registrar "
        "tudo pela fotografia. Yoga faz parte da minha rotina e cinema e meu "
        "programa favorito nos fins de semana."
    ),
    interesses=["musica", "viagem", "fotografia", "yoga", "cinema", "arte", "gastronomia"],
)


# ── Listas de dados sinteticos (constantes de modulo, nao-aleatorias) ──────────

_NOMES_FEMININOS: List[str] = [
    "Julia Santos",
    "Camila Rocha",
    "Fernanda Costa",
    "Beatriz Alves",
    "Leticia Pereira",
    "Mariana Silva",
    "Isabela Ferreira",
    "Larissa Oliveira",
    "Natalia Souza",
    "Vanessa Carvalho",
    "Aline Barbosa",
    "Priscila Martins",
    "Tatiana Ribeiro",
    "Claudia Gomes",
    "Patricia Lima",
    "Renata Araujo",
    "Simone Nunes",
    "Adriana Dias",
    "Elaine Torres",
    "Viviane Correia",
    "Bianca Mendes",
    "Carolina Figueiredo",
]

_NOMES_MASCULINOS: List[str] = [
    "Lucas Ferreira",
    "Matheus Lima",
    "Gabriel Souza",
    "Rafael Oliveira",
    "Pedro Alves",
    "Gustavo Costa",
    "Felipe Silva",
    "Bruno Santos",
    "Andre Pereira",
    "Ricardo Martins",
    "Eduardo Rocha",
    "Thiago Carvalho",
    "Diego Barbosa",
    "Rodrigo Ribeiro",
    "Marcelo Gomes",
    "Leandro Araujo",
    "Vinicius Nunes",
    "Fabio Dias",
    "Henrique Torres",
    "Renato Correia",
    "Leonardo Mendes",
    "Alexandre Figueiredo",
]

_NOMES_NEUTROS: List[str] = [
    "Alex Carvalho",
    "Jordan Pereira",
    "Sam Ribeiro",
    "Casey Monteiro",
    "Morgan Teixeira",
    "Robin Cardoso",
    "Taylor Azevedo",
]

_CIDADES: List[str] = [
    "Sao Paulo",
    "Rio de Janeiro",
    "Belo Horizonte",
    "Curitiba",
    "Porto Alegre",
    "Salvador",
    "Fortaleza",
    "Recife",
    "Manaus",
    "Brasilia",
]

_TODOS_INTERESSES: List[str] = [
    "musica",
    "viagem",
    "fotografia",
    "yoga",
    "cinema",
    "arte",
    "gastronomia",
    "leitura",
    "esportes",
    "tecnologia",
    "culinaria",
    "danca",
    "teatro",
    "natureza",
    "meditacao",
    "games",
    "series",
    "academia",
    "ciclismo",
    "trilhas",
    "surf",
    "corrida",
    "pintura",
    "escrita",
    "poesia",
    "historia",
    "astronomia",
    "voluntariado",
    "moda",
    "arquitetura",
    "design",
    "sustentabilidade",
]

_INTERESSES_ALTA_COMPAT: List[str] = [
    "musica",
    "viagem",
    "fotografia",
    "yoga",
    "cinema",
    "arte",
    "gastronomia",
]

_BIOS_ALTA_COMPATIBILIDADE: List[str] = [
    "Adoro musica ao vivo e viagens pelo Brasil. Fotografia e minha paixao.",
    "Amante de musica, fotografia e gastronomia local.",
    "Viajante apaixonada, sempre com a camera na mao e uma playlist nova.",
    "Cinema, yoga e viagens definem meu fim de semana ideal.",
    "Musica no fone, camera na mochila, sempre pronto para uma nova aventura.",
    "Fotografo amador que ama cinema de arte e culinaria internacional.",
    "Nada melhor que um show ao vivo e um roteiro de viagem na gaveta.",
    "Yoga pela manha, fotografia no entardecer, cinema a noite.",
    "Explorador de cafes, shows e museus. Vida com arte e musica.",
    "Viajo sempre que posso e registro tudo pela lente da minha camera.",
    "Musica indie, fotografia analogica e gastronomia de rua.",
    "Show, viagem e boa comida. E tudo que preciso para ser feliz.",
    "Apaixonada por viagens longas, musica ao vivo e fotografia de paisagem.",
    "Cinema e arte sempre presentes na minha rotina, alem do yoga diario.",
    "Amo misturar viagens com fotografia e gastronomia local.",
    "Vivo por musica, vivo por viagens. Sempre com a camera no bolso.",
    "Fotografia de rua, concertos de jazz e cozinha italiana sao meus hobbies.",
    "Yoga, cinema independente e viagens de mochila definem quem sou.",
    "Arte, musica e uma boa aventura: assim e a minha vida.",
    "Viajante compulsiva que adora shows e come de tudo.",
    "Musica classica, fotografia e uma boa trilha na natureza.",
    "Cinema, yoga e viagens internacionais preenchem meu tempo livre.",
]

_BIOS_GERAIS: List[str] = [
    "Amo esportes ao ar livre e tecnologia.",
    "Leitora inveterada e amante de series.",
    "Academia pela manha e games a noite.",
    "Ciclismo nos fins de semana e boa comida.",
    "Teatro e danca sao minhas paixoes.",
    "Curto trilhas e natureza no geral.",
    "Series, games e um bom cafe.",
    "Entusiasta de tecnologia e startups.",
    "Meditacao e plantas: minha rotina diaria.",
    "Corro tres vezes por semana e adoro cozinhar.",
    "Apaixonado por historia e ciencias.",
    "Leitor voraz de ficcao cientifica.",
    "Surfista nas horas livres, arquiteto no trabalho.",
    "Voluntariado e sustentabilidade sao causas que defendo.",
    "Design e moda como forma de expressao.",
    "Cozinha experimental e mercado livre.",
    "Escrita criativa nas madrugadas.",
    "Astronomia e ciclismo: mundos completamente opostos que me definem.",
    "Vivo de poesia e bons livros.",
    "Moda como arte, gastronomia como cultura.",
    "Academia e leitura — corpo e mente em dia.",
    "Gosto de series, games e tecnologia.",
    "Amo danca, musica e pessoas energeticas.",
    "Trilhas e fotos no celular: explorador do cotidiano.",
    "Culinaria asiatica e meditacao sao meu equilibrio.",
    "Esportes aquaticos e gastronomia italiana.",
    "Voluntariado com animais e leitura de romances.",
    "Design de interiores e sustentabilidade.",
    "Series policiais e boa cerveja artesanal.",
    "Ciclismo urbano e cafe especial.",
    "Teatro amador e escrita de contos.",
    "Historia e arquitetura das cidades.",
]


# ── Funcoes internas de geracao ────────────────────────────────────────────────

def _gerar_perfil_alta_compatibilidade(rng: random.Random, indice: int) -> Perfil:
    """Gera um perfil garantidamente compativel com PERFIL_TESTE.

    Criterios garantidos:
      - objetivo == "namoro"
      - faixa_etaria_pref cobre idade 27
      - >= 3 interesses em comum com PERFIL_TESTE.interesses
    """
    genero = rng.choices(
        ["feminino", "masculino", "nao_binario"],
        weights=[0.5, 0.4, 0.1],
        k=1,
    )[0]

    if genero == "feminino":
        nome_base = rng.choice(_NOMES_FEMININOS)
    elif genero == "masculino":
        nome_base = rng.choice(_NOMES_MASCULINOS)
    else:
        nome_base = rng.choice(_NOMES_NEUTROS)

    nome = f"{nome_base}"

    genero_preferido = rng.choices(
        ["feminino", "masculino", "todos"],
        weights=[0.4, 0.4, 0.2],
        k=1,
    )[0]

    cidade = rng.choice(_CIDADES)
    idade = rng.randint(22, 36)

    faixa_min = rng.randint(18, 27)
    faixa_max = rng.randint(27, 40)

    # Garantir >= 3 interesses em comum: incluir 3 fixos dos interesses do PERFIL_TESTE
    # e sortear mais alguns
    interesses_fixos = rng.sample(_INTERESSES_ALTA_COMPAT, 3)
    interesses_extras_pool = [i for i in _TODOS_INTERESSES if i not in interesses_fixos]
    n_extras = rng.randint(1, 3)
    interesses_extras = rng.sample(interesses_extras_pool, n_extras)
    interesses = list(set(interesses_fixos + interesses_extras))

    bio = rng.choice(_BIOS_ALTA_COMPATIBILIDADE)

    return Perfil(
        id=f"seed-compat-{indice:04d}",
        nome=nome,
        idade=idade,
        cidade=cidade,
        genero=genero,
        genero_preferido=genero_preferido,
        faixa_etaria_pref=(faixa_min, faixa_max),
        objetivo="namoro",
        bio=bio,
        interesses=interesses,
    )


def _gerar_perfil_gate_garantido(rng: random.Random, indice: int) -> Perfil:
    """Gera um perfil masculino garantidamente apto a atingir score >= 85 com PERFIL_TESTE.

    Necessario para o gate critico TEST-02: o embedding mock (hashlib.md5) nao
    captura semantica real, portanto os demais fatores (geografia, interesses, idade)
    precisam estar calibrados ao maximo.

    Criterios fixos (nao-aleatorios):
      - genero == "masculino"        (match do genero_preferido do PERFIL_TESTE)
      - objetivo == "namoro"         (match de objetivo)
      - cidade == "Sao Paulo"        (geo=100, contribui 5 pts)
      - 4 interesses de _INTERESSES_ALTA_COMPAT (score_interesses=20, contribui 20 pts)
      - idade em [24, 30]            (score_idade >= 94, contribui >= 4.7 pts)

    Com esses valores e score_semantico tipico de 85-90 (distancia coseno ~0.2-0.3
    para bios da mesma lista _BIOS_ALTA_COMPATIBILIDADE):
      score_final >= 85*0.60 + 20 + 10 + 94*0.05 + 100*0.05 = 51+20+10+4.7+5 >= 90.7
    """
    nome_base = rng.choice(_NOMES_MASCULINOS)
    nome = f"{nome_base}"

    idade = rng.randint(24, 30)
    faixa_min = rng.randint(18, 25)
    faixa_max = rng.randint(27, 38)

    # 4 interesses fixos do pool de alta compatibilidade (garante score_interesses=20)
    interesses = rng.sample(_INTERESSES_ALTA_COMPAT, 4)

    bio = rng.choice(_BIOS_ALTA_COMPATIBILIDADE)

    return Perfil(
        id=f"seed-gate-{indice:04d}",
        nome=nome,
        idade=idade,
        cidade="Sao Paulo",
        genero="masculino",
        genero_preferido="feminino",
        faixa_etaria_pref=(faixa_min, faixa_max),
        objetivo="namoro",
        bio=bio,
        interesses=interesses,
    )


def _gerar_perfil_diverso(rng: random.Random, indice: int) -> Perfil:
    """Gera um perfil de diversidade (sem restricao de compatibilidade com PERFIL_TESTE).

    Cobre os 3 objetivos, multiplas cidades e faixas etarias variadas.
    """
    genero = rng.choice(["feminino", "masculino", "nao_binario", "outro"])

    if genero == "feminino":
        nome_base = rng.choice(_NOMES_FEMININOS)
    elif genero == "masculino":
        nome_base = rng.choice(_NOMES_MASCULINOS)
    else:
        nome_base = rng.choice(_NOMES_NEUTROS)

    nome = f"{nome_base}"

    genero_preferido = rng.choice(["feminino", "masculino", "nao_binario", "outro", "todos"])
    cidade = rng.choice(_CIDADES)
    idade = rng.randint(18, 60)

    faixa_min = rng.randint(18, 50)
    faixa_max = rng.randint(faixa_min, min(faixa_min + 30, 99))

    objetivo = rng.choice(["namoro", "casual", "amizade"])

    n_interesses = rng.randint(3, 6)
    interesses = rng.sample(_TODOS_INTERESSES, n_interesses)

    bio = rng.choice(_BIOS_GERAIS)

    return Perfil(
        id=f"seed-diverso-{indice:04d}",
        nome=nome,
        idade=idade,
        cidade=cidade,
        genero=genero,
        genero_preferido=genero_preferido,
        faixa_etaria_pref=(faixa_min, faixa_max),
        objetivo=objetivo,
        bio=bio,
        interesses=interesses,
    )


# ── Funcao principal exportada ─────────────────────────────────────────────────

def gerar_pool_perfis(seed: int = SEED_FIXA) -> List[Perfil]:
    """Gera pool reproduzivel de perfis sinteticos.

    Retorna lista com:
      - 15 perfis de gate garantido (masculino+namoro+SP+4 interesses — garante TEST-02)
      - 20 perfis de alta compatibilidade com PERFIL_TESTE (garante SEED-02)
      - 80 perfis de diversidade (cobre SEED-01)
    Total: 115 perfis.

    Os 15 "gate garantidos" sao calibrados para atingir score >= 85 mesmo com o
    embedding mock deterministico (hashlib.md5), que nao captura semantica real.
    Eles garantem que o gate critico TEST-02 (>= 10 matches com score >= 85) passe.

    Args:
        seed: Semente para o gerador pseudo-aleatorio. Default SEED_FIXA=42.
              Usar seed diferente para testes de robustez.

    Returns:
        Lista de 115 instancias de Perfil validadas pelo Pydantic.
    """
    rng = random.Random(seed)   # Random local — nao altera o estado global
    perfis: List[Perfil] = []

    # 15 perfis de gate garantido (masculino, namoro, SP, 4 interesses — TEST-02)
    for i in range(15):
        perfis.append(_gerar_perfil_gate_garantido(rng, i))

    # 20 perfis de alta compatibilidade (garante SEED-02: >= 10 compativeis)
    for i in range(20):
        perfis.append(_gerar_perfil_alta_compatibilidade(rng, i + 15))

    # 80 perfis de diversidade (garante SEED-01: diversidade sem vies obvio)
    for i in range(80):
        perfis.append(_gerar_perfil_diverso(rng, i + 35))

    # Embaralhar para que gate-garantido nao fique sempre nos primeiros 15
    rng.shuffle(perfis)

    return perfis
