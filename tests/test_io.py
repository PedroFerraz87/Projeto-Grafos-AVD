# Testes obrigatorios de io (tarefa T07 do plano).
# [IA] Claude (Anthropic) - gerado a pedido do grupo; revisar e declarar.
from pathlib import Path

import pytest

from src.graphs.io import MapaInvalido, ler_mapa

MAPAS = sorted((Path(__file__).parent.parent / "data" / "mapas").glob("m0*.txt"))


def escrever(tmp_path, texto):
    arquivo = tmp_path / "mapa.txt"
    arquivo.write_text(texto, encoding="utf-8")
    return arquivo


def test_mapa_valido_devolve_a_grade(tmp_path):
    arquivo = escrever(tmp_path, "#####\n#S.G#\n#####\n")
    assert ler_mapa(arquivo) == ["#####", "#S.G#", "#####"]


def test_comentarios_e_linhas_em_branco_sao_ignorados(tmp_path):
    arquivo = escrever(tmp_path, "; titulo\n#####\n; meio\n#S.G#\n\n#####\n\n")
    assert ler_mapa(arquivo) == ["#####", "#S.G#", "#####"]


def test_fim_de_linha_windows(tmp_path):
    arquivo = tmp_path / "mapa.txt"
    arquivo.write_bytes(b"#####\r\n#S.G#\r\n#####\r\n")
    assert ler_mapa(arquivo) == ["#####", "#S.G#", "#####"]


def test_todos_os_simbolos_validos_sao_aceitos(tmp_path):
    arquivo = escrever(tmp_path, "#" * 15 + "\n#S.,~aA><^v+*G#\n" + "#" * 15 + "\n")
    assert len(ler_mapa(arquivo)) == 3


def test_linhas_de_larguras_diferentes(tmp_path):
    arquivo = escrever(tmp_path, "#####\n#S.G#\n####\n")
    with pytest.raises(MapaInvalido, match="linha 3 tem 4 colunas, esperado 5"):
        ler_mapa(arquivo)


def test_sem_S(tmp_path):
    arquivo = escrever(tmp_path, "#####\n#..G#\n#####\n")
    with pytest.raises(MapaInvalido, match="exatamente um S, encontrado 0"):
        ler_mapa(arquivo)


def test_dois_S(tmp_path):
    arquivo = escrever(tmp_path, "#####\n#SSG#\n#####\n")
    with pytest.raises(MapaInvalido, match="exatamente um S, encontrado 2"):
        ler_mapa(arquivo)


def test_sem_G(tmp_path):
    arquivo = escrever(tmp_path, "#####\n#S..#\n#####\n")
    with pytest.raises(MapaInvalido, match="nenhum G"):
        ler_mapa(arquivo)


def test_simbolo_desconhecido(tmp_path):
    arquivo = escrever(tmp_path, "#####\n#SXG#\n#####\n")
    with pytest.raises(MapaInvalido, match="símbolo desconhecido 'X' na linha 2, coluna 3"):
        ler_mapa(arquivo)


def test_mapa_vazio_so_com_comentarios(tmp_path):
    arquivo = escrever(tmp_path, "; so comentario\n\n")
    with pytest.raises(MapaInvalido, match="vazio"):
        ler_mapa(arquivo)


def test_m02_real_tem_S_em_1_1():
    grade = ler_mapa(next(m for m in MAPAS if m.name.startswith("m02")))
    assert len(grade) == 5 and len(grade[0]) == 13
    assert grade[1][1] == "S"


def test_ha_8_mapas_fornecidos():
    assert len(MAPAS) == 8


@pytest.mark.parametrize("mapa", MAPAS, ids=lambda m: m.name)
def test_mapas_fornecidos_sao_validos(mapa):
    grade = ler_mapa(mapa)
    assert len({len(linha) for linha in grade}) == 1
