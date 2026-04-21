"""Pipeline de ingestao de perfis do CONNECT.AI.

Implementa o fluxo completo de ingestao de um Perfil no banco vetorial (ChromaDB),
cobrindo os requisitos ING-01 a ING-04:

  ING-01 — ingerir_perfil executa o fluxo: validacao → Perfilador (IA) →
            embedding (text-embedding-004 ou mock hashlib) → upsert no ChromaDB.
  ING-02 — ingerir_lote processa uma lista de Perfis e retorna contagens de
            sucesso/falha/total.
  ING-03 — Todos os logs emitidos estao em PT-BR e usam o modulo `logging`
            (nunca `print`).
  ING-04 — A ingestao e idempotente: re-ingerir o mesmo perfil nao duplica a
            colecao (garantido pelo upsert do Repositorio).

Uso tipico:
    from connect_ai.ingestao import ingerir_perfil, ingerir_lote
    resultado = ingerir_perfil(perfil, colecao)  # {"sucesso": True, "id": ..., "erro": None}
    totais   = ingerir_lote(perfis, colecao)     # {"sucesso": N, "falha": 0, "total": N}
"""

from __future__ import annotations

import hashlib
import logging
from typing import List

import google.generativeai as genai

from connect_ai.agentes import AgentState, agente_perfilador
from connect_ai.config import obter_chave_api
from connect_ai.repositorio import Repositorio
from connect_ai.schema import Perfil, construir_documento_semantico

# ── Logger do modulo (mensagens sempre em PT-BR — ING-03) ─────────────────────
logger = logging.getLogger(__name__)


# ── Embedding ────────────────────────────────────────────────────────────────


def _gerar_embedding(texto: str) -> list:
    """Gera o vetor de embedding para um texto semantico.

    Estrategia (ING-03 / sem credencial hardcoded):
      1. Le GOOGLE_API_KEY via obter_chave_api com padrao="" — nunca levanta
         ConfigError; permite que o modulo funcione sem credencial.
      2. Se a chave estiver ausente/vazia, retorna embedding deterministico
         baseado em hashlib.md5 (vetor de 768 dimensoes, reproducivel).
      3. Se a chave estiver presente, usa google.generativeai com o modelo
         "models/text-embedding-004" e task_type="RETRIEVAL_DOCUMENT".

    A chave de API nunca e logada (seguranca — ACC-09).

    Args:
        texto: Documento semantico montado por construir_documento_semantico.

    Returns:
        Lista de 768 floats representando o embedding do texto.
    """
    api_key: str = obter_chave_api("GOOGLE_API_KEY", padrao="")

    if not api_key:
        logger.debug("Gerando embedding via mock (GOOGLE_API_KEY ausente).")
        hash_bytes = hashlib.md5(texto.encode("utf-8")).digest()  # 16 bytes
        vetor = [(b / 255.0) for b in hash_bytes] * 48 + [(b / 255.0) for b in hash_bytes[:16]]
        return vetor[:768]  # exatamente 768 dimensoes

    logger.debug("Gerando embedding via API Google.")
    genai.configure(api_key=api_key)
    resultado = genai.embed_content(
        model="models/text-embedding-004",
        content=texto,
        task_type="RETRIEVAL_DOCUMENT",
    )
    return resultado["embedding"]


# ── Pipeline individual ───────────────────────────────────────────────────────


def ingerir_perfil(perfil: Perfil, colecao: Repositorio) -> dict:
    """Ingere um unico Perfil no banco vetorial (fluxo ING-01).

    Fluxo:
      1. Loga inicio da ingestao (ING-03).
      2. Chama agente_perfilador para preencher personalidade_ia no Perfil.
      3. Constroi o documento semantico via construir_documento_semantico.
      4. Gera o embedding via _gerar_embedding (API Google ou mock).
      5. Persiste o perfil processado na colecao via colecao.inserir (upsert).
      6. Loga conclusao e retorna resultado.

    Args:
        perfil: Instancia valida de Perfil a ser ingerida.
        colecao: Repositorio (wrapper ChromaDB) onde o perfil sera armazenado.

    Returns:
        Dict com:
          - "sucesso" (bool): True se ingestao bem-sucedida.
          - "id" (str): ID do perfil processado.
          - "erro" (str | None): Mensagem de erro se falha, None se sucesso.
    """
    try:
        logger.info("Ingerindo perfil id=%s nome=%s", perfil.id, perfil.nome)

        # Passo 1: enriquecer o Perfil com personalidade_ia via Perfilador
        state_inicial: AgentState = {
            "perfil": perfil,
            "candidatos": [],
            "matches": [],
            "justificativas": {},
            "erro": None,
        }
        state_saida = agente_perfilador(state_inicial)
        perfil_processado: Perfil = state_saida["perfil"]

        # Passo 2: montar documento semantico
        texto = construir_documento_semantico(perfil_processado)

        # Passo 3: gerar embedding
        embedding = _gerar_embedding(texto)

        # Passo 4: persistir (upsert idempotente — ING-04)
        colecao.inserir(perfil_processado, embedding)

        logger.info("Perfil id=%s ingerido com sucesso.", perfil_processado.id)
        return {"sucesso": True, "id": perfil_processado.id, "erro": None}

    except Exception as e:  # noqa: BLE001
        logger.error("Falha ao ingerir perfil id=%s: %s", perfil.id, str(e))
        return {"sucesso": False, "id": perfil.id, "erro": str(e)}


# ── Pipeline em lote ──────────────────────────────────────────────────────────


def ingerir_lote(perfis: List[Perfil], colecao: Repositorio) -> dict:
    """Ingere uma lista de Perfis no banco vetorial (fluxo ING-02).

    Processa cada Perfil individualmente via ingerir_perfil, acumulando
    contagens de sucesso e falha. Nao interrompe o lote em caso de falha
    individual — garante que todos os perfis da lista sejam tentados.

    Args:
        perfis: Lista de instancias validas de Perfil.
        colecao: Repositorio (wrapper ChromaDB) onde os perfis serao armazenados.

    Returns:
        Dict com:
          - "sucesso" (int): Quantidade de perfis ingeridos com sucesso.
          - "falha" (int): Quantidade de perfis com erro.
          - "total" (int): Quantidade total de perfis na lista (sucesso + falha).
    """
    logger.info("Iniciando ingestao de lote com %d perfis.", len(perfis))

    sucesso = 0
    falha = 0

    for perfil in perfis:
        resultado = ingerir_perfil(perfil, colecao)
        if resultado["sucesso"]:
            sucesso += 1
        else:
            falha += 1

    logger.info(
        "Lote concluido: %d sucesso, %d falha, %d total.",
        sucesso,
        falha,
        len(perfis),
    )
    return {"sucesso": sucesso, "falha": falha, "total": len(perfis)}
