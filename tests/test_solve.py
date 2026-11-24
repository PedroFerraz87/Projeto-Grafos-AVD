# [IA] Claude (Anthropic)
# Testes do T22 (solve.py e cli.py da Parte 1).
import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

import src.viz as viz
from src import cli
from src.graphs.algorithms import bfs
from src.graphs.metricas import tamanho
from src.solve import (ALGORITMOS, analisar, caminho_mapa, dados_interativos, gerar_saidas, linha_solucao,
                       listar_mapas, montar_ciclo, montar_percurso)

RAIZ = Path(__file__).parent.parent
MAPAS = RAIZ / "data" / "mapas"


@pytest.fixture(scope="module")
def mapas():
    return {m.stem: analisar(m) for m in sorted(MAPAS.glob("m0*.txt"))}


def solucao(a, algoritmo):
    return linha_solucao(a, algoritmo)


def ler(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


# ---------- localizar mapas ----------

@pytest.mark.parametrize("nome", ["m03", "m03_tres_chaves", "m03_tres_chaves.txt", str(MAPAS / "m03_tres_chaves.txt")])
def test_caminho_mapa_aceita_nome_curto_completo_e_caminho(nome):
    assert caminho_mapa(RAIZ, nome) == (MAPAS / "m03_tres_chaves.txt").resolve()


def test_caminho_mapa_desconhecido():
    with pytest.raises(ValueError, match="m99"):
        caminho_mapa(RAIZ, "m99")


def test_listar_mapas_inclui_os_8_fornecidos_em_ordem():
    nomes = [m.stem for m in listar_mapas(RAIZ)]
    assert nomes[:8] == sorted(nomes[:8]) and nomes[0] == "m01_terreno" and nomes[7] == "m08_grande"


# ---------- solucoes.csv ----------

def test_m02_os_tres_algoritmos_batem_com_o_T04(mapas):
    for alg in ALGORITMOS:
        s = solucao(mapas["m02_uma_chave"], alg)
        assert (s["status"], s["passos"], s["custo"]) == ("OK", 34, 46)
        assert (s["ordem"], s["tamanho"], s["estados_visitados"]) == (39, 74, 39)
    caminho = solucao(mapas["m02_uma_chave"], "BFS")["caminho"]
    assert caminho.startswith("(1,1)|-|{} > ") and caminho.endswith("(1,11)|a|{}")
    assert "ALVO" not in caminho and caminho.count(" > ") == 34


def test_m01_menos_passos_nao_e_menor_custo(mapas):
    # contas à mão: pela linha de cima são 10 passos e custo 30 (5 casas de água); por baixo, 14 passos e custo 20
    a = mapas["m01_terreno"]
    assert (solucao(a, "BFS")["passos"], solucao(a, "BFS")["custo"]) == (10, 30)
    assert (solucao(a, "DIJKSTRA")["passos"], solucao(a, "DIJKSTRA")["custo"]) == (14, 20)


def test_m05_dijkstra_recusa_e_bellman_ford_aproveita_o_bonus(mapas):
    a = mapas["m05_bonus"]
    recusa = solucao(a, "DIJKSTRA")
    assert recusa["status"] == "RECUSA" and recusa["observacao"] == "arco com peso negativo"
    assert all(recusa[c] is None for c in ("passos", "custo", "estados_visitados", "tempo_ms"))
    assert recusa["caminho"] == "" and recusa["ordem"] == a["ordem"]
    assert solucao(a, "BELLMAN_FORD")["status"] == "OK"
    assert solucao(a, "BELLMAN_FORD")["custo"] < solucao(a, "BFS")["custo"]


def test_m06_ciclo_negativo_alcanca_alvo(mapas):
    a = mapas["m06_fonte"]
    bf = solucao(a, "BELLMAN_FORD")
    assert bf["status"] == "CICLO_NEGATIVO"
    assert all(bf[c] is None for c in ("passos", "custo")) and bf["caminho"] == ""
    assert bf["estados_visitados"] == a["ordem"]
    assert solucao(a, "DIJKSTRA")["status"] == "RECUSA"
    assert (solucao(a, "BFS")["passos"], solucao(a, "BFS")["custo"]) == (10, 10)  # a linha de cima, à mão


def test_m06_fonte_consumivel_so_calcula_a_correcao_e_nao_muda_as_solucoes(mapas):
    a = analisar(MAPAS / "m06_fonte.txt", fonte_consumivel=True)
    assert a["custo_corrigido"] == 10
    sem_tempo = lambda linha: {k: v for k, v in linha.items() if k != "tempo_ms"}
    for alg in ALGORITMOS:  # as linhas de solucoes.csv são as mesmas, com ou sem a opção
        assert sem_tempo(solucao(a, alg)) == sem_tempo(solucao(mapas["m06_fonte"], alg))
    assert solucao(a, "BELLMAN_FORD")["status"] == "CICLO_NEGATIVO"


def test_m07_sem_solucao_nos_tres_algoritmos(mapas):
    a = mapas["m07_impossivel"]
    for alg in ALGORITMOS:
        s = solucao(a, alg)
        assert (s["status"], s["passos"], s["custo"], s["caminho"]) == ("SEM_SOLUCAO", None, None, "")
        assert s["estados_visitados"] == a["ordem"] == 16 and s["observacao"] == "ALVO inalcançável"


# ---------- percurso_<mapa>.json ----------

def test_percurso_m02_passo_a_passo(mapas):
    p = montar_percurso(mapas["m02_uma_chave"], "DIJKSTRA")
    assert (p["encontrou"], p["passos"], p["custo"], p["fim"], p["modelagem"]) == (True, 34, 46, "ALVO", "G_est")
    assert p["opcoes"] == {"fonte_consumivel": False, "porta_como": "parede"} and p["inicio"] == "(1,1)|-|{}"
    passos = p["percurso"]
    assert len(passos) == 35 and [x["passo"] for x in passos] == list(range(35))
    assert passos[0]["evento"] == "inicio" and passos[0]["movimento"] is None and passos[0]["peso"] == 0
    assert passos[-1]["evento"] == "chegada" and passos[-1]["custo_acumulado"] == 46
    assert [x["evento"] for x in passos if x["evento"] not in (None, "inicio")] == ["chave_a", "porta_A", "chegada"]
    chave = next(x for x in passos if x["evento"] == "chave_a")
    assert (chave["linha"], chave["coluna"], chave["chaves"], chave["camada"]) == (3, 11, "a", "a")
    assert passos[1]["chaves"] == "" and passos[1]["camada"] == "-"
    for antes, depois in zip(passos, passos[1:]):
        assert abs(antes["linha"] - depois["linha"]) + abs(antes["coluna"] - depois["coluna"]) == 1
        assert depois["custo_acumulado"] == antes["custo_acumulado"] + depois["peso"]


def test_percurso_m05_tem_evento_de_bonus_e_indices(mapas):
    p = montar_percurso(mapas["m05_bonus"], "BELLMAN_FORD")
    passos = p["percurso"]
    assert p["encontrou"] and passos[-1]["custo_acumulado"] == p["custo"]
    consumos = [x for x in passos if x["evento"] == "bonus"]
    assert consumos and all(x["peso"] == -4 for x in consumos)
    assert passos[-1]["bonus"] == sorted(passos[-1]["bonus"]) and len(passos[-1]["bonus"]) == len(consumos)


@pytest.mark.parametrize("mapa, algoritmo, status", [("m07_impossivel", "BFS", "SEM_SOLUCAO"),
                                                     ("m06_fonte", "DIJKSTRA", "RECUSA"),
                                                     ("m06_fonte", "BELLMAN_FORD", "CICLO_NEGATIVO")])
def test_percurso_sem_caminho(mapas, mapa, algoritmo, status):
    p = montar_percurso(mapas[mapa], algoritmo)
    assert (p["encontrou"], p["status"], p["percurso"], p["passos"], p["custo"]) == (False, status, [], None, None)


# ---------- ciclo_negativo_m06.json ----------

def test_ciclo_negativo_m06(mapas):
    a = mapas["m06_fonte"]
    c = montar_ciclo(a)
    assert c["ciclo_encontrado"] and c["afeta_alvo"] and c["fonte"] == "(1,1)|-|{}"
    assert c["ciclo"][0] == c["ciclo"][-1] and len(c["ciclo"]) == len(c["arcos"]) + 1  # ciclo fechado
    assert c["custo_ciclo"] == sum(x["peso"] for x in c["arcos"]) < 0
    for x, de, para in zip(c["arcos"], c["ciclo"], c["ciclo"][1:]):
        assert (x["origem"], x["destino"]) == (de, para)
        assert any(r.destino == para and r.peso == x["peso"] for r in a["g"].arcos_saindo(de))  # o arco existe
    assert c["correcao"] == {"aplicada": False, "descricao": None, "custo_minimo_apos_correcao": None}


def test_ciclo_negativo_com_fonte_consumivel_mantem_o_ciclo_e_preenche_a_correcao():
    c = montar_ciclo(analisar(MAPAS / "m06_fonte.txt", fonte_consumivel=True))
    assert c["ciclo_encontrado"] and c["fonte"] == "(1,1)|-|{}" and c["opcoes"] == {"fonte_consumivel": True}
    assert c["correcao"]["aplicada"] is True and c["correcao"]["custo_minimo_apos_correcao"] == 10


def test_mapas_sem_fonte_nao_tem_ciclo(mapas):
    assert [n for n, a in mapas.items() if a["execucoes"]["BELLMAN_FORD"]["resultado"].ciclo_negativo] == ["m06_fonte"]


# ---------- DFS e armadilhas ----------

def test_dfs_as_quatro_classes_somam_o_tamanho(mapas):
    for nome, a in mapas.items():
        d = a["dfs"]
        assert d["arvore"] + d["retorno"] + d["avanco"] + d["cruzamento"] == a["tamanho"] == tamanho(a["g"]), nome
        assert d["possui_ciclo"] == (d["retorno"] > 0)


def test_armadilhas_m07_sao_todos_os_estados_e_m02_nao_tem(mapas):
    assert len(mapas["m07_impossivel"]["armadilhas"]) == mapas["m07_impossivel"]["ordem"] == 16
    assert mapas["m02_uma_chave"]["armadilhas"] == []


def test_armadilhas_m04_nao_chegam_ao_alvo_e_estao_ordenadas(mapas):
    a = mapas["m04_esteiras"]
    linhas = a["armadilhas"]
    assert linhas and linhas == sorted(linhas, key=lambda x: (x["linha"], x["coluna"], x["chaves"]))
    for x in linhas:
        assert "ALVO" not in bfs(a["g"], x["estado"]).distancias
        assert x["simbolo"] == a["grade"][x["linha"]][x["coluna"]] and x["distancia_bfs"] >= 0
        assert x["mapa"] == "m04_esteiras"


# ---------- arquivos gerados ----------

def test_gerar_saidas_formato_e_ordem(mapas, tmp_path):
    escolhidos = [mapas["m02_uma_chave"], mapas["m05_bonus"], mapas["m06_fonte"]]
    escritos = gerar_saidas(escolhidos, tmp_path, armadilhas=True)
    assert {p.name for p in escritos} == {
        "solucoes.csv", "dfs_classificacao.csv", "percurso_m02.json", "percurso_m05.json", "percurso_m06.json",
        "ciclo_negativo_m06.json", "armadilhas_m02.csv", "armadilhas_m05.csv", "armadilhas_m06.csv"}
    bruto = (tmp_path / "solucoes.csv").read_bytes()
    assert not bruto.startswith(b"\xef\xbb\xbf") and b"\r" not in bruto
    assert bruto.decode("utf-8").split("\n")[0] == ("mapa,algoritmo,passos,custo,status,caminho,ordem,tamanho,"
                                                    "estados_visitados,tempo_ms,observacao")
    linhas = ler(tmp_path / "solucoes.csv")
    assert [(r["mapa"], r["algoritmo"]) for r in linhas] == [
        (m, alg) for m in ("m02_uma_chave", "m05_bonus", "m06_fonte") for alg in ALGORITMOS]
    recusa = next(r for r in linhas if r["mapa"] == "m05_bonus" and r["algoritmo"] == "DIJKSTRA")
    assert (recusa["status"], recusa["passos"], recusa["custo"], recusa["estados_visitados"], recusa["tempo_ms"]) == \
        ("RECUSA", "", "", "", "")
    dfs = {r["mapa"]: r for r in ler(tmp_path / "dfs_classificacao.csv")}
    assert list(dfs) == ["m02_uma_chave", "m05_bonus", "m06_fonte"] and dfs["m02_uma_chave"]["possui_ciclo"] == "true"


def test_json_gerado_segue_a_convencao(mapas, tmp_path):
    gerar_saidas([mapas["m06_fonte"], mapas["m07_impossivel"]], tmp_path)
    bruto = (tmp_path / "ciclo_negativo_m06.json").read_bytes()
    texto = bruto.decode("utf-8")
    assert b"\r" not in bruto and texto.endswith("}\n") and '\n  "mapa": "m06_fonte",' in texto  # indent=2, \n
    # ensure_ascii=False: o acento fica no arquivo, e não como ç
    assert "ALVO inalcançável" in (tmp_path / "percurso_m07.json").read_text(encoding="utf-8")


def test_percurso_usa_dijkstra_e_cai_para_bellman_ford_e_bfs(mapas, tmp_path):
    gerar_saidas([mapas["m03_tres_chaves"], mapas["m05_bonus"], mapas["m06_fonte"]], tmp_path)
    escolhido = {m: json.loads((tmp_path / f"percurso_{m}.json").read_text(encoding="utf-8"))
                 for m in ("m03", "m05", "m06")}
    assert (escolhido["m03"]["algoritmo"], escolhido["m03"]["status"]) == ("DIJKSTRA", "OK")
    assert (escolhido["m05"]["algoritmo"], escolhido["m05"]["status"]) == ("BELLMAN_FORD", "OK")  # Dijkstra recusa
    # m06: nem Dijkstra nem Bellman-Ford dão mínimo; sobra o caminho de menos passos do BFS
    assert (escolhido["m06"]["algoritmo"], escolhido["m06"]["status"]) == ("BFS", "OK")


def test_gerar_saidas_respeita_o_filtro_de_algoritmo(mapas, tmp_path):
    gerar_saidas([mapas["m06_fonte"]], tmp_path / "dfs", algoritmos=["DFS"])
    assert sorted(p.name for p in (tmp_path / "dfs").iterdir()) == ["dfs_classificacao.csv"]
    gerar_saidas([mapas["m06_fonte"]], tmp_path / "bfs", algoritmos=["BFS"])
    assert sorted(p.name for p in (tmp_path / "bfs").iterdir()) == ["percurso_m06.json", "solucoes.csv"]
    assert [r["algoritmo"] for r in ler(tmp_path / "bfs" / "solucoes.csv")] == ["BFS"]


# ---------- dados do labirinto interativo ----------

def test_dados_interativos(mapas):
    dados = dados_interativos(list(mapas.values()), "m03_tres_chaves")
    json.dumps(dados)  # tem que ser serializável
    assert dados["mapa_inicial"] == "m03_tres_chaves" and dados["algoritmos"] == ALGORITMOS
    assert list(dados["mapas"]) == list(mapas)
    m02 = dados["mapas"]["m02_uma_chave"]
    assert set(m02) == {"grade", "inicio", "percursos", "armadilhas", "camadas", "trocas_de_camada"}
    assert set(m02["percursos"]) == set(ALGORITMOS) and m02["percursos"]["BFS"]["passos"] == 34
    assert {c["camada"]: len(c["casas"]) for c in m02["camadas"]} == {"-": 16, "a": 23}
    assert m02["trocas_de_camada"] == [{"de": "-", "para": "a", "quantidade": 1, "casas": [[3, 11]]}]
    assert dados["mapas"]["m07_impossivel"]["percursos"]["DIJKSTRA"]["status"] == "SEM_SOLUCAO"
    assert len(dados["mapas"]["m07_impossivel"]["armadilhas"]) == 16


# ---------- cli ----------

def test_cli_um_mapa(tmp_path, capsys):
    assert cli.main(["--mapa", "m02", "--out", str(tmp_path)]) == 0
    assert sorted(p.name for p in tmp_path.iterdir()) == ["dfs_classificacao.csv", "percurso_m02.json", "solucoes.csv"]
    assert [r["mapa"] for r in ler(tmp_path / "solucoes.csv")] == ["m02_uma_chave"] * 3
    assert "solucoes.csv" in capsys.readouterr().out


def test_cli_todos_os_mapas_com_armadilhas(tmp_path):
    assert cli.main(["--armadilhas", "--out", str(tmp_path)]) == 0
    esperados = listar_mapas(RAIZ)
    assert len(ler(tmp_path / "solucoes.csv")) == 3 * len(esperados)
    assert len(ler(tmp_path / "dfs_classificacao.csv")) == len(esperados)
    for nome in ("m01", "m04", "m07", "m08"):
        assert (tmp_path / f"percurso_{nome}.json").exists() and (tmp_path / f"armadilhas_{nome}.csv").exists()
    assert (tmp_path / "ciclo_negativo_m06.json").exists() and not (tmp_path / "ciclo_negativo_m05.json").exists()
    assert len(ler(tmp_path / "armadilhas_m07.csv")) == 16 and ler(tmp_path / "armadilhas_m02.csv") == []


def test_cli_fonte_consumivel_so_muda_a_correcao_do_ciclo(tmp_path):
    cli.main(["--mapa", "m06", "--fonte-consumivel", "--out", str(tmp_path / "com")])
    cli.main(["--mapa", "m06", "--out", str(tmp_path / "sem")])
    ciclo = json.loads((tmp_path / "com" / "ciclo_negativo_m06.json").read_text(encoding="utf-8"))
    assert ciclo["ciclo_encontrado"] and ciclo["correcao"]["aplicada"]
    assert ciclo["correcao"]["custo_minimo_apos_correcao"] == 10
    sem_correcao = json.loads((tmp_path / "sem" / "ciclo_negativo_m06.json").read_text(encoding="utf-8"))
    assert sem_correcao["correcao"]["aplicada"] is False
    sem_tempo = lambda pasta: [{k: v for k, v in r.items() if k != "tempo_ms"} for r in ler(pasta / "solucoes.csv")]
    assert sem_tempo(tmp_path / "com") == sem_tempo(tmp_path / "sem")  # solucoes.csv não é sobrescrito com a regra corrigida
    assert {r["algoritmo"]: r["status"] for r in sem_tempo(tmp_path / "com")}["BELLMAN_FORD"] == "CICLO_NEGATIVO"
    for pasta in ("com", "sem"):
        assert (tmp_path / pasta / "percurso_m06.json").read_bytes() == (tmp_path / "com" / "percurso_m06.json").read_bytes()


def test_armadilhas_do_m04_e_do_m07_saem_sempre(mapas, tmp_path):
    gerar_saidas([mapas["m02_uma_chave"], mapas["m04_esteiras"], mapas["m07_impossivel"]], tmp_path)
    assert sorted(p.name for p in tmp_path.glob("armadilhas_*")) == ["armadilhas_m04.csv", "armadilhas_m07.csv"]


def test_cli_todos_os_mapas_sem_armadilhas_ainda_gera_m04_e_m07(tmp_path):
    cli.main(["--out", str(tmp_path)])
    assert sorted(p.name for p in tmp_path.glob("armadilhas_*")) == ["armadilhas_m04.csv", "armadilhas_m07.csv"]
    assert len(ler(tmp_path / "armadilhas_m07.csv")) == 16 and ler(tmp_path / "armadilhas_m04.csv")


def test_cli_alg_em_minusculas_e_so_dfs(tmp_path):
    cli.main(["--mapa", "m02", "--alg", "dfs", "--out", str(tmp_path)])
    assert [p.name for p in tmp_path.iterdir()] == ["dfs_classificacao.csv"]


def test_cli_erros(tmp_path, capsys):
    with pytest.raises(SystemExit) as erro:
        cli.main(["--mapa", "m99", "--out", str(tmp_path)])
    assert erro.value.code == 2 and "m99" in capsys.readouterr().err
    with pytest.raises(SystemExit) as erro:
        cli.main(["--alg", "XYZ"])
    assert erro.value.code == 2


def test_cli_interactive_gera_o_html_com_todos_os_mapas(tmp_path, monkeypatch):
    chamadas = []
    monkeypatch.setattr(viz, "gerar_labirinto_interativo", lambda dados, saida: chamadas.append((dados, saida)),
                        raising=False)
    # o comando do enunciado: caminho do mapa + --interactive + --out
    assert cli.main(["--mapa", "./data/mapas/m03_tres_chaves.txt", "--interactive", "--out", str(tmp_path) + "/"]) == 0
    (dados, saida), = chamadas
    assert saida == tmp_path / "labirinto_interativo.html"
    assert dados["mapa_inicial"] == "m03_tres_chaves"
    assert {m.stem for m in sorted(MAPAS.glob("m0*.txt"))} <= set(dados["mapas"])
    assert (tmp_path / "percurso_m03.json").exists() and not (tmp_path / "percurso_m02.json").exists()  # arquivos só do m03


def test_cli_interactive_sem_a_funcao_do_viz_falha_antes_de_gerar_arquivos(tmp_path, monkeypatch, capsys):
    monkeypatch.delattr(viz, "gerar_labirinto_interativo", raising=False)
    with pytest.raises(SystemExit) as erro:
        cli.main(["--mapa", "m03", "--interactive", "--out", str(tmp_path)])
    assert erro.value.code == 1 and "gerar_labirinto_interativo" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []


# ---------- T34: mapa inválido na CLI ----------

@pytest.mark.parametrize("grade, causa", [
    ("#####\n#SXG#\n#####\n", "símbolo desconhecido 'X' na linha 2, coluna 3"),
    ("#####\n#SSG#\n#####\n", "esperado exatamente um S, encontrado 2"),
    ("#####\n#S..#\n#####\n", "o mapa não tem nenhum G"),
    ("#####\n#SG#\n#####\n", "linha 2 tem 4 colunas, esperado 5"),
])
def test_cli_mapa_invalido_mostra_uma_linha_com_o_mapa_e_a_causa_e_sai_com_1(tmp_path, capsys, grade, causa):
    mapa = tmp_path / "mapa_ruim.txt"
    mapa.write_text(grade, encoding="utf-8")
    with pytest.raises(SystemExit) as erro:
        cli.main(["--mapa", str(mapa), "--out", str(tmp_path / "saida")])
    assert erro.value.code == 1
    assert capsys.readouterr().err == f"erro: mapa mapa_ruim inválido: {causa}\n"
    assert not (tmp_path / "saida").exists()  # nada é gerado quando o mapa é inválido


def test_cli_mapa_invalido_na_linha_de_comando_nao_mostra_traceback(tmp_path):
    mapa = tmp_path / "mapa_ruim.txt"
    mapa.write_text("#####\n#SXG#\n#####\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "src.cli", "--mapa", str(mapa), "--out", str(tmp_path / "saida")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=RAIZ)
    assert r.returncode == 1 and r.stdout == ""
    assert "Traceback" not in r.stderr and r.stderr.startswith("erro: mapa mapa_ruim inv")
    assert len(r.stderr.strip().splitlines()) == 1


# [IA] OpenAI Codex – teste de regressão para a leitura de mapas na CLI.
def test_cli_mapa_com_codificacao_invalida(tmp_path, capsys):
    mapa = tmp_path / "mapa_ruim.txt"
    mapa.write_bytes(b"#####\n#S\xffG#\n#####\n")
    saida = tmp_path / "saida"

    with pytest.raises(SystemExit) as erro:
        cli.main(["--mapa", str(mapa), "--out", str(saida)])

    assert erro.value.code == 1
    assert capsys.readouterr().err == "erro: mapa mapa_ruim inválido: o arquivo precisa estar em UTF-8\n"
    assert not saida.exists()
