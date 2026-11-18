# [IA] OpenAI Codex - orquestração e registro dos casos da T25.
"""Executa os casos da Parte 2 usando o leitor e os algoritmos do projeto."""

import argparse
import json
from collections import Counter
from pathlib import Path

from .graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from .graphs.graph import Graph
from .graphs.io import ler_dataset


def custo_dijkstra(nota):
    if not -10 <= nota <= 10:
        raise ValueError(f'Nota fora da escala do Bitcoin Alpha: {nota}')
    return 10 - nota


def grafo_dijkstra(grafo):
    transformado = Graph()
    for vertice in grafo.vertices():
        transformado.adicionar_vertice(vertice)
    for arco in grafo.arcos():
        transformado.adicionar_arco(
            arco.origem, arco.destino, custo_dijkstra(arco.peso), arco.metadados
        )
    return transformado


def _resumo_grafo(grafo):
    return {'vertices': len(grafo), 'arcos': sum(1 for _ in grafo.arcos())}


def _cinco_pares(larguras):
    destinos = {
        fonte: sorted(
            (vertice for vertice in resultado.distancias if vertice != fonte),
            key=lambda vertice: (-resultado.distancias[vertice], vertice),
        )
        for fonte, resultado in larguras.items()
    }
    pares = []
    for posicao in range(max(map(len, destinos.values()))):
        for fonte, lista in destinos.items():
            if posicao < len(lista):
                pares.append((fonte, lista[posicao]))
                if len(pares) == 5:
                    return pares
    raise ValueError('O grafo não oferece cinco pares alcançáveis para as três fontes.')


def _custo_transformado_do_caminho(resultado, caminho):
    return sum(custo_dijkstra(resultado.predecessores[v].peso) for v in caminho[1:])


def _caso_sem_ciclo(grafo):
    arco_negativo = next((arco for arco in grafo.arcos() if arco.peso < 0 and arco.origem != arco.destino), None)
    if arco_negativo is None:
        raise ValueError('O caso sem ciclo exige um arco negativo entre vértices distintos.')

    fonte = arco_negativo.origem
    niveis = bfs(grafo, fonte).distancias
    aciclico = Graph()
    for vertice in niveis:
        aciclico.adicionar_vertice(vertice)
    for arco in grafo.arcos():
        if arco.origem in niveis and niveis[arco.origem] < niveis[arco.destino]:
            aciclico.adicionar_arco(arco.origem, arco.destino, arco.peso, arco.metadados)

    resultado = bellman_ford(aciclico, fonte)
    if resultado.ciclo_negativo:
        raise RuntimeError('O subgrafo de níveis crescentes apresentou um ciclo negativo.')
    destino = arco_negativo.destino
    return {
        'caso': 'sem_ciclo_negativo', 'fonte': fonte, 'recorte': 100, 'status': 'OK',
        'ciclo': [], 'custo_ciclo': None,
        'criterio_subgrafo': 'Arcos originais que avançam de nível BFS a partir da fonte.',
        **_resumo_grafo(aciclico),
        'arcos_negativos': sum(arco.peso < 0 for arco in aciclico.arcos()),
        'destino_exemplo': destino, 'custo_exemplo': resultado.distancias[destino],
        'caminho_exemplo': resultado.caminho_ate(destino),
    }


def _caso_com_ciclo(grafo, fontes):
    for fonte in fontes:
        resultado = bellman_ford(grafo, fonte)
        if resultado.ciclo_negativo:
            arcos = resultado.ciclo_negativo
            return {
                'caso': 'com_ciclo_negativo', 'fonte': fonte, 'recorte': 100,
                'status': 'CICLO_NEGATIVO', 'ciclo': [arcos[0].origem, *(a.destino for a in arcos)],
                'custo_ciclo': sum(a.peso for a in arcos),
                'arcos_do_ciclo': [
                    {'origem': arco.origem, 'destino': arco.destino, 'peso': arco.peso}
                    for arco in arcos
                ],
                'afetados': len(resultado.afetados),
            }
    raise ValueError('Nenhuma das três fontes alcança um ciclo negativo no grafo original.')


def gerar_casos(arquivo):
    """Produz as seções T25 para composição do relatório T26."""
    arquivo = Path(arquivo)
    grafo = ler_dataset(arquivo)
    fontes = sorted(grafo.vertices(), key=lambda v: (-len(grafo.arcos_saindo(v)), v))[:3]
    if len(fontes) < 3:
        raise ValueError('São necessárias três fontes distintas.')

    larguras = {fonte: bfs(grafo, fonte) for fonte in fontes}
    casos_dfs = []
    for fonte in fontes:
        resultado = dfs(grafo, fonte)
        contagens = Counter(classe for _, classe in resultado.arcos_classificados)
        casos_dfs.append({
            'fonte': fonte, 'recorte': 100, 'alcancados': len(resultado.descoberta),
            'classes': {classe: contagens[classe] for classe in ('arvore', 'retorno', 'avanco', 'cruzamento')},
            'possui_ciclo': resultado.possui_ciclo,
        })
    pares = _cinco_pares(larguras)
    transformado = grafo_dijkstra(grafo)
    ponderados = {fonte: dijkstra(transformado, fonte) for fonte in dict.fromkeys(f for f, _ in pares)}
    casos_dijkstra = []
    comparacoes = []
    for origem, destino in pares:
        bfs_resultado = larguras[origem]
        dijkstra_resultado = ponderados[origem]
        caminho_bfs = bfs_resultado.caminho_ate(destino)
        caminho_dijkstra = dijkstra_resultado.caminho_ate(destino)
        custo = dijkstra_resultado.distancias[destino]
        casos_dijkstra.append({
            'origem': origem, 'destino': destino, 'recorte': 100, 'status': 'OK',
            'custo': custo, 'passos': len(caminho_dijkstra) - 1, 'caminho': caminho_dijkstra,
        })
        comparacoes.append({
            'origem': origem, 'destino': destino, 'recorte': 100,
            'passos_bfs': len(caminho_bfs) - 1, 'passos_dijkstra': len(caminho_dijkstra) - 1,
            'caminho_bfs': caminho_bfs, 'caminho_dijkstra': caminho_dijkstra,
            'custo_transformado_bfs': _custo_transformado_do_caminho(bfs_resultado, caminho_bfs),
            'custo_transformado_dijkstra': custo,
        })

    recortes = [
        {'recorte': percentual, **_resumo_grafo(grafo if percentual == 100 else ler_dataset(arquivo, percentual))}
        for percentual in (10, 50, 100)
    ]
    return {
        'dataset': {
            'arquivo': arquivo.as_posix(), **_resumo_grafo(grafo),
            'arcos_negativos': sum(arco.peso < 0 for arco in grafo.arcos()),
            'criterio_recorte': 'Primeiras avaliações por timestamp após ordenação estável.',
            'recortes': recortes,
        },
        'selecao_casos': {
            'fontes': 'Três maiores graus de saída, com desempate pelo menor ID.',
            'pares': 'Seleção alternada por fonte em ordem decrescente de distância BFS e crescente de ID.',
        },
        'transformacao_pesos': {
            'dijkstra': 'Custo = 10 - nota (0 a 20 por arco). Notas maiores custam menos por arco.',
            'bellman_ford': 'Nota original assinada de -10 a 10.',
        },
        'bfs': [
            {'fonte': fonte, 'recorte': 100, 'alcancados': len(resultado.distancias),
             'niveis': dict(sorted(Counter(resultado.distancias.values()).items())),
             'nivel_max': max(resultado.distancias.values())}
            for fonte, resultado in larguras.items()
        ],
        'dfs': casos_dfs,
        'dijkstra': casos_dijkstra,
        'bellman_ford': [_caso_sem_ciclo(grafo), _caso_com_ciclo(grafo, fontes)],
        'comparacao_caminhos': comparacoes,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description='Executa os casos do Bitcoin Alpha da T25.')
    parser.add_argument('--dataset', type=Path, default=Path('data/dataset_parte2/soc-sign-bitcoinalpha.csv'))
    parser.add_argument('--out', type=Path, default=Path('out/parte2/parte2_report.json'))
    args = parser.parse_args(argv)

    try:
        if args.out.exists():
            atual = json.loads(args.out.read_text(encoding='utf-8'))
            if not isinstance(atual, dict) or 'benchmark' in atual:
                parser.error('A saída contém dados de benchmark ou formato desconhecido. Use outro caminho em --out.')
        relatorio = gerar_casos(args.dataset)
        texto = json.dumps(relatorio, ensure_ascii=False, indent=2, allow_nan=False)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(texto + '\n', encoding='utf-8')
    except (OSError, ValueError) as erro:
        parser.error(str(erro))
    print(args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
