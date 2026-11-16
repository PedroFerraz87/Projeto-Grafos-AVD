# [IA] OpenAI Codex - testes de referência da T14.
from math import inf

import pytest

from src.graphs import algorithms
from src.graphs.graph import Graph


def verificar_ciclo(grafo, ciclo):
    assert ciclo
    assert all(arco.destino == proximo.origem for arco, proximo in zip(ciclo, ciclo[1:]))
    assert ciclo[-1].destino == ciclo[0].origem
    assert sum(arco.peso for arco in ciclo) < 0
    for arco in ciclo:
        assert any(arco is candidato for candidato in grafo.arcos_saindo(arco.origem))


def test_peso_negativo_sem_ciclo_e_caminho_finito():
    grafo = Graph()
    for origem, destino, peso in [
        ('S', 'A', 4), ('S', 'B', 5), ('A', 'B', -2), ('A', 'T', 8), ('B', 'T', 3)
    ]:
        grafo.adicionar_arco(origem, destino, peso)
    grafo.adicionar_vertice('I')

    resultado = algorithms.bellman_ford(grafo, 'S')

    assert resultado.distancias == {'S': 0, 'A': 4, 'B': 2, 'T': 5}
    assert resultado.caminho_ate('T') == ['S', 'A', 'B', 'T']
    assert resultado.caminho_ate('I') == []
    assert resultado.ciclo_negativo == ()
    assert resultado.afetados == frozenset()


def test_ciclo_atinge_descendente_e_preserva_ramo_finito():
    grafo = Graph()
    for origem, destino, peso in [
        ('S', 'A', 2), ('S', 'T', 4), ('A', 'B', -3), ('B', 'A', 1), ('B', 'C', 9)
    ]:
        grafo.adicionar_arco(origem, destino, peso)

    resultado = algorithms.bellman_ford(grafo, 'S')

    verificar_ciclo(grafo, resultado.ciclo_negativo)
    assert sum(arco.peso for arco in resultado.ciclo_negativo) == -2
    assert resultado.afetados == frozenset({'A', 'B', 'C'})
    assert all(resultado.distancias[vertice] == -inf for vertice in resultado.afetados)
    assert resultado.caminho_ate('C') == []
    assert resultado.distancias['T'] == 4
    assert resultado.caminho_ate('T') == ['S', 'T']


def test_ciclo_negativo_desconectado_nao_afeta_fonte():
    grafo = Graph()
    grafo.adicionar_arco('S', 'T', 4)
    grafo.adicionar_arco('X', 'Y', -3)
    grafo.adicionar_arco('Y', 'X', 1)

    resultado = algorithms.bellman_ford(grafo, 'S')

    assert resultado.distancias == {'S': 0, 'T': 4}
    assert resultado.ciclo_negativo == ()
    assert resultado.afetados == frozenset()


def test_laco_negativo_na_fonte_conserva_arco_paralelo_exato():
    grafo = Graph()
    grafo.adicionar_arco('S', 'S', 1)
    grafo.adicionar_arco('S', 'S', -1)
    grafo.adicionar_arco('S', 'T', 2)

    resultado = algorithms.bellman_ford(grafo, 'S')

    verificar_ciclo(grafo, resultado.ciclo_negativo)
    assert len(resultado.ciclo_negativo) == 1
    assert resultado.ciclo_negativo[0] is grafo.arcos_saindo('S')[1]
    assert resultado.afetados == frozenset({'S', 'T'})
    assert resultado.distancias == {'S': -inf, 'T': -inf}
    assert resultado.caminho_ate('S') == []


def test_afetados_inclui_dois_ciclos_independentes():
    grafo = Graph()
    grafo.adicionar_arco('S', 'A', 1)
    grafo.adicionar_arco('S', 'B', 2)
    grafo.adicionar_arco('A', 'A', -1)
    grafo.adicionar_arco('B', 'B', -1)
    grafo.adicionar_arco('B', 'C', 3)

    resultado = algorithms.bellman_ford(grafo, 'S')

    verificar_ciclo(grafo, resultado.ciclo_negativo)
    assert resultado.afetados == frozenset({'A', 'B', 'C'})
    assert resultado.distancias['S'] == 0


def test_fonte_ausente():
    with pytest.raises(ValueError):
        algorithms.bellman_ford(Graph(), 'S')
