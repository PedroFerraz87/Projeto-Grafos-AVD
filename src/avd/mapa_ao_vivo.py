# [IA] OpenAI Codex – adaptação das saídas dos algoritmos para mapas enviados ao painel.
"""Analisa um arquivo temporário com os mesmos solvers usados pela CLI."""

import json
import sys
from pathlib import Path

from ..exploracao import dados_exploracao
from ..graphs.io import MapaInvalido
from ..solve import analisar, dados_interativos


def analisar_envio(caminho):
    analise = analisar(caminho)
    analise["nome"] = "mapa_enviado"
    return {
        "interativo": dados_interativos([analise], "mapa_enviado"),
        "exploracao": dados_exploracao([analise], "mapa_enviado"),
    }


if __name__ == "__main__":
    caminho = Path(sys.argv[1])
    try:
        dados = analisar_envio(caminho)
    except MapaInvalido as erro:
        dados = {"erro": str(erro).removeprefix(f"{caminho}: ")}
    except UnicodeDecodeError:
        dados = {"erro": "Salve o mapa como texto em UTF-8."}
    sys.stdout.buffer.write(json.dumps(dados, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
