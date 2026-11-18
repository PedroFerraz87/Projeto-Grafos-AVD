#T26 - Victor

import csv
import time
from pathlib import Path

from .graphs.io import ler_dataset
from .graphs.algorithms import bfs, dfs, dijkstra, bellman_ford
from .parte2 import grafo_dijkstra


def executar_benchmark(caminho, saida="out/parte2/benchmark.csv"):
    resultados = []

    for recorte in (10, 50, 100):
        grafo = ler_dataset(caminho, recorte)
        grafo_positivo = grafo_dijkstra(grafo)

        vertices = len(grafo)
        arcos = sum(1 for arco in grafo.arcos())

        fontes = sorted(
            grafo.vertices(),
            key=lambda v: (-len(grafo.arcos_saindo(v)), v)
        )[:3]

        algoritmos = [
            ("BFS", bfs, grafo),
            ("DFS", dfs, grafo),
            ("DIJKSTRA", dijkstra, grafo_positivo),
            ("BELLMAN_FORD", bellman_ford, grafo)
        ]

        for nome, algoritmo, grafo_usado in algoritmos:
            for fonte in fontes:
                for execucao in range(1, 6):
                    inicio = time.perf_counter()

                    algoritmo(grafo_usado, fonte)

                    fim = time.perf_counter()
                    tempo_ms = (fim - inicio) * 1000

                    resultados.append({
                        "algoritmo": nome,
                        "recorte": recorte,
                        "vertices": vertices,
                        "arcos": arcos,
                        "execucao": execucao,
                        "fonte": fonte,
                        "tempo_ms": tempo_ms
                    })

                    print(
                        nome,
                        recorte,
                        fonte,
                        execucao,
                        round(tempo_ms, 3),
                        "ms"
                    )

    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)

    colunas = [
        "algoritmo", "recorte", "vertices", "arcos",
        "execucao", "fonte", "tempo_ms"
    ]

    with open(saida, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(resultados)

    return resultados


if __name__ == "__main__":
    executar_benchmark(
        "data/dataset_parte2/soc-sign-bitcoinalpha.csv"
    )
