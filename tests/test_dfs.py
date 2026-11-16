# [IA] OpenAI Codex - testes da versão de estudo da T12.
from src.graphs import algorithms
from src.graphs.graph import Graph


def test_dfs_tempos_e_quatro_classes_na_ordem_de_exame():
    grafo = Graph()
    for origem, destino in [('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('C', 'A'), ('D', 'C')]:
        grafo.adicionar_arco(origem, destino)

    resultado = algorithms.dfs(grafo, 'A')

    assert resultado.descoberta == {'A': 1, 'B': 2, 'C': 3, 'D': 6}
    assert resultado.finalizacao == {'C': 4, 'B': 5, 'D': 7, 'A': 8}
    assert [(a.origem, a.destino, classe) for a, classe in resultado.arcos_classificados] == [
        ('A', 'B', 'arvore'), ('B', 'C', 'arvore'), ('C', 'A', 'retorno'),
        ('A', 'C', 'avanco'), ('A', 'D', 'arvore'), ('D', 'C', 'cruzamento'),
    ]
    assert resultado.possui_ciclo


def test_dfs_classifica_arcos_paralelos_e_restringe_alcance():
    grafo = Graph()
    grafo.adicionar_arco('S', 'T', 3)
    grafo.adicionar_arco('S', 'T', 2)
    grafo.adicionar_arco('I', 'I')

    resultado = algorithms.dfs(grafo, 'S')

    assert [(a.peso, classe) for a, classe in resultado.arcos_classificados] == [(3, 'arvore'), (2, 'avanco')]
    assert not resultado.possui_ciclo
    assert 'I' not in resultado.descoberta


def test_dfs_processa_cadeia_maior_que_o_limite_usual_de_recursao():
    grafo = Graph()
    for origem in range(1200):
        grafo.adicionar_arco(origem, origem + 1)

    resultado = algorithms.dfs(grafo, 0)

    assert resultado.descoberta[1200] == 1201
    assert resultado.finalizacao[0] == 2402
    assert not resultado.possui_ciclo
