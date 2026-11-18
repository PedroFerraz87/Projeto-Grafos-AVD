import csv
import json
import time
from pathlib import Path

from .graphs.algorithms import bellman_ford, bfs, dfs, dijkstra, estados_armadilha
from .graphs.estados import construir_g_est, nome_curto
from .graphs.io import ler_mapa
from .graphs.metricas import arcos_entre_camadas, camadas, decompor_rotulo, ordem, tamanho

ALGORITMOS = ["BFS", "DIJKSTRA", "BELLMAN_FORD"]
TODOS = ["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"]

ARMADILHAS_OBRIGATORIAS = ["m04", "m07"]

COLUNAS_SOLUCOES = ["mapa", "algoritmo", "passos", "custo", "status", "caminho", "ordem", "tamanho",
                    "estados_visitados", "tempo_ms", "observacao"]
COLUNAS_ARMADILHAS = ["mapa", "estado", "linha", "coluna", "chaves", "simbolo", "distancia_bfs"]
COLUNAS_DFS = ["mapa", "arvore", "retorno", "avanco", "cruzamento", "possui_ciclo"]


# ---------- localizar mapas ----------

def listar_mapas(raiz):
    pastas = [Path(raiz) / "data" / "mapas", Path(raiz) / "data" / "mapas_grupo"]
    return sorted((m.resolve() for pasta in pastas for m in pasta.glob("*.txt")), key=lambda m: m.stem)


def caminho_mapa(raiz, mapa):
    if Path(mapa).is_file():
        return Path(mapa).resolve()
    for arquivo in listar_mapas(raiz):
        if mapa in (arquivo.stem, arquivo.name, nome_curto(arquivo)):
            return arquivo
    raise ValueError(f"mapa não encontrado: {mapa!r}")


# ---------- análise de um mapa ----------

def executar(g, inicio, algoritmo):
    funcao = {"BFS": bfs, "DIJKSTRA": dijkstra, "BELLMAN_FORD": bellman_ford}[algoritmo]
    t0 = time.perf_counter()
    try:
        resultado = funcao(g, inicio)
    except ValueError:
        if algoritmo != "DIJKSTRA":
            raise
        return {"status": "RECUSA", "observacao": "arco com peso negativo", "estados": [], "arcos": [],
                "passos": None, "custo": None, "visitados": None, "tempo_ms": None, "resultado": None}
    tempo_ms = round((time.perf_counter() - t0) * 1000, 3)

    observacao = ""
    if "ALVO" in getattr(resultado, "afetados", ()):
        status, observacao = "CICLO_NEGATIVO", "ciclo negativo alcança ALVO"
    elif "ALVO" not in resultado.distancias:
        status, observacao = "SEM_SOLUCAO", "ALVO inalcançável"
    else:
        status = "OK"
        if getattr(resultado, "ciclo_negativo", ()):
            observacao = "há ciclo negativo, mas ele não alcança ALVO"

    estados = resultado.caminho_ate("ALVO")[:-1] if status == "OK" else []
    arcos = [resultado.predecessores[v] for v in estados[1:]]
    return {"status": status, "observacao": observacao, "estados": estados, "arcos": arcos,
            "passos": len(arcos) if estados else None, "custo": sum(a.peso for a in arcos) if estados else None,
            "visitados": len(resultado.distancias) - ("ALVO" in resultado.distancias), "tempo_ms": tempo_ms,
            "resultado": resultado}


def classificar_dfs(g, inicio):
    contagem = {"arvore": 0, "retorno": 0, "avanco": 0, "cruzamento": 0}
    for arco, classe in dfs(g, inicio).arcos_classificados:
        if arco.destino != "ALVO":
            contagem[classe] += 1
    return {**contagem, "possui_ciclo": contagem["retorno"] > 0}


def linhas_armadilhas(nome, grade, g, inicio):
    linhas = []
    for estado, distancia in estados_armadilha(g, inicio).items():
        l, c, chaves, _ = decompor_rotulo(estado)
        linhas.append({"mapa": nome, "estado": estado, "linha": l, "coluna": c, "chaves": chaves,
                       "simbolo": grade[l][c], "distancia_bfs": distancia})
    return sorted(linhas, key=lambda x: (x["linha"], x["coluna"], x["chaves"]))


def analisar(caminho, fonte_consumivel=False):
    caminho = Path(caminho)
    grade = ler_mapa(caminho)
    g = construir_g_est(grade)
    inicio = g.vertices()[0]
    a = {"nome": caminho.stem, "curto": nome_curto(caminho), "grade": grade, "g": g, "inicio": inicio,
         "fonte_consumivel": fonte_consumivel, "ordem": ordem(g), "tamanho": tamanho(g)}
    a["execucoes"] = {alg: executar(g, inicio, alg) for alg in ALGORITMOS}
    a["dfs"] = classificar_dfs(g, inicio)
    a["armadilhas"] = linhas_armadilhas(a["nome"], grade, g, inicio)
    if fonte_consumivel:
        g1 = construir_g_est(grade, True)
        a["custo_corrigido"] = executar(g1, g1.vertices()[0], "BELLMAN_FORD")["custo"]
    return a


# ---------- montagem das saídas ----------

def linha_solucao(a, algoritmo):
    e = a["execucoes"][algoritmo]
    return {"mapa": a["nome"], "algoritmo": algoritmo, "passos": e["passos"], "custo": e["custo"],
            "status": e["status"], "caminho": " > ".join(e["estados"]), "ordem": a["ordem"],
            "tamanho": a["tamanho"], "estados_visitados": e["visitados"], "tempo_ms": e["tempo_ms"],
            "observacao": e["observacao"]}


def _evento(i, simbolo, anterior, atual):
    if i == 0:
        return "inicio"
    if simbolo == "G":
        return "chegada"
    if simbolo in "abcd" and simbolo not in anterior[2]:
        return f"chave_{simbolo}"
    if simbolo in "ABCD":
        return f"porta_{simbolo}"
    if simbolo == "+" and len(atual[3]) > len(anterior[3]):
        return "bonus"
    if simbolo == "*":
        return "fonte"
    if simbolo in "><^v":
        return "esteira"
    return None


def montar_percurso(a, algoritmo):
    e = a["execucoes"][algoritmo]
    encontrou = e["status"] == "OK"
    passos, acumulado, anterior = [], 0, None
    for i, estado in enumerate(e["estados"]):
        atual = decompor_rotulo(estado)
        arco = e["arcos"][i - 1] if i else None
        peso = arco.peso if arco else 0
        acumulado += peso
        passos.append({"passo": i, "estado": estado, "linha": atual[0], "coluna": atual[1],
                       "chaves": "" if atual[2] == "-" else atual[2], "bonus": list(atual[3]), "camada": atual[2],
                       "movimento": arco.metadados["movimento"] if arco else None, "peso": peso,
                       "custo_acumulado": acumulado,
                       "evento": _evento(i, arco.metadados["casa_destino"] if arco else "", anterior, atual)})
        anterior = atual
    return {"mapa": a["nome"], "algoritmo": algoritmo, "modelagem": "G_est",
            "opcoes": {"fonte_consumivel": False, "porta_como": "parede"},
            "grade": a["grade"], "inicio": a["inicio"], "fim": "ALVO", "encontrou": encontrou,
            "status": e["status"], "observacao": e["observacao"],
            "passos": e["passos"], "custo": e["custo"], "percurso": passos}


def montar_ciclo(a):
    bf = a["execucoes"]["BELLMAN_FORD"]["resultado"]
    arcos = list(bf.ciclo_negativo)
    ciclo = {"mapa": a["nome"], "modelagem": "G_est", "algoritmo": "BELLMAN_FORD",
             "opcoes": {"fonte_consumivel": a["fonte_consumivel"]}, "fonte": bf.fonte,
             "ciclo_encontrado": bool(arcos),
             "ciclo": [arcos[0].origem] + [x.destino for x in arcos] if arcos else [],
             "arcos": [{"origem": x.origem, "destino": x.destino, "peso": x.peso,
                        "movimento": x.metadados["movimento"]} for x in arcos],
             "custo_ciclo": sum(x.peso for x in arcos) if arcos else None,
             "afeta_alvo": "ALVO" in bf.afetados,
             "correcao": {"aplicada": False, "descricao": None, "custo_minimo_apos_correcao": None}}
    if a["fonte_consumivel"]:
        ciclo["correcao"] = {"aplicada": True,
                             "descricao": "a fonte vale -2 só na primeira vez em que o estado entra nela; depois custa 1",
                             "custo_minimo_apos_correcao": a["custo_corrigido"]}
    return ciclo


def algoritmo_do_percurso(a, algoritmos):
    candidatos = [alg for alg in ("DIJKSTRA", "BELLMAN_FORD", "BFS") if alg in algoritmos]
    return next((alg for alg in candidatos if a["execucoes"][alg]["status"] == "OK"),
                candidatos[0] if candidatos else None)


def dados_interativos(analises, mapa_inicial):
    mapas = {}
    for a in analises:
        mapas[a["nome"]] = {
            "grade": a["grade"],
            "inicio": a["inicio"],
            "percursos": {alg: montar_percurso(a, alg) for alg in ALGORITMOS},
            "armadilhas": a["armadilhas"],
            "camadas": [{"camada": nome, "casas": [list(p) for p in sorted({decompor_rotulo(v)[:2] for v in estados})]}
                        for nome, estados in camadas(a["g"]).items()],
            "trocas_de_camada": arcos_entre_camadas(a["g"]),
        }
    return {"mapa_inicial": mapa_inicial, "algoritmos": ALGORITMOS, "mapas": mapas}


# ---------- escrita ----------

def _celula(valor):
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return str(valor).lower()
    return valor


def escrever_csv(caminho, colunas, linhas):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo, lineterminator="\n")
        escritor.writerow(colunas)
        for linha in linhas:
            escritor.writerow([_celula(linha[c]) for c in colunas])


def escrever_json(caminho, objeto):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(json.dumps(objeto, ensure_ascii=False, indent=2) + "\n")


def gerar_saidas(analises, out, algoritmos=TODOS, armadilhas=False):
    out, escritos = Path(out), []

    def gravar(nome, escrever, *args):
        escrever(out / nome, *args)
        escritos.append(out / nome)

    linhas = [linha_solucao(a, alg) for a in analises for alg in ALGORITMOS if alg in algoritmos]
    if linhas:
        gravar("solucoes.csv", escrever_csv, COLUNAS_SOLUCOES, linhas)
    if "DFS" in algoritmos:
        gravar("dfs_classificacao.csv", escrever_csv, COLUNAS_DFS, [{"mapa": a["nome"], **a["dfs"]} for a in analises])
    for a in analises:
        alg = algoritmo_do_percurso(a, algoritmos)
        if alg:
            gravar(f"percurso_{a['curto']}.json", escrever_json, montar_percurso(a, alg))
        if "BELLMAN_FORD" in algoritmos and a["execucoes"]["BELLMAN_FORD"]["resultado"].ciclo_negativo:
            gravar(f"ciclo_negativo_{a['curto']}.json", escrever_json, montar_ciclo(a))
        if armadilhas or a["curto"] in ARMADILHAS_OBRIGATORIAS:
            gravar(f"armadilhas_{a['curto']}.csv", escrever_csv, COLUNAS_ARMADILHAS, a["armadilhas"])
    return escritos
