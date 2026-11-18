# [IA] Claude (Anthropic)
import json
from pathlib import Path

MODELO = Path(__file__).resolve().parent / "templates" / "labirinto_interativo.html"
MARCADOR = "__DADOS__"


def gerar_labirinto_interativo(dados, caminho_saida):
    """Grava o HTML autocontido: o modelo com o dicionário `dados` embutido (docs/contratos.md, seção 3.13)."""
    html = MODELO.read_text(encoding="utf-8")
    if html.count(MARCADOR) != 1:
        raise ValueError(f"o modelo {MODELO.name} deve ter exatamente um marcador {MARCADOR}")
    # "</" vira "<\/" para um texto do dicionário nunca fechar a tag <script>
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(html.replace(MARCADOR, texto))
    return caminho_saida
