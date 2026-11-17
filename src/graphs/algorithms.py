from collections.abc import Hashable
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from math import inf

from .graph import Arco, Graph

@dataclass
class ResultadoCaminhos:
    fonte: Hashable
    distancias: dict[Hashable, int | float]
    predecessores: dict[Hashable, Arco]

    def pais(self) -> dict[Hashable, Hashable]:
        pares = self.predecessores.items()
        pais = {}
        for vertice, arco in pares:
            pais[vertice] = arco.origem

        return pais

    def caminho_ate(self, destino: Hashable) -> list[Hashable]:
        if self.distancias.get(destino, inf) in (inf, -inf):
            return []
        caminho = [destino]
        while caminho[-1] != self.fonte:
            caminho.append(self.predecessores[caminho[-1]].origem)
        caminho.reverse()
        return caminho

@dataclass
class ResultadoBellmanFord(ResultadoCaminhos):
    ciclo_negativo: tuple[Arco, ...]
    afetados: frozenset[Hashable]

@dataclass
class ResultadoDFS:
    descoberta: dict[Hashable, int]
    finalizacao: dict[Hashable, int]
    arcos_classificados: list[tuple[Arco, str]]
    possui_ciclo: bool

def _validar_fonte(grafo: Graph, fonte: Hashable) -> None:
    if fonte not in grafo:
        raise ValueError(f'A fonte {fonte!r} não pertence ao grafo.')

def bfs(grafo: Graph, fonte: Hashable) -> ResultadoCaminhos:
    _validar_fonte(grafo, fonte)
    distancias = {fonte: 0}
    predecessores = {}
    fila = [fonte]
    while fila:
        atual = fila.pop(0)
        for arco in grafo.arcos_saindo(atual):
            destino = arco.destino
            if destino not in distancias:
                distancias[destino] = distancias[atual] + 1
                predecessores[destino] = arco
                fila.append(destino)

    return ResultadoCaminhos(fonte, distancias, predecessores)

def dfs(grafo: Graph, fonte: Hashable) -> ResultadoDFS:
    _validar_fonte(grafo, fonte)
    descoberta = {fonte: 1}
    finalizacao = {}
    classificados = []
    possui_ciclo = False
    tempo = 1
   
    pilha = [(fonte, iter(grafo.arcos_saindo(fonte)))]
    while pilha:
        atual, vizinhos = pilha[-1]
        arco = next(vizinhos, None)
        if arco is None:
            tempo += 1
            finalizacao[atual] = tempo
            pilha.pop()
            continue

        destino = arco.destino

        if destino not in descoberta:
            classe = 'arvore'
            tempo += 1
            descoberta[destino] = tempo
            pilha.append((destino, iter(grafo.arcos_saindo(destino))))
        elif destino not in finalizacao:
            classe = 'retorno'
            possui_ciclo = True
        elif descoberta[atual] < descoberta[destino]:
            classe = 'avanco'
        else:
            classe = 'cruzamento'

        classificados.append((arco, classe))

    return ResultadoDFS(descoberta, finalizacao, classificados, possui_ciclo)

def estados_armadilha(grafo: Graph, fonte: Hashable, alvo: Hashable = 'ALVO') -> dict[Hashable, int]:
    alcancaveis = bfs(grafo, fonte).distancias
    chegam_ao_alvo = bfs(grafo.transposto(), alvo).distancias if alvo in grafo else {}
    
    return {
        estado: distancia
        for estado, distancia in alcancaveis.items()
        if estado != alvo and estado not in chegam_ao_alvo
    }

def dijkstra(grafo: Graph, fonte: Hashable) -> ResultadoCaminhos:
    _validar_fonte(grafo, fonte)
    if any(arco.peso < 0 for arco in grafo.arcos()):
        raise ValueError('Dijkstra não aceita arcos com peso negativo.')

    distancias = {fonte: 0}
    predecessores = {}
    sequencia = count()
    fila = [(0, next(sequencia), fonte)]

    while fila:
        custo, _, vertice = heappop(fila)
        if custo != distancias[vertice]:
            continue
        for arco in grafo.arcos_saindo(vertice):
            novo_custo = custo + arco.peso
            if novo_custo < distancias.get(arco.destino, inf):
                distancias[arco.destino] = novo_custo
                predecessores[arco.destino] = arco
                heappush(fila, (novo_custo, next(sequencia), arco.destino))

    return ResultadoCaminhos(fonte, distancias, predecessores)

def bellman_ford(grafo: Graph, fonte: Hashable) -> ResultadoBellmanFord:
    _validar_fonte(grafo, fonte)
    arcos = list(grafo.arcos())
    distancias = {fonte: 0}
    predecessores = {}

    def relaxar(arco: Arco) -> bool:
        if arco.origem not in distancias:
            return False
        novo_custo = distancias[arco.origem] + arco.peso
        if novo_custo >= distancias.get(arco.destino, inf):
            return False
        distancias[arco.destino] = novo_custo
        predecessores[arco.destino] = arco
        return True

    for _ in range(len(grafo) - 1):
        houve_mudanca = False
        for arco in arcos:
            if relaxar(arco):
                houve_mudanca = True
        if not houve_mudanca:
            break

    atualizados = [arco.destino for arco in arcos if relaxar(arco)]
    if not atualizados:
        return ResultadoBellmanFord(fonte, distancias, predecessores, (), frozenset())

    vertice = atualizados[-1]
    for _ in range(len(grafo)):
        vertice = predecessores[vertice].origem
    inicio = vertice
    ciclo_invertido = [predecessores[inicio]]
    vertice = ciclo_invertido[-1].origem
    while vertice != inicio:
        arco = predecessores[vertice]
        ciclo_invertido.append(arco)
        vertice = arco.origem
    ciclo = tuple(reversed(ciclo_invertido))

    afetados = set(atualizados)
    fila = list(afetados)
    while fila:
        vertice = fila.pop(0)
        for arco in grafo.arcos_saindo(vertice):
            if arco.destino not in afetados:
                afetados.add(arco.destino)
                fila.append(arco.destino)
    for vertice in afetados:
        distancias[vertice] = -inf
        predecessores.pop(vertice, None)

    return ResultadoBellmanFord(fonte, distancias, predecessores, ciclo, frozenset(afetados))
