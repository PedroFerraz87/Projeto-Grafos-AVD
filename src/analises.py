import argparse
from datetime import datetime
from pathlib import Path

from .graphs import metricas
from .graphs.algorithms import bellman_ford, bfs
from .graphs.estados import SETA, construir_g_pos, rotulo_pos
from .graphs.io import ler_mapa
from .solve import analisar, escrever_csv, escrever_json, listar_mapas

RAIZ = Path(__file__).resolve().parents[1]
MAPAS = RAIZ / "data" / "mapas"

COLUNAS_GRAUS = ["estado", "grau_entrada", "grau_saida", "linha", "coluna", "camada", "beco"]
COLUNAS_MULTIPLICIDADE = ["linha", "coluna", "simbolo", "multiplicidade"]
COLUNAS_COMPARACAO = ["mapa", "abordagem", "passos", "caminho_valido", "observacao"]
MAPAS_COMPARACAO = ["m02_uma_chave", "m03_tres_chaves", "m04_esteiras"]
TAMANHO_RANKING = 5

def teto_teorico(grade):
    texto = "".join(grade)
    livres = sum(1 for s in texto if s != "#")
    return livres * 2 ** len(set(texto) & set("abcd")) * 2 ** texto.count("+")

def bloco_g_pos(grade):
    g = construir_g_pos(grade)
    return {"ordem": metricas.ordem(g), "tamanho": metricas.tamanho(g), "densidade": metricas.densidade(g)}

def bloco_g_est(a):
    g, ordem = a["g"], a["ordem"]
    saida, entrada = metricas.graus_saida(g), metricas.graus_entrada(g)
    mult = metricas.multiplicidade(g)
    teto = teto_teorico(a["grade"])
    return {
        "ordem": ordem,
        "tamanho": a["tamanho"],
        "densidade": metricas.densidade(g),
        "teto_teorico": teto,
        "taxa_ocupacao": ordem / teto if teto else 0.0,
        "grau_saida": metricas.resumo_graus(saida),
        "grau_entrada": metricas.resumo_graus(entrada),
        "maior_grau_saida": metricas.maior_grau(saida),
        "maior_grau_entrada": metricas.maior_grau(entrada),
        "becos": len(metricas.becos(g)),
        "multiplicidade": metricas.resumo_multiplicidade(mult),
        "camadas": len(metricas.camadas(g)),
        "arcos_entre_camadas": metricas.n_arcos_entre_camadas(g),
        "armadilhas": len(a["armadilhas"]),
        "pct_armadilhas": 100 * len(a["armadilhas"]) / ordem if ordem else 0.0,
        "dfs": a["dfs"],
        "rankings": {
            "grau_saida": metricas.ranking_graus(saida, TAMANHO_RANKING),
            "grau_entrada": metricas.ranking_graus(entrada, TAMANHO_RANKING),
            "multiplicidade": metricas.ranking_multiplicidade(mult, TAMANHO_RANKING),
        },
    }

def linhas_graus(g):
    saida, entrada = metricas.graus_saida(g), metricas.graus_entrada(g)
    becos = set(metricas.becos(g))
    linhas = []
    for estado in saida:
        l, c = metricas.posicao(estado)
        linhas.append({"estado": estado, "grau_entrada": entrada[estado], "grau_saida": saida[estado],
                       "linha": l, "coluna": c, "camada": metricas.camada(estado), "beco": estado in becos})
    return linhas

def linhas_multiplicidade(grade, g):
    mult = metricas.multiplicidade(g)
    return [{"linha": l, "coluna": c, "simbolo": s, "multiplicidade": mult.get((l, c), 0)}
            for l, texto in enumerate(grade) for c, s in enumerate(texto) if s != "#"]

def gerar_metricas(analises, out):
    out, escritos = Path(out), []
    globais, por_camada = {}, {}
    for a in analises:
        globais[a["nome"]] = {"G_pos": bloco_g_pos(a["grade"]), "G_est": bloco_g_est(a)}
        por_camada[a["nome"]] = {"camadas": metricas.metricas_camadas(a["g"]),
                                 "arcos_entre_camadas": metricas.arcos_entre_camadas(a["g"])}
        escrever_csv(out / f"graus_{a['curto']}.csv", COLUNAS_GRAUS, linhas_graus(a["g"]))
        escritos.append(out / f"graus_{a['curto']}.csv")
        if a["curto"] == "m08":
            escrever_csv(out / "multiplicidade_m08.csv", COLUNAS_MULTIPLICIDADE,
                         linhas_multiplicidade(a["grade"], a["g"]))
            escritos.append(out / "multiplicidade_m08.csv")

    escrever_json(out / "metricas_global.json",
                  {"gerado_em": datetime.now().isoformat(timespec="seconds"), "mapas": globais})
    escrever_json(out / "camadas.json", por_camada)
    return escritos + [out / "metricas_global.json", out / "camadas.json"]

def validar_percurso(grade, casas):
    deslocamento = {"N": (-1, 0), "L": (0, 1), "S": (1, 0), "O": (0, -1)}
    chaves = set()
    for (l, c), (nl, nc) in zip(casas, casas[1:]):
        origem, destino = grade[l][c], grade[nl][nc]
        if origem in SETA and (nl - l, nc - c) != deslocamento[SETA[origem]]:
            return False, f"sai da esteira {origem} em ({l},{c}) contra a seta"
        if destino in "ABCD" and destino.lower() not in chaves:
            return False, f"atravessa a porta {destino} em ({nl},{nc}) sem a chave {destino.lower()}"
        if destino in "abcd":
            chaves.add(destino)
    return True, ""

def _casas_do_objetivo(grade):
    return [(l, c) for l, texto in enumerate(grade) for c, s in enumerate(texto) if s == "G"]

def comparar_g_pos(nome, grade, porta_como):
    g = construir_g_pos(grade, porta_como)
    inicio = next((l, c) for l, texto in enumerate(grade) for c, s in enumerate(texto) if s == "S")
    resultado = bfs(g, rotulo_pos(*inicio))
    alcancados = [casa for casa in _casas_do_objetivo(grade) if rotulo_pos(*casa) in resultado.distancias]
    linha = {"mapa": nome, "abordagem": f"pos_porta_{porta_como}"}
    if not alcancados:
        return {**linha, "passos": None, "caminho_valido": False, "observacao": "não alcança G"}
    alvo = min(alcancados, key=lambda casa: (resultado.distancias[rotulo_pos(*casa)], casa))
    casas = [metricas.posicao(v) for v in resultado.caminho_ate(rotulo_pos(*alvo))]
    valido, observacao = validar_percurso(grade, casas)
    return {**linha, "passos": len(casas) - 1, "caminho_valido": valido, "observacao": observacao}

def comparar_g_est(a):
    linha = {"mapa": a["nome"], "abordagem": "estados"}
    resultado = bfs(a["g"], a["inicio"])
    if "ALVO" not in resultado.distancias:
        return {**linha, "passos": None, "caminho_valido": False, "observacao": "não alcança G"}
    casas = [metricas.posicao(v) for v in resultado.caminho_ate("ALVO")[:-1]]
    valido, observacao = validar_percurso(a["grade"], casas)
    return {**linha, "passos": len(casas) - 1, "caminho_valido": valido, "observacao": observacao}

def linhas_comparacao(analises):
    linhas = []
    for a in analises:
        if a["nome"] in MAPAS_COMPARACAO:
            linhas += [comparar_g_pos(a["nome"], a["grade"], "chao"),
                       comparar_g_pos(a["nome"], a["grade"], "parede"),
                       comparar_g_est(a)]
    return linhas

def ciclo_m05_pos(a_m05):
    grade = a_m05["grade"]
    g = construir_g_pos(grade)
    inicio = next((l, c) for l, texto in enumerate(grade) for c, s in enumerate(texto) if s == "S")
    bf = bellman_ford(g, rotulo_pos(*inicio))
    arcos = list(bf.ciclo_negativo)
    objetivos = {rotulo_pos(*casa) for casa in _casas_do_objetivo(grade)}
    est = a_m05["execucoes"]["BELLMAN_FORD"]
    return {
        "mapa": a_m05["nome"],
        "modelagem": "G_pos",
        "algoritmo": "BELLMAN_FORD",
        "opcoes": {"fonte_consumivel": False, "porta_como": "parede"},
        "fonte": bf.fonte,
        "ciclo_encontrado": bool(arcos),
        "ciclo": [arcos[0].origem] + [x.destino for x in arcos] if arcos else [],
        "arcos": [{"origem": x.origem, "destino": x.destino, "peso": x.peso,
                   "movimento": x.metadados["movimento"]} for x in arcos],
        "custo_ciclo": sum(x.peso for x in arcos) if arcos else None,
        "afeta_alvo": bool(objetivos & bf.afetados),
        "correcao": {"aplicada": False, "descricao": None, "custo_minimo_apos_correcao": None},
        # extra do grupo (T24): o mesmo mapa no G_est, onde cada bônus só vale -4 uma vez
        "g_est": {"ciclo_encontrado": bool(est["resultado"].ciclo_negativo), "status": est["status"],
                  "passos": est["passos"], "custo_minimo": est["custo"]},
    }


def gerar_comparacao(analises, out):
    out, escritos = Path(out), []
    escrever_csv(out / "comparacao_modelagem.csv", COLUNAS_COMPARACAO, linhas_comparacao(analises))
    escritos.append(out / "comparacao_modelagem.csv")
    m05 = next((a for a in analises if a["curto"] == "m05"), None)
    if m05:
        escrever_json(out / "ciclo_negativo_m05_pos.json", ciclo_m05_pos(m05))
        escritos.append(out / "ciclo_negativo_m05_pos.json")
    return escritos

def gerar_tudo(out, raiz=RAIZ, figuras=True):
    analises = [analisar(caminho) for caminho in listar_mapas(raiz)]
    escritos = gerar_metricas(analises, out) + gerar_comparacao(analises, out)
    if figuras:
        from .viz_analises import gerar_figuras_t30
        escritos += gerar_figuras_t30(analises, out)
    return escritos

def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m src.analises",
                                     description="Gera as análises da Parte 1 (T23, T24 e T30) em out/parte1.")
    parser.add_argument("--out", default=str(RAIZ / "out" / "parte1"), help="pasta de saída")
    parser.add_argument("--sem-figuras", action="store_true", help="não gera os PNG da T30")
    args = parser.parse_args(argv)
    for arquivo in gerar_tudo(Path(args.out), figuras=not args.sem_figuras):
        print(arquivo)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
