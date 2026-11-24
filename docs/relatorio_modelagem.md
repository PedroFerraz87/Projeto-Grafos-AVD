# Modelagem dos labirintos e mapas do grupo

Seção de Ricardo Machado (P1) para revisão de Artur Antunes e incorporação ao relatório técnico na T36 (seções 2.1, 2.2 e 2.6 do modelo). Os números foram conferidos em 23/11/2026 com `python -m pytest -q` (570 testes passando) e com os arquivos de `out/parte1/`.

## 1. O mapa não é o grafo: modelagem do estado

Um mapa é uma grade de símbolos, mas o que o jogador pode fazer em uma casa depende do que ele já fez: com a chave `a`, a porta `A` é passável; sem ela, é parede. Por isso o nó do grafo não é a casa, e sim o **estado**: `(posição, chaves coletadas, bônus consumidos)`. Uma mesma casa gera vários nós.

O rótulo é `(l,c)|chaves|{bônus}`. As coordenadas são de base 0 e contam a borda de `#`, então `S` está em `(1,1)` nos mapas fornecidos. As chaves aparecem em ordem alfabética (`-` se não há nenhuma) e os bônus são os índices, em ordem de leitura do mapa, dos que já foram consumidos. Exemplos: `(1,1)|-|{}` (estado inicial do m02), `(3,11)|a|{}` (na casa da chave `a`) e `(3,5)|ab|{0,2}`. Com a opção `--fonte-consumivel`, o rótulo ganha um quarto campo com as fontes consumidas (decisão do grupo, seção 2 de `docs/contratos.md`).

### 1.1 Grafo de posições e grafo de estados

| | Grafo de posições (`G_pos`) | Grafo de estados (`G_est`) |
|---|---|---|
| Nó | casa livre | `(posição, chaves, bônus)` |
| Chaves e bônus | ignorados | fazem parte do estado |
| Construção | varredura da grade | exploração em largura a partir de `S`; só entram estados alcançáveis |
| Papel | modelo ingênuo, usado para comparação | grafo em que os algoritmos rodam |

No m02, a diferença muda a resposta:

| Modelagem | Nós | Arcos | De `S` até `G` | Resultado |
|---|---:|---:|---|---|
| `G_pos`, porta como chão | 23 | 43 | 10 passos, custo 10, pela porta `A` trancada | caminho inválido |
| `G_pos`, porta como parede | 22 | 39 | `G` inalcançável | falha |
| `G_est` | 39 | 74 | 34 passos, custo 46: pega a chave e volta | caminho válido |

Em `G_est`, a ordem e o tamanho não contam o nó virtual `ALVO` nem os arcos até ele. Os testes dessa comparação estão em `tests/test_estados.py`.

### 1.2 Regras implementadas

| Regra | Implementação |
|---|---|
| Movimento | quatro direções, sempre na ordem N, L, S, O; o custo do movimento é o custo da casa de destino |
| Custos | `.`, `S`, `G`, chaves, portas e esteiras valem 1; lama `,` vale 3; água `~` vale 5 |
| Parede e porta | não se entra em `#`; a porta `A`–`D` só com a chave `a`–`d` correspondente |
| Chave | é coletada ao entrar na casa, muda a camada e fica para sempre |
| Esteira `>` `<` `^` `v` | de uma esteira só se sai na direção da seta; entrar nela vindo de outro lado é permitido. Se a seta aponta para uma parede, o estado fica sem saída |
| Bônus `+` | vale −4 só na primeira vez (o índice entra no rótulo); depois custa 1 |
| Fonte `*` | vale −2 toda vez, o que cria ciclo negativo no m06. Com a fonte consumível, vale −2 só na primeira vez |
| `G` | fim do jogo: nenhum arco sai de um estado em `G`, exceto o arco de custo 0 até `ALVO` |
| Exploração | BFS a partir de `(1,1)|-|{}`; os vizinhos entram em N, L, S, O e a ordem de inserção no grafo é a de descoberta |

O código está em `src/graphs/io.py` (leitura e validação: retangular, um `S`, ao menos um `G`, símbolos conhecidos) e `src/graphs/estados.py` (`construir_g_pos`, `construir_g_est`, `rotulo_est`).

### 1.3 Tamanho do espaço de estados

O teto teórico é `casas livres × 2^(chaves) × 2^(bônus)`, em que casas livres são todas as que não são parede. O grafo real fica abaixo dele, porque só entram os estados alcançáveis.

| Mapa | Casas livres | Chaves | Bônus | Teto | Estados alcançáveis | Ocupação |
|---|---:|---:|---:|---:|---:|---:|
| m02 | 23 | 1 | 0 | 46 | 39 | 84,78% |
| Mapa mínimo | 7 | 1 | 0 | 14 | 11 | 78,57% |
| m1 | 69 | 3 | 3 | 4.416 | 1.904 | 43,12% |
| m2 | 18 | 0 | 0 | 18 | 13 | 72,22% |

No m1, dos 8 conjuntos possíveis de chaves aparecem 6 (`-`, `a`, `b`, `ab`, `bc` e `abc`): a chave `c` só se alcança depois da porta `B`, que exige `b`. Por isso não existem estados com `c` sem `b`.

## 2. Por que o grafo é dirigido

Um arco `u → v` significa que o movimento de `u` para `v` é permitido. As regras do jogo tornam essa relação assimétrica, então o grafo não pode ser tratado como não dirigido. Nos dez mapas (m01 a m08, m1 e m2), cada arco sem arco inverso é explicado por exatamente uma de quatro regras, e nenhum fica sem explicação. A tabela mostra cinco deles:

| Mapa | Arcos | Sem arco inverso | Troca de camada (chave) | Consumo de bônus | Esteira | Chegada a `G` | Arcos cujo inverso tem outro peso |
|---|---:|---:|---:|---:|---:|---:|---:|
| m02 | 74 | 2 | 1 | 0 | 0 | 1 | 8 |
| m04 | 66 | 6 | 1 | 0 | 4 | 1 | 14 |
| m05 | 438 | 22 | 0 | 12 | 0 | 10 | 24 |
| Mapa mínimo | 16 | 4 | 1 | 0 | 2 | 1 | 0 |
| m1 | 3.752 | 280 | 32 | 40 | 200 | 8 | 352 |

Os arcos da tabela não incluem os arcos até `ALVO`. Cada causa tem um exemplo concreto:

- **Chave.** No m02, o arco `(3,10)|-|{}` → `(3,11)|a|{}` existe, mas `(3,11)|a|{}` só leva a `(3,10)|a|{}`: não há como "descoletar" a chave. Nenhum dos arcos que mudam de camada tem volta, nos dez mapas. As camadas só avançam, e os ciclos ficam dentro de cada camada.
- **Bônus.** Consumir o bônus muda o estado e o torna de custo 1 dali em diante. No m05, os 12 arcos de consumo não têm inverso.
- **Esteira.** Entra-se numa esteira por qualquer lado, mas sai-se só pela seta. No mapa mínimo, a esteira de `(3,1)` aponta para a parede: o estado existe e não tem saída.
- **`G`.** O jogo acaba; só sai o arco virtual até `ALVO`.
- **Pesos.** O custo do arco é o custo da casa de destino, então ir e voltar custam diferente. No m02, 8 arcos têm um inverso de outro peso, por causa da lama.

A direção é o que permite os resultados da Parte 1:

1. **Ciclo negativo.** Em um grafo não dirigido, qualquer aresta negativa já formaria o ciclo `u → v → u` de custo negativo. Em `G_est`, o bônus vale −4 só uma vez, então o m05 não tem ciclo negativo. Em `G_pos`, com o bônus fixo em −4, tem. No m06, a fonte forma um ciclo dirigido real: `(3,6)|-|{}` → `(3,5)|-|{}` custa −2 e a volta custa 1, para um custo de ciclo de −1.
2. **Armadilhas.** Um estado-armadilha é alcançável a partir de `S`, mas não alcança `ALVO`. Achá-los exige a busca reversa no grafo transposto (`Graph.transposto`), que só existe como operação em grafo dirigido: o m04 tem 4 e o m07 tem 16, todos os seus estados.
3. **DFS.** Um arco de retorno indica ciclo dirigido; a classificação dos arcos depende do sentido de cada um.

A Parte 2 também é dirigida (um usuário avalia outro), como descrito na seção 3.3 do relatório.

## 3. O mapa mínimo (T04)

O plano pediu o `G_est` do m02 e um mapa mínimo de até 5×7, com estados e arcos contados antes de programar. O mapa mínimo é o `tests/fixtures/mapa_minimo.txt`:

```
#######
#S.aAG#
#.#####
#>#####
#######
```

| Contagem | Valor |
|---|---|
| Estados | 11: 4 sem chaves e 7 com a chave `a` |
| Arcos | 16 (17 com o arco `G → ALVO`) |
| Troca de camada | 1: entrar em `(1,3)`, a casa da chave |
| Estados-armadilha | 2: a esteira de `(3,1)`, apontando para a parede, nas duas camadas |
| Menor caminho | 4 passos, custo 4: `S`, `(1,2)`, chave `a`, porta `A`, `G` |

Ele cobre o que o `test_estados` exige: troca de camada, esteira para parede e a combinação de chave e porta. O m02 serve de exemplo maior. Seus 39 estados se conferem por estrutura: sem a chave, as 16 casas formam uma cadeia, com 15 pares de arcos e 30 arcos; com a chave, as 23 casas formam uma cadeia com 22 pares, 44 arcos, menos o do `G`, que não tem saída, o que dá 43; mais 1 arco de troca de camada, 74 no total.

As figuras estão em `docs/t04_g_est_m02.png` e `docs/t04_g_est_mapa_minimo.png`. Elas foram geradas digitalmente, com apoio, e as contagens foram conferidas por script e manualmente pelo grupo. As contagens seguem a orientação de não incluir o nó `ALVO` nem o arco até ele.

## 4. Mapas do grupo (T29): gabarito

Os dois mapas estão em `data/mapas_grupo/` e foram validados pelo código (`ler_mapa`, `analisar`, `exportar_todos`) e pelos testes de `tests/test_mapas_grupo.py`.

| Mapa | Estados | Arcos | Passos (BFS) | Custo mínimo | Percentual de estados-armadilha |
|---|---:|---:|---:|---:|---:|
| m1 — chaves, esteiras e bônus | 1.904 | 3.752 | 46 | 42 | 0% |
| m2 — mapa armadilha | 13 | 17 | 5 | 5 | 46,15% (6 de 13) |

Os arcos não incluem os arcos até `ALVO`. O custo mínimo do m1 vem do Bellman-Ford, porque o Dijkstra recusa o mapa por causa do bônus.

### 4.1 m1

O m1 tem 10×31, com 3 chaves (`a`, `b`, `c`) e suas 3 portas, 7 casas de esteira e 3 bônus. Ele combina decisões:

- contornar a porta `A` por baixo custa 10 a mais do que atravessá-la, e buscar a chave `a` custa 6 a mais, então o caminho ótimo busca a chave e economiza 4;
- a faixa de esteiras `>>>>` custa 9 contra 13 do trecho de lama que ela evita, e economiza 4;
- o bônus da rua rende 3 (−4 e mais 1 de volta à rua); o bônus-isca da coluna 21 custaria 1 a mais, e o ótimo o ignora;
- a "estrada" de esteiras para baixo existe, mas é mais cara e fica fora do caminho ótimo.

O caminho de menor custo tem 52 passos e custo 42, enquanto o de menos passos (BFS) tem 46 passos e custo 49: menos passos não é menor custo. A sequência de eventos do caminho ótimo é: chave `a` (passo 6), bônus (12), porta `A` (16), esteiras (23 a 26), chave `b` (33), porta `B` (39), bônus (44), chave `c` (45), porta `C` (51) e chegada (52). Ele coleta bônus, passa por esteira e usa as três chaves.

O custo 42 foi conferido de três formas independentes: o Bellman-Ford do projeto, o `networkx` (oráculo dos testes) e a soma casa a casa do percurso lendo só a grade.

### 4.2 m2

O m2 tem um corredor de `S` até `G` e um ramal que desce até uma faixa de 6 esteiras que termina na parede. Entrar no ramal é um beco sem saída: os 6 estados da faixa são armadilha, 46,15% dos 13 estados alcançáveis. As contagens foram feitas à mão: 13 estados (5 do corredor, `G`, a casa do ramal e as 6 esteiras) e 17 arcos (9 do corredor, 2 do ramal, 1 de entrada na esteira e 5 da faixa).

### 4.3 Conferência com as exigências do enunciado

| Exigência (leitura do grupo) | Evidência |
|---|---|
| m1 com pelo menos 3 chaves | `a`, `b`, `c` |
| m1 com esteiras e bônus | 7 esteiras e 3 bônus |
| O caminho de menor custo coleta um bônus e passa por uma esteira | eventos `bonus` (passos 12 e 44) e `esteira` (passos 23 a 26) |
| m2 com mais de 20% dos estados alcançáveis em armadilha | 6 de 13, 46,15% |

## 5. Reprodução

```
python -m pytest -q tests/test_io.py tests/test_estados.py tests/test_mapas_grupo.py
python -m src.cli --mapa m1 --out out/verificacao
python -m src.cli --mapa m2 --out out/verificacao
python -m src.graphs.estados
```

Os dois `src.cli` geram `percurso_m1.json`, `percurso_m2.json` e as linhas do mapa em `solucoes.csv` e `dfs_classificacao.csv` na pasta `out/verificacao`; os arquivos entregues em `out/parte1/` vêm de `python -m src.cli` sem `--mapa`. A pasta separada é necessária porque `--mapa` regrava o `solucoes.csv` só com o mapa escolhido. O último comando gera os `arestas_<mapa>.csv`.
