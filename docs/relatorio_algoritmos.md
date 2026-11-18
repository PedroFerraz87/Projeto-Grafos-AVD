# Algoritmos e resultados dos labirintos

Rascunho para a seção de Artur na T36, preparado com assistência de IA sobre a versão `f03c80c` do repositório.

## Buscas e caminhos

A BFS minimiza a quantidade de arcos. A fila recebe cada estado na primeira descoberta, e a busca guarda a distância e o arco predecessor. Nos labirintos, a construção do grafo insere os vizinhos em ordem N, L, S e O. Essa ordem determina a escolha entre percursos empatados. A exportação desconta o arco virtual até `ALVO` da contagem dos passos físicos.

Dijkstra usa uma fila de prioridades para explorar a menor distância conhecida. Antes da busca, verifica os pesos e retorna uma recusa se encontrar algum arco negativo. Com pesos válidos, guarda o arco escolhido para reconstruir o caminho. Isso também preserva o peso efetivo quando há arcos paralelos.

Bellman-Ford aceita pesos negativos. O algoritmo tenta melhorar as distâncias em até `V − 1` passagens pelos arcos e faz uma passagem adicional para detectar ciclos negativos alcançáveis. Quando encontra um ciclo, extrai uma sequência fechada de arcos e propaga seu efeito aos vértices que podem ser alcançados a partir dele. O resultado até `ALVO` só recebe `CICLO_NEGATIVO` quando esse nó está entre os afetados.

| Algoritmo | Tempo da versão testada |
|---|---|
| BFS | `O(V_R² + E_R)` no pior caso devido à retirada do início de uma lista com `pop(0)`. Uma fila com remoção constante permite o limite usual `O(V_R + E_R)`. |
| DFS | `O(V_R + E_R)`. |
| Dijkstra | `O(E + (V_R + E_R) log(2 + E_R))` contando a checagem global de pesos e as entradas repetidas no heap. |
| Bellman-Ford | `O(VE)` no pior caso. |

`V_R` e `E_R` representam os vértices e arcos alcançáveis da fonte. `V` e `E` representam todo o grafo.

## Classificação dos arcos da DFS

Na DFS iterativa, a pilha guarda o estado atual e a posição na lista de vizinhos. Cada descoberta e finalização avança o relógio. A classe é definida na ordem de exame dos arcos.

| Classe | Condição durante o exame |
|---|---|
| `arvore` | O destino ainda não foi descoberto e o arco inicia sua exploração. |
| `retorno` | O destino continua ativo na pilha. Esse arco indica um ciclo dirigido alcançável. |
| `avanco` | O destino já foi finalizado e foi descoberto depois da origem. |
| `cruzamento` | O destino já foi finalizado e foi descoberto antes da origem. |

O CSV exportado exclui da contagem os arcos com destino `ALVO`. Em m06, foram registrados 23 arcos de árvore, 22 de retorno, nenhum de avanço e 1 de cruzamento. Em m07, foram 15 de árvore, 19 de retorno, 4 de avanço e nenhum de cruzamento. Os ciclos da DFS são detectados pela direção dos arcos, sem usar os pesos.

## Ciclo negativo e correção do m06

Na regra original, o percurso de ida e volta entre `(3,6)|-|{}` e `(3,5)|-|{}` usa arcos de pesos −2 e +1, com soma −1. O ciclo é alcançável do início e permite seguir até `ALVO`. Cada repetição reduz o custo em uma unidade, de modo que o custo até o alvo não tem mínimo finito.

A opção `--fonte-consumivel` acrescenta ao estado o conjunto das fontes já usadas. Entrar numa fonte pela primeira vez custa −2. Entrar novamente na mesma fonte custa 1.

| Resultado | Regra original | Fonte consumível |
|---|---:|---:|
| Estados físicos | 24 | 40 |
| Arcos físicos | 46 | 76 |
| Nós com `ALVO` | 25 | 41 |
| Arcos com `ALVO` | 47 | 78 |
| Ciclo negativo encontrado | Custo −1 | Nenhum |
| Bellman-Ford até `ALVO` | `CICLO_NEGATIVO` | `OK` |
| Menor custo | Sem mínimo finito | 10 em 10 passos físicos |

A conferência local da regra consumível usou o comando abaixo e a chamada direta ao construtor do grafo. Dijkstra ainda recusa o grafo corrigido, pois a primeira entrada na fonte conserva peso negativo.

```powershell
python -m src.cli --mapa m06 --alg BELLMAN_FORD --fonte-consumivel --out ../t36-algoritmos/m06-fonte-consumivel
```

Na CLI, a sequência principal de ciclo em `ciclo_negativo_m06.json` corresponde à regra original. O campo `correcao` registra o custo 10 do grafo consumível.

## Ausência de solução no m07

A busca a partir de `(1,1)|-|{}` chega a 16 estados físicos. Nenhum alcança `ALVO`. A busca inversa parte do alvo no grafo transposto e identifica quais estados conseguem chegar até ele. Ao descontar esse conjunto dos estados alcançáveis a partir do início, obtêm-se as 16 armadilhas registradas em `armadilhas_m07.csv`. A maior distância da fonte nessa lista é 7 passos.

BFS, Dijkstra e Bellman-Ford registram `SEM_SOLUCAO` em `solucoes.csv`. A ausência de caminho decorre da exploração de todos os estados alcançáveis sob as regras do mapa.

Os dados publicados da Parte 1 estão em [solucoes.csv](../out/parte1/solucoes.csv), [dfs_classificacao.csv](../out/parte1/dfs_classificacao.csv), [ciclo_negativo_m06.json](../out/parte1/ciclo_negativo_m06.json) e [armadilhas_m07.csv](../out/parte1/armadilhas_m07.csv).
