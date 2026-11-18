# Tabelas de comparação para a T32

Na raiz do projeto, `python -m src.parte2` executa os casos da T25 e grava `out/parte2/parte2_report.json`. A função `src.parte2.gerar_casos(caminho_csv)` retorna os mesmos dados para a integração da T26. Se o JSON no caminho de saída já contém benchmark, use `--out` para escolher outro arquivo.

Use o relatório da Parte 2 para preparar tabelas de BFS, DFS, Dijkstra e Bellman-Ford. Quando a T26 publicar `benchmark_parte2.csv`, passe também esse arquivo para obter as medições e o resumo por algoritmo, recorte e fonte.

```powershell
python -m src.avd.comparacao_algoritmos --out out/parte2/tabelas_t32

python -m src.avd.comparacao_algoritmos --benchmark out/parte2/benchmark_parte2.csv --out out/parte2/tabelas_t32
```

O resumo mantém `vertices` e `arcos` para relacionar cada medição ao tamanho real do grafo. Use `execucoes` para conferir a quantidade de repetições em cada combinação. O tempo médio e o desvio padrão amostral estão em milissegundos. Uma combinação com uma única execução tem o desvio vazio.

Em `comparacao_caminhos.csv`, `passos_bfs` e `passos_dijkstra` contam os arcos dos caminhos obtidos para o mesmo par. `custo_transformado_bfs` e `custo_transformado_dijkstra` somam `10 - nota` ao longo de cada caminho. O BFS escolhe seu caminho pelo número de arcos e esse custo transformado é calculado sobre o caminho encontrado. Os custos dos ciclos de Bellman-Ford seguem os pesos descritos no relatório da T25.

Para usar as tabelas em um notebook, importe `ler_tabelas` de `src.avd.comparacao_algoritmos` e passe os caminhos dos arquivos. A função retorna DataFrames com as listas originais de caminhos e ciclos. Os CSVs produzidos pela linha de comando mantêm essas listas em JSON nas células.
