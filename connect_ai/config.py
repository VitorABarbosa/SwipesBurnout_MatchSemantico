"""Modulo de configuracao do CONNECT.AI.

Centraliza a leitura de variaveis de ambiente e chaves de API.
Por decisao de projeto (PROJECT.md), credenciais sao lidas exclusivamente
via `.env` ou variaveis de ambiente -- nunca hardcoded.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Erro de configuracao do CONNECT.AI (chave ausente, .env mal formado, etc.)."""


_ENV_CARREGADO = False


def carregar_env() -> None:
    """Carrega o arquivo `.env` da raiz do projeto.

    Idempotente: chamar varias vezes nao reprocessa o arquivo.
    Se o `.env` nao existir, segue silenciosamente — variaveis podem vir
    do ambiente do sistema.
    """
    global _ENV_CARREGADO
    if _ENV_CARREGADO:
        return
    load_dotenv()
    _ENV_CARREGADO = True


def obter_chave_api(nome: str, padrao: Optional[str] = None) -> str:
    """Le uma variavel de ambiente, com mensagem de erro clara em PT-BR.

    Args:
        nome: Nome da variavel de ambiente (ex: "GOOGLE_API_KEY").
        padrao: Valor a retornar se a variavel nao existir. Quando None
            (default) e a variavel estiver ausente, levanta ConfigError.

    Returns:
        O valor da variavel de ambiente, ou `padrao` se fornecido.

    Raises:
        ConfigError: Se a variavel nao existir e `padrao` for None.
    """
    carregar_env()
    valor = os.environ.get(nome)
    if valor is not None and valor != "":
        return valor
    if padrao is not None:
        return padrao
    raise ConfigError(
        f"A variavel de ambiente '{nome}' nao esta definida. "
        f"Configure-a no arquivo .env (copie .env.example para .env e "
        f"preencha o valor) ou exporte-a no terminal antes de executar a aplicacao."
    )


def obter_diretorio_chroma() -> str:
    """Retorna o diretorio de persistencia do ChromaDB.

    Le `CHROMA_PERSIST_DIR` do ambiente; padrao = './chroma_db'.
    """
    return obter_chave_api("CHROMA_PERSIST_DIR", padrao="./chroma_db")


def obter_nome_colecao() -> str:
    """Retorna o nome da colecao do ChromaDB.

    Le `CHROMA_COLLECTION` do ambiente; padrao = 'perfis_connect_ai'.
    """
    return obter_chave_api("CHROMA_COLLECTION", padrao="perfis_connect_ai")
