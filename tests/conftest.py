"""Configuração compartilhada do pytest para o projeto CONNECT.AI."""

import sys
from pathlib import Path

# Garante que o pacote `connect_ai` é importável durante os testes,
# mesmo antes do `pip install -e .`.
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
