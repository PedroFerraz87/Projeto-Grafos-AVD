import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .graphs.algorithms import bfs
from .graphs.metricas import decompor_rotulo
from .solve import analisar, montar_percurso

MODELO = Path(__file__).resolve().parent / "templates" / "labirinto_interativo.html"
MARCADOR = "__DADOS__"

CORES_CAMADAS = {"-": "#b8c5d1", "a": "#4c78a8", "ab": "#f2cf5b",
                 "abc": "#59a14f", "d": "#af7aa1", "ad": "#ff9da6"}


def gerar_percurso_png(analise, caminho_saida, algoritmo=None):
    algoritmo = algoritmo or ("DIJKSTRA" if "DIJKSTRA" in analise["execucoes"] else "BFS")
    percurso = montar_percurso(analise, algoritmo)
    grade = analise["grade"]

    fig, eixo = plt.subplots(figsize=(max(8, len(grade[0]) * 0.42), max(5, len(grade) * 0.42)))
    eixo.set_facecolor("#171a21")

    for linha, texto in enumerate(grade):
        for coluna, simbolo in enumerate(texto):
            cor = "#171a21" if simbolo == "#" else "#f1f3f5"
            eixo.add_patch(plt.Rectangle((coluna - 0.5, -linha - 0.5), 1, 1,
                                         facecolor=cor, edgecolor="#2f3542", linewidth=0.25))

    estados = percurso["percurso"]
    if estados:
        linhas = [item["linha"] for item in estados]
        colunas = [item["coluna"] for item in estados]
        eixo.plot(colunas, [-l for l in linhas], color="#e45756", linewidth=2.2,
                  markersize=3.8, marker="o", markerfacecolor="#ffd166", zorder=3)
        eixo.scatter([colunas[0]], [-linhas[0]], s=80, color="#4daf4a", zorder=4, label="S")
        eixo.scatter([colunas[-1]], [-linhas[-1]], s=80, color="#984ea3", zorder=4, label="ALVO")

    eixo.set_xlim(-0.7, len(grade[0]) - 0.3)
    eixo.set_ylim(-len(grade) + 0.3, 0.7)
    eixo.set_aspect("equal")
    eixo.axis("off")
    eixo.set_title(f"{analise['nome']} — percurso {algoritmo} "
                   f"(passos: {percurso['passos']}, custo: {percurso['custo']})")
    eixo.legend(loc="upper right")

    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return caminho_saida


def gerar_arvore_bfs_png(analise, caminho_saida):
    resultado = bfs(analise["g"], analise["inicio"])
    pais = resultado.pais()

    posicoes = {}
    pais_rotulo = {}
    visitados = set(resultado.distancias)
    for estado in visitados:
        if estado == "ALVO":
            continue
        l, c, chaves, _ = decompor_rotulo(estado)
        posicoes[estado] = (c + (0.18 if chaves != "-" else 0), -l)
        if estado in pais:
            pais_rotulo[estado] = pais[estado]

    fig, eixo = plt.subplots(figsize=(12, 7))
    eixo.set_facecolor("#f7f8fa")

    for filho, pai in pais_rotulo.items():
        if pai in posicoes and pai != "ALVO" and filho != "ALVO":
            x1, y1 = posicoes[pai]
            x2, y2 = posicoes[filho]
            eixo.plot([x1, x2], [y1, y2], color="#aab2bd", linewidth=0.7, zorder=1)

    for estado, (x, y) in posicoes.items():
        chaves = estado.split("|")[1] if "|" in estado else "-"
        cor = CORES_CAMADAS.get(chaves, "#d62728")
        eixo.scatter([x], [y], s=28, color=cor, edgecolor="#555", linewidth=0.35, zorder=2)

    eixo.scatter([], [], s=28, color=CORES_CAMADAS["-"], label="camada sem chaves")
    eixo.scatter([], [], s=28, color=CORES_CAMADAS["a"], label="camada a")
    eixo.set_aspect("equal")
    eixo.set_title(f"Árvore BFS — {analise['nome']} ({len(posicoes)} estados)")
    eixo.axis("off")
    eixo.legend(loc="lower left")

    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(caminho_saida, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return caminho_saida


def gerar_figuras_t28(raiz, pasta_saida):
    raiz, pasta_saida = Path(raiz), Path(pasta_saida)
    gerados = []
    for nome, algoritmo in (("m03_tres_chaves", "DIJKSTRA"), ("m08_grande", "DIJKSTRA")):
        caminho = raiz / "data" / "mapas" / f"{nome}.txt"
        gerados.append(gerar_percurso_png(analisar(caminho), pasta_saida / f"percurso_{nome[:3]}.png", algoritmo))
    gerados.append(gerar_arvore_bfs_png(analisar(raiz / "data" / "mapas" / "m02_uma_chave.txt"),
                                        pasta_saida / "arvore_bfs_m02.png"))
    return gerados


def gerar_labirinto_interativo(dados, caminho_saida):
    html = MODELO.read_text(encoding="utf-8")
    if html.count(MARCADOR) != 1:
        raise ValueError(f"o modelo {MODELO.name} deve ter exatamente um marcador {MARCADOR}")
    for marcador, nome in (("__MESA_ROTAS_HTML__", "mesa_rotas.html"), ("__MESA_ROTAS_JS__", "mesa_rotas.js")):
        if marcador in html:
            html = html.replace(marcador, MODELO.with_name(nome).read_text(encoding="utf-8"))
    return _gravar_html(html, dados, caminho_saida)


# [IA] OpenAI Codex – exportação da página de exploração com dados locais.
def gerar_pagina_algoritmos(dados, caminho_saida):
    modelo = MODELO.with_name("algoritmos_em_acao.html")
    return _gravar_html(modelo.read_text(encoding="utf-8"), dados, caminho_saida)


def _gravar_html(html, dados, caminho_saida):
    texto = json.dumps(dados, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(html.replace(MARCADOR, texto))
    return caminho_saida
