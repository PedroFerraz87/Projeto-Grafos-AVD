# [IA] Claude – escrita dos testes do T02 a partir dos casos sintéticos de Artur.
"""Testes do grafo dirigido (T02) contra src/graphs/graph.py.

Os dois primeiros cenários vêm de tests/fixtures/p2_casos_sinteticos.json
(casos T02_*); os demais cobrem decisões documentadas no próprio graph.py.
"""
import json
from pathlib import Path

import pytest

from src.graphs.graph import Arco, Graph

FIXTURE = Path(__file__).parent / "fixtures" / "p2_casos_sinteticos.json"
CASOS_T02 = [
    caso
    for caso in json.loads(FIXTURE.read_text(encoding="utf-8"))["casos"]
    if caso["id"].startswith("T02")
]


def montar(caso):
    g = Graph()
    for v in caso["vertices"]:
        g.adicionar_vertice(v)
    for e in caso["arestas"]:
        g.adicionar_arco(e["origem"], e["destino"], e["peso"], e["metadados"])
    return g


@pytest.mark.parametrize("caso", CASOS_T02, ids=[c["id"] for c in CASOS_T02])
def test_adjacencia_preserva_ordem_e_nao_espelha(caso):
    g = montar(caso)
    esperado = caso["expectativas"].get("adjacencias")
    if esperado is None:
        pytest.skip("caso sem expectativa de adjacências")
    obtido = {v: [a.destino for a in g.arcos_saindo(v)] for v in g.vertices()}
    assert obtido == esperado


@pytest.mark.parametrize("caso", CASOS_T02, ids=[c["id"] for c in CASOS_T02])
def test_pesos_e_metadados_conservados(caso):
    g = montar(caso)
    obtido = [(a.origem, a.destino, a.peso, a.metadados) for a in g.arcos()]
    esperado = [(e["origem"], e["destino"], e["peso"], e["metadados"]) for e in caso["arestas"]]
    assert obtido == esperado


@pytest.mark.parametrize("caso", CASOS_T02, ids=[c["id"] for c in CASOS_T02])
def test_transposto_inverte_arcos_e_mantem_vertices(caso):
    g = montar(caso)
    arcos_antes = list(g.arcos())
    t = g.transposto()

    assert set(t.vertices()) == set(caso["vertices"])
    esperado = {
        (e["origem"], e["destino"]): (e["peso"], e["metadados"])
        for e in caso["expectativas"].get("transposto", [])
    }
    obtido = {(a.origem, a.destino): (a.peso, a.metadados) for a in t.arcos()}
    assert obtido == esperado
    # o original não muda
    assert list(g.arcos()) == arcos_antes
    assert t is not g


def test_vertice_repetido_nao_duplica():
    g = Graph()
    g.adicionar_vertice("A")
    g.adicionar_vertice("A")
    assert len(g) == 1
    assert g.arcos_saindo("A") == []


def test_arco_cria_vertices_e_um_so_sentido():
    g = Graph()
    g.adicionar_arco("A", "B", 3)
    assert "A" in g and "B" in g
    assert [a.destino for a in g.arcos_saindo("A")] == ["B"]
    assert g.arcos_saindo("B") == []


def test_peso_padrao_e_metadados_vazios():
    g = Graph()
    g.adicionar_arco("A", "B")
    assert list(g.arcos()) == [Arco("A", "B", 1, {})]


def test_arcos_repetidos_sao_mantidos():
    g = Graph()
    g.adicionar_arco("A", "B", 1)
    g.adicionar_arco("A", "B", 5)
    assert [a.peso for a in g.arcos_saindo("A")] == [1, 5]


def test_metadados_sao_copiados():
    meta = {"movimento": "N"}
    g = Graph()
    g.adicionar_arco("A", "B", 1, meta)
    meta["movimento"] = "S"
    assert g.arcos_saindo("A")[0].metadados == {"movimento": "N"}
    t = g.transposto()
    t.arcos_saindo("B")[0].metadados["movimento"] = "O"
    assert g.arcos_saindo("A")[0].metadados == {"movimento": "N"}


def test_aceita_estado_como_vertice():
    estado = ((1, 1), frozenset(), frozenset())
    g = Graph()
    g.adicionar_arco(estado, "ALVO", 0, {"movimento": "-"})
    assert g.vertices() == [estado, "ALVO"]
    assert g.arcos_saindo(estado)[0].peso == 0
