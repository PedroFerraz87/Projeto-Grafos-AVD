"""Grafo dirigido por lista de adjacência (T02).

Os vizinhos de cada vértice saem na ordem em que os arcos foram inseridos
(N, L, S, O na exploração dos mapas). O grafo só guarda arcos; regras do
jogo (esteira, porta, chave) ficam em estados.py.
"""
from collections import namedtuple

# Um arco é uma tupla com nomes:
#   origem, destino: vértices (qualquer valor que sirva de chave de dict)
#   peso: número
#   metadados: dict com informações do arco, ex.: {"movimento": "N"}
Arco = namedtuple("Arco", ["origem", "destino", "peso", "metadados"])


class Graph:
    def __init__(self):
        # vértice -> lista de Arcos que saem dele
        # dict preserva a ordem de inserção dos vértices e, em cada lista, dos arcos
        self._adj = {}

    def __len__(self):
        """Ordem do grafo (número de vértices)."""
        return len(self._adj)

    def __contains__(self, v):
        return v in self._adj

    def adicionar_vertice(self, v):
        """Cadastra v (sem arcos). Não faz nada se já existir."""
        self._adj.setdefault(v, [])

    def adicionar_arco(self, origem, destino, peso=1, metadados=None):
        """Insere o arco origem -> destino (nunca cria o reverso).

        Cria os vértices que ainda não existem. Arcos repetidos entre o mesmo
        par são mantidos (multigrafo), cada um com seu peso e metadados.
        """
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self._adj[origem].append(Arco(origem, destino, peso, dict(metadados or {})))

    def vertices(self):
        """Lista dos vértices, na ordem de inserção."""
        return list(self._adj)

    def arcos_saindo(self, v):
        """Lista de Arcos que saem de v, na ordem de inserção. Não modificar a lista."""
        return self._adj[v]

    def arcos(self):
        """Gera todos os Arcos, por vértice de origem e depois por ordem de inserção."""
        for lista in self._adj.values():
            yield from lista

    def transposto(self):
        """Novo Graph com todos os vértices e cada arco invertido (peso e metadados mantidos)."""
        t = Graph()
        for v in self._adj:
            t.adicionar_vertice(v)
        for a in self.arcos():
            t.adicionar_arco(a.destino, a.origem, a.peso, a.metadados)
        return t
