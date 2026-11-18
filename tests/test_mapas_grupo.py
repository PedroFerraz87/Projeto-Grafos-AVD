# Mapas definitivos do grupo (data/mapas_grupo/m1.txt e m2.txt) e as saídas de out/parte1 que dependem deles.
# m2: números contados à mão. m1: custo conferido com networkx e somado pela grade (ver os testes).
import csv
import json
from pathlib import Path

import pytest

from src.graphs.io import ler_mapa
from src.solve import (ALGORITMOS, analisar, linha_solucao, listar_mapas, montar_percurso)

RAIZ = Path(__file__).parent.parent
GRUPO = RAIZ / "data" / "mapas_grupo"
OUT = RAIZ / "out" / "parte1"


@pytest.fixture(scope="module")
def m1():
    return analisar(GRUPO / "m1.txt")


@pytest.fixture(scope="module")
def m2():
    return analisar(GRUPO / "m2.txt")


def ler(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


# ---------- os arquivos ----------

def test_sao_exatamente_dois_mapas():
    assert sorted(p.name for p in GRUPO.glob("*.txt")) == ["m1.txt", "m2.txt"]


@pytest.mark.parametrize("nome", ["m1", "m2"])
def test_mapa_valido_e_sem_marca_de_rascunho(nome):
    ler_mapa(GRUPO / f"{nome}.txt")  # levanta MapaInvalido se algo estiver errado
    texto = (GRUPO / f"{nome}.txt").read_text(encoding="utf-8")
    assert texto.startswith(f"; {nome} - ") and texto.isascii()
    assert "T21" not in texto and "rascunho" not in texto.lower()


# ---------- m1: mapa com chaves, esteiras e bônus ----------
# O enunciado pede pelo menos 3 chaves, esteiras e bônus, e que o caminho de menor custo colete um
# bônus e passe por uma esteira.

CUSTOS = {**dict.fromkeys(".SGabcABC><^v", 1), ",": 3, "~": 5}


def custo_pela_grade(grade, posicoes):
    """Soma o custo de um percurso lendo só a grade (sem o grafo): o bônus vale -4 na 1ª vez e 1 depois."""
    total, colhidos = 0, set()
    for l, c in posicoes[1:]:
        if grade[l][c] == "+":
            total += 1 if (l, c) in colhidos else -4
            colhidos.add((l, c))
        else:
            total += CUSTOS[grade[l][c]]
    return total


def test_m1_atende_o_enunciado():
    grade = ler_mapa(GRUPO / "m1.txt")
    texto = "".join(grade)
    assert all(c in texto for c in "abcABC")  # 3 chaves, cada uma com a sua porta
    assert sum(texto.count(c) for c in "><^v") >= 3 and texto.count("+") >= 3
    assert len(grade) >= 8 and len(grade[0]) >= 25  # espaço para decisões; não é um corredor


def test_m1_caminho_de_menor_custo_coleta_bonus_e_passa_por_esteira(m1):
    eventos = [x["evento"] for x in montar_percurso(m1, "BELLMAN_FORD")["percurso"]]
    assert eventos.count("bonus") >= 1 and eventos.count("esteira") >= 1
    assert sorted(e[-1] for e in eventos if e and e.startswith("chave_")) == ["a", "b", "c"]


def test_m1_custo_minimo_confere_com_networkx_e_com_a_soma_pela_grade(m1):
    import networkx as nx
    grafo = nx.DiGraph()
    for arco in m1["g"].arcos():
        grafo.add_edge(arco.origem, arco.destino, weight=arco.peso)
    assert nx.bellman_ford_path_length(grafo, m1["inicio"], "ALVO") == 42  # oráculo independente
    p = montar_percurso(m1, "BELLMAN_FORD")
    assert custo_pela_grade(m1["grade"], [(x["linha"], x["coluna"]) for x in p["percurso"]]) == p["custo"] == 42


def test_m1_menos_passos_nao_e_menor_custo(m1):
    bfs, bf = linha_solucao(m1, "BFS"), linha_solucao(m1, "BELLMAN_FORD")
    assert (bfs["passos"], bfs["custo"]) == (46, 49) and (bf["passos"], bf["custo"]) == (52, 42)
    assert linha_solucao(m1, "DIJKSTRA")["status"] == "RECUSA"  # há bônus (peso negativo)


def test_m1_percurso_otimo_passo_a_passo(m1):
    p = montar_percurso(m1, "BELLMAN_FORD")["percurso"]
    assert [(x["evento"], x["linha"], x["coluna"]) for x in p if x["evento"] is not None] == [
        ("inicio", 4, 1), ("chave_a", 1, 4), ("bonus", 5, 6), ("porta_A", 4, 9),
        ("esteira", 2, 14), ("esteira", 2, 15), ("esteira", 2, 16), ("esteira", 2, 17),
        ("chave_b", 7, 19), ("porta_B", 4, 22), ("bonus", 2, 25), ("chave_c", 1, 25),
        ("porta_C", 4, 28), ("chegada", 4, 29)]
    assert (7, 21) not in {(x["linha"], x["coluna"]) for x in p}  # o bônus-isca custaria +1: não compensa


def test_m1_contagens(m1):
    # conferidas com uma segunda implementação do G_est escrita à parte (a mesma usada nos mapas fornecidos)
    assert (m1["ordem"], m1["tamanho"]) == (1904, 3752)  # estados e arcos, sem os arcos G -> ALVO
    assert m1["armadilhas"] == []  # todo estado ainda chega a G


# ---------- m2: mapa armadilha ----------

def test_m2_contagens_a_mao(m2):
    # estados: 5 (corredor) + G + (2,3) + 6 esteiras = 13
    # arcos: 9 (corredor; G sem saída) + 2 (ramal) + 1 (entrada na esteira) + 5 (esteira para a direita) = 17
    assert (m2["ordem"], m2["tamanho"]) == (13, 17)
    for alg in ALGORITMOS:
        s = linha_solucao(m2, alg)
        assert (s["status"], s["passos"], s["custo"]) == ("OK", 5, 5)


def test_m2_armadilhas_sao_as_seis_esteiras(m2):
    assert [(x["linha"], x["coluna"], x["simbolo"]) for x in m2["armadilhas"]] == [(3, c, ">") for c in range(3, 9)]
    assert round(100 * len(m2["armadilhas"]) / m2["ordem"], 2) == 46.15  # percentual da tabela 2.6 do relatório


# ---------- as saídas de out/parte1 estão em dia com os mapas ----------

def test_saidas_do_grupo_existem_em_out_parte1():
    for nome in ("m1", "m2"):
        assert (OUT / f"arestas_{nome}.csv").exists() and (OUT / f"percurso_{nome}.json").exists()


def test_solucoes_e_dfs_cobrem_todos_os_mapas_e_estao_em_dia():
    analises = {m.stem: analisar(m) for m in listar_mapas(RAIZ)}
    sem_tempo = lambda linha: {k: v for k, v in linha.items() if k != "tempo_ms"}
    esperado = [sem_tempo({k: ("" if v is None else str(v)) for k, v in linha_solucao(a, alg).items()})
                for a in analises.values() for alg in ALGORITMOS]
    assert [sem_tempo(r) for r in ler(OUT / "solucoes.csv")] == esperado
    dfs = {r["mapa"]: r for r in ler(OUT / "dfs_classificacao.csv")}
    assert list(dfs) == list(analises)
    for nome, a in analises.items():
        assert {k: dfs[nome][k] for k in ("arvore", "retorno", "avanco", "cruzamento")} == \
            {k: str(a["dfs"][k]) for k in ("arvore", "retorno", "avanco", "cruzamento")}


@pytest.mark.parametrize("nome", ["m1", "m2"])
def test_percurso_json_do_grupo_em_dia(nome):
    a = analisar(GRUPO / f"{nome}.txt")
    gravado = json.loads((OUT / f"percurso_{nome}.json").read_text(encoding="utf-8"))
    escolhido = "BELLMAN_FORD" if nome == "m1" else "DIJKSTRA"  # m1: o Dijkstra recusa o bônus
    assert gravado == json.loads(json.dumps(montar_percurso(a, escolhido)))
