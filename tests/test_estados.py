# Testes obrigatorios de estados (tarefa T10 do plano).
# [IA] Claude (Anthropic) - testes do G_pos (T08) gerados a pedido do grupo; revisar e declarar.
from pathlib import Path

import pytest

from src.graphs.algorithms import bellman_ford
from src.graphs.estados import construir_g_est, construir_g_pos
from src.graphs.io import ler_mapa

MAPAS = Path(__file__).parent.parent / "data" / "mapas"


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
