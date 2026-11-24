import argparse
from pathlib import Path

from .graphs.io import MapaInvalido
from .solve import TODOS, analisar, caminho_mapa, dados_interativos, gerar_saidas, listar_mapas

RAIZ = Path(__file__).resolve().parents[1]


def criar_parser():
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Resolve os mapas do labirinto no grafo de estados e gera os arquivos de out/parte1.")
    parser.add_argument("--mapa", help="mapa a resolver: caminho do .txt ou nome (m03, m03_tres_chaves). "
                                       "Sem --mapa, resolve todos os mapas; com --mapa, solucoes.csv e "
                                       "dfs_classificacao.csv trazem só esse mapa")
    parser.add_argument("--alg", type=str.upper, choices=TODOS,
                        help="algoritmo (padrão: todos). A DFS só gera dfs_classificacao.csv")
    parser.add_argument("--out", default="out/parte1", help="pasta de saída (padrão: out/parte1)")
    parser.add_argument("--armadilhas", action="store_true",
                        help="gera armadilhas_<mapa>.csv de todos os mapas (os do m04 e do m07 saem sempre)")
    parser.add_argument("--fonte-consumivel", action="store_true",
                        help="calcula a correção do m06 (a fonte * vale -2 só na primeira vez) e a registra em "
                             "ciclo_negativo_m06.json; as demais saídas não mudam")
    parser.add_argument("--interactive", action="store_true",
                        help="gera labirinto_interativo.html em --out, com todos os mapas; --mapa vira o mapa inicial")
    parser.add_argument(
        "--dataset",
        type=Path,
        help="Caminho do arquivo CSV do Bitcoin Alpha."
    )

    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Executa o benchmark da Parte 2."
    )
    
    return parser


def main(argv=None):
    parser = criar_parser()
    args = parser.parse_args(argv)

    # [IA] Executa a T26 quando --benchmark for informado.
    if args.benchmark:
        if args.mapa or args.alg or args.interactive:
            parser.error(
                "--benchmark não pode ser combinado com opções de mapas."
            )

        from .benchmark import executar_benchmark

        dataset = args.dataset or (
            RAIZ / "data/dataset_parte2/soc-sign-bitcoinalpha.csv"
        )

        pasta_saida = Path(args.out)

        if pasta_saida == Path("out/parte1"):
            pasta_saida = Path("out/parte2")

        arquivo_saida = pasta_saida / "benchmark.csv"

        try:
            executar_benchmark(dataset, arquivo_saida)
        except (OSError, ValueError) as erro:
            parser.error(str(erro))

        print(f"Benchmark salvo em: {arquivo_saida}")
        return 0

    if args.dataset:
        parser.error("--dataset deve ser usado com --benchmark.")

    out = Path(args.out)
    algoritmos = [args.alg] if args.alg else TODOS

    if args.interactive:
        from . import viz
        if not hasattr(viz, "gerar_labirinto_interativo"):
            parser.exit(1, "erro: src/viz.py ainda não tem gerar_labirinto_interativo(dados, caminho_saida) (T31)\n")

    try:
        selecionado = caminho_mapa(RAIZ, args.mapa) if args.mapa else None
    except ValueError as erro:
        parser.error(str(erro))

    caminhos = listar_mapas(RAIZ) if (selecionado is None or args.interactive) else [selecionado]
    if selecionado and selecionado not in caminhos:
        caminhos.append(selecionado)
    analises = {}
    for c in caminhos:
        try:
            analises[c] = analisar(c, args.fonte_consumivel)
        except MapaInvalido as erro:
            causa = str(erro).removeprefix(f"{c}: ")  # a mensagem do io.py começa pelo caminho do arquivo
            parser.exit(1, f"erro: mapa {c.stem} inválido: {causa}\n")
        # [IA] OpenAI Codex – tratamento de falhas de leitura na interface da CLI.
        except UnicodeDecodeError:
            parser.exit(1, f"erro: mapa {c.stem} inválido: o arquivo precisa estar em UTF-8\n")
        except OSError as erro:
            parser.exit(1, f"erro: não foi possível ler o mapa {c.stem}: {erro.strerror or str(erro)}\n")
    escolhidas = [analises[selecionado]] if selecionado else list(analises.values())

    out.mkdir(parents=True, exist_ok=True)
    escritos = gerar_saidas(escolhidas, out, algoritmos, args.armadilhas)

    if args.interactive:
        inicial =analises[selecionado]["nome"] if selecionado else escolhidas[0]["nome"]
        viz.gerar_labirinto_interativo(dados_interativos(list(analises.values()), inicial),
                                       out / "labirinto_interativo.html")
        escritos.append(out / "labirinto_interativo.html")

    for arquivo in escritos:
        print(arquivo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
