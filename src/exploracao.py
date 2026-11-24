# [IA] OpenAI Codex – coleta dos resultados reais para a demonstração dos quatro algoritmos.
from .graphs.algorithms import dfs, dijkstra
from .graphs.metricas import posicao


class Expansoes:
    """Registra os estados cujos arcos de saída Dijkstra efetivamente consulta."""

    def __init__(self, grafo):
        self.grafo = grafo
        self.ordem = []

    def __contains__(self, estado):
        return estado in self.grafo

    def arcos(self):
        return self.grafo.arcos()

    def arcos_saindo(self, estado):
        self.ordem.append(estado)
        return self.grafo.arcos_saindo(estado)


def _passos(ordem):
    return [(*posicao(estado), 0) for estado in ordem if estado != "ALVO"]


def _execucao_mapa(analise):
    execucoes = analise["execucoes"]
    dijkstra_registrado = Expansoes(analise["g"])
    buscas = {nome: {**{chave: resultado[chave] for chave in ("status", "passos", "custo")},
                     "rota": [posicao(estado) for estado in resultado["estados"]]}
              for nome, resultado in execucoes.items()}
    if buscas["DIJKSTRA"]["status"] != "RECUSA":
        dijkstra(dijkstra_registrado, analise["inicio"])
    buscas["BFS"]["eventos"] = _passos(execucoes["BFS"]["resultado"].distancias)
    buscas["DIJKSTRA"]["eventos"] = _passos(dijkstra_registrado.ordem)

    resultado_bf = execucoes["BELLMAN_FORD"]["resultado"]
    buscas["BELLMAN_FORD"]["eventos"] = _passos(resultado_bf.distancias)
    buscas["BELLMAN_FORD"]["ciclo"] = [posicao(arco.origem) for arco in resultado_bf.ciclo_negativo
                                        if arco.origem != "ALVO"]

    resultado_dfs = dfs(analise["g"], analise["inicio"])
    eventos_dfs = [(t, estado, fase)
                   for fase, tempos in enumerate((resultado_dfs.descoberta, resultado_dfs.finalizacao))
                   for estado, t in tempos.items() if estado != "ALVO"]
    buscas["DFS"] = {
        "status": "EXPLORACAO",
        "eventos": [(*posicao(estado), fase) for _, estado, fase in sorted(eventos_dfs)],
    }
    return {"grade": analise["grade"], "buscas": buscas}


def dados_exploracao(analises, mapa_inicial):
    return {"mapa_inicial": mapa_inicial, "mapas": {
        analise["nome"]: _execucao_mapa(analise) for analise in analises
    }}
