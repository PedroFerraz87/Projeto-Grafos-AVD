from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def gerar_graficos(
    entrada="out/parte2/dados_comparacao_algoritmos",
    saida="out/parte2/avd/comparacao_algoritmos"
):
    entrada = Path(entrada)
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)

    benchmark = pd.read_csv(
        entrada / "benchmark_resumo.csv"
    )

    caminhos = pd.read_csv(
        entrada / "comparacao_caminhos.csv"
    )

    # Gráfico 1: comparação dos tempos médios
    resumo = (
        benchmark.groupby(["recorte", "algoritmo"])["tempo_medio_ms"]
        .mean()
        .unstack()
    )

    ax = resumo.plot(kind="bar", figsize=(11, 6))
    ax.set_yscale("log")
    ax.set_title("Tempo médio por algoritmo e recorte")
    ax.set_xlabel("Recorte do dataset (%)")
    ax.set_ylabel("Tempo médio (ms) - escala logarítmica")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(saida / "comparacao_tempos_execucao.png", dpi=150)
    plt.close()

    # Gráfico 2: escalabilidade
    resumo_tamanho = (
        benchmark.groupby(
            ["algoritmo", "vertices"], as_index=False
        )["tempo_medio_ms"]
        .mean()
    )

    plt.figure(figsize=(11, 6))

    for algoritmo, grupo in resumo_tamanho.groupby("algoritmo"):
        grupo = grupo.sort_values("vertices")

        plt.plot(
            grupo["vertices"],
            grupo["tempo_medio_ms"],
            marker="o",
            label=algoritmo
        )

    plt.yscale("log")
    plt.title("Escalabilidade dos algoritmos")
    plt.xlabel("Quantidade de vértices")
    plt.ylabel("Tempo médio (ms) - escala logarítmica")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(saida / "escalabilidade_algoritmos.png", dpi=150)
    plt.close()

    # Gráfico 3: comparação de caminhos BFS e Dijkstra
    pares = (
        caminhos["origem"].astype(str)
        + " → "
        + caminhos["destino"].astype(str)
    )

    posicoes = list(range(len(caminhos)))
    largura = 0.35

    plt.figure(figsize=(11, 6))

    plt.bar(
        [p - largura / 2 for p in posicoes],
        caminhos["passos_bfs"],
        width=largura,
        label="BFS"
    )

    plt.bar(
        [p + largura / 2 for p in posicoes],
        caminhos["passos_dijkstra"],
        width=largura,
        label="Dijkstra"
    )

    plt.xticks(posicoes, pares)
    plt.title("Quantidade de arcos nos caminhos")
    plt.xlabel("Origem → Destino")
    plt.ylabel("Quantidade de arcos")
    plt.legend()
    plt.tight_layout()
    plt.savefig(saida / "comparacao_quantidade_arcos.png", dpi=150)
    plt.close()

    # Gráfico 4: custo transformado dos caminhos
    plt.figure(figsize=(11, 6))

    plt.bar(
        [p - largura / 2 for p in posicoes],
        caminhos["custo_transformado_bfs"],
        width=largura,
        label="BFS"
    )

    plt.bar(
        [p + largura / 2 for p in posicoes],
        caminhos["custo_transformado_dijkstra"],
        width=largura,
        label="Dijkstra"
    )

    plt.xticks(posicoes, pares)
    plt.title("Custo transformado dos caminhos")
    plt.xlabel("Origem → Destino")
    plt.ylabel("Custo total (10 - nota)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(saida / "comparacao_custos_caminhos.png", dpi=150)
    plt.close()

    print("Quatro gráficos da T32 gerados em:", saida)


if __name__ == "__main__":
    gerar_graficos()
