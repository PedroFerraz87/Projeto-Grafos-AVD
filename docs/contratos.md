# Contratos de dados — `out/parte1` e `out/parte2`

> **Regra de prioridade:** onde este documento e o enunciado divergirem, vale o enunciado
> (`Projeto_Final_TEORIADOSGRAFOS262-1.pdf`). As colunas exigidas pelo enunciado vêm sempre
> primeiro, com o nome e a ordem do enunciado; colunas extras do grupo vêm depois delas.
> Os números que aparecem nos exemplos são ilustrativos (zeros ou `<n>`), não resultados dos mapas.

## 1. Convenções gerais

### 1.1 CSV

| Item | Regra |
|---|---|
| Codificação | UTF-8, sem BOM |
| Separador | vírgula (`,`) |
| Fim de linha | `\n` |
| Cabeçalho | obrigatório, na primeira linha, com os nomes exatos deste documento e na mesma ordem (colunas do enunciado primeiro, extras depois) |
| Decimais | ponto (`.`), sem separador de milhar |
| Booleanos | `true` / `false` (minúsculos) |
| Valor ausente / não se aplica | campo vazio |
| Infinito (sem caminho) | campo vazio na coluna numérica + `status` explicando o motivo |
| Texto com vírgula ou aspas | entre aspas duplas, aspas internas duplicadas (padrão do módulo `csv` do Python). Como todo rótulo de estado tem vírgula, ele sempre sai entre aspas |
| Ordem das linhas | a indicada em cada arquivo; quando não indicada, a ordem de geração (determinística) |

### 1.2 JSON

| Item | Regra |
|---|---|
| Codificação | UTF-8, `ensure_ascii=False`, `indent=2` |
| Chaves | `snake_case`, sem acento |
| Infinito / sem caminho | `null`, nunca `Infinity` nem string |
| Listas de estados | sempre com o rótulo de estado da seção 2 (string) |
| Raiz | sempre um objeto, nunca uma lista solta |

### 1.3 Nomes de mapas

- `mapa` é o nome do arquivo sem extensão, exatamente como em `data/mapas/` ou
  `data/mapas_grupo/`: `m01_terreno`, `m02_uma_chave`, `m03_tres_chaves`, `m04_esteiras`,
  `m05_bonus`, `m06_fonte`, `m07_impossivel`, `m08_grande` e os dois mapas do grupo.
- Nos nomes de arquivo com `<mapa>` usa-se o **prefixo curto** (`m01` ... `m08`, e o nome
  do arquivo para os mapas do grupo). Ex.: `arestas_m03.csv`, `graus_m08.csv`.

### 1.4 Coordenadas, movimentos e algoritmos

- Coordenadas `(l,c)`: **linha e coluna base 0**, contadas na grade já sem as linhas de
  comentário (`;`). A borda de `#` conta, então em todos os mapas fornecidos `S` está em `(1,1)`.
- Movimentos, sempre nesta ordem de geração (a mesma ordem de inserção preservada pelo
  `graph.py`): `N` (linha − 1), `L` (coluna + 1), `S` (linha + 1), `O` (coluna − 1).
  O arco virtual até o nó `ALVO` usa movimento `-`.
- Nomes de algoritmo, em maiúsculas, iguais aos aceitos em `--alg` da CLI:
  `BFS`, `DFS`, `DIJKSTRA`, `BELLMAN_FORD`.
- Modelagem: `G_est` (grafo de estados) ou `G_pos` (grafo de posições).

---

## 2. Rótulo de estado

Todo estado do `G_est` é identificado, em **todos** os arquivos, pelo rótulo obrigatório do
enunciado (Seção 1 da Parte 1):

```
(l,c)|chaves|{bonus}
```

| Parte | Conteúdo | Regras |
|---|---|---|
| `(l,c)` | posição atual | sem espaços: `(3,12)` |
| `chaves` | chaves já coletadas | letras minúsculas em **ordem alfabética**, concatenadas; **`-` se nenhuma** |
| `{bonus}` | bônus (`+`) **já consumidos** | **índices** dos bônus, numerados a partir de 0 em ordem de leitura do mapa (linha, depois coluna), em ordem crescente, separados por vírgula, sem espaços; `{}` se nenhum. Ex.: `{0,2}` |

Com a opção `--fonte-consumivel` ligada, acrescenta-se um quarto campo com as fontes (`*`)
já consumidas, numeradas do mesmo jeito (índices a partir de 0, em ordem de leitura). Essa
extensão é decisão do grupo, já que o enunciado só define as três partes:

```
(l,c)|chaves|{bonus}|{fontes}
```

Sem a opção, o quarto campo **não aparece** (o rótulo continua com três partes).

**Nó alvo:** o nó virtual que recebe um arco de custo 0 de cada estado sobre `G` tem rótulo
exatamente `ALVO`. Ele **não entra nas métricas** (ordem, tamanho, densidade, graus, camadas).

**Grafo de posições (`G_pos`):** o rótulo é só `(l,c)`.

Exemplos:

| Situação | Rótulo |
|---|---|
| Início de qualquer mapa fornecido (exemplo do enunciado para o m02) | `(1,1)\|-\|{}` |
| m02, ao entrar na casa da chave `a` em `(3,11)` | `(3,11)\|a\|{}` |
| Formato com duas chaves e dois bônus consumidos (exemplo do enunciado) | `(3,5)\|ab\|{0,2}` |
| m05, ao entrar no bônus de índice 0, em `(3,2)` | `(3,2)\|-\|{0}` |
| m06 com fonte consumível, ao entrar na fonte de índice 0, em `(3,5)` | `(3,5)\|-\|{}\|{0}` |
| Nó virtual de chegada | `ALVO` |

A **camada** de um estado é a sua parte `chaves`; a camada sem chaves é `-`.

---

## 3. `out/parte1/`

### 3.1 `arestas_<mapa>.csv`

Um arquivo por mapa (inclusive `m08`), uma linha por arco de `G_est`, na ordem de inserção
(BFS de exploração a partir de `S`, vizinhos em `N, L, S, O`). Inclui os arcos até `ALVO`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `origem` | str | rótulo do estado de origem |
| `destino` | str | rótulo do estado de destino (ou `ALVO`) |
| `movimento` | str | `N`, `L`, `S`, `O` ou `-` (arco até `ALVO`) |
| `casa_destino` | str | caractere da casa onde o movimento termina (`.`, `,`, `~`, `a`, `A`, `+`, `*`, `G`, ...); vazio para `ALVO` |
| `peso` | número | custo do arco (pode ser negativo: bônus e fonte) |
| `via_esteira` | bool | *extra:* `true` se o arco sai de uma esteira |
| `camada_origem` | str | *extra:* chaves da origem (`-` se nenhuma) |
| `camada_destino` | str | *extra:* chaves do destino (`-` se nenhuma; vazio para `ALVO`) |

As cinco primeiras colunas são as do enunciado, na mesma ordem. Exemplo (as três primeiras
linhas de dados são as do próprio enunciado):

```csv
origem,destino,movimento,casa_destino,peso,via_esteira,camada_origem,camada_destino
"(1,1)|-|{}","(2,1)|-|{}",S,.,1,false,-,-
"(3,10)|-|{}","(3,11)|a|{}",L,a,1,false,-,a
"(1,5)|a|{}","(1,6)|a|{}",L,A,1,false,a,a
"(1,11)|a|{}",ALVO,-,,0,false,a,
```

### 3.2 `solucoes.csv`

BFS, Dijkstra e Bellman-Ford em `G_est`, em todos os mapas (m01 a m08 e os mapas do grupo).
Uma linha por par (mapa, algoritmo), ordenada por `mapa` e depois por
`BFS, DIJKSTRA, BELLMAN_FORD`. A DFS tem arquivo próprio (3.6).

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa (seção 1.3) |
| `algoritmo` | str | `BFS`, `DIJKSTRA`, `BELLMAN_FORD` |
| `passos` | int | número de movimentos até `ALVO`, sem contar o arco virtual até `ALVO`; vazio se não houver caminho |
| `custo` | número | soma dos pesos do caminho; vazio se não houver caminho, recusa ou ciclo negativo |
| `status` | str | exatamente um de `OK`, `RECUSA`, `CICLO_NEGATIVO`, `SEM_SOLUCAO` (valores do enunciado) |
| `caminho` | str | rótulos do caminho, do estado inicial ao último estado antes de `ALVO`, separados por ` > `; vazio se não houver |
| `ordem` | int | *extra:* `\|V\|` de `G_est`, sem `ALVO` |
| `tamanho` | int | *extra:* `\|E\|` de `G_est`, sem os arcos até `ALVO` |
| `estados_visitados` | int | *extra:* estados alcançados pelo algoritmo a partir de `S` |
| `tempo_ms` | número | *extra:* tempo do algoritmo (sem leitura nem construção do grafo) |
| `observacao` | str | *extra:* texto curto, ex.: motivo da recusa do Dijkstra |

`RECUSA` = Dijkstra diante de arco negativo; `CICLO_NEGATIVO` = Bellman-Ford encontrou ciclo
negativo que alcança `ALVO`; `SEM_SOLUCAO` = `ALVO` inalcançável.

```csv
mapa,algoritmo,passos,custo,status,caminho,ordem,tamanho,estados_visitados,tempo_ms,observacao
m02_uma_chave,BFS,<n>,<n>,OK,"(1,1)|-|{} > (2,1)|-|{} > ...",<n>,<n>,<n>,<n>,
m05_bonus,DIJKSTRA,,,RECUSA,,<n>,<n>,,,arco com peso negativo
m07_impossivel,BFS,,,SEM_SOLUCAO,,<n>,<n>,<n>,<n>,ALVO inalcançável
```

### 3.3 Percurso em JSON — `percurso_m03.json` (e qualquer `percurso_<mapa>.json`)

Caminho de menor custo, estado a estado. Valores ilustrativos:

```json
{
  "mapa": "m03_tres_chaves",
  "algoritmo": "DIJKSTRA",
  "modelagem": "G_est",
  "opcoes": { "fonte_consumivel": false, "porta_como": "parede" },
  "grade": [
    "#################",
    "#S.....A....b...#"
  ],
  "inicio": "(1,1)|-|{}",
  "fim": "ALVO",
  "encontrou": true,
  "passos": 0,
  "custo": 0,
  "percurso": [
    {
      "passo": 0,
      "estado": "(1,1)|-|{}",
      "linha": 1,
      "coluna": 1,
      "chaves": "",
      "bonus": [],
      "camada": "-",
      "movimento": null,
      "peso": 0,
      "custo_acumulado": 0,
      "evento": "inicio"
    },
    {
      "passo": 1,
      "estado": "(1,2)|-|{}",
      "linha": 1,
      "coluna": 2,
      "chaves": "",
      "bonus": [],
      "camada": "-",
      "movimento": "L",
      "peso": 1,
      "custo_acumulado": 1,
      "evento": null
    }
  ]
}
```

| Chave | Tipo | Descrição |
|---|---|---|
| `mapa`, `algoritmo`, `modelagem` | str | como na seção 1 |
| `opcoes` | objeto | opções usadas na construção do grafo (`fonte_consumivel`: bool; `porta_como`: `"parede"` ou `"chao"`, só relevante em `G_pos`) |
| `grade` | lista de str | o mapa lido, uma string por linha, já sem comentários (permite desenhar sem reler o `.txt`) |
| `inicio` | str | rótulo do estado inicial |
| `fim` | str | `ALVO` |
| `encontrou` | bool | `false` → `percurso` vazio, `passos` e `custo` `null` |
| `passos`, `custo` | int / número / `null` | iguais aos de `solucoes.csv` |
| `percurso` | lista | um item por estado do caminho, do início ao último estado físico antes de `ALVO` (o arco até `ALVO` não aparece) |

Cada item de `percurso`:

| Chave | Tipo | Descrição |
|---|---|---|
| `passo` | int | 0 no estado inicial, depois 1, 2, ... |
| `estado` | str | rótulo completo |
| `linha`, `coluna` | int | posição (repete a do rótulo, para não precisar decompor a string) |
| `chaves` | str | chaves no estado, em ordem alfabética (`""` se nenhuma) |
| `bonus` | lista de int | índices dos bônus já consumidos (os mesmos do rótulo) |
| `camada` | str | igual a `chaves`, com `-` para vazio |
| `movimento` | str / `null` | movimento que levou a este estado (`null` no passo 0) |
| `peso` | número | peso do arco que levou a este estado (0 no passo 0) |
| `custo_acumulado` | número | soma dos pesos até aqui |
| `evento` | str / `null` | `inicio`, `chave_a` ... `chave_d`, `porta_A` ... `porta_D`, `esteira`, `bonus`, `fonte`, `chegada` ou `null` |

Quando um passo dispara mais de um evento, usa-se o mais importante na ordem
`chegada > chave > porta > bonus > fonte > esteira`.

### 3.4 `ciclo_negativo_m06.json`

Ciclo negativo encontrado pelo Bellman-Ford, exibido como sequência de estados e custo.
Estrutura (rótulos e pesos são marcadores, não o resultado do m06):

```json
{
  "mapa": "m06_fonte",
  "modelagem": "G_est",
  "algoritmo": "BELLMAN_FORD",
  "opcoes": { "fonte_consumivel": false },
  "fonte": "(1,1)|-|{}",
  "ciclo_encontrado": true,
  "ciclo": ["<estado X>", "<estado Y>", "<estado X>"],
  "arcos": [
    { "origem": "<estado X>", "destino": "<estado Y>", "peso": 0, "movimento": "-" },
    { "origem": "<estado Y>", "destino": "<estado X>", "peso": 0, "movimento": "-" }
  ],
  "custo_ciclo": 0,
  "afeta_alvo": true,
  "correcao": {
    "aplicada": false,
    "descricao": null,
    "custo_minimo_apos_correcao": null
  }
}
```

| Chave | Tipo | Descrição |
|---|---|---|
| `ciclo` | lista de str | ciclo **fechado**: o primeiro rótulo se repete no fim; pode começar em qualquer estado do ciclo |
| `arcos` | lista | os arcos do ciclo, na ordem, com o peso de cada um |
| `custo_ciclo` | número | soma dos pesos de `arcos` (< 0) |
| `afeta_alvo` | bool | o ciclo alcança `ALVO` (o mínimo até `ALVO` fica indefinido) |
| `correcao` | objeto | preenchido com `--fonte-consumivel` (correção do m06, P3): `aplicada`, texto curto e o custo mínimo finito obtido depois dela |

Sem ciclo: `ciclo_encontrado: false`, `ciclo` e `arcos` vazios, `custo_ciclo: null`.

### 3.5 `armadilhas_m04.csv` e `armadilhas_m07.csv`

Estados alcançáveis a partir de `S` dos quais `ALVO` é inalcançável (busca a partir de `ALVO`
no transposto). Uma linha por estado, ordenada por `linha`, `coluna`, `chaves`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa |
| `estado` | str | rótulo |
| `linha`, `coluna` | int | posição |
| `chaves` | str | chaves (`-` se nenhuma) |
| `simbolo` | str | caractere da casa |
| `distancia_bfs` | int | distância em passos de `S` até o estado |

O total e o percentual de armadilhas sobre os estados alcançáveis vão em
`metricas_global.json` (`armadilhas` e `pct_armadilhas`), não neste CSV.

### 3.6 `dfs_classificacao.csv`

DFS a partir do estado inicial, vizinhos em `N, L, S, O`. **Uma linha por mapa** com a
contagem de arcos de cada classe, como no enunciado.

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa |
| `arvore` | int | arcos de árvore |
| `retorno` | int | arcos de retorno |
| `avanco` | int | arcos de avanço |
| `cruzamento` | int | arcos de cruzamento |
| `possui_ciclo` | bool | *extra:* `true` se houver arco de retorno |

```csv
mapa,arvore,retorno,avanco,cruzamento,possui_ciclo
m02_uma_chave,<n>,<n>,<n>,<n>,true
```

Opcional, para depuração e para o relatório: `dfs_arcos_<mapa>.csv`, uma linha por arco
examinado (`origem,destino,classe,d_origem,f_origem,d_destino,f_destino`). Convenção do relógio:
começa em 1 e é incrementado a cada descoberta e a cada finalização (CLRS).

### 3.7 `metricas_global.json`

Um objeto por mapa, com `G_pos` e `G_est` lado a lado (o enunciado pede ordem, tamanho e
densidade dos dois, além do teto teórico e da taxa de ocupação). `ALVO` e seus arcos
**não são contados**.

```json
{
  "gerado_em": "2026-11-18T20:00:00",
  "mapas": {
    "m02_uma_chave": {
      "G_pos": { "ordem": 0, "tamanho": 0, "densidade": 0.0 },
      "G_est": {
        "ordem": 0,
        "tamanho": 0,
        "densidade": 0.0,
        "teto_teorico": 0,
        "taxa_ocupacao": 0.0,
        "grau_saida": { "min": 0, "max": 0, "medio": 0.0 },
        "grau_entrada": { "min": 0, "max": 0, "medio": 0.0 },
        "maior_grau_saida": { "estado": "(l,c)|-|{}", "grau": 0 },
        "maior_grau_entrada": { "estado": "(l,c)|-|{}", "grau": 0 },
        "becos": 0,
        "multiplicidade": { "max": 0, "casas_no_max": 0, "media": 0.0 },
        "camadas": 0,
        "arcos_entre_camadas": 0,
        "armadilhas": 0,
        "pct_armadilhas": 0.0,
        "dfs": { "arvore": 0, "retorno": 0, "avanco": 0, "cruzamento": 0, "possui_ciclo": false }
      }
    }
  }
}
```

| Chave | Descrição |
|---|---|
| `ordem` / `tamanho` | `\|V\|` e `\|E\|`, sem `ALVO` nem os arcos até ele |
| `densidade` | densidade dirigida `\|E\| / (\|V\| · (\|V\| − 1))`; 0 se `\|V\| < 2` |
| `teto_teorico` | casas livres × 2^(nº de chaves) × 2^(nº de bônus) (fórmula do enunciado) |
| `taxa_ocupacao` | `ordem` de `G_est` ÷ `teto_teorico` |
| `maior_grau_saida` / `maior_grau_entrada` | estado com maior grau; desempate pela ordem de leitura do rótulo |
| `becos` | estados com grau de saída 0 que não estão em `G` (ex.: esteira apontando para a parede) |
| `multiplicidade` | estados de `G_est` por casa: máximo, quantas casas o atingem e média |
| `camadas` / `arcos_entre_camadas` | quantidade de conjuntos de chaves distintos e arcos cuja camada muda |

### 3.8 `camadas.json`

Métricas por camada (subgrafo induzido pelos estados com o mesmo conjunto de chaves), por mapa,
e os arcos entre camadas com as casas que os geram.

```json
{
  "m02_uma_chave": {
    "camadas": [
      { "camada": "-", "ordem": 0, "tamanho": 0, "densidade": 0.0 },
      { "camada": "a", "ordem": 0, "tamanho": 0, "densidade": 0.0 }
    ],
    "arcos_entre_camadas": [
      { "de": "-", "para": "a", "quantidade": 0, "casas": [[0, 0]] }
    ]
  }
}
```

### 3.9 `graus_<mapa>.csv`

Uma linha por estado (sem `ALVO`), na ordem de inserção dos vértices no `Graph`. Os arcos até
`ALVO` não entram nos graus, por isso um estado sobre `G` tem grau de saída 0 e **não** é beco.

| Coluna | Tipo | Descrição |
|---|---|---|
| `estado` | str | rótulo |
| `grau_entrada` | int | grau de entrada em `G_est` |
| `grau_saida` | int | grau de saída em `G_est` |
| `linha`, `coluna` | int | *extra:* posição |
| `camada` | str | *extra:* chaves (`-` se nenhuma) |
| `beco` | bool | *extra:* `grau_saida` = 0 e o estado não está em `G` |

### 3.10 `multiplicidade_m08.csv` (extra, base do heatmap)

Uma linha por casa não-parede da grade, ordenada por `linha`, `coluna`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `linha`, `coluna` | int | posição |
| `simbolo` | str | caractere da casa |
| `multiplicidade` | int | quantos estados de `G_est` estão nessa casa (0 se inalcançável) |

### 3.11 `comparacao_modelagem.csv`

BFS em passos de `S` até `G` nas três modelagens, para `m02`, `m03` e `m04`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa |
| `abordagem` | str | `pos_porta_chao` (G_pos, porta como chão), `pos_porta_parede` (G_pos, porta como parede) ou `estados` (G_est) |
| `passos` | int | passos do BFS até `G`; vazio se não chegar |
| `caminho_valido` | bool | o caminho respeita as regras do jogo (ex.: não atravessa porta sem a chave); `false` se não houver caminho |
| `observacao` | str | texto curto (ex.: "atravessa porta trancada", "não alcança G") |

O ciclo negativo do m05 em `G_pos` (bônus −4 fixo) e a ausência dele em `G_est` vão no
relatório; se o grupo quiser um arquivo, usar `ciclo_negativo_m05_pos.json` com a mesma
estrutura da seção 3.4.

### 3.12 Arquivos não tabulares

| Arquivo | Produtor | Lê |
|---|---|---|
| `percurso_m03.png`, `percurso_m08.png` | P5 (T28) | `percurso_<mapa>.json` |
| figura da árvore BFS do m02, figura de `G_est` em camadas, heatmap do m08 | P5/P3 (T28, T30) | `arestas_m02.csv`, `camadas.json`, `multiplicidade_m08.csv` |
| `labirinto_interativo.html` | P5 (T20, T31) | `percurso_<mapa>.json`, `armadilhas_<mapa>.csv`, `metricas_global.json` (dados embutidos no HTML pelo Python) |

---

## 4. `out/parte2/`

Dataset: `data/dataset_parte2/soc-sign-bitcoinalpha.csv`, sem cabeçalho, colunas
`origem,destino,nota,timestamp`. O
arco vai de quem **avalia** (`origem`) para quem é **avaliado** (`destino`). Os vértices são
os ids numéricos do dataset convertidos para `int`.

### 4.1 Recortes

Todo resultado da Parte 2 indica o `recorte` usado: `10`, `50` ou `100` (percentual das
avaliações). O critério de corte (ex.: primeiras N avaliações por `timestamp`) é decidido no
leitor e registrado em `parte2_report.json` → `dataset.criterio_recorte`.

### 4.2 

```json
{
  "dataset": {
    "arquivo": "data/dataset_parte2/soc-sign-bitcoinalpha.csv",
    "vertices": 3783,
    "arcos": 24186,
    "arcos_negativos": 1536,
    "criterio_recorte": "texto curto",
    "recortes": [
      { "recorte": 10, "vertices": 0, "arcos": 0 },
      { "recorte": 50, "vertices": 0, "arcos": 0 },
      { "recorte": 100, "vertices": 3783, "arcos": 24186 }
    ]
  },
  "transformacao_pesos": {
    "dijkstra": "texto curto descrevendo a transformação da nota em peso não negativo",
    "bellman_ford": "texto curto descrevendo o peso usado"
  },
  "bfs": [
    { "fonte": 1, "recorte": 100, "alcancados": 0, "niveis": { "0": 1, "1": 0 }, "nivel_max": 0 }
  ],
  "dfs": [
    { "fonte": 1, "recorte": 100, "alcancados": 0,
      "classes": { "arvore": 0, "retorno": 0, "avanco": 0, "cruzamento": 0 },
      "possui_ciclo": true }
  ],
  "dijkstra": [
    { "origem": 1, "destino": 2, "recorte": 100, "status": "OK",
      "custo": 0, "passos": 0, "caminho": [1, 2] }
  ],
  "bellman_ford": [
    { "caso": "sem_ciclo_negativo", "fonte": 1, "recorte": 100, "status": "OK",
      "ciclo": [], "custo_ciclo": null },
    { "caso": "com_ciclo_negativo", "fonte": 1, "recorte": 100, "status": "CICLO_NEGATIVO",
      "ciclo": [1, 2, 1], "custo_ciclo": -1 }
  ],
  "benchmark": {
    "ambiente": { "python": "3.11.x", "so": "texto", "cpu": "texto", "ram_gb": 0 },
    "execucoes": 5,
    "arquivo_detalhado": "benchmark_parte2.csv",
    "resumo": [
      { "algoritmo": "BFS", "recorte": 100, "vertices": 3783, "arcos": 24186,
        "tempo_medio_ms": 0.0, "tempo_desvio_ms": 0.0 }
    ]
  }
}
```

Regras:

- `bfs` e `dfs`: uma entrada por fonte (3 fontes) e recorte usado.
- `dijkstra`: uma entrada por par (5 pares). `status` ∈ `OK`, `SEM_SOLUCAO`,
  `RECUSA` (mesmos valores de `solucoes.csv`); sem caminho → `custo`, `passos` `null` e `caminho` vazio.
- `bellman_ford`: pelo menos os dois casos obrigatórios (`sem_ciclo_negativo` e
  `com_ciclo_negativo`); `ciclo` é fechado (primeiro id repetido no fim).
- Caminhos e ciclos são listas de ids `int`.

### 4.3 

Uma linha por execução medida (5 execuções × algoritmos × 3 recortes).

| Coluna | Tipo | Descrição |
|---|---|---|
| `algoritmo` | str | `BFS`, `DFS`, `DIJKSTRA`, `BELLMAN_FORD` |
| `recorte` | int | 10, 50 ou 100 |
| `vertices`, `arcos` | int | tamanho do grafo no recorte |
| `execucao` | int | 1 a 5 |
| `fonte` | int | vértice de partida usado |
| `tempo_ms` | número | tempo medido (sem leitura do arquivo nem construção do grafo) |


## 5. Quem produz e quem consome

| Arquivo | Produz | Consome |
|---|---|---|
| `arestas_<mapa>.csv` | P1 (T10) | P3 (T17, T23), P5 (T28) |
| `solucoes.csv` | P1 (T22) | P5 (T31, relatório) |
| `percurso_<mapa>.json` | P1 (T22) | P5 (T20, T28, T31) |
| `ciclo_negativo_m06.json` | P1 (T22) | P3 (correção do m06), relatório |
| `armadilhas_m04.csv`, `armadilhas_m07.csv` | P1/P2 (T15, T22) | P3 (métricas), P5 (T31) |
| `dfs_classificacao.csv` | P1/P2 (T12, T22) | P3 (métricas), relatório |
| `metricas_global.json`, `camadas.json`, `graus_<mapa>.csv`, `multiplicidade_m08.csv` | P3 (T23) | P5 (T30, T31), relatório |
| `comparacao_modelagem.csv` | P3 (T24) | relatório |
| `parte2_report.json`, `benchmark_parte2.csv` | P4 (T26), P2 (T25) | P4/P5 (T32), relatório |

