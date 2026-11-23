# Ensaio de Artur Antunes (T39)

## Explicar o P1

1. Abra `data/mapas/m02_uma_chave.txt` e identifique início, saída, chave e porta. Em `src/graphs/io.py`, localize as validações da leitura do mapa.
2. Em `src/graphs/estados.py`, acompanhe a geração dos estados a partir de `S`. Use o rótulo `(linha,coluna)|chaves|{bonus}` para explicar por que a posição, as chaves coletadas e os bônus já usados fazem parte do estado.
3. Mostre uma linha de [arestas_m02.csv](../out/parte1/arestas_m02.csv) e o arco virtual até `ALVO`. Na grade, localize uma passagem pela porta após encontrar a chave.

## Rodar o mapa novo

Na raiz do projeto, com o ambiente virtual ativo, passe à CLI o caminho do arquivo que o grupo receber. O modo interativo inclui esse mapa e o seleciona na abertura do HTML.

```powershell
$saida = Join-Path ([System.IO.Path]::GetTempPath()) ("grafos-ensaio-" + [guid]::NewGuid())
python -m src.cli --mapa "C:\caminho\mapa.txt" --interactive --out $saida
```

Abra `labirinto_interativo.html` e consulte `solucoes.csv` para comparar passos, custo e status. No ensaio local, o mapa abaixo retornou quatro passos e custo 4 para BFS, Dijkstra e Bellman-Ford.

```text
#######
#S...G#
#######
```

## Demonstrar o P2

- **m03:** compare BFS e Dijkstra. A execução conferida retornou 87 passos e custo 119 na BFS, e 91 passos e custo 99 em Dijkstra.
- **m06:** selecione Bellman-Ford para mostrar o ciclo original. O resultado da fonte consumível consta no campo `correcao` do JSON. O [roteiro da T36](relatorio_algoritmos.md#reprodução-e-testes) reproduz esse caso.
- **m07:** mostre o status `SEM_SOLUCAO` e os 16 estados-armadilha no painel.

O ensaio coletivo é de 15 a 20 minutos e inclui a explicação por integrantes de um pacote diferente do próprio.

<!-- [IA] OpenAI Codex – organização dos comandos e conferência local da demonstração. -->
