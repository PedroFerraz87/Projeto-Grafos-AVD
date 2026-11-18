# [IA] OpenAI Codex - apoio à organização das tabelas para a T32.
"""Organiza as saídas da Parte 2 para a comparação visual de algoritmos."""

import argparse
import json
from math import isfinite
from pathlib import Path

import pandas as pd


COLUNAS_BENCHMARK = (
    "algoritmo", "recorte", "vertices", "arcos", "execucao", "fonte", "tempo_ms",
)
ALGORITMOS = {"BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"}
COMPARACAO = {
    "origem", "destino", "recorte", "passos_bfs", "passos_dijkstra", "caminho_bfs",
    "caminho_dijkstra", "custo_transformado_bfs", "custo_transformado_dijkstra",
}


def _ler_benchmark(caminho):
    execucoes = pd.read_csv(caminho)
    faltantes = set(COLUNAS_BENCHMARK) - set(execucoes.columns)
    if faltantes:
        raise ValueError(f"Colunas ausentes no benchmark: {', '.join(sorted(faltantes))}")
    if execucoes.empty:
        raise ValueError("O benchmark não contém execuções.")

    execucoes = execucoes.loc[:, list(COLUNAS_BENCHMARK)].copy()
    for coluna in COLUNAS_BENCHMARK[1:]:
        valores = pd.to_numeric(execucoes[coluna], errors="coerce")
        if not valores.map(isfinite).all():
            raise ValueError(f"O benchmark exige números finitos em {coluna}.")
        if coluna != "tempo_ms" and not (valores % 1 == 0).all():
            raise ValueError(f"O benchmark exige inteiros em {coluna}.")
        execucoes[coluna] = valores
    if not execucoes["algoritmo"].isin(ALGORITMOS).all():
        raise ValueError("O benchmark contém um algoritmo desconhecido.")
    if not execucoes["recorte"].isin({10, 50, 100}).all():
        raise ValueError("Os recortes do benchmark devem ser 10, 50 ou 100.")
    if (execucoes[["tempo_ms", "vertices", "arcos"]] < 0).any().any() or not execucoes["execucao"].gt(0).all():
        raise ValueError("O benchmark contém tempo, tamanho ou número de execução inválido.")
    if (execucoes.groupby("recorte")[["vertices", "arcos"]].nunique() > 1).any().any():
        raise ValueError("Um mesmo recorte tem tamanhos de grafo diferentes no benchmark.")
    if execucoes.duplicated(["algoritmo", "recorte", "fonte", "execucao"]).any():
        raise ValueError("O benchmark contém execuções duplicadas para a mesma fonte.")
    return execucoes


def ler_tabelas(relatorio, benchmark=None):
    """Retorna DataFrames com caminhos, casos e, quando fornecidos, tempos medidos.

    O resumo mede a média e o desvio padrão amostral das execuções do CSV.
    Resultados de fontes diferentes permanecem em linhas separadas.
    """
    with Path(relatorio).open(encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    tabelas = {}
    for secao in ("bfs", "dfs", "dijkstra", "bellman_ford"):
        if not isinstance(dados.get(secao), list):
            raise ValueError(f"O relatório deve conter a lista {secao}.")
        tabelas[secao] = pd.DataFrame(dados[secao])

    if "comparacao_caminhos" in dados:
        comparacao = pd.DataFrame(dados["comparacao_caminhos"])
        if COMPARACAO - set(comparacao.columns):
            raise ValueError("A comparação de caminhos precisa identificar o par e usar o mesmo peso transformado.")
        tabelas["comparacao_caminhos"] = comparacao

    if benchmark is not None:
        execucoes = _ler_benchmark(benchmark)
        tabelas["benchmark_execucoes"] = execucoes
        tabelas["benchmark_resumo"] = execucoes.groupby(
            ["algoritmo", "recorte", "vertices", "arcos", "fonte"], as_index=False,
        ).agg(
            execucoes=("tempo_ms", "size"),
            tempo_medio_ms=("tempo_ms", "mean"),
            tempo_desvio_ms=("tempo_ms", "std"),
        )
    return tabelas


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepara os dados das tabelas para a T32.")
    parser.add_argument("--relatorio", type=Path, default=Path("out/parte2/parte2_report.json"))
    parser.add_argument("--benchmark", type=Path, help="CSV de execuções medidas na T26.")
    parser.add_argument("--out", type=Path, required=True, help="Pasta para as tabelas de comparação.")
    args = parser.parse_args(argv)

    try:
        tabelas = ler_tabelas(args.relatorio, args.benchmark)
        args.out.mkdir(parents=True, exist_ok=True)
        for nome, tabela in tabelas.items():
            tabela = tabela.apply(
                lambda coluna: coluna.map(
                    lambda valor: json.dumps(valor, ensure_ascii=False) if isinstance(valor, (dict, list)) else valor
                )
            )
            caminho = args.out / f"{nome}.csv"
            tabela.to_csv(caminho, index=False, lineterminator="\n")
            print(caminho)
    except (ValueError, OSError) as erro:
        parser.error(str(erro))


if __name__ == "__main__":
    main()
