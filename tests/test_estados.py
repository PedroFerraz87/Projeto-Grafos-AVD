# Testes obrigatorios de estados (tarefa T10 do plano).
# [IA] Claude (Anthropic) - testes do G_pos (T08) gerados a pedido do grupo; revisar e declarar.
from pathlib import Path

import pytest

from src.graphs.estados import construir_g_pos
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
