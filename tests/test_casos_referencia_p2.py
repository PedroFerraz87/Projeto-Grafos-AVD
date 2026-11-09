# [IA] OpenAI Codex - conferência dos casos sintéticos sugeridos para o P2.
"""Valida SOMENTE expectativas das fixtures com NetworkX como oráculo.

Não importa graph.py/algorithms.py nem comprova sua implementação. Os testes
dos algoritmos do grupo continuam pendentes até serem escritos contra sua API.
"""
import json
from pathlib import Path

import networkx as nx
import pytest


# Os casos T02_* ja sao testados contra src/graphs/graph.py em tests/test_graph.py;
# aqui ficam so os casos dos algoritmos (T11-T15), ate existir algorithms.py.
CASOS = [
    caso
    for caso in json.loads((Path(__file__).parent / 'fixtures' / 'p2_casos_sinteticos.json').read_text(encoding='utf-8'))['casos']
    if not caso['id'].startswith('T02')
]


def grafo_referencia(caso):
    graph = nx.DiGraph()
    graph.add_nodes_from(caso['vertices'])
    for edge in caso['arestas']:
        graph.add_edge(edge['origem'], edge['destino'], weight=edge['peso'], metadados=edge['metadados'])
    return graph


@pytest.mark.parametrize('caso', CASOS, ids=[caso['id'] for caso in CASOS])
def test_expectativas_sinteticas_conferidas_com_oraculo(caso):
    graph = grafo_referencia(caso)
    expected = caso['expectativas']
    if 'adjacencias' in expected:
        assert {node: list(graph.successors(node)) for node in graph} == expected['adjacencias']
    if 'transposto' in expected:
        reverse = graph.reverse(copy=True)
        actual_edges = {(u, v): (attrs['weight'], attrs['metadados']) for u, v, attrs in reverse.edges(data=True)}
        expected_edges = {(e['origem'], e['destino']): (e['peso'], e['metadados']) for e in expected['transposto']}
        assert actual_edges == expected_edges
        assert set(reverse) == set(caso['vertices'])
    if 'bfs' in expected:
        query = expected['bfs']
        paths = nx.single_source_shortest_path(graph, query['fonte'])
        assert {node: len(path)-1 for node, path in paths.items()} == query['distancias_finitas']
        assert set(graph) - set(paths) == set(query['inalcancaveis'])
        if 'caminho' in query:
            assert paths[query['destino']] == query['caminho']
    if 'dfs' in expected:
        query = expected['dfs']
        order = list(nx.dfs_preorder_nodes(graph, query['fonte']))
        assert order == query['ordem']
        tree_edges = set(nx.dfs_edges(graph, query['fonte']))
        tree = nx.DiGraph()
        tree.add_nodes_from(order)
        tree.add_edges_from(tree_edges)
        classes = {kind: set() for kind in ['arvore', 'retorno', 'avanco', 'cruzamento']}
        for u in order:
            for v in graph.successors(u):
                if (u, v) in tree_edges:
                    kind = 'arvore'
                elif u == v or u in nx.descendants(tree, v):
                    kind = 'retorno'
                elif v in nx.descendants(tree, u):
                    kind = 'avanco'
                else:
                    kind = 'cruzamento'
                classes[kind].add((u, v))
        assert classes == {kind: set(map(tuple, pairs)) for kind, pairs in query['classes'].items()}
        assert bool(classes['retorno']) == query['possui_ciclo']
    if 'dijkstra' in expected:
        query = expected['dijkstra']
        negative = any(edge['peso'] < 0 for edge in caso['arestas'])
        # A recusa global é requisito do projeto; não é comportamento prometido pelo NetworkX.
        assert query['recusa'] == negative
        if not query['recusa']:
            lengths, paths = nx.single_source_dijkstra(graph, query['fonte'])
            assert lengths == query['distancias_finitas']
            assert set(graph) - set(lengths) == set(query['inalcancaveis'])
            if 'caminho' in query:
                assert paths[query['destino']] == query['caminho']
    if 'bellman_ford' in expected:
        query = expected['bellman_ford']
        source = query['fonte']
        reachable = {source} | nx.descendants(graph, source)
        affected = set()
        for cycle in nx.simple_cycles(graph.subgraph(reachable)):
            closed = cycle + [cycle[0]]
            if sum(graph[u][v]['weight'] for u, v in zip(closed, closed[1:])) < 0:
                for node in cycle:
                    affected |= {node} | nx.descendants(graph, node)
        assert affected == set(query['afetados'])
        assert bool(affected) == query['ciclo_negativo_alcancavel']
        assert set(graph) - reachable == set(query['inalcancaveis'])
        finite_graph = graph.subgraph(set(graph) - affected)
        lengths, paths = nx.single_source_bellman_ford(finite_graph, source)
        assert lengths == query['distancias_finitas']
        if 'caminho' in query:
            assert paths[query['destino']] == query['caminho']
        if 'ciclo_exemplo' in query:
            cycle = query['ciclo_exemplo']
            assert cycle[0] == cycle[-1]
            assert sum(graph[u][v]['weight'] for u, v in zip(cycle, cycle[1:])) == query['custo_ciclo_exemplo'] < 0
    if 'armadilhas' in expected:
        query = expected['armadilhas']
        reachable = {query['fonte']} | nx.descendants(graph, query['fonte'])
        can_reach_goal = {query['alvo']} | nx.ancestors(graph, query['alvo'])
        actual = (reachable - can_reach_goal) & set(query['estados_fisicos'])
        assert actual == set(query['esperado'])
