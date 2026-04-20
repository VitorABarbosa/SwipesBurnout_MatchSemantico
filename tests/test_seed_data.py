"""Testes TDD do gerador de seed data do CONNECT.AI.

Cobre SEED-01 (diversidade), SEED-02 (>= 10 compativeis), SEED-03 (perfil de
teste explicito), SEED-04 (reproducibilidade com seed fixa).

Estes testes sao escritos ANTES da implementacao (fase RED do TDD).
Todos devem falhar com ImportError ate que connect_ai/seed_data.py exista.
"""

from connect_ai.schema import Perfil
from connect_ai.seed_data import PERFIL_TESTE, SEED_FIXA, gerar_pool_perfis


# ── helpers de analise estatica ────────────────────────────────────────────────

def _interesses_em_comum(a: list, b: list) -> int:
    """Conta interesses identicos (case-sensitive) entre duas listas."""
    return len(set(a) & set(b))


def _faixa_etaria_compativel(idade: int, faixa: tuple) -> bool:
    """Retorna True se `idade` esta dentro de `faixa` (inclusive)."""
    return faixa[0] <= idade <= faixa[1]


# ── SEED-04: reproducibilidade ─────────────────────────────────────────────────

def test_reproducibilidade_seed_fixa():
    """Duas chamadas com seed=42 devem produzir o mesmo pool (SEED-04)."""
    pool_a = gerar_pool_perfis(seed=42)
    pool_b = gerar_pool_perfis(seed=42)
    nomes_a = [p.nome for p in pool_a]
    nomes_b = [p.nome for p in pool_b]
    assert nomes_a == nomes_b, (
        "gerar_pool_perfis(seed=42) deve retornar perfis com mesmos nomes "
        "e mesma ordem em execucoes distintas."
    )


# ── SEED-03: perfil de teste explicito ─────────────────────────────────────────

def test_perfil_teste_e_explicito():
    """PERFIL_TESTE deve ter campos fixos e documentados, nao aleatorios (SEED-03).

    Campos verificados: nome 'Ana Lima', objetivo 'namoro', idade 27,
    pelo menos 5 interesses incluindo 'musica' e 'viagem'.
    """
    assert isinstance(PERFIL_TESTE, Perfil), "PERFIL_TESTE deve ser uma instancia de Perfil."
    assert PERFIL_TESTE.nome == "Ana Lima", f"Esperado 'Ana Lima', obtido '{PERFIL_TESTE.nome}'"
    assert PERFIL_TESTE.objetivo == "namoro", (
        f"Esperado objetivo 'namoro', obtido '{PERFIL_TESTE.objetivo}'"
    )
    assert PERFIL_TESTE.idade == 27, f"Esperada idade 27, obtida {PERFIL_TESTE.idade}"
    assert len(PERFIL_TESTE.interesses) >= 5, (
        f"PERFIL_TESTE deve ter >= 5 interesses, tem {len(PERFIL_TESTE.interesses)}"
    )
    assert "musica" in PERFIL_TESTE.interesses, "'musica' deve estar nos interesses do PERFIL_TESTE"
    assert "viagem" in PERFIL_TESTE.interesses, "'viagem' deve estar nos interesses do PERFIL_TESTE"


# ── SEED-01: pool com tamanho e validade ───────────────────────────────────────

def test_pool_tem_minimo_100_perfis():
    """Pool deve ter >= 100 perfis, todos instancias validas de Perfil (SEED-01)."""
    pool = gerar_pool_perfis()
    assert len(pool) >= 100, f"Pool deve ter >= 100 perfis, tem {len(pool)}"
    assert all(isinstance(p, Perfil) for p in pool), (
        "Todos os elementos do pool devem ser instancias de Perfil."
    )


# ── SEED-02: garantia matematica de >= 10 compativeis ─────────────────────────

def test_pool_tem_10_compativeis_com_perfil_teste():
    """Analise estatica: >= 10 perfis compativeis com PERFIL_TESTE (SEED-02).

    Criterios (sem ChromaDB, analise puramente estrutural):
      - interesses_em_comum(p.interesses, PERFIL_TESTE.interesses) >= 3
      - p.objetivo == PERFIL_TESTE.objetivo
      - faixa_etaria_pref de p cobre a idade de PERFIL_TESTE (27)
    """
    pool = gerar_pool_perfis()
    compativeis = [
        p for p in pool
        if (
            _interesses_em_comum(p.interesses, PERFIL_TESTE.interesses) >= 3
            and p.objetivo == PERFIL_TESTE.objetivo
            and _faixa_etaria_compativel(PERFIL_TESTE.idade, p.faixa_etaria_pref)
        )
    ]
    assert len(compativeis) >= 10, (
        f"Pool deve ter >= 10 perfis compativeis com PERFIL_TESTE, "
        f"encontrados {len(compativeis)}. "
        f"Calibre os perfis de alta compatibilidade no seed_data.py."
    )


# ── SEED-01: diversidade do pool ──────────────────────────────────────────────

def test_pool_diversidade():
    """Pool deve cobrir diversidade de cidade, objetivo e faixa etaria (SEED-01)."""
    pool = gerar_pool_perfis()

    cidades_unicas = {p.cidade for p in pool}
    assert len(cidades_unicas) >= 5, (
        f"Pool deve ter >= 5 cidades unicas, tem {len(cidades_unicas)}: {cidades_unicas}"
    )

    objetivos_presentes = {p.objetivo for p in pool}
    assert objetivos_presentes == {"namoro", "casual", "amizade"}, (
        f"Pool deve cobrir os 3 objetivos, encontrados: {objetivos_presentes}"
    )

    idades = [p.idade for p in pool]
    assert min(idades) <= 28, (
        f"Pool deve incluir pessoas jovens (<= 28 anos), minimo encontrado: {min(idades)}"
    )
    assert max(idades) >= 40, (
        f"Pool deve incluir pessoas acima de 40 anos, maximo encontrado: {max(idades)}"
    )
