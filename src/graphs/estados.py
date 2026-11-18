from collections import deque

from .graph import Graph

CUSTO = {**dict.fromkeys(".SGabcdABCD><^v", 1), ",": 3, "~": 5, "+": -4, "*": -2}

DIRECOES = [("N", -1, 0), ("L", 0, 1), ("S", 1, 0), ("O", 0, -1)]

SETA = {">": "L", "<": "O", "^": "N", "v": "S"}

def rotulo_pos(l, c):
    return f"({l},{c})"

def construir_g_pos(grade, porta_como="parede"):
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


def rotulo_est(l, c, chaves, bonus, fontes=None):
    texto = f"({l},{c})|{chaves or '-'}|{{{','.join(map(str, sorted(bonus)))}}}"
    if fontes is not None:
        texto += f"|{{{','.join(map(str, sorted(fontes)))}}}"
    return texto


def construir_g_est(grade, fonte_consumivel=False):
    bonus_idx, fonte_idx = {}, {}
    for l, linha in enumerate(grade):
        for c, simbolo in enumerate(linha):
            if simbolo == "+":
                bonus_idx[(l, c)] = len(bonus_idx)
            elif simbolo == "*":
                fonte_idx[(l, c)] = len(fonte_idx)
            elif simbolo == "S":
                inicio = (l, c)

    rotulos = {}

    def rotulo(estado):
        if estado not in rotulos:
            l, c, chaves, bonus, fontes = estado
            rotulos[estado] = rotulo_est(l, c, chaves, bonus, fontes if fonte_consumivel else None)
        return rotulos[estado]

    ini = (*inicio, "", frozenset(), frozenset())
    g = Graph()
    g.adicionar_vertice(rotulo(ini))
    vistos, fila = {ini}, deque([ini])
    while fila:
        estado = fila.popleft()
        l, c, chaves, bonus, fontes = estado
        origem = grade[l][c]
        if origem == "G":
            g.adicionar_arco(rotulo(estado), "ALVO", 0, {"movimento": "-", "casa_destino": "", "via_esteira": False})
            continue
        for nome, dl, dc in DIRECOES:
            if origem in SETA and SETA[origem] != nome:
                continue
            nl, nc = l + dl, c + dc
            if not (0 <= nl < len(grade) and 0 <= nc < len(grade[nl])):
                continue
            destino = grade[nl][nc]
            if destino == "#" or (destino in "ABCD" and destino.lower() not in chaves):
                continue
            custo, novas_chaves, novos_bonus, novas_fontes = CUSTO[destino], chaves, bonus, fontes
            if destino in "abcd":
                novas_chaves = "".join(sorted(set(chaves) | {destino}))
            elif destino == "+":
                i = bonus_idx[(nl, nc)]
                if i in bonus:
                    custo = 1
                else:
                    novos_bonus = bonus | {i}
            elif destino == "*" and fonte_consumivel:
                i = fonte_idx[(nl, nc)]
                if i in fontes:
                    custo = 1
                else:
                    novas_fontes = fontes | {i}
            novo = (nl, nc, novas_chaves, novos_bonus, novas_fontes)
            metadados = {"movimento": nome, "casa_destino": destino, "via_esteira": origem in SETA}
            g.adicionar_arco(rotulo(estado), rotulo(novo), custo, metadados)
            if novo not in vistos:
                vistos.add(novo)
                fila.append(novo)
    g.adicionar_vertice("ALVO")
    return g
