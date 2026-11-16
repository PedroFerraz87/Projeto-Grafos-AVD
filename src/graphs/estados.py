"""Grafos do labirinto: G_pos (T08). O G_est entra na T09.

G_pos é o modelo ingênuo: um nó por casa livre, sem chaves nem bônus consumidos.
O vértice é o rótulo "(l,c)" (docs/contratos.md) e o custo de um movimento é o
custo da casa de destino.
"""
from .graph import Graph

# custo de entrar em cada casa; "+" vale -4 sempre no G_pos (nunca é consumido)
CUSTO = {**dict.fromkeys(".SGabcdABCD><^v", 1), ",": 3, "~": 5, "+": -4, "*": -2}

# N, L, S, O: sempre nesta ordem (docs/contratos.md, seção 1.4)
DIRECOES = [("N", -1, 0), ("L", 0, 1), ("S", 1, 0), ("O", 0, -1)]

# direção única de quem está sobre cada esteira
SETA = {">": "L", "<": "O", "^": "N", "v": "S"}


def rotulo_pos(l, c):
    return f"({l},{c})"


def construir_g_pos(grade, porta_como="parede"):
    """Constrói o G_pos a partir da grade devolvida por ler_mapa.

    porta_como: "parede" (a porta A-D não é nó) ou "chao" (a porta é uma casa
    comum de custo 1, mesmo sem chave). Os vértices entram por linha e depois
    coluna, e os arcos de cada casa saem em N, L, S, O. Nenhum arco sai de G,
    e quem está numa esteira só sai na direção da seta.
    """
    if porta_como not in ("parede", "chao"):
        raise ValueError(f"porta_como deve ser 'parede' ou 'chao', recebido {porta_como!r}")

    def livre(l, c):
        if not (0 <= l < len(grade) and 0 <= c < len(grade[l])):
            return False
        simbolo = grade[l][c]
        return simbolo != "#" and not (simbolo in "ABCD" and porta_como == "parede")

    casas = [(l, c) for l in range(len(grade)) for c in range(len(grade[l])) if livre(l, c)]
    g = Graph()
    for l, c in casas:
        g.adicionar_vertice(rotulo_pos(l, c))
    for l, c in casas:
        origem = grade[l][c]
        if origem == "G":
            continue
        for nome, dl, dc in DIRECOES:
            if origem in SETA and SETA[origem] != nome:
                continue
            if livre(l + dl, c + dc):
                destino = grade[l + dl][c + dc]
                metadados = {"movimento": nome, "casa_destino": destino, "via_esteira": origem in SETA}
                g.adicionar_arco(rotulo_pos(l, c), rotulo_pos(l + dl, c + dc), CUSTO[destino], metadados)
    return g
