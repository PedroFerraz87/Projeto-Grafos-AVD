# Tabelas de comparação para a T32

O [relatório integrado](../../out/parte2/parte2_report.json) reúne os casos da T25 e o resumo de desempenho da T26. As medições individuais do Victor estão em [benchmark.csv](../../out/parte2/benchmark.csv). As [tabelas publicadas](../../out/parte2/tabelas_t32/) incluem resultados por algoritmo, comparação dos caminhos, medições individuais e resumo por algoritmo, recorte e fonte.

Para reproduzir as tabelas sem alterar as saídas publicadas, rode os comandos abaixo na raiz do projeto. O primeiro comando reexecuta os casos da T25. O segundo usa os tempos já medidos na T26.

```powershell
$repro = Join-Path ([System.IO.Path]::GetTempPath()) ("grafos-t32-" + [guid]::NewGuid())
$relatorio = Join-Path $repro "parte2_report.json"
python -m src.parte2 --out $relatorio
python -m src.avd.comparacao_algoritmos --relatorio $relatorio --benchmark out/parte2/benchmark.csv --out (Join-Path $repro "tabelas_t32")
```

O resumo mantém `vertices` e `arcos` para relacionar cada medição ao tamanho real do grafo. Use `execucoes` para conferir a quantidade de repetições em cada combinação. O tempo médio e o desvio padrão amostral estão em milissegundos. Uma combinação com uma única execução tem o desvio vazio.

| Recorte | Vértices | Arcos | Fontes medidas |
|---|---:|---:|---|
| 10% | 572 | 2.418 | 2, 4, 129 |
| 50% | 2.223 | 12.093 | 1, 2, 4 |
| 100% | 3.783 | 24.186 | 1, 3, 8 |

São 180 medições em 36 combinações, com cinco execuções por combinação. O conjunto de fontes varia com o recorte. A T26 mede a execução do algoritmo depois de carregar e preparar o grafo. O JSON publicado ainda não identifica a configuração da máquina de medição.

Em `comparacao_caminhos.csv`, `passos_bfs` e `passos_dijkstra` contam os arcos dos caminhos obtidos para o mesmo par. `custo_transformado_bfs` e `custo_transformado_dijkstra` somam `10 - nota` ao longo de cada caminho. O BFS escolhe seu caminho pelo número de arcos e esse custo transformado é calculado sobre o caminho encontrado. Os custos dos ciclos de Bellman-Ford seguem os pesos descritos no relatório da T25.

Para usar as tabelas em um notebook, importe `ler_tabelas` de `src.avd.comparacao_algoritmos` e passe os caminhos dos arquivos. A função retorna DataFrames com as listas originais de caminhos e ciclos. Os CSVs produzidos pela linha de comando mantêm essas listas em JSON nas células.

<!-- [IA] OpenAI Codex – revisão dos comandos e conferência das tabelas com as medições publicadas da T26. -->
