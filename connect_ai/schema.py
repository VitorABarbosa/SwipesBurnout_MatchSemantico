"""Schema de dados do CONNECT.AI.

Define o modelo `Perfil` com 3 grupos de campos (BRIEFING secao 6):
  - Estruturados: id, nome, idade, cidade, genero, genero_preferido,
    faixa_etaria_pref, objetivo
  - Semanticos: bio, interesses
  - Multimodais: foto_perfil, fotos_extras
  - Gerado: personalidade_ia (preenchido pelo Agente Perfilador)

Este modulo e a fonte da verdade do schema usado em TODAS as fases:
seed data, agentes (Perfilador/Casamenteiro/RAG), pipeline de ingestao,
pipeline de consumo, front Streamlit e notebook. Mudancas aqui propagam
para o resto do projeto.
"""

from __future__ import annotations

import uuid
from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator


# Tipos literais (Pydantic gera ValidationError automaticamente para valores fora do conjunto).
Genero = Literal["feminino", "masculino", "nao_binario", "outro"]
GeneroPreferido = Literal["feminino", "masculino", "nao_binario", "outro", "todos"]
Objetivo = Literal["namoro", "casual", "amizade"]


def gerar_uuid() -> str:
    """Gera um identificador UUIDv4 como string.

    Usado como id padrao do Perfil quando nao fornecido pelo chamador.
    Garante unicidade praticamente certa (probabilidade de colisao < 1e-15
    para milhoes de chamadas) e e seguro para uso como chave primaria do
    ChromaDB e como identificador exposto no front.
    """
    return str(uuid.uuid4())


class Perfil(BaseModel):
    """Modelo de perfil do CONNECT.AI.

    Combina dados estruturados (filtros hard), semanticos (alimento do
    embedding) e multimodais (placeholder por decisao do PROJECT.md, ja
    que a entrega usa mocks textuais para Gemini Vision). O campo
    `personalidade_ia` e preenchido apos a passagem pelo Agente Perfilador
    e fica vazio (None) ate la.

    A validacao garante:
      - idade no intervalo [18, 99] (sem cadastro de menores)
      - genero/genero_preferido/objetivo nos conjuntos definidos
      - faixa_etaria_pref com ordem correta e dentro de [18, 99]
      - lista de interesses nao vazia (apos remocao de strings vazias)
      - bio nao vazia (necessaria para o embedding semantico)
    """

    # === Campos estruturados (filtros hard no ChromaDB) ===
    id: str = Field(default_factory=gerar_uuid)
    nome: str = Field(min_length=1, max_length=120)
    idade: int = Field(ge=18, le=99)
    cidade: str = Field(min_length=1, max_length=120)
    genero: Genero
    genero_preferido: GeneroPreferido
    faixa_etaria_pref: Tuple[int, int]
    objetivo: Objetivo

    # === Campos semanticos (compoem o documento embedado) ===
    bio: str = Field(min_length=1, max_length=2000)
    interesses: List[str] = Field(min_length=1)

    # === Campos multimodais (placeholders -- mocks textuais nesta entrega) ===
    foto_perfil: Optional[str] = None
    fotos_extras: List[str] = Field(default_factory=list)

    # === Campo gerado pelo Perfilador ===
    personalidade_ia: Optional[str] = None

    @field_validator("interesses")
    @classmethod
    def _interesses_nao_vazios(cls, v: List[str]) -> List[str]:
        """Remove strings vazias/whitespace e exige pelo menos 1 interesse restante.

        A lista de interesses alimenta tanto o documento semantico (concatenado
        no embedding) quanto o calculo de "interesses em comum" (20% do score).
        Permitir lista vazia inviabiliza o pipeline.
        """
        limpos = [s.strip() for s in v if s and s.strip()]
        if not limpos:
            raise ValueError("A lista de interesses nao pode ser vazia.")
        return limpos

    @model_validator(mode="after")
    def _validar_faixa_etaria(self) -> "Perfil":
        """Valida a tupla `faixa_etaria_pref`: ordem e dominio [18, 99].

        Validacao em modo `after` permite acesso aos dois elementos da tupla
        ja convertidos para int e comparar entre si — o que field_validator
        sobre tupla nao oferece de forma natural.
        """
        minimo, maximo = self.faixa_etaria_pref
        if not (18 <= minimo <= 99 and 18 <= maximo <= 99):
            raise ValueError(
                "faixa_etaria_pref deve conter dois inteiros entre 18 e 99."
            )
        if minimo > maximo:
            raise ValueError(
                "faixa_etaria_pref deve ter o limite inferior <= limite superior."
            )
        return self
