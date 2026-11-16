# [IA] OpenAI Codex - testes da versão de estudo da T15.
from src.graphs import algorithms
from src.graphs.graph import Graph


def test_armadilhas_levam_em_conta_alcance_nos_dois_sentidos():
    grafo = Graph()
    for origem, destino in [('S', 'A'), ('A', 'B'), ('B', 'A'), ('S', 'G'), ('G', 'ALVO')]:
        grafo.adicionar_arco(origem, destino)
    grafo.adicionar_vertice('I')

    assert algorithms.estados_armadilha(grafo, 'S') == {'A': 1, 'B': 2}


def test_armadilhas_fallback_quando_o_alvo_virtual_nao_existe():
    grafo = Graph()
    grafo.adicionar_arco('S', 'A')
    grafo.adicionar_vertice('I')

    assert algorithms.estados_armadilha(grafo, 'S') == {'S': 0, 'A': 1}
