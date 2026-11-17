from collections import Counter

from .graph import Graph

ALVO = "ALVO"


# ---------- rótulos ----------

def decompor_rotulo(rotulo):
    """"(l,c)|chaves|{bonus}[|{fontes}]" -> (l, c, chaves, bonus).

    chaves é a string do rótulo ("-" se nenhuma) e bonus é uma tupla de int.
    No G_pos o rótulo é só "(l,c)": chaves vira "-" e bonus vira ().
    """
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
    """Conjunto de chaves do estado ("-" se nenhuma)."""
    return decompor_rotulo(rotulo)[2]


def _chave_leitura(rotulo):
    """Ordem de leitura: linha, coluna, chaves, bônus."""
    l, c, chaves, bonus = decompor_rotulo(rotulo)
    return (l, c, "" if chaves == "-" else chaves, bonus)


# ---------- base: vértices e arcos sem ALVO ----------

def _vertices(g):
    return [v for v in g.vertices() if v != ALVO]


def _arcos(g):
    return [a for a in g.arcos() if a.origem != ALVO and a.destino != ALVO]


def estados_em_g(g):
    """Estados sobre G: os que têm arco até ALVO."""
    return {a.origem for a in g.arcos() if a.destino == ALVO}


# ---------- ordem, tamanho, densidade ----------

def ordem(g):
    """|V| sem ALVO."""
    return len(_vertices(g))


def tamanho(g):
    """|E| sem os arcos até ALVO. Arcos paralelos contam separadamente."""
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
    """vértice -> grau de saída, na ordem de inserção dos vértices."""
    graus = {v: 0 for v in _vertices(g)}
    for a in _arcos(g):
        graus[a.origem] += 1
    return graus


def graus_entrada(g):
    """vértice -> grau de entrada, na ordem de inserção dos vértices."""
    graus = {v: 0 for v in _vertices(g)}
    for a in _arcos(g):
        graus[a.destino] += 1
    return graus


def resumo_graus(graus):
    """{"min", "max", "medio"} de um dict vértice -> grau."""
    if not graus:
        return {"min": 0, "max": 0, "medio": 0.0}
    valores = list(graus.values())
    return {"min": min(valores), "max": max(valores), "medio": sum(valores) / len(valores)}


def maior_grau(graus):
    """{"estado", "grau"} do maior grau; desempate pela ordem de leitura do rótulo."""
    if not graus:
        return {"estado": None, "grau": 0}
    maximo = max(graus.values())
    estado = min((v for v, d in graus.items() if d == maximo), key=_chave_leitura)
    return {"estado": estado, "grau": maximo}


# ---------- becos ----------

def becos(g, em_g=None):
    """Estados com grau de saída 0 que não estão sobre G, na ordem de inserção.

    em_g: conjunto de estados sobre G. Se None, usa estados_em_g(g) (arcos até
    ALVO). No G_pos, que não tem ALVO, passe os estados de G explicitamente.
    """
    em_g = estados_em_g(g) if em_g is None else set(em_g)
    return [v for v, d in graus_saida(g).items() if d == 0 and v not in em_g]


# ---------- multiplicidade ----------

def multiplicidade(g):
    """(l,c) -> quantos estados do grafo estão naquela casa."""
    return dict(Counter(posicao(v) for v in _vertices(g)))


def resumo_multiplicidade(mult):
    """{"max", "casas_no_max", "media"}; a média é sobre as casas com ao menos um estado."""
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
    """camada -> lista de estados, camadas e estados na ordem de inserção."""
    resultado = {}
    for v in _vertices(g):
        resultado.setdefault(camada(v), []).append(v)
    return resultado


def subgrafo_induzido(g, vertices):
    """Novo Graph só com esses vértices e os arcos entre eles (ordem preservada)."""
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
    """Lista de {"camada", "ordem", "tamanho", "densidade"} do subgrafo induzido de cada camada."""
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
    """Arcos cuja camada muda, agrupados por (de, para).

    Cada item: {"de", "para", "quantidade", "casas"}, onde casas são as casas de
    destino dos arcos (onde a chave é pega), [l, c] sem repetição e em ordem.
    Grupos na ordem em que aparecem pela primeira vez.
    """
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
