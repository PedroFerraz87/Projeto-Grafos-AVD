# [IA] GitHub Copilot no VS Code - testes dos geradores de figuras da T28.
# Testes do labirinto interativo (viz.py e do modelo HTML).
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import src.viz as viz
from src import cli
from src.solve import analisar, dados_interativos

RAIZ = Path(__file__).parent.parent
MAPAS = RAIZ / "data" / "mapas"


@pytest.fixture(scope="module")
def dados():
    analises = [analisar(MAPAS / nome) for nome in ("m02_uma_chave.txt", "m06_fonte.txt", "m07_impossivel.txt")]
    return dados_interativos(analises, "m02_uma_chave")


def dados_embutidos(html):
    achou = re.search(r'<script id="dados" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(achou.group(1))


def test_gera_o_html_com_os_dados_embutidos(dados, tmp_path):
    saida = tmp_path / "pasta" / "labirinto_interativo.html"
    assert viz.gerar_labirinto_interativo(dados, saida) == saida
    html = saida.read_text(encoding="utf-8")
    assert viz.MARCADOR not in html and "\r" not in html
    assert dados_embutidos(html) == dados  # o que entrou é o que o navegador lê


def test_texto_com_fim_de_script_nao_quebra_a_pagina(tmp_path):
    perigoso = {"mapa_inicial": "x</script><b>", "algoritmos": [], "mapas": {}}
    viz.gerar_labirinto_interativo(perigoso, tmp_path / "a.html")
    html = (tmp_path / "a.html").read_text(encoding="utf-8")
    assert dados_embutidos(html) == perigoso
    assert html.count("</script>") == viz.MODELO.read_text(encoding="utf-8").count("</script>")


def test_modelo_precisa_de_exatamente_um_marcador(tmp_path, monkeypatch):
    for texto in ("<html></html>", f"{viz.MARCADOR}{viz.MARCADOR}"):
        modelo = tmp_path / "modelo.html"
        modelo.write_text(texto, encoding="utf-8")
        monkeypatch.setattr(viz, "MODELO", modelo)
        with pytest.raises(ValueError, match="marcador"):
            viz.gerar_labirinto_interativo({}, tmp_path / "saida.html")


def test_o_modelo_tem_um_marcador():
    assert viz.MODELO.read_text(encoding="utf-8").count(viz.MARCADOR) == 1


def test_html_tem_os_controles_do_enunciado(dados, tmp_path):
    viz.gerar_labirinto_interativo(dados, tmp_path / "a.html")
    html = (tmp_path / "a.html").read_text(encoding="utf-8")
    ids = {
        "mapa": "seleção de mapa", "algoritmo": "seleção de algoritmo",
        "tocar": "animação", "proximo": "avanço manual", "anterior": "avanço manual", "reiniciar": "reinício",
        "velocidade": "controle de velocidade", "linha-do-tempo": "salto para um passo", "selo": "status do algoritmo",
        "tema": "tema claro/escuro",
        "i-posicao": "posição", "i-chaves": "chaves", "i-bonus": "bônus consumidos", "i-custo": "custo acumulado",
        "i-camada": "camada", "ver-armadilhas": "realce das armadilhas", "ver-trocas": "realce da troca de camada",
    }
    for identificador, para_que in ids.items():
        assert f'id="{identificador}"' in html, para_que


def test_html_e_autocontido(dados, tmp_path):
    viz.gerar_labirinto_interativo(dados, tmp_path / "a.html")
    html = (tmp_path / "a.html").read_text(encoding="utf-8")
    assert not re.search(r'(src|href)="https?:', html) and "@import" not in html and "<script src" not in html


@pytest.mark.skipif(shutil.which("node") is None, reason="node não instalado")
def test_javascript_do_modelo_tem_sintaxe_valida(tmp_path):
    scripts = re.findall(r"<script>(.*?)</script>", viz.MODELO.read_text(encoding="utf-8"), re.S)
    assert len(scripts) == 1
    arquivo = tmp_path / "modelo.js"
    arquivo.write_text(scripts[0], encoding="utf-8")
    resultado = subprocess.run(["node", "--check", str(arquivo)], capture_output=True, text=True)
    assert resultado.returncode == 0, resultado.stderr


def test_cli_interactive_gera_o_html_de_verdade(tmp_path):
    # o comando do enunciado, sem substituir o viz
    assert cli.main(["--mapa", "./data/mapas/m03_tres_chaves.txt", "--interactive", "--out", str(tmp_path) + "/"]) == 0
    html = (tmp_path / "labirinto_interativo.html").read_text(encoding="utf-8")
    embutido = dados_embutidos(html)
    assert embutido["mapa_inicial"] == "m03_tres_chaves"
    assert {m.stem for m in MAPAS.glob("m0*.txt")} | {"m1", "m2"} <= set(embutido["mapas"])  # fornecidos e do grupo
    assert embutido["mapas"]["m03_tres_chaves"]["percursos"]["DIJKSTRA"]["passos"] == 91
    assert embutido["mapas"]["m1"]["percursos"]["BELLMAN_FORD"]["custo"] == 42
    assert len(embutido["mapas"]["m2"]["armadilhas"]) == 6


def test_geradores_de_figuras_t28(tmp_path):
    gerados = viz.gerar_figuras_t28(RAIZ, tmp_path)
    assert [p.name for p in gerados] == [
        "percurso_m03.png",
        "percurso_m08.png",
        "arvore_bfs_m02.png",
    ]
    for caminho in gerados:
        assert caminho.exists()
        assert caminho.read_bytes().startswith(b"\x89PNG")
