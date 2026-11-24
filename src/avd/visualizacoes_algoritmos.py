# [IA] OpenAI Codex – semelhança por cor e marcador, agrupamento por caso e rótulos diretos.
from pathlib import Path

import pandas as pd
from matplotlib.ticker import FuncFormatter, NullLocator

from .estilo_graficos import ALGORITMOS, TINTA, formatar_eixo, numero, prancha, salvar

FONTE_TEMPOS = "Fonte: benchmark do grupo (T26) · cinco execuções por fonte"
FONTE_CAMINHOS = "Fonte: experimentos da T25 · grafo completo do Bitcoin Alpha"


def tempo_log(ax):
    ax.set_yscale("log")
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: numero(v, 1 if v < 1 else 0)))


def comparacao_tempos(benchmark, destino):
    grupos = benchmark.groupby(["recorte", "algoritmo"])["tempo_medio_ms"].mean().unstack()
    fig, ax = prancha("Tempo médio por algoritmo", "Em cada recorte, os quatro marcadores comparam as médias das três fontes.",
                      "Recorte temporal", "Tempo médio (ms) · escala log")
    centros = list(range(len(grupos.index)))
    disponiveis = [(id_alg, estilo) for id_alg, estilo in ALGORITMOS.items() if id_alg in grupos]
    for i, (id_alg, (nome, cor, marcador)) in enumerate(disponiveis):
        deslocamento = (i - (len(disponiveis) - 1)/2)*.145
        ax.scatter([x + deslocamento for x in centros], grupos[id_alg], label=nome,
                   color=cor, marker=marcador, s=74, edgecolors="white", linewidths=.75, zorder=3)
    for limite in range(len(centros)-1):
        ax.axvline(limite+.5, linewidth=.8, color="#d6dce2")
    ax.set(xlim=(-.45, len(centros)-.55), xticks=centros)
    ax.set_xticklabels([f"{recorte}%" for recorte in grupos.index])
    tempo_log(ax)
    ax.legend(loc="upper left", frameon=False, ncol=4, bbox_to_anchor=(0, .999),
              markerscale=.8, labelcolor=TINTA, fontsize=9)
    ax.set_ylim(top=grupos.max().max()*5)
    salvar(fig, destino, FONTE_TEMPOS, "As fontes variam entre recortes")


def escalabilidade(benchmark, destino):
    resumo = benchmark.groupby(["algoritmo", "vertices"], as_index=False)["tempo_medio_ms"].mean()
    tamanhos = benchmark[["vertices", "arcos"]].drop_duplicates().sort_values("vertices")
    fig, ax = prancha("Escalabilidade dos algoritmos", "Cada linha acompanha um algoritmo nos três tamanhos medidos.",
                      "Tamanho do grafo (usuários / avaliações)", "Tempo médio (ms) · escala log")
    for id_alg, (nome, cor, marcador) in ALGORITMOS.items():
        grupo = resumo[resumo["algoritmo"] == id_alg].sort_values("vertices")
        if grupo.empty:
            continue
        ax.plot(grupo["vertices"], grupo["tempo_medio_ms"], color=cor,
                marker=marcador, markersize=6.3, linewidth=2)
        ultima = grupo.iloc[-1]
        ax.annotate(nome, (ultima["vertices"], ultima["tempo_medio_ms"]), xytext=(8, 0),
                    textcoords="offset points", color=cor, va="center", weight="bold", size=10)
    ax.set_xticks(tamanhos["vertices"])
    ax.set_xticklabels([f"{numero(v)} / {numero(e)}" for v, e in tamanhos.itertuples(index=False, name=None)])
    amplitude = tamanhos["vertices"].max() - tamanhos["vertices"].min()
    ax.set_xlim(tamanhos["vertices"].min()-amplitude*.08, tamanhos["vertices"].max()+amplitude*.26)
    tempo_log(ax)
    salvar(fig, destino, FONTE_TEMPOS, "Três tamanhos observados")


def comparar_caminhos(caminhos, titulo, descricao, eixo_x, colunas, destino):
    pares = caminhos["origem"].astype(str) + " → " + caminhos["destino"].astype(str)
    fig, ax = prancha(titulo, descricao, eixo_x, grade="x", esquerda=.17)
    indices = list(range(len(pares)))
    for deslocamento, id_alg, coluna in zip([-.175,.175], ["BFS","DIJKSTRA"], colunas):
        nome, cor, _ = ALGORITMOS[id_alg]
        barras = ax.barh([i + deslocamento for i in indices], caminhos[coluna],
                         height=.29, color=cor, label=nome)
        ax.bar_label(barras, labels=[numero(v) for v in caminhos[coluna]], color=cor, weight="bold", padding=5)
    ax.set_yticks(indices, pares)
    ax.set_xlim(0, caminhos[list(colunas)].max().max()*1.24)
    ax.invert_yaxis()
    formatar_eixo(ax.xaxis)
    fig.legend(loc="upper right", bbox_to_anchor=(.956,.8), frameon=False, ncol=2, labelcolor=TINTA)
    salvar(fig, destino, FONTE_CAMINHOS, "Cada grupo: origem → destino")


def gerar_graficos(entrada="out/parte2/dados_comparacao_algoritmos",
                   saida="out/parte2/avd/comparacao_algoritmos"):
    entrada, saida = Path(entrada), Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    benchmark = pd.read_csv(entrada / "benchmark_resumo.csv")
    caminhos = pd.read_csv(entrada / "comparacao_caminhos.csv")
    comparacao_tempos(benchmark, saida / "comparacao_tempos_execucao.png")
    escalabilidade(benchmark, saida / "escalabilidade_algoritmos.png")
    comparar_caminhos(caminhos, "Quantidade de arcos nos caminhos", "Compare o número de avaliações nas duas rotas de cada par.",
                      "Arcos percorridos", ("passos_bfs", "passos_dijkstra"), saida / "comparacao_quantidade_arcos.png")
    comparar_caminhos(caminhos, "Custo dos caminhos por par", "A transformação é aplicada também à rota escolhida pela BFS.",
                      "Custo total (10 − nota por arco)", ("custo_transformado_bfs", "custo_transformado_dijkstra"),
                      saida / "comparacao_custos_caminhos.png")
    print("Quatro gráficos da T32 gerados em:", saida)


if __name__ == "__main__":
    gerar_graficos()
