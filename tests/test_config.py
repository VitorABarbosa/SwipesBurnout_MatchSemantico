"""Testes do modulo de configuracao do CONNECT.AI."""

import pytest

from connect_ai.config import (
    ConfigError,
    carregar_env,
    obter_chave_api,
    obter_diretorio_chroma,
    obter_nome_colecao,
)


def test_obter_chave_api_retorna_valor_quando_definida(monkeypatch):
    """Quando a variavel esta definida, deve retornar o valor."""
    monkeypatch.setenv("GOOGLE_API_KEY", "chave-fake-123")
    assert obter_chave_api("GOOGLE_API_KEY") == "chave-fake-123"


def test_obter_chave_api_levanta_erro_ptbr_quando_ausente(monkeypatch):
    """Quando a variavel esta ausente e nao ha padrao, deve levantar ConfigError em PT-BR."""
    monkeypatch.delenv("VAR_QUE_NAO_EXISTE", raising=False)
    with pytest.raises(ConfigError) as exc:
        obter_chave_api("VAR_QUE_NAO_EXISTE")
    mensagem = str(exc.value)
    # Mensagem deve estar em PT-BR e citar a variavel ausente
    assert "VAR_QUE_NAO_EXISTE" in mensagem
    assert ".env" in mensagem
    # Deve conter ao menos uma palavra inequivocamente PT-BR
    assert any(t in mensagem.lower() for t in ["nao", "configur", "ausente", "definida", "faltando"])


def test_obter_chave_api_aceita_padrao(monkeypatch):
    """Quando a variavel esta ausente mas ha padrao, deve retornar o padrao."""
    monkeypatch.delenv("VAR_OPCIONAL", raising=False)
    assert obter_chave_api("VAR_OPCIONAL", padrao="fallback") == "fallback"


def test_carregar_env_e_idempotente(tmp_path, monkeypatch):
    """Chamar carregar_env() varias vezes nao deve levantar erro."""
    # Nao deve levantar erro mesmo sem .env presente, nem ao chamar 2x
    monkeypatch.chdir(tmp_path)
    carregar_env()
    carregar_env()


def test_obter_diretorio_chroma_padrao(monkeypatch):
    """Sem CHROMA_PERSIST_DIR no ambiente, deve retornar o padrao './chroma_db'."""
    monkeypatch.delenv("CHROMA_PERSIST_DIR", raising=False)
    assert obter_diretorio_chroma() == "./chroma_db"


def test_obter_diretorio_chroma_customizado(monkeypatch):
    """Com CHROMA_PERSIST_DIR no ambiente, deve retornar o valor customizado."""
    monkeypatch.setenv("CHROMA_PERSIST_DIR", "/tmp/meu_chroma")
    assert obter_diretorio_chroma() == "/tmp/meu_chroma"


def test_obter_nome_colecao_padrao(monkeypatch):
    """Sem CHROMA_COLLECTION no ambiente, deve retornar o padrao 'perfis_connect_ai'."""
    monkeypatch.delenv("CHROMA_COLLECTION", raising=False)
    assert obter_nome_colecao() == "perfis_connect_ai"


def test_config_error_e_runtime_error():
    """ConfigError deve ser uma subclasse de RuntimeError."""
    assert issubclass(ConfigError, RuntimeError)
