# [IA] OpenAI Codex - testes de referência da T13.
import pytest

from src.graphs import algorithms
from src.graphs.graph import Graph


def test_menor_custo_pode_usar_mais_arcos():
    grafo = Graph()
    for origem, destino, peso in [
        ('S', 'A', 4), ('S', 'B', 1), ('B', 'A', 2), ('A', 'T', 1), ('B', 'T', 7)
    ]:
        grafo.adicionar_arco(origem, destino, peso)
    grafo.adicionar_vertice('I')

    resultado = algorithms.dijkstra(grafo, 'S')

    assert resultado.distancias == {'S': 0, 'B': 1, 'A': 3, 'T': 4}
    assert resultado.caminho_ate('T') == ['S', 'B', 'A', 'T']
    assert resultado.caminho_ate('S') == ['S']
    assert resultado.caminho_ate('I') == []


def test_zero_e_empate_com_vertices_de_tipos_diferentes():
    grafo = Graph()
    grafo.adicionar_arco('S', 1, 0)
    grafo.adicionar_arco('S', ('A', 2), 0)
    grafo.adicionar_arco(1, 'T', 2)
    grafo.adicionar_arco(('A', 2), 'T', 2)

    resultado = algorithms.dijkstra(grafo, 'S')

    assert resultado.distancias == {'S': 0, 1: 0, ('A', 2): 0, 'T': 2}
    assert resultado.caminho_ate('T') == ['S', 1, 'T']


def test_escolhe_o_arco_paralelo_mais_barato():
    grafo = Graph()
    grafo.adicionar_arco('S', 'T', 7, {'id': 'caro'})
    grafo.adicionar_arco('S', 'T', 3, {'id': 'barato'})

    resultado = algorithms.dijkstra(grafo, 'S')

    assert resultado.distancias['T'] == 3
    assert resultado.predecessores['T'] is grafo.arcos_saindo('S')[1]


def test_recusa_peso_negativo_em_componente_desconectada():
    grafo = Graph()
    grafo.adicionar_arco('S', 'T', 4)
    grafo.adicionar_arco('X', 'Y', -2)

    with pytest.raises(ValueError, match='negativ'):
        algorithms.dijkstra(grafo, 'S')


def test_fonte_ausente():
    with pytest.raises(ValueError):
        algorithms.dijkstra(Graph(), 'S')
