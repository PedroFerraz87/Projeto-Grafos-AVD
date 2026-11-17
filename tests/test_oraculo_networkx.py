import random
from math import inf
from pathlib import Path

import networkx as nx
import pytest

from src.graphs import algorithms
from src.graphs.estados import construir_g_pos, rotulo_pos
from src.graphs.graph import Graph
from src.graphs.io import ler_mapa

MAPAS = sorted((Path(__file__).parent.parent / "data" / "mapas").glob("*.txt"))
SEMENTES = range(80)


# ---------- conversão e geração ----------

def para_networkx(grafo):
    """MultiDiGraph com os mesmos vértices e arcos (paralelos incluídos)."""
    g = nx.MultiDiGraph()
    g.add_nodes_from(grafo.vertices())
    for arco in grafo.arcos():
        g.add_edge(arco.origem, arco.destino, weight=arco.peso)
    return g


def grafo_aleatorio(semente, peso_min, peso_max):
    rng = random.Random(semente)
    n = rng.randint(1, 12)
    grafo = Graph()
    for v in range(n):
        grafo.adicionar_vertice(v)
    for _ in range(rng.randint(0, 3 * n)):
        grafo.adicionar_arco(rng.randrange(n), rng.randrange(n), rng.randint(peso_min, peso_max))
    return grafo


def g_pos_do_mapa(caminho):
    grade = ler_mapa(caminho)
    l, c = next((l, c) for l, linha in enumerate(grade) for c, s in enumerate(linha) if s == "S")
    return construir_g_pos(grade), rotulo_pos(l, c)


# ---------- verificações ----------

def custo_pelos_predecessores(resultado, destino):
    """Soma os pesos dos arcos de predecessores da fonte até destino."""
    custo, vertice, passos = 0, destino, 0
    while vertice != resultado.fonte:
        arco = resultado.predecessores[vertice]
        custo += arco.peso
        vertice = arco.origem
        passos += 1
        assert passos <= len(resultado.distancias), "predecessores formam um ciclo"
    return custo


def arco_existe(grafo, arco):
    return any(arco is candidato for candidato in grafo.arcos_saindo(arco.origem))


def conferir_bfs(grafo, fonte):
    resultado = algorithms.bfs(grafo, fonte)
    esperado = nx.single_source_shortest_path_length(para_networkx(grafo), fonte)
    assert resultado.distancias == esperado
    for destino, distancia in esperado.items():
        caminho = resultado.caminho_ate(destino)
        assert caminho[0] == fonte and caminho[-1] == destino
        assert len(caminho) - 1 == distancia
        for u, v in zip(caminho, caminho[1:]):
            assert any(a.destino == v for a in grafo.arcos_saindo(u))


def conferir_dijkstra(grafo, fonte):
    resultado = algorithms.dijkstra(grafo, fonte)
    esperado = nx.single_source_dijkstra_path_length(para_networkx(grafo), fonte)
    assert resultado.distancias == esperado
    for destino, distancia in esperado.items():
        assert custo_pelos_predecessores(resultado, destino) == distancia
        if destino != fonte:
            assert arco_existe(grafo, resultado.predecessores[destino])


def vertices_afetados_por_ciclo(g_nx, fonte):
    """Vértices alcançáveis por algum ciclo negativo que a fonte alcança."""
    alcancaveis = nx.descendants(g_nx, fonte) | {fonte}
    h = g_nx.subgraph(alcancaveis).copy()
    afetados = set()
    for componente in nx.strongly_connected_components(h):
        if nx.negative_edge_cycle(h.subgraph(componente).copy(), weight="weight"):
            for v in componente:
                afetados |= nx.descendants(h, v) | {v}
    return afetados


def conferir_bellman_ford(grafo, fonte):
    resultado = algorithms.bellman_ford(grafo, fonte)
    g_nx = para_networkx(grafo)
    afetados = vertices_afetados_por_ciclo(g_nx, fonte)

    assert resultado.afetados == frozenset(afetados)
    assert bool(resultado.ciclo_negativo) == bool(afetados)
    if afetados:
        ciclo = resultado.ciclo_negativo
        assert all(a.destino == b.origem for a, b in zip(ciclo, ciclo[1:]))
        assert ciclo[-1].destino == ciclo[0].origem
        assert sum(a.peso for a in ciclo) < 0
        assert all(arco_existe(grafo, a) for a in ciclo)
        assert all(resultado.distancias[v] == -inf for v in afetados)

    # Fora dos afetados o mínimo é finito; afetados é fechado por descendentes,
    # então os caminhos mínimos dos demais não passam por eles.
    restante = g_nx.subgraph(set(g_nx) - afetados)
    esperado = nx.single_source_bellman_ford_path_length(restante, fonte) if fonte in restante else {}
    finitos = {v: d for v, d in resultado.distancias.items() if d != -inf}
    assert finitos == esperado
    for destino, distancia in esperado.items():
        assert custo_pelos_predecessores(resultado, destino) == distancia


# ---------- grafos aleatórios ----------

@pytest.mark.parametrize("semente", SEMENTES)
def test_bfs_igual_ao_networkx(semente):
    grafo = grafo_aleatorio(semente, 1, 1)
    for fonte in grafo.vertices():
        conferir_bfs(grafo, fonte)


@pytest.mark.parametrize("semente", SEMENTES)
def test_dijkstra_igual_ao_networkx(semente):
    grafo = grafo_aleatorio(semente, 0, 9)
    for fonte in grafo.vertices():
        conferir_dijkstra(grafo, fonte)


@pytest.mark.parametrize("semente", SEMENTES)
def test_bellman_ford_sem_negativos_igual_ao_dijkstra_do_networkx(semente):
    grafo = grafo_aleatorio(semente, 0, 9)
    g_nx = para_networkx(grafo)
    for fonte in grafo.vertices():
        resultado = algorithms.bellman_ford(grafo, fonte)
        assert resultado.ciclo_negativo == ()
        assert resultado.distancias == nx.single_source_dijkstra_path_length(g_nx, fonte)


@pytest.mark.parametrize("semente", SEMENTES)
def test_bellman_ford_com_negativos_igual_ao_networkx(semente):
    grafo = grafo_aleatorio(semente, -3, 9)
    for fonte in grafo.vertices():
        conferir_bellman_ford(grafo, fonte)


def test_amostra_aleatoria_tem_casos_com_e_sem_ciclo_negativo():
    """Garante que os testes acima exercitam os dois ramos do Bellman-Ford."""
    com_ciclo = sem_ciclo = 0
    for semente in SEMENTES:
        grafo = grafo_aleatorio(semente, -3, 9)
        for fonte in grafo.vertices():
            if algorithms.bellman_ford(grafo, fonte).ciclo_negativo:
                com_ciclo += 1
            else:
                sem_ciclo += 1
    assert com_ciclo > 0 and sem_ciclo > 0


# ---------- G_pos dos mapas fornecidos ----------

@pytest.mark.parametrize("caminho", MAPAS, ids=lambda p: p.stem)
def test_bfs_no_g_pos_igual_ao_networkx(caminho):
    conferir_bfs(*g_pos_do_mapa(caminho))


@pytest.mark.parametrize("caminho", MAPAS, ids=lambda p: p.stem)
def test_dijkstra_no_g_pos_igual_ao_networkx_ou_recusa(caminho):
    grafo, fonte = g_pos_do_mapa(caminho)
    if any(arco.peso < 0 for arco in grafo.arcos()):
        with pytest.raises(ValueError, match="negativ"):
            algorithms.dijkstra(grafo, fonte)
    else:
        conferir_dijkstra(grafo, fonte)


@pytest.mark.parametrize("caminho", MAPAS, ids=lambda p: p.stem)
def test_bellman_ford_no_g_pos_igual_ao_networkx(caminho):
    conferir_bellman_ford(*g_pos_do_mapa(caminho))
