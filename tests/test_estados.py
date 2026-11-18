# Testes obrigatorios de estados (tarefa T10 do plano).
# [IA] Claude (Anthropic) - testes do G_pos (T08) gerados a pedido do grupo; revisar e declarar.
import csv
from pathlib import Path

import pytest

from src.graphs.algorithms import bellman_ford
from src.graphs.estados import construir_g_est, construir_g_pos, exportar_arestas, exportar_todos, nome_curto
from src.graphs.io import ler_mapa

RAIZ = Path(__file__).parent.parent
MAPAS = RAIZ / "data" / "mapas"


def alcancaveis(g, origem):
    vistos, pilha = {origem}, [origem]
    while pilha:
        for arco in g.arcos_saindo(pilha.pop()):
            if arco.destino not in vistos:
                vistos.add(arco.destino)
                pilha.append(arco.destino)
    return vistos


def n_arcos(g):
    return sum(1 for _ in g.arcos())


# ---------- G_pos (T08) ----------

def test_g_pos_vizinhos_em_N_L_S_O():
    grade = ["#####", "#...#", "#.S.#", "#..G#", "#####"]
    g = construir_g_pos(grade)
    assert [a.destino for a in g.arcos_saindo("(2,2)")] == ["(1,2)", "(2,3)", "(3,2)", "(2,1)"]
    assert [a.metadados["movimento"] for a in g.arcos_saindo("(2,2)")] == ["N", "L", "S", "O"]


def test_g_pos_vertices_por_linha_e_coluna_sem_paredes():
    g = construir_g_pos(["####", "#SG#", "#..#", "####"])
    assert g.vertices() == ["(1,1)", "(1,2)", "(2,1)", "(2,2)"]


def test_g_pos_custo_e_o_da_casa_de_destino():
    g = construir_g_pos(["#######", "#S,~.G#", "#######"])
    assert [a.peso for a in g.arcos_saindo("(1,1)")] == [3]
    assert [a.peso for a in g.arcos_saindo("(1,2)")] == [5, 1]  # L (agua), O (S)
    assert g.arcos_saindo("(1,1)")[0].metadados == {"movimento": "L", "casa_destino": ",", "via_esteira": False}


def test_g_pos_bonus_vale_menos_4_sempre_e_cria_ciclo_negativo():
    g = construir_g_pos(["#####", "#S+G#", "#####"])
    ida = [a for a in g.arcos_saindo("(1,1)") if a.destino == "(1,2)"][0]
    volta = [a for a in g.arcos_saindo("(1,2)") if a.destino == "(1,1)"][0]
    assert ida.peso == -4 and volta.peso == 1
    assert ida.peso + volta.peso < 0


def test_g_pos_fonte_vale_menos_2():
    g = construir_g_pos(["#####", "#S*G#", "#####"])
    assert [a.peso for a in g.arcos_saindo("(1,1)")] == [-2]


def test_g_pos_nenhum_arco_sai_de_G():
    g = construir_g_pos(["#####", "#S.G#", "#####"])
    assert g.arcos_saindo("(1,3)") == []
    assert [a.destino for a in g.arcos_saindo("(1,2)")] == ["(1,3)", "(1,1)"]


def test_g_pos_esteira_so_sai_na_direcao_da_seta():
    g = construir_g_pos(["######", "#S>.G#", "######"])
    saidas = g.arcos_saindo("(1,2)")
    assert [a.destino for a in saidas] == ["(1,3)"]
    assert saidas[0].metadados["via_esteira"] is True
    assert g.arcos_saindo("(1,1)")[0].metadados["via_esteira"] is False


def test_g_pos_esteira_apontando_para_parede_nao_tem_saida():
    g = construir_g_pos(["####", "#S>#", "#G##", "####"])
    assert g.arcos_saindo("(1,2)") == []


def test_g_pos_chave_e_chao_comum():
    g = construir_g_pos(["#####", "#SaG#", "#####"])
    assert [a.peso for a in g.arcos_saindo("(1,1)")] == [1]
    assert g.arcos_saindo("(1,1)")[0].metadados["casa_destino"] == "a"


def test_g_pos_porta_como_parede_ou_chao():
    grade = ["######", "#SAaG#", "######"]
    parede = construir_g_pos(grade, porta_como="parede")
    chao = construir_g_pos(grade, porta_como="chao")
    assert "(1,2)" not in parede and "(1,2)" in chao
    assert "(1,4)" not in alcancaveis(parede, "(1,1)")
    assert "(1,4)" in alcancaveis(chao, "(1,1)")
    assert chao.arcos_saindo("(1,1)")[0].peso == 1


def test_g_pos_porta_como_invalido():
    with pytest.raises(ValueError, match="porta_como"):
        construir_g_pos(["#####", "#SAG#", "#####"], porta_como="aberta")


def test_g_pos_m02_porta_parede_nao_chega_em_G_e_porta_chao_chega():
    grade = ler_mapa(MAPAS / "m02_uma_chave.txt")
    assert "(1,11)" not in alcancaveis(construir_g_pos(grade, "parede"), "(1,1)")
    assert "(1,11)" in alcancaveis(construir_g_pos(grade, "chao"), "(1,1)")


@pytest.mark.parametrize("mapa", sorted(MAPAS.glob("m0*.txt")), ids=lambda m: m.name)
@pytest.mark.parametrize("porta_como", ["parede", "chao"])
def test_g_pos_dos_mapas_fornecidos(mapa, porta_como):
    grade = ler_mapa(mapa)
    g = construir_g_pos(grade, porta_como)
    livres = sum(1 for linha in grade for s in linha if s != "#" and not (s in "ABCD" and porta_como == "parede"))
    assert len(g) == livres
    assert "(1,1)" in g


# ---------- G_est (T09) ----------

MINIMO = Path(__file__).parent / "fixtures" / "mapa_minimo.txt"


def arco(g, origem, destino):
    return next(a for a in g.arcos_saindo(origem) if a.destino == destino)


def test_g_est_estado_inicial_e_ordem_N_L_S_O():
    g = construir_g_est(ler_mapa(MAPAS / "m02_uma_chave.txt"))
    assert g.vertices()[0] == "(1,1)|-|{}"
    assert [a.destino for a in g.arcos_saindo("(1,1)|-|{}")] == ["(1,2)|-|{}", "(2,1)|-|{}"]
    assert [a.metadados["movimento"] for a in g.arcos_saindo("(1,1)|-|{}")] == ["L", "S"]


def test_g_est_m02_contagens_do_T04():
    g = construir_g_est(ler_mapa(MAPAS / "m02_uma_chave.txt"))
    estados = [v for v in g.vertices() if v != "ALVO"]
    assert len(estados) == 39
    assert sum(v.endswith("|-|{}") for v in estados) == 16
    assert sum(v.endswith("|a|{}") for v in estados) == 23
    assert n_arcos(g) == 75  # 74 movimentos + o arco G -> ALVO


def test_g_est_mapa_minimo_contagens_do_T04():
    g = construir_g_est(ler_mapa(MINIMO))
    assert len(g) == 12 and n_arcos(g) == 17  # 11 estados + ALVO; 16 movimentos + G -> ALVO
    assert sum(v.endswith("|-|{}") for v in g.vertices()) == 4
    assert sum(v.endswith("|a|{}") for v in g.vertices()) == 7


def test_g_est_pegar_a_chave_troca_de_camada():
    g = construir_g_est(ler_mapa(MAPAS / "m02_uma_chave.txt"))
    a = arco(g, "(3,10)|-|{}", "(3,11)|a|{}")
    assert (a.peso, a.metadados["movimento"], a.metadados["casa_destino"]) == (1, "L", "a")
    assert "(3,11)|-|{}" not in g  # a casa da chave só existe com a chave


def test_g_est_porta_so_com_a_chave():
    g = construir_g_est(ler_mapa(MAPAS / "m02_uma_chave.txt"))
    assert "(1,6)|-|{}" not in g
    assert arco(g, "(1,5)|a|{}", "(1,6)|a|{}").peso == 1


def test_g_est_G_so_tem_arco_para_ALVO_com_custo_0():
    g = construir_g_est(ler_mapa(MAPAS / "m02_uma_chave.txt"))
    saidas = g.arcos_saindo("(1,11)|a|{}")
    assert [(a.destino, a.peso, a.metadados["movimento"], a.metadados["casa_destino"]) for a in saidas] == [("ALVO", 0, "-", "")]
    assert g.arcos_saindo("ALVO") == []


def test_g_est_ALVO_existe_mesmo_sem_G_alcancavel():
    g = construir_g_est(ler_mapa(MAPAS / "m07_impossivel.txt"))
    assert "ALVO" in g
    assert all(a.destino != "ALVO" for a in g.arcos())


def test_g_est_chaves_em_ordem_alfabetica():
    # b é pega antes de a, mas o rótulo é sempre "ab"
    grade = ["#######", "#SbaG##", "#######"]
    g = construir_g_est(grade)
    assert "(1,3)|ab|{}" in g
    assert arco(g, "(1,2)|b|{}", "(1,3)|ab|{}").peso == 1


def test_g_est_esteira_so_sai_na_direcao_da_seta():
    g = construir_g_est(["######", "#S>.G#", "######"])
    saidas = g.arcos_saindo("(1,2)|-|{}")
    assert [a.destino for a in saidas] == ["(1,3)|-|{}"]
    assert saidas[0].metadados["via_esteira"] is True


def test_g_est_esteira_para_parede_e_estado_sem_saida():
    g = construir_g_est(ler_mapa(MINIMO))
    assert g.arcos_saindo("(3,1)|-|{}") == [] and g.arcos_saindo("(3,1)|a|{}") == []


def test_g_est_bonus_vale_menos_4_so_na_primeira_vez():
    g = construir_g_est(["######", "#S+.G#", "######"])
    assert arco(g, "(1,1)|-|{}", "(1,2)|-|{0}").peso == -4
    assert arco(g, "(1,2)|-|{0}", "(1,1)|-|{0}").peso == 1
    assert arco(g, "(1,1)|-|{0}", "(1,2)|-|{0}").peso == 1  # já consumido: vale 1


def test_g_est_bonus_indices_em_ordem_de_leitura():
    g = construir_g_est(["#######", "#S+.+G#", "#######"])
    assert arco(g, "(1,3)|-|{0}", "(1,4)|-|{0,1}").peso == -4
    assert "(1,4)|-|{0,1}" in g


def test_g_est_fonte_vale_menos_2_toda_vez_e_cria_ciclo_negativo():
    g = construir_g_est(["######", "#S*.G#", "######"])
    ida = arco(g, "(1,1)|-|{}", "(1,2)|-|{}")
    volta = arco(g, "(1,2)|-|{}", "(1,1)|-|{}")
    assert ida.peso == -2 and volta.peso == 1
    assert ida.peso + volta.peso < 0  # ciclo negativo (o "exploit" do m06)


def test_g_est_fonte_consumivel_vale_so_na_primeira_vez_e_muda_o_rotulo():
    g = construir_g_est(["######", "#S*.G#", "######"], fonte_consumivel=True)
    assert g.vertices()[0] == "(1,1)|-|{}|{}"
    assert arco(g, "(1,1)|-|{}|{}", "(1,2)|-|{}|{0}").peso == -2
    assert arco(g, "(1,1)|-|{}|{0}", "(1,2)|-|{}|{0}").peso == 1


def ciclo_negativo(g, fonte):
    return bool(bellman_ford(g, fonte).ciclo_negativo)


def test_g_est_m06_fonte_gera_ciclo_negativo_e_fonte_consumivel_corrige():
    grade = ler_mapa(MAPAS / "m06_fonte.txt")
    assert ciclo_negativo(construir_g_est(grade), "(1,1)|-|{}")
    assert not ciclo_negativo(construir_g_est(grade, fonte_consumivel=True), "(1,1)|-|{}|{}")


def test_m05_bonus_gera_ciclo_negativo_no_g_pos_mas_nao_no_g_est():
    grade = ler_mapa(MAPAS / "m05_bonus.txt")
    assert ciclo_negativo(construir_g_pos(grade), "(1,1)")
    assert not ciclo_negativo(construir_g_est(grade), "(1,1)|-|{}")


@pytest.mark.parametrize("mapa", sorted(MAPAS.glob("m0*.txt")), ids=lambda m: m.name)
@pytest.mark.parametrize("fonte_consumivel", [False, True])
def test_g_est_dos_mapas_fornecidos(mapa, fonte_consumivel):
    g = construir_g_est(ler_mapa(mapa), fonte_consumivel)
    assert g.vertices()[0].startswith("(1,1)|-|{}")
    assert "ALVO" in g and g.arcos_saindo("ALVO") == []
    assert len(set(g.vertices())) == len(g)


# ---------- T10: arestas_<mapa>.csv ----------

CABECALHO = "origem,destino,movimento,casa_destino,peso,via_esteira,camada_origem,camada_destino"

ARCOS_ESPERADOS = {"m01": 47, "m02": 75, "m03": 467, "m04": 67, "m05": 444, "m06": 47, "m07": 38, "m08": 6365}


def exportar(tmp_path, mapa):
    g = construir_g_est(ler_mapa(mapa))
    caminho = tmp_path / "arestas.csv"
    exportar_arestas(g, caminho)
    return g, caminho


def linhas_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        return list(csv.DictReader(arquivo))


@pytest.mark.parametrize("arquivo, esperado", [
    ("m03_tres_chaves.txt", "m03"), ("m08_grande.txt", "m08"), ("m1.txt", "m1"),
    ("meu_mapa.txt", "meu_mapa"), ("data/mapas/m05_bonus.txt", "m05"),
])
def test_nome_curto(arquivo, esperado):
    assert nome_curto(arquivo) == esperado


def test_csv_formato_do_contrato(tmp_path):
    _, caminho = exportar(tmp_path, MAPAS / "m02_uma_chave.txt")
    bruto = caminho.read_bytes()
    assert not bruto.startswith(b"\xef\xbb\xbf") and b"\r" not in bruto  # UTF-8 sem BOM, fim de linha \n
    linhas = bruto.decode("utf-8").split("\n")
    assert linhas[0] == CABECALHO
    assert linhas[1] == '"(1,1)|-|{}","(1,2)|-|{}",L,.,1,false,-,-'  # rótulo sempre entre aspas
    assert linhas[-1] == ""  # termina com \n


def test_csv_uma_linha_por_arco_na_ordem_de_insercao(tmp_path):
    g, caminho = exportar(tmp_path, MAPAS / "m02_uma_chave.txt")
    assert [(r["origem"], r["destino"]) for r in linhas_csv(caminho)] == [(a.origem, a.destino) for a in g.arcos()]


def test_csv_linhas_do_exemplo_do_contrato(tmp_path):
    _, caminho = exportar(tmp_path, MAPAS / "m02_uma_chave.txt")
    linhas = caminho.read_text(encoding="utf-8").split("\n")
    for exemplo in ['"(1,1)|-|{}","(2,1)|-|{}",S,.,1,false,-,-',
                    '"(3,10)|-|{}","(3,11)|a|{}",L,a,1,false,-,a',
                    '"(1,5)|a|{}","(1,6)|a|{}",L,A,1,false,a,a',
                    '"(1,11)|a|{}",ALVO,-,,0,false,a,']:
        assert exemplo in linhas


def test_csv_m02_tem_os_39_estados_do_T04(tmp_path):
    _, caminho = exportar(tmp_path, MAPAS / "m02_uma_chave.txt")
    linhas = linhas_csv(caminho)
    estados = {r["origem"] for r in linhas} | {r["destino"] for r in linhas if r["destino"] != "ALVO"}
    assert len(estados) == 39 and len(linhas) == 75
    assert [r["destino"] for r in linhas].count("ALVO") == 1


def test_csv_mapa_minimo_troca_de_camada_e_esteira_para_parede(tmp_path):
    _, caminho = exportar(tmp_path, MINIMO)
    linhas = linhas_csv(caminho)
    assert len(linhas) == 17
    troca = [r for r in linhas if r["camada_origem"] != r["camada_destino"] and r["destino"] != "ALVO"]
    assert [(r["origem"], r["destino"], r["casa_destino"]) for r in troca] == [("(1,2)|-|{}", "(1,3)|a|{}", "a")]
    # (3,1) é uma esteira apontando para parede: o estado existe, mas nenhum arco sai dele
    assert {r["origem"] for r in linhas}.isdisjoint({"(3,1)|-|{}", "(3,1)|a|{}"})
    assert {"(3,1)|-|{}", "(3,1)|a|{}"} <= {r["destino"] for r in linhas}


def test_csv_via_esteira_e_pesos_especiais(tmp_path):
    assert any(r["via_esteira"] == "true" for r in linhas_csv(exportar(tmp_path, MAPAS / "m04_esteiras.txt")[1]))
    assert all(r["via_esteira"] == "false" for r in linhas_csv(exportar(tmp_path, MAPAS / "m02_uma_chave.txt")[1]))
    assert "-4" in {r["peso"] for r in linhas_csv(exportar(tmp_path, MAPAS / "m05_bonus.txt")[1])}
    assert "-2" in {r["peso"] for r in linhas_csv(exportar(tmp_path, MAPAS / "m06_fonte.txt")[1])}


def test_csv_casa_destino_virgula_e_lida_de_volta(tmp_path):
    # a lama "," precisa de aspas no CSV; o leitor deve devolvê-la intacta
    linhas = linhas_csv(exportar(tmp_path, MAPAS / "m01_terreno.txt")[1])
    assert any(r["casa_destino"] == "," and r["peso"] == "3" for r in linhas)


def test_csv_m07_nao_tem_arco_para_ALVO(tmp_path):
    linhas = linhas_csv(exportar(tmp_path, MAPAS / "m07_impossivel.txt")[1])
    assert all(r["destino"] != "ALVO" for r in linhas)


def test_exportar_cria_a_pasta_de_saida(tmp_path):
    g = construir_g_est(ler_mapa(MINIMO))
    exportar_arestas(g, tmp_path / "out" / "parte1" / "arestas_minimo.csv")
    assert (tmp_path / "out" / "parte1" / "arestas_minimo.csv").exists()


def test_exportar_todos_gera_um_arquivo_por_mapa_fornecido(tmp_path):
    gerados = exportar_todos(RAIZ, tmp_path)
    por_nome = {arquivo.name: arcos for arquivo, (estados, arcos) in gerados.items()}
    for nome, arcos in ARCOS_ESPERADOS.items():
        assert por_nome[f"arestas_{nome}.csv"] == arcos
        assert len(linhas_csv(tmp_path / f"arestas_{nome}.csv")) == arcos


def test_arquivos_em_out_parte1_estao_em_dia_com_o_codigo(tmp_path):
    # out/parte1 foi gerado pelo código (python -m src.graphs.estados); se o G_est mudar, gerar de novo
    exportar_todos(RAIZ, tmp_path)
    for nome in ARCOS_ESPERADOS:
        commitado = (RAIZ / "out" / "parte1" / f"arestas_{nome}.csv").read_bytes().replace(b"\r\n", b"\n")  # o git no Windows pode converter
        assert commitado == (tmp_path / f"arestas_{nome}.csv").read_bytes()
