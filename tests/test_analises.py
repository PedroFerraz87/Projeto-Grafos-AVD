# [IA] Claude (Anthropic) - testes da T23, T24 e T30 gerados a pedido do Luca; revisar e declarar.
import csv
import json
from pathlib import Path

import pytest

from src import analises
from src.solve import analisar

MAPAS = Path(__file__).parent.parent / "data" / "mapas"


@pytest.fixture(scope="module")
def lista():
    nomes = ["m02_uma_chave", "m03_tres_chaves", "m04_esteiras", "m05_bonus", "m07_impossivel", "m08_grande"]
    return [analisar(MAPAS / f"{nome}.txt") for nome in nomes]


@pytest.fixture(scope="module")
def saida(lista, tmp_path_factory):
    pasta = tmp_path_factory.mktemp("out")
    analises.gerar_metricas(lista, pasta)
    analises.gerar_comparacao(lista, pasta)
    return pasta


def ler_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


# ---------- T23 ----------

def test_teto_teorico():
    # 3 casas livres, 1 chave, 1 bônus: 3 × 2 × 2
    assert analises.teto_teorico(["#####", "#Sa+#", "#####"]) == 12
    assert analises.teto_teorico(["####", "#SG#", "####"]) == 2


def test_metricas_global_tem_as_chaves_do_contrato(saida):
    dados = json.loads((saida / "metricas_global.json").read_text(encoding="utf-8"))
    m02 = dados["mapas"]["m02_uma_chave"]
    assert set(m02["G_pos"]) == {"ordem", "tamanho", "densidade"}
    esperado = {"ordem", "tamanho", "densidade", "teto_teorico", "taxa_ocupacao", "grau_saida", "grau_entrada",
                "maior_grau_saida", "maior_grau_entrada", "becos", "multiplicidade", "camadas",
                "arcos_entre_camadas", "armadilhas", "pct_armadilhas", "dfs", "rankings"}
    assert set(m02["G_est"]) == esperado
    assert m02["G_est"]["ordem"] == 39 and m02["G_est"]["camadas"] == 2
    assert m02["G_est"]["arcos_entre_camadas"] == 1
    assert 0 < m02["G_est"]["taxa_ocupacao"] <= 1


def test_m07_todo_armadilha_e_m04_tem_becos(saida):
    mapas = json.loads((saida / "metricas_global.json").read_text(encoding="utf-8"))["mapas"]
    assert mapas["m07_impossivel"]["G_est"]["pct_armadilhas"] == 100.0
    assert mapas["m04_esteiras"]["G_est"]["becos"] > 0


def test_rankings_ordenados(saida):
    mapas = json.loads((saida / "metricas_global.json").read_text(encoding="utf-8"))["mapas"]
    rankings = mapas["m08_grande"]["G_est"]["rankings"]
    graus = [item["grau"] for item in rankings["grau_saida"]]
    assert len(graus) == analises.TAMANHO_RANKING and graus == sorted(graus, reverse=True)
    assert rankings["multiplicidade"][0]["estados"] == mapas["m08_grande"]["G_est"]["multiplicidade"]["max"]


def test_graus_csv_bate_com_o_tamanho(saida, lista):
    linhas = ler_csv(saida / "graus_m02.csv")
    assert list(linhas[0]) == analises.COLUNAS_GRAUS
    assert len(linhas) == 39 and all(l["estado"] != "ALVO" for l in linhas)
    assert sum(int(l["grau_saida"]) for l in linhas) == lista[0]["tamanho"]
    assert {l["beco"] for l in linhas} <= {"true", "false"}


def test_multiplicidade_m08_uma_linha_por_casa_livre(saida, lista):
    grade = lista[-1]["grade"]
    linhas = ler_csv(saida / "multiplicidade_m08.csv")
    assert len(linhas) == sum(s != "#" for texto in grade for s in texto)
    assert sum(int(l["multiplicidade"]) for l in linhas) == lista[-1]["ordem"]


def test_camadas_json(saida):
    camadas = json.loads((saida / "camadas.json").read_text(encoding="utf-8"))
    m02 = camadas["m02_uma_chave"]
    assert [c["camada"] for c in m02["camadas"]] == ["-", "a"]
    assert m02["arcos_entre_camadas"] == [{"de": "-", "para": "a", "quantidade": 1, "casas": [[3, 11]]}]


# ---------- T24 ----------

def test_validar_percurso():
    grade = ["#######", "#SaA.G#", "#######"]
    assert analises.validar_percurso(grade, [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)]) == (True, "")
    valido, obs = analises.validar_percurso(["######", "#SA.G#", "######"], [(1, 1), (1, 2), (1, 3)])
    assert not valido and "porta A" in obs
    valido, obs = analises.validar_percurso(["######", "#S>.G#", "#....#", "######"], [(1, 2), (2, 2)])
    assert not valido and "esteira" in obs


def test_comparacao_modelagem(saida):
    linhas = ler_csv(saida / "comparacao_modelagem.csv")
    assert list(linhas[0]) == analises.COLUNAS_COMPARACAO
    assert [(l["mapa"], l["abordagem"]) for l in linhas] == [
        (m, a) for m in analises.MAPAS_COMPARACAO for a in ("pos_porta_chao", "pos_porta_parede", "estados")]
    for l in linhas:
        if l["abordagem"] == "estados":
            assert l["caminho_valido"] == "true" and l["passos"]
        if l["abordagem"] == "pos_porta_parede":
            assert l["passos"] == "" and l["observacao"] == "não alcança G"
        if l["abordagem"] == "pos_porta_chao":
            assert l["caminho_valido"] == "false" and "sem a chave" in l["observacao"]


def test_passos_do_g_est_iguais_ao_bfs_do_solve(saida, lista):
    linhas = {l["mapa"]: l for l in ler_csv(saida / "comparacao_modelagem.csv") if l["abordagem"] == "estados"}
    for a in lista:
        if a["nome"] in linhas:
            assert int(linhas[a["nome"]]["passos"]) == a["execucoes"]["BFS"]["passos"]


def test_m05_ciclo_negativo_no_g_pos_e_nao_no_g_est(saida):
    dados = json.loads((saida / "ciclo_negativo_m05_pos.json").read_text(encoding="utf-8"))
    assert dados["modelagem"] == "G_pos" and dados["ciclo_encontrado"]
    assert dados["ciclo"][0] == dados["ciclo"][-1]
    assert dados["custo_ciclo"] == sum(a["peso"] for a in dados["arcos"]) < 0
    assert dados["g_est"]["ciclo_encontrado"] is False and dados["g_est"]["status"] == "OK"


# ---------- T30 ----------

def test_figuras_t30(lista, tmp_path):
    from src.viz_analises import gerar_figuras_t30
    gerados = gerar_figuras_t30(lista, tmp_path)
    assert [p.name for p in gerados] == ["g_est_camadas_m02.png", "heatmap_multiplicidade_m08.png"]
    for p in gerados:
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
