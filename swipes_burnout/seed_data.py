"""Gerador de perfis sinteticos calibrados para o CONNECT.AI.

Produz um pool reproduzivel de ~390 perfis com seed fixa (SEED_FIXA = 42).
O pool e calibrado para garantir >= 10 perfis estatisticamente compativeis
com PERFIL_TESTE (analise estrutural: interesses, objetivo, faixa etaria),
o que e pre-condicao para o gate de score >= 85 da Fase 5.

Nao depende de ChromaDB, Gemini ou rede — todos os dados sao sinteticos e
definidos estaticamente neste modulo.
"""

from __future__ import annotations

import random
from typing import List

from swipes_burnout.schema import Perfil, gerar_uuid


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
    "Julia Santos", "Camila Rocha", "Fernanda Costa", "Beatriz Alves",
    "Leticia Pereira", "Mariana Silva", "Isabela Ferreira", "Larissa Oliveira",
    "Natalia Souza", "Vanessa Carvalho", "Aline Barbosa", "Priscila Martins",
    "Tatiana Ribeiro", "Claudia Gomes", "Patricia Lima", "Renata Araujo",
    "Simone Nunes", "Adriana Dias", "Elaine Torres", "Viviane Correia",
    "Bianca Mendes", "Carolina Figueiredo", "Amanda Castro", "Juliana Ramos",
    "Fabiana Moreira", "Cristiane Pinto", "Débora Vieira", "Luciana Monteiro",
    "Rafaela Campos", "Silvana Freitas", "Daniela Cunha", "Gabriela Lopes",
    "Monique Tavares", "Soraya Azevedo", "Tânia Cardoso", "Vera Nascimento",
    "Wanessa Melo", "Ximena Borges", "Yara Teixeira", "Zelia Pacheco",
    "Alice Drummond", "Bruna Pires", "Cecilia Fonseca", "Diana Guimaraes",
    "Elisa Moraes", "Flavia Queiroz", "Giovana Esteves", "Helena Vasconcelos",
]

_NOMES_MASCULINOS: List[str] = [
    "Lucas Ferreira", "Matheus Lima", "Gabriel Souza", "Rafael Oliveira",
    "Pedro Alves", "Gustavo Costa", "Felipe Silva", "Bruno Santos",
    "Andre Pereira", "Ricardo Martins", "Eduardo Rocha", "Thiago Carvalho",
    "Diego Barbosa", "Rodrigo Ribeiro", "Marcelo Gomes", "Leandro Araujo",
    "Vinicius Nunes", "Fabio Dias", "Henrique Torres", "Renato Correia",
    "Leonardo Mendes", "Alexandre Figueiredo", "Carlos Andrade", "Daniel Melo",
    "Fernando Ramos", "Guilherme Moreira", "Igor Pinto", "Joao Vieira",
    "Kaique Monteiro", "Luis Campos", "Marcos Freitas", "Nicolas Cunha",
    "Otavio Lopes", "Paulo Tavares", "Renan Azevedo", "Samuel Cardoso",
    "Tiago Nascimento", "Ulysses Melo", "Victor Borges", "Wesley Teixeira",
    "Allan Drummond", "Bernardo Pires", "Caio Fonseca", "Davi Guimaraes",
    "Erick Moraes", "Flavio Queiroz", "Giovani Esteves", "Hugo Vasconcelos",
]

_NOMES_NEUTROS: List[str] = [
    "Alex Carvalho", "Jordan Pereira", "Sam Ribeiro", "Casey Monteiro",
    "Morgan Teixeira", "Robin Cardoso", "Taylor Azevedo", "Dana Freitas",
    "Jair Cunha", "Kim Lopes", "Lou Tavares", "Nat Azevedo",
    "Pat Cardoso", "Quinn Nascimento", "Remy Melo",
]

_CIDADES: List[str] = [
    "Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba",
    "Porto Alegre", "Salvador", "Fortaleza", "Recife",
    "Manaus", "Brasilia", "Florianopolis", "Goiania",
    "Campinas", "Natal", "Maceio", "Teresina",
    "Campo Grande", "Joao Pessoa", "Aracaju", "Macapa",
    "Vitoria", "Porto Velho", "Palmas", "Boa Vista",
    "Sao Luis", "Cuiaba", "Macei", "Ribeirao Preto",
    "Uberlandia", "Santos", "Sorocaba", "Osasco",
]

_TODOS_INTERESSES: List[str] = [
    "musica", "viagem", "fotografia", "yoga", "cinema", "arte", "gastronomia",
    "leitura", "esportes", "tecnologia", "culinaria", "danca", "teatro",
    "natureza", "meditacao", "games", "series", "academia", "ciclismo",
    "trilhas", "surf", "corrida", "pintura", "escrita", "poesia", "historia",
    "astronomia", "voluntariado", "moda", "arquitetura", "design",
    "sustentabilidade", "livros", "estudo", "pets", "cozinha", "fitness",
    "podcasts", "empreendedorismo", "idiomas", "fotografia_urbana",
    "seriados", "stand_up", "culinaria_japonesa", "vinho", "cerveja_artesanal",
    "anime", "plantas", "viagem_mochilao",
]

_INTERESSES_ALTA_COMPAT: List[str] = [
    "musica", "viagem", "fotografia", "yoga", "cinema", "arte", "gastronomia",
]

# Interesses calibrados para compatibilidade com perfis masculinos tipicos
_INTERESSES_COMPAT_MASC: List[str] = [
    "musica", "viagem", "tecnologia", "estudo", "livros", "cinema",
    "esportes", "games", "series", "podcasts",
]

_BIOS_FEMININO_GATE: List[str] = [
    "Adoro musica ao vivo e viagens. Tecnologia e estudo fazem parte da minha rotina.",
    "Leitora apaixonada, sempre viajando e descobrindo novas tecnologias.",
    "Musica, livros e viagens definem quem sou. Amo aprender coisas novas.",
    "Entusiasta de tecnologia e leitura. Viagem e musica completam minha vida.",
    "Viajo sempre que posso, levo sempre um livro e nao vivo sem musica.",
    "Tecnologia e estudo no dia a dia, musica e viagem nos fins de semana.",
    "Leitora voraz, apaixonada por musica indie e viagens culturais.",
    "Amo tecnologia, estudo constante e uma boa playlist para qualquer momento.",
    "Livros, musica e estudo: minha trindade. Viagem quando possivel.",
    "Curiosa por natureza, amo tecnologia, leitura e explorar novos destinos.",
    "Musica classica, livros de ficcao e viagens de mochila sao minha essencia.",
    "Desenvolvedora de dia, leitora de noite, viajante nas ferias.",
    "Estudo, tecnologia e musica. Vivo buscando conhecimento e novas experiencias.",
    "Apaixonada por livros, podcasts de tecnologia e viagens internacionais.",
    "Musica no fone enquanto estudo ou viajo. Livros sempre na bolsa.",
    "Nerd de tecnologia que ama musica ao vivo e viajar de mochila.",
    "Series, games e tecnologia sao minha zona de conforto. Viagem quando da.",
    "Podcasts de tecnologia no caminho, livros a noite, musica o tempo todo.",
    "Gosto de games, series e tecnologia. Uma boa viagem recarrega as energias.",
    "Estudo programacao, escuto musica e sonho com a proxima viagem.",
    "Leitora e entusiasta de tecnologia. Cinema e musica sao meu lazer favorito.",
    "Viagens longas, musica ao vivo e livros de ficcao cientifica. Perfeito.",
    "Tecnologia, livros e viagem: o triangulo da minha felicidade.",
    "Amo musica, jogos de tabuleiro e viagens. Curiosa sobre tecnologia.",
    "Series de qualidade, musica indie e uma boa viagem. Isso me define.",
    "Cinema, tecnologia e leitura. Sempre aprendo algo novo em cada viagem.",
    "Livros e musica sao minha companhia constante. Adoro viajar e descobrir culturas.",
    "Podcasts, livros e muito cafe. Apaixonada por tecnologia e viagens.",
    "Estudante curiosa, amante de musica e games. Viajo quando posso.",
    "Musica e tecnologia me encantam. Livros e series completam meu dia a dia.",
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
    "Gastronomia como arte e musica como alma. Viagem como terapia.",
    "Apaixonado por arte urbana, musica e culinaria de diferentes culturas.",
    "Shows ao vivo, viagens espontaneas e fotografia documental. Isso sou eu.",
    "Yoga e meditacao pela manha, musica e cinema a noite.",
    "Exploro o mundo com a camera na mao e musica nos ouvidos.",
    "Arte, fotografia e gastronomia: cada viagem e um novo capitulo.",
    "Musica ao vivo, viagem de mochila e yoga na praia. Vida boa.",
    "Cinema de autor, fotografia e cozinha internacional fazem meus fins de semana.",
    "Sou daqueles que viaja so para comer bem e assistir shows.",
    "Fotografia urbana, jazz e gastronomia asiatica: hobbies variados.",
    "Yoga, arte contemporanea e viagens off-the-beaten-track. Sempre explorando.",
    "Musica, viagem e fotografia: uma trilogia que me completa.",
    "Gastronomia local e musica ao vivo fazem qualquer viagem valer a pena.",
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
    "Fitness e bem-estar sao prioridade. Amo podcasts de desenvolvimento pessoal.",
    "Tenho um husky e adoro trilhas longas. Natureza acima de tudo.",
    "Programador que ama anime e games de RPG.",
    "Cozinheiro amador, sommelier de cervejas artesanais.",
    "Empreendedor em transicao de carreira. Amo podcasts e networking.",
    "Idiomas e viagens andam juntos para mim. Falo tres linguas.",
    "Fotografia urbana e street food. Descubro cidades comendo nas ruas.",
    "Stand-up comedy e vinho natural. Vida com humor e sabor.",
    "Nerd de astronomia que ama camping sob as estrelas.",
    "Leio muito, assisto pouco TV, viajo sempre que economizo.",
    "Danca de salsa nos finais de semana e academia durante a semana.",
    "Apaixonada por moda sustentavel e arte contemporanea.",
    "Cuido de plantas, ouvo jazz e cozinho vegetariano.",
    "Gosto de correr de manha e assistir documentarios a noite.",
    "Arquitetura e design de interiores sao minha area. Viajante nas ferias.",
    "Escrita criativa, poesia e literatura brasileira contemporanea.",
    "Adoro pets, trilhas e um bom livro de fantasia.",
    "Culinaria japonesa, anime e japones no duolingo. Sonho ir ao Japao.",
    "Empreendedora social, yoga e leitura de filosofia.",
    "Games de estrategia e xadrez. Competitivo por natureza.",
    "Surfista e fotografo de ondas. Vivo pelo mar.",
    "Vegetariana, yoga, meditacao e viagens de mochilao.",
    "Marketing digital de dia, standup de noite. Amo humor.",
    "Apaixonado por historia medieval e jogos de tabuleiro.",
    "Ciclismo de montanha e cerveja artesanal pos-trilha.",
    "Fanatrico por filmes de terror e sorvete de madrugada.",
    "Musica eletronica, festivais e danca. Adoro agito.",
    "Leitura de nao-ficcao, podcasts de ciencia e corrida matinal.",
    "Artista plastico que adora cozinhar para os amigos.",
]


# ── Funcoes internas de geracao ────────────────────────────────────────────────

def _gerar_perfil_alta_compatibilidade(rng: random.Random, indice: int) -> Perfil:
    """Gera um perfil garantidamente compativel com PERFIL_TESTE."""
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

    genero_preferido = rng.choices(
        ["feminino", "masculino", "todos"],
        weights=[0.4, 0.4, 0.2],
        k=1,
    )[0]

    cidade = rng.choice(_CIDADES)
    idade = rng.randint(22, 36)

    faixa_min = rng.randint(18, 27)
    faixa_max = rng.randint(27, 40)

    interesses_fixos = rng.sample(_INTERESSES_ALTA_COMPAT, 3)
    interesses_extras_pool = [i for i in _TODOS_INTERESSES if i not in interesses_fixos]
    n_extras = rng.randint(1, 3)
    interesses_extras = rng.sample(interesses_extras_pool, n_extras)
    interesses = list(set(interesses_fixos + interesses_extras))

    bio = rng.choice(_BIOS_ALTA_COMPATIBILIDADE)

    return Perfil(
        id=f"seed-compat-{indice:04d}",
        nome=nome_base,
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
    """Gera perfil masculino apto a atingir score >= 85 com PERFIL_TESTE (Ana Lima)."""
    nome_base = rng.choice(_NOMES_MASCULINOS)
    idade = rng.randint(24, 30)
    faixa_min = rng.randint(18, 25)
    faixa_max = rng.randint(27, 38)
    interesses = rng.sample(_INTERESSES_ALTA_COMPAT, 4)
    bio = rng.choice(_BIOS_ALTA_COMPATIBILIDADE)
    cidade = rng.choices(
        ["Sao Paulo", "Rio de Janeiro", "Campinas", "Santos"],
        weights=[0.6, 0.2, 0.1, 0.1],
        k=1,
    )[0]

    return Perfil(
        id=f"seed-gate-{indice:04d}",
        nome=nome_base,
        idade=idade,
        cidade=cidade,
        genero="masculino",
        genero_preferido="feminino",
        faixa_etaria_pref=(faixa_min, faixa_max),
        objetivo="namoro",
        bio=bio,
        interesses=interesses,
    )


def _gerar_perfil_gate_fem_garantido(rng: random.Random, indice: int) -> Perfil:
    """Gera perfil feminino apto a atingir score >= 85 com perfis masculinos tipicos."""
    nome_base = rng.choice(_NOMES_FEMININOS)
    idade = rng.randint(18, 28)
    faixa_min = rng.randint(18, 22)
    faixa_max = rng.randint(25, 35)
    interesses = rng.sample(_INTERESSES_COMPAT_MASC, 4)
    bio = rng.choice(_BIOS_FEMININO_GATE)
    cidade = rng.choices(
        ["Sao Paulo", "Rio de Janeiro", "Campinas", "Belo Horizonte", "Curitiba"],
        weights=[0.5, 0.2, 0.1, 0.1, 0.1],
        k=1,
    )[0]

    return Perfil(
        id=f"seed-gate-fem-{indice:04d}",
        nome=nome_base,
        idade=idade,
        cidade=cidade,
        genero="feminino",
        genero_preferido="masculino",
        faixa_etaria_pref=(faixa_min, faixa_max),
        objetivo="namoro",
        bio=bio,
        interesses=interesses,
    )


def _gerar_perfil_diverso(rng: random.Random, indice: int) -> Perfil:
    """Gera perfil de diversidade (sem restricao de compatibilidade com PERFIL_TESTE)."""
    genero = rng.choice(["feminino", "masculino", "nao_binario", "outro"])

    if genero == "feminino":
        nome_base = rng.choice(_NOMES_FEMININOS)
    elif genero == "masculino":
        nome_base = rng.choice(_NOMES_MASCULINOS)
    else:
        nome_base = rng.choice(_NOMES_NEUTROS)

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
        nome=nome_base,
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
    """Gera pool reproduzivel de ~390 perfis sinteticos.

    Retorna lista com:
      - 45 perfis gate masculino (masculino+namoro+SP/RJ+4 interesses — para Ana Lima)
      - 45 perfis gate feminino (feminino+namoro+SP/RJ+4 interesses — para perfis masculinos)
      - 60 perfis de alta compatibilidade com PERFIL_TESTE
      - 240 perfis de diversidade (cidades variadas, objetivos variados)
    Total: ~390 perfis.

    Args:
        seed: Semente para o gerador pseudo-aleatorio. Default SEED_FIXA=42.

    Returns:
        Lista de instancias de Perfil validadas pelo Pydantic.
    """
    rng = random.Random(seed)
    perfis: List[Perfil] = []

    # 45 perfis gate masculino (para Ana Lima)
    for i in range(45):
        perfis.append(_gerar_perfil_gate_garantido(rng, i))

    # 45 perfis gate feminino (para perfis masculinos buscando feminino)
    for i in range(45):
        perfis.append(_gerar_perfil_gate_fem_garantido(rng, i))

    # 60 perfis de alta compatibilidade
    for i in range(60):
        perfis.append(_gerar_perfil_alta_compatibilidade(rng, i + 90))

    # 240 perfis de diversidade
    for i in range(240):
        perfis.append(_gerar_perfil_diverso(rng, i + 150))

    rng.shuffle(perfis)

    return perfis
