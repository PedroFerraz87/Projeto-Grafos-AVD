# [IA] OpenAI Codex – instrumentação para reproduzir execuções reais da Parte 2.
"""Executa os algoritmos existentes e registra eventos para o painel Bitcoin Alpha."""
from collections import Counter
import json
from pathlib import Path
from time import perf_counter

from ..exploracao import Expansoes
from ..graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from ..graphs.io import ler_dataset
from ..parte2 import custo_dijkstra, grafo_dijkstra

RAIZ = Path(__file__).resolve().parents[2]
DATASET = RAIZ / "data/dataset_parte2/soc-sign-bitcoinalpha.csv"
SAIDAS = RAIZ / "out/parte2"
ALGORITMOS = {"BFS": bfs, "DFS": dfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}


def pares_publicados(pasta=SAIDAS):
    relatorio = json.loads((Path(pasta) / "parte2_report.json").read_text(encoding="utf-8"))
    pares = {}
    for item in relatorio["comparacao_caminhos"]:
        pares.setdefault(item["origem"], []).append(item["destino"])
    return pares


def topologia_publicada(fontes, arquivo=DATASET):
    grafo = ler_dataset(arquivo)
    return {
        "vertices": grafo.vertices(),
        "arcos": [[a.origem, a.destino, a.peso] for a in grafo.arcos()],
        "niveis": {fonte: bfs(grafo, fonte).distancias for fonte in fontes},
    }


class RedeBitcoin:
    """Compartilha os grafos original e com custos transformados entre os experimentos."""

    def __init__(self, arquivo=DATASET):
        self.original = ler_dataset(arquivo)
        self.transformado = grafo_dijkstra(self.original)

    def executar(self, algoritmo, fonte, destinos):
        grafo = self.original
        if algoritmo == "DIJKSTRA":
            grafo = Expansoes(self.transformado)

        inicio = perf_counter()
        resultado = ALGORITMOS[algoritmo](grafo, fonte)
        tempo_ms = (perf_counter() - inicio) * 1000

        saida = {"algoritmo": algoritmo, "fonte": fonte, "tempo_ms": tempo_ms}
        if algoritmo == "DFS":
            predecessores = {arco.destino: arco.origem for arco, classe in resultado.arcos_classificados
                             if classe == "arvore"}
            descoberta, finalizacao = resultado.descoberta, resultado.finalizacao
            eventos = [(t, usuario, fase) for fase, tempos in enumerate((descoberta, finalizacao))
                       for usuario, t in tempos.items()]
            grupos = Counter(classe for _, classe in resultado.arcos_classificados)
            saida.update(eventos=[[usuario, fase] for _, usuario, fase in sorted(eventos)],
                         alcancados=len(descoberta), classes=grupos, possui_ciclo=resultado.possui_ciclo,
                         destinos={destino: _trilha_dfs(predecessores, fonte, destino)
                                   for destino in destinos})
        else:
            ordem = grafo.ordem if algoritmo == "DIJKSTRA" else resultado.distancias
            saida.update(eventos=[[usuario, 0] for usuario in ordem], alcancados=len(resultado.distancias),
                         destinos={destino: _caminho(resultado, algoritmo, destino) for destino in destinos})
        if algoritmo == "BELLMAN_FORD":
            saida["ciclo"] = [[a.origem, a.destino, a.peso] for a in resultado.ciclo_negativo]
            saida["afetados"] = len(resultado.afetados)
        return saida

    def amostra(self, fonte, destinos, resultados):
        """Escolhe usuários para desenhar e retorna apenas arcos reais entre eles."""
        vertices = dict.fromkeys([fonte, *destinos])
        for resultado in resultados:
            for origem, destino, _ in resultado.get("ciclo", []):
                vertices[origem] = vertices[destino] = None
            for caso in resultado["destinos"].values():
                caminho = caso["caminho"]
                for usuario in caminho[:8] + caminho[-8:]:
                    vertices[usuario] = None
        primeiros_bfs = next(r["eventos"] for r in resultados if r["algoritmo"] == "BFS")
        for usuario, _ in primeiros_bfs:
            if len(vertices) >= 44:
                break
            vertices[usuario] = None
        arestas = [[a.origem, a.destino, a.peso] for v in vertices
                   for a in self.original.arcos_saindo(v) if a.destino in vertices]
        return {"vertices": list(vertices), "arcos": arestas}


def _trilha_dfs(predecessores, fonte, destino):
    if destino != fonte and destino not in predecessores:
        return {"status": "INALCANCAVEL", "caminho": []}
    caminho = [destino]
    while caminho[-1] != fonte:
        caminho.append(predecessores[caminho[-1]])
    caminho.reverse()
    return {"status": "ARVORE_DFS", "caminho": caminho, "passos": len(caminho) - 1}


def _caminho(resultado, algoritmo, destino):
    if destino in getattr(resultado, "afetados", ()):
        return {"status": "CICLO_NEGATIVO", "caminho": []}
    if destino not in resultado.distancias:
        return {"status": "INALCANCAVEL", "caminho": []}
    caminho = resultado.caminho_ate(destino)
    custo = resultado.distancias[destino]
    if algoritmo == "BFS":
        custo = sum(custo_dijkstra(resultado.predecessores[v].peso) for v in caminho[1:])
    return {"status": "OK", "caminho": caminho, "passos": len(caminho) - 1, "custo": custo}


def gerar_experimentos(rede, pares):
    experimentos = {}
    for fonte, destinos in pares.items():
        resultados = [rede.executar(algoritmo, fonte, destinos) for algoritmo in ALGORITMOS]
        experimentos[fonte] = {"resultados": resultados, "grafo": rede.amostra(fonte, destinos, resultados)}
        print(f"Fonte {fonte}: quatro algoritmos, {len(destinos)} destinos.", flush=True)
    return experimentos


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Registra explorações reais para reprodução offline.")
    parser.add_argument("--out", type=Path, default=SAIDAS / "execucoes_interativas.json")
    args = parser.parse_args()
    dados = gerar_experimentos(RedeBitcoin(), pares_publicados())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
