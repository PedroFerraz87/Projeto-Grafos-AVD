from collections import Counter

from .graph import Graph

ALVO = "ALVO"

# ---------- rótulos ----------

def decompor_rotulo(rotulo):
    partes = rotulo.split("|")
    pos = partes[0]
    if not (pos.startswith("(") and pos.endswith(")")):
        raise ValueError(f"rótulo inválido: {rotulo!r}")
    l, c = (int(x) for x in pos[1:-1].split(","))
    chaves = partes[1] if len(partes) > 1 else "-"
    bonus = ()
    if len(partes) > 2:
        dentro = partes[2].strip("{}")
        bonus = tuple(int(x) for x in dentro.split(",")) if dentro else ()
    return l, c, chaves, bonus

def posicao(rotulo):
    l, c, _, _ = decompor_rotulo(rotulo)
    return l, c

def camada(rotulo):
    return decompor_rotulo(rotulo)[2]

def _chave_leitura(rotulo):
    l, c, chaves, bonus = decompor_rotulo(rotulo)
    return (l, c, "" if chaves == "-" else chaves, bonus)


# ---------- base: vértices e arcos sem ALVO ----------

def _vertices(g):
    return [v for v in g.vertices() if v != ALVO]

def _arcos(g):
    return [a for a in g.arcos() if a.origem != ALVO and a.destino != ALVO]

def estados_em_g(g):
    return {a.origem for a in g.arcos() if a.destino == ALVO}


# ---------- ordem, tamanho, densidade ----------

def ordem(g):
    return len(_vertices(g))

def tamanho(g):
    return len(_arcos(g))

def densidade_dirigida(n_vertices, n_arcos):
    """|E| / (|V| (|V| - 1)); 0 se |V| < 2."""
    if n_vertices < 2:
        return 0.0
    return n_arcos / (n_vertices * (n_vertices - 1))

def densidade(g):
    return densidade_dirigida(ordem(g), tamanho(g))

# ---------- graus ----------

def graus_saida(g):
    graus = {v: 0 for v in _vertices(g)}
    for a in _arcos(g):
        graus[a.origem] += 1
    return graus

def graus_entrada(g):
    graus = {v: 0 for v in _vertices(g)}
    for a in _arcos(g):
        graus[a.destino] += 1
    return graus

def resumo_graus(graus):
    if not graus:
        return {"min": 0, "max": 0, "medio": 0.0}
    valores = list(graus.values())
    return {"min": min(valores), "max": max(valores), "medio": sum(valores) / len(valores)}

def maior_grau(graus):
    if not graus:
        return {"estado": None, "grau": 0}
    maximo = max(graus.values())
    estado = min((v for v, d in graus.items() if d == maximo), key=_chave_leitura)
    return {"estado": estado, "grau": maximo}

# ---------- becos ----------

def becos(g, em_g=None):
    em_g = estados_em_g(g) if em_g is None else set(em_g)
    return [v for v, d in graus_saida(g).items() if d == 0 and v not in em_g]

# ---------- multiplicidade ----------

def multiplicidade(g):
    return dict(Counter(posicao(v) for v in _vertices(g)))

def resumo_multiplicidade(mult):
    if not mult:
        return {"max": 0, "casas_no_max": 0, "media": 0.0}
    maximo = max(mult.values())
    return {
        "max": maximo,
        "casas_no_max": sum(1 for m in mult.values() if m == maximo),
        "media": sum(mult.values()) / len(mult),
    }

# ---------- camadas ----------

def camadas(g):
    resultado = {}
    for v in _vertices(g):
        resultado.setdefault(camada(v), []).append(v)
    return resultado

def subgrafo_induzido(g, vertices):
    conjunto = set(vertices)
    sub = Graph()
    for v in g.vertices():
        if v in conjunto:
            sub.adicionar_vertice(v)
    for a in g.arcos():
        if a.origem in conjunto and a.destino in conjunto:
            sub.adicionar_arco(a.origem, a.destino, a.peso, a.metadados)
    return sub

def metricas_camadas(g):
    resultado = []
    for nome, estados in camadas(g).items():
        sub = subgrafo_induzido(g, estados)
        resultado.append({
            "camada": nome,
            "ordem": ordem(sub),
            "tamanho": tamanho(sub),
            "densidade": densidade(sub),
        })
    return resultado

def arcos_entre_camadas(g):
    grupos = {}
    for a in _arcos(g):
        de, para = camada(a.origem), camada(a.destino)
        if de == para:
            continue
        item = grupos.setdefault((de, para), {"de": de, "para": para, "quantidade": 0, "casas": set()})
        item["quantidade"] += 1
        item["casas"].add(posicao(a.destino))
    return [{**item, "casas": [list(p) for p in sorted(item["casas"])]} for item in grupos.values()]

def n_arcos_entre_camadas(g):
    return sum(item["quantidade"] for item in arcos_entre_camadas(g))
