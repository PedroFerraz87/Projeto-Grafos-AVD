# [IA] OpenAI Codex - verificações da orquestração da T25.
import pytest

from src.graphs.graph import Graph
from src.parte2 import gerar_casos, grafo_dijkstra, main


def test_transformacao_preserva_grafo_original_e_metadados():
    original = Graph()
    original.adicionar_arco(1, 2, -10, {'timestamp': 7})
    original.adicionar_arco(1, 2, 10, {'timestamp': 8})
    original.adicionar_vertice(3)

    transformado = grafo_dijkstra(original)

    assert list(original.arcos()) == [(1, 2, -10, {'timestamp': 7}), (1, 2, 10, {'timestamp': 8})]
    assert list(transformado.arcos()) == [(1, 2, 20, {'timestamp': 7}), (1, 2, 0, {'timestamp': 8})]
    assert transformado.vertices() == [1, 2, 3]


def test_casos_tem_caminhos_validos_e_separam_pesos_originais_do_dijkstra(tmp_path):
    caminho = tmp_path / 'avaliacoes.csv'
    caminho.write_text('1,2,-5,1\n2,1,1,2\n1,3,10,3\n3,4,9,4\n4,2,8,5\n', encoding='utf-8')

    relatorio = gerar_casos(caminho)

    assert [entrada['fonte'] for entrada in relatorio['bfs']] == [1, 2, 3]
    assert all(entrada['alcancados'] == 4 for entrada in relatorio['bfs'])
    assert len(relatorio['dijkstra']) == 5
    sem, com = relatorio['bellman_ford']
    assert (sem['caminho_exemplo'], sem['custo_exemplo'], sem['ciclo']) == ([1, 2], -5, [])
    assert com['ciclo'][0] == com['ciclo'][-1]
    assert com['custo_ciclo'] == -4
    assert all(row['custo_transformado_dijkstra'] <= row['custo_transformado_bfs']
               for row in relatorio['comparacao_caminhos'])


def test_cli_protege_relatorio_com_benchmark(tmp_path):
    saida = tmp_path / 'parte2_report.json'
    original = '{"benchmark": {"execucoes": 5}}'
    saida.write_text(original, encoding='utf-8')

    with pytest.raises(SystemExit) as erro:
        main(['--out', str(saida)])

    assert erro.value.code == 2
    assert saida.read_text(encoding='utf-8') == original
