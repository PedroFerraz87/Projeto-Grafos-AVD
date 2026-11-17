from collections import namedtuple

# Um arco é uma tupla com nomes:
#   origem, destino: vértices (qualquer valor que sirva de chave de dict)
#   peso: número
#   metadados: dict com informações do arco, ex.: {"movimento": "N"}
Arco = namedtuple("Arco", ["origem", "destino", "peso", "metadados"])

class Graph:
    def __init__(self):
        self._adj = {}

    def __len__(self):
        return len(self._adj)

    def __contains__(self, v):
        return v in self._adj

    def adicionar_vertice(self, v):
        self._adj.setdefault(v, [])

    def adicionar_arco(self, origem, destino, peso=1, metadados=None):
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self._adj[origem].append(Arco(origem, destino, peso, dict(metadados or {})))

    def vertices(self):
        return list(self._adj)

    def arcos_saindo(self, v):
        return self._adj[v]

    def arcos(self):
        for lista in self._adj.values():
            yield from lista

    def transposto(self):
        t = Graph()
        for v in self._adj:
            t.adicionar_vertice(v)
        for a in self.arcos():
            t.adicionar_arco(a.destino, a.origem, a.peso, a.metadados)
        return t
