# [IA] OpenAI Codex - testes da versão de estudo da T11.
import pytest

from src.graphs import algorithms
from src.graphs.graph import Graph


def test_bfs_escolhe_menos_arcos_e_preserva_a_ordem():
    grafo = Graph()
    grafo.adicionar_arco('S', 'A', 8)
    grafo.adicionar_arco('S', 'B', 1)
    grafo.adicionar_arco('A', 'T', 8)
    grafo.adicionar_arco('B', 'T', 1)
    grafo.adicionar_arco('T', 'S')
    grafo.adicionar_vertice('I')

    resultado = algorithms.bfs(grafo, 'S')

    assert resultado.distancias == {'S': 0, 'A': 1, 'B': 1, 'T': 2}
    assert resultado.pais() == {'A': 'S', 'B': 'S', 'T': 'A'}
    assert resultado.caminho_ate('T') == ['S', 'A', 'T']
    assert resultado.caminho_ate('S') == ['S']
    assert resultado.caminho_ate('I') == []


def test_bfs_rejeita_fonte_desconhecida():
    with pytest.raises(ValueError, match='fonte'):
        algorithms.bfs(Graph(), 'S')
