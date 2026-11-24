from pathlib import Path

import pytest

from src.graphs import metricas
from src.graphs.estados import construir_g_pos
from src.graphs.graph import Graph
from src.graphs.io import ler_mapa

MAPAS = Path(__file__).parent.parent / "data" / "mapas"

# Mini G_est feito à mão: chave "a" em (1,3), G em (1,4), esteira em (1,1)
# que leva a (2,1), de onde não há saída (beco).
S0 = "(1,1)|-|{}"
S1 = "(1,2)|-|{}"
S5 = "(2,1)|-|{}"
S2 = "(1,3)|a|{}"
S3 = "(1,2)|a|{}"
S4 = "(1,4)|a|{}"


@pytest.fixture
def mini():
    g = Graph()
    g.adicionar_vertice(S2)  # entra primeiro para testar o desempate por leitura
    for origem, destino, peso in [
        (S0, S1, 1), (S0, S5, 1), (S1, S0, 1), (S1, S2, 1),
        (S2, S3, 1), (S3, S2, 1), (S2, S4, 1), (S4, "ALVO", 0),
    ]:
        g.adicionar_arco(origem, destino, peso)
    return g


# ---------- rótulos ----------

def test_decompor_rotulo_g_est_g_pos_e_fontes():
    assert metricas.decompor_rotulo("(3,5)|ab|{0,2}") == (3, 5, "ab", (0, 2))
    assert metricas.decompor_rotulo("(1,1)|-|{}") == (1, 1, "-", ())
    assert metricas.decompor_rotulo("(3,5)|-|{}|{0}") == (3, 5, "-", ())
    assert metricas.decompor_rotulo("(12,3)") == (12, 3, "-", ())


def test_decompor_rotulo_invalido():
    with pytest.raises(ValueError):
        metricas.decompor_rotulo("ALVO")


# ---------- ordem, tamanho, densidade ----------

def test_ordem_tamanho_densidade_ignoram_alvo(mini):
    assert metricas.ordem(mini) == 6
    assert metricas.tamanho(mini) == 7
    assert metricas.densidade(mini) == pytest.approx(7 / 30)


def test_arcos_paralelos_contam_no_tamanho():
    g = Graph()
    g.adicionar_arco("(1,1)", "(1,2)", 1, {"movimento": "L"})
    g.adicionar_arco("(1,1)", "(1,2)", 1, {"movimento": "L", "via_esteira": True})
    assert metricas.tamanho(g) == 2
    assert metricas.densidade(g) == pytest.approx(1.0)


def test_densidade_com_menos_de_dois_vertices():
    assert metricas.densidade(Graph()) == 0.0
    g = Graph()
    g.adicionar_vertice("(1,1)")
    assert metricas.densidade(g) == 0.0
    assert metricas.densidade_dirigida(1, 0) == 0.0


def test_grafo_completo_tem_densidade_1():
    g = Graph()
    casas = ["(0,0)", "(0,1)", "(0,2)"]
    for u in casas:
        for v in casas:
            if u != v:
                g.adicionar_arco(u, v)
    assert metricas.densidade(g) == 1.0


# ---------- graus ----------

def test_graus_ignoram_alvo_e_seguem_ordem_de_insercao(mini):
    saida = metricas.graus_saida(mini)
    entrada = metricas.graus_entrada(mini)
    assert list(saida) == [S2, S0, S1, S5, S3, S4]
    assert saida == {S0: 2, S1: 2, S5: 0, S2: 2, S3: 1, S4: 0}
    assert entrada == {S0: 1, S1: 1, S5: 1, S2: 2, S3: 1, S4: 1}
    assert "ALVO" not in saida and "ALVO" not in entrada
    assert sum(saida.values()) == sum(entrada.values()) == metricas.tamanho(mini)


def test_resumo_graus(mini):
    assert metricas.resumo_graus(metricas.graus_saida(mini)) == {
        "min": 0, "max": 2, "medio": pytest.approx(7 / 6)
    }
    assert metricas.resumo_graus({}) == {"min": 0, "max": 0, "medio": 0.0}


def test_maior_grau_desempata_pela_ordem_de_leitura(mini):
    # S2 foi inserido primeiro, mas S0 vem antes na leitura (linha 1, coluna 1)
    assert metricas.maior_grau(metricas.graus_saida(mini)) == {"estado": S0, "grau": 2}
    assert metricas.maior_grau(metricas.graus_entrada(mini)) == {"estado": S2, "grau": 2}
    assert metricas.maior_grau({}) == {"estado": None, "grau": 0}


# ---------- becos ----------

def test_beco_nao_inclui_estado_sobre_g(mini):
    # S4 tem grau de saída 0 mas está em G (tem arco até ALVO)
    assert metricas.estados_em_g(mini) == {S4}
    assert metricas.becos(mini) == [S5]


def test_becos_no_g_pos_com_g_explicito():
    g = construir_g_pos(["#####", "#S>##", "#..G#", "#####"])
    # a esteira em (1,2) aponta para a parede: sem saída
    assert metricas.becos(g, em_g={"(2,3)"}) == ["(1,2)"]
    assert set(metricas.becos(g)) == {"(1,2)", "(2,3)"}


# ---------- multiplicidade ----------

def test_multiplicidade(mini):
    mult = metricas.multiplicidade(mini)
    assert mult == {(1, 1): 1, (1, 2): 2, (2, 1): 1, (1, 3): 1, (1, 4): 1}
    assert metricas.resumo_multiplicidade(mult) == {
        "max": 2, "casas_no_max": 1, "media": pytest.approx(1.2)
    }
    assert metricas.resumo_multiplicidade({}) == {"max": 0, "casas_no_max": 0, "media": 0.0}


def test_multiplicidade_do_g_pos_e_sempre_1():
    g = construir_g_pos(ler_mapa(MAPAS / "m01_terreno.txt"))
    resumo = metricas.resumo_multiplicidade(metricas.multiplicidade(g))
    assert resumo["max"] == 1
    assert resumo["casas_no_max"] == metricas.ordem(g)


# ---------- camadas ----------

def test_camadas(mini):
    assert metricas.camadas(mini) == {"a": [S2, S3, S4], "-": [S0, S1, S5]}


def test_metricas_por_camada(mini):
    por_camada = {item["camada"]: item for item in metricas.metricas_camadas(mini)}
    assert por_camada["-"] == {"camada": "-", "ordem": 3, "tamanho": 3, "densidade": 0.5}
    assert por_camada["a"] == {"camada": "a", "ordem": 3, "tamanho": 3, "densidade": 0.5}


def test_arcos_entre_camadas(mini):
    assert metricas.arcos_entre_camadas(mini) == [
        {"de": "-", "para": "a", "quantidade": 1, "casas": [[1, 3]]}
    ]
    assert metricas.n_arcos_entre_camadas(mini) == 1


def test_arcos_entre_camadas_agrupa_e_ordena_casas():
    g = Graph()
    g.adicionar_arco("(5,5)|-|{}", "(5,6)|b|{}")
    g.adicionar_arco("(1,1)|-|{}", "(1,2)|b|{}")
    g.adicionar_arco("(4,6)|-|{}", "(5,6)|b|{}")
    g.adicionar_arco("(1,2)|b|{}", "(1,3)|ab|{}")
    assert metricas.arcos_entre_camadas(g) == [
        {"de": "-", "para": "b", "quantidade": 3, "casas": [[1, 2], [5, 6]]},
        {"de": "b", "para": "ab", "quantidade": 1, "casas": [[1, 3]]},
    ]


def test_subgrafo_induzido_preserva_peso_e_metadados(mini):
    sub = metricas.subgrafo_induzido(mini, [S0, S1])
    assert sub.vertices() == [S0, S1]
    assert [(a.origem, a.destino) for a in sub.arcos()] == [(S0, S1), (S1, S0)]


# ---------- G_pos de um mapa real ----------

def test_ordem_e_tamanho_do_g_pos_do_m01():
    grade = ler_mapa(MAPAS / "m01_terreno.txt")
    g = construir_g_pos(grade)
    livres = sum(1 for linha in grade for s in linha if s != "#")
    assert metricas.ordem(g) == livres
    assert metricas.camadas(g).keys() == {"-"}
    assert metricas.arcos_entre_camadas(g) == []


# ---------- rankings (T23) ----------
# [IA] Claude (Anthropic) - testes dos rankings da T23 gerados a pedido do Luca; revisar e declarar.

def test_ranking_graus_maior_primeiro_e_empate_pela_leitura(mini):
    assert metricas.ranking_graus(metricas.graus_saida(mini), 4) == [
        {"estado": S0, "grau": 2}, {"estado": S1, "grau": 2},
        {"estado": S2, "grau": 2}, {"estado": S3, "grau": 1},
    ]
    # mesma casa (1,2): a camada sem chaves vem antes da camada "a"
    assert metricas.ranking_graus(metricas.graus_entrada(mini), 4) == [
        {"estado": S2, "grau": 2}, {"estado": S0, "grau": 1},
        {"estado": S1, "grau": 1}, {"estado": S3, "grau": 1},
    ]
    assert metricas.ranking_graus({}) == []


def test_ranking_multiplicidade(mini):
    assert metricas.ranking_multiplicidade(metricas.multiplicidade(mini), 3) == [
        {"linha": 1, "coluna": 2, "estados": 2},
        {"linha": 1, "coluna": 1, "estados": 1},
        {"linha": 1, "coluna": 3, "estados": 1},
    ]
