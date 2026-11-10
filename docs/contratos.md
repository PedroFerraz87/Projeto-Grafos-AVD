# Contratos de dados — `out/parte1` e `out/parte2`

**Tarefa:** T03 (Sprint 0) · **Responsável:** Luca Albuquerque · **Revisor:** Pedro Ferraz

Este documento fixa o formato de todos os arquivos CSV/JSON gerados em `out/parte1/` e
`out/parte2/`, o formato do rótulo de estado e o formato do percurso em JSON. Ele existe para
que as cinco frentes trabalhem em paralelo a partir de 11/11: quem **produz** um arquivo
escreve exatamente estas colunas/chaves, e quem **consome** (métricas, figuras, interativo,
relatório) pode começar com dados de exemplo neste formato antes de o código real existir.

Qualquer mudança de coluna ou chave deve ser feita **primeiro aqui**, no mesmo commit (ou
antes) do código que a altera, e avisada ao grupo.

---

## 1. Convenções gerais

### 1.1 CSV

| Item | Regra |
|---|---|
| Codificação | UTF-8, sem BOM |
| Separador | vírgula (`,`) |
| Fim de linha | `\n` |
| Cabeçalho | obrigatório, na primeira linha, com os nomes exatos deste documento e na mesma ordem |
| Decimais | ponto (`.`), sem separador de milhar |
| Booleanos | `true` / `false` (minúsculos) |
| Valor ausente / não se aplica | campo vazio |
| Infinito (sem caminho) | campo vazio na coluna numérica + `status` explicando o motivo |
| Texto com vírgula ou aspas | entre aspas duplas, aspas internas duplicadas (padrão do módulo `csv` do Python) |
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

Todo estado do `G_est` é identificado, em **todos** os arquivos, por uma string única:

```
(l,c)|chaves|{bonus}
```

| Parte | Conteúdo | Regras |
|---|---|---|
| `(l,c)` | posição atual | sem espaços: `(3,12)` |
| `chaves` | chaves já coletadas | letras minúsculas em **ordem alfabética**, concatenadas; vazio se nenhuma |
| `{bonus}` | posições de bônus (`+`) **já consumidos** | lista de `(l,c)` em ordem crescente de linha e depois coluna, separadas por vírgula, sem espaços; `{}` se nenhum |

Com a opção **fonte consumível** ligada, acrescenta-se um quarto campo com as fontes (`*`)
já consumidas, no mesmo formato do campo de bônus:

```
(l,c)|chaves|{bonus}|{fontes}
```

Sem a opção, o quarto campo **não aparece** (o rótulo continua com três partes).

**Nó alvo:** o nó virtual que recebe um arco de custo 0 de cada estado sobre `G` tem rótulo
exatamente `ALVO`.

**Grafo de posições (`G_pos`):** o rótulo é só `(l,c)`.

Exemplos:

| Situação | Rótulo |
|---|---|
| Início de qualquer mapa fornecido | `(1,1)||{}` |
| m02, em `(3,11)` depois de pegar `a` | `(3,11)|a|{}` |
| m03, com `a` e `c`, nenhum bônus | `(6,7)|ac|{}` |
| m05, depois de consumir o bônus em `(3,2)` | `(3,3)||{(3,2)}` |
| m06 com fonte consumível, após usar `(3,5)` | `(3,6)||{}|{(3,5)}` |
| Nó virtual de chegada | `ALVO` |

A **camada** de um estado é a sua string `chaves` (camada `""` = nenhuma chave). Nos
arquivos, a camada vazia é escrita como `-` para não ser confundida com campo ausente.

Quem gera o rótulo é `estados.py` (P1); todos os outros módulos só leem/comparam a string e
**não** devem reconstruí-la por conta própria. Se for preciso decompor, usar uma única
função auxiliar de `estados.py`.

---

## 3. `out/parte1/`

### 3.1 `arestas_<mapa>.csv` — produtor: P1 (T10)

Um arquivo por mapa (inclusive `m08`), uma linha por arco de `G_est`, na ordem de inserção
(BFS de exploração a partir de `S`, vizinhos em `N, L, S, O`). Inclui os arcos até `ALVO`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `origem` | str | rótulo do estado de origem |
| `destino` | str | rótulo do estado de destino (ou `ALVO`) |
| `peso` | número | custo do arco (pode ser negativo, ex.: bônus) |
| `movimento` | str | `N`, `L`, `S`, `O` ou `-` (arco até `ALVO`) |
| `simbolo_destino` | str | caractere da casa onde o movimento termina (`.`, `,`, `~`, `a`, `A`, `+`, `*`, `G`, ...); vazio para `ALVO` |
| `via_esteira` | bool | `true` se o arco inclui deslocamento forçado por esteira |
| `camada_origem` | str | chaves da origem (`-` se nenhuma) |
| `camada_destino` | str | chaves do destino (`-` se nenhuma; vazio para `ALVO`) |

Exemplo:

```csv
origem,destino,peso,movimento,simbolo_destino,via_esteira,camada_origem,camada_destino
(1,1)||{},(1,2)||{},1,L,.,false,-,-
(1,1)||{},(2,1)||{},1,S,.,false,-,-
(1,10)|a|{},(1,11)|a|{},1,L,G,false,a,a
(1,11)|a|{},ALVO,0,-,,false,a,
```

### 3.2 `solucoes.csv` — produtor: P1 (T22, via `solve.py`/`cli.py`)

Uma linha por par (mapa, algoritmo) executado, ordenada por `mapa` e depois por
`BFS, DFS, DIJKSTRA, BELLMAN_FORD`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa (seção 1.3) |
| `algoritmo` | str | `BFS`, `DFS`, `DIJKSTRA`, `BELLMAN_FORD` |
| `modelagem` | str | `G_est` ou `G_pos` |
| `status` | str | `ok`, `sem_caminho`, `recusado_peso_negativo`, `ciclo_negativo` |
| `passos` | int | número de movimentos do caminho encontrado, sem contar o arco até `ALVO`; vazio se não houver caminho |
| `custo` | número | soma dos pesos do caminho; vazio se não houver caminho ou mínimo indefinido |
| `ordem` | int | número de estados de `G_est` (inclui `ALVO`) |
| `tamanho` | int | número de arcos de `G_est` |
| `estados_visitados` | int | estados efetivamente alcançados pelo algoritmo a partir de `S` |
| `tempo_ms` | número | tempo da execução do algoritmo (sem leitura nem construção do grafo) |
| `observacao` | str | texto curto, ex.: motivo da recusa do Dijkstra |

```csv
mapa,algoritmo,modelagem,status,passos,custo,ordem,tamanho,estados_visitados,tempo_ms,observacao
m02_uma_chave,BFS,G_est,ok,24,24,61,151,60,0.41,
m05_bonus,DIJKSTRA,G_est,recusado_peso_negativo,,,,,,,arco com peso -4
m07_impossivel,BFS,G_est,sem_caminho,,,40,98,39,0.20,ALVO inalcançável
```

*(valores ilustrativos, não são resultados)*

### 3.3 Percurso em JSON — `percurso_m03.json` (T22) e qualquer `percurso_<mapa>.json`

É o formato consumido pelas figuras (T28) e pelo labirinto interativo (T20/T31). O
interativo deve aceitar qualquer arquivo neste formato, de qualquer mapa.

```json
{
  "mapa": "m03_tres_chaves",
  "algoritmo": "BFS",
  "modelagem": "G_est",
  "opcoes": { "fonte_consumivel": false, "porta_como": "parede" },
  "grade": [
    "#################",
    "#S.....A....b...#"
  ],
  "inicio": "(1,1)||{}",
  "fim": "ALVO",
  "encontrou": true,
  "passos": 2,
  "custo": 2,
  "percurso": [
    {
      "passo": 0,
      "estado": "(1,1)||{}",
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
      "estado": "(1,2)||{}",
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
| `percurso` | lista | um item por estado visitado no caminho, do início ao último estado físico antes de `ALVO` (o arco até `ALVO` não aparece) |

Cada item de `percurso`:

| Chave | Tipo | Descrição |
|---|---|---|
| `passo` | int | 0 no estado inicial, depois 1, 2, ... |
| `estado` | str | rótulo completo |
| `linha`, `coluna` | int | posição (repete a do rótulo, para não precisar decompor a string) |
| `chaves` | str | chaves no estado, em ordem alfabética (`""` se nenhuma) |
| `bonus` | lista de `[l, c]` | bônus já consumidos |
| `camada` | str | igual a `chaves`, com `-` para vazio |
| `movimento` | str / `null` | movimento que levou a este estado (`null` no passo 0) |
| `peso` | número | peso do arco que levou a este estado (0 no passo 0) |
| `custo_acumulado` | número | soma dos pesos até aqui |
| `evento` | str / `null` | `inicio`, `chave_a` ... `chave_d`, `porta_A` ... `porta_D`, `esteira`, `bonus`, `fonte`, `chegada` ou `null` |

Quando um passo dispara mais de um evento, usa-se o mais importante na ordem
`chegada > chave > porta > bonus > fonte > esteira`.

### 3.4 `ciclo_negativo_m06.json` — produtor: P1 (T22)

Ciclo negativo extraído pelo Bellman-Ford (o mesmo formato serve para o `G_pos` do m05 em
T24, gravado como `ciclo_negativo_m05_gpos.json`).

```json
{
  "mapa": "m06_fonte",
  "modelagem": "G_est",
  "algoritmo": "BELLMAN_FORD",
  "opcoes": { "fonte_consumivel": false },
  "fonte": "(1,1)||{}",
  "ciclo_encontrado": true,
  "ciclo": ["(3,5)||{}", "(3,4)||{}", "(3,5)||{}"],
  "arcos": [
    { "origem": "(3,5)||{}", "destino": "(3,4)||{}", "peso": 1, "movimento": "O" },
    { "origem": "(3,4)||{}", "destino": "(3,5)||{}", "peso": -5, "movimento": "L" }
  ],
  "custo_ciclo": -4,
  "afeta_alvo": true,
  "correcao": {
    "aplicada": false,
    "descricao": null,
    "custo_minimo_apos_correcao": null
  }
}
```

*(estados e pesos ilustrativos)*

| Chave | Tipo | Descrição |
|---|---|---|
| `ciclo` | lista de str | ciclo **fechado**: o primeiro rótulo se repete no fim; pode começar em qualquer estado do ciclo |
| `arcos` | lista | os arcos do ciclo, na ordem, com o peso de cada um |
| `custo_ciclo` | número | soma dos pesos de `arcos` (< 0) |
| `afeta_alvo` | bool | o ciclo alcança `ALVO` (o mínimo até `ALVO` fica indefinido) |
| `correcao` | objeto | preenchido na correção do m06 (P3): `aplicada`, texto curto e o custo mínimo obtido depois dela |

Sem ciclo: `ciclo_encontrado: false`, `ciclo` e `arcos` vazios, `custo_ciclo: null`.

### 3.5 `armadilhas_m04.csv` e `armadilhas_m07.csv` — produtor: P1/P2 (T15 + T22)

Estados alcançáveis a partir de `S` que **não** alcançam `ALVO` (busca reversa no
transposto). Uma linha por estado, ordenada por `linha`, `coluna`, `chaves`.

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

### 3.6 `dfs_classificacao.csv` — produtor: P1/P2 (T12 + T22)

Uma linha por arco examinado pela DFS a partir de `S`, na ordem em que foi examinado.

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa |
| `origem`, `destino` | str | rótulos |
| `classe` | str | `arvore`, `retorno`, `avanco` ou `cruzamento` |
| `d_origem`, `f_origem` | int | tempos de descoberta/finalização da origem |
| `d_destino`, `f_destino` | int | tempos de descoberta/finalização do destino |

Convenção do relógio: começa em 1 e é incrementado a cada descoberta e a cada finalização
(CLRS). O resumo por classe (contagens e `possui_ciclo`) vai em `metricas_global.json`.

### 3.7 `metricas_global.json` — produtor: P3 (T23)

Um objeto por mapa, na chave com o nome do mapa.

```json
{
  "gerado_em": "2026-11-18T20:00:00",
  "mapas": {
    "m02_uma_chave": {
      "modelagem": "G_est",
      "ordem": 61,
      "tamanho": 151,
      "densidade": 0.0412,
      "estados_fisicos": 30,
      "teto_teorico_estados": 60,
      "ocupacao_teto": 1.0,
      "grau_saida": { "min": 0, "max": 4, "medio": 2.48 },
      "grau_entrada": { "min": 0, "max": 4, "medio": 2.48 },
      "becos": 4,
      "multiplicidade": { "max": 2, "media": 2.0 },
      "camadas": 2,
      "arcos_entre_camadas": 1,
      "armadilhas": 0,
      "pct_armadilhas": 0.0,
      "dfs": { "arvore": 60, "retorno": 70, "avanco": 0, "cruzamento": 21, "possui_ciclo": true },
      "ranking_grau": [
        { "estado": "(1,5)||{}", "grau_entrada": 4, "grau_saida": 4 }
      ]
    }
  }
}
```

*(valores ilustrativos)*

| Chave | Descrição |
|---|---|
| `ordem` / `tamanho` | `|V|` (com `ALVO`) e `|A|` |
| `densidade` | densidade dirigida `|A| / (|V| · (|V| − 1))` |
| `estados_fisicos` | casas não-parede alcançadas (posições distintas entre os estados) |
| `teto_teorico_estados` | casas livres × combinações possíveis de chaves (× bônus/fontes, quando houver) |
| `ocupacao_teto` | `ordem` sem `ALVO` ÷ `teto_teorico_estados` |
| `becos` | estados com `grau_saida` = 0, excluindo `ALVO` |
| `multiplicidade` | número de estados por casa física (máximo e média) |
| `camadas` / `arcos_entre_camadas` | quantidade de conjuntos de chaves distintos e arcos cuja camada muda |
| `ranking_grau` | os 10 estados de maior grau total, em ordem decrescente (obrigatório no `m08`, opcional nos demais) |

### 3.8 `camadas.json` — produtor: P3 (T23); consumido pela figura em camadas (T30)

```json
{
  "m02_uma_chave": {
    "camadas": [
      { "camada": "-", "chaves": "", "estados": 30, "arcos_internos": 74 },
      { "camada": "a", "chaves": "a", "estados": 30, "arcos_internos": 74 }
    ],
    "arcos_entre_camadas": [
      { "de": "-", "para": "a", "quantidade": 1 }
    ]
  }
}
```

### 3.9 `graus_<mapa>.csv` — produtor: P3 (T23)

Uma linha por estado, na ordem de inserção dos vértices no `Graph`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `estado` | str | rótulo |
| `linha`, `coluna` | int | posição (vazio para `ALVO`) |
| `camada` | str | chaves (`-` se nenhuma) |
| `grau_entrada`, `grau_saida`, `grau_total` | int | graus em `G_est` |
| `beco` | bool | `grau_saida` = 0 e não é `ALVO` |

### 3.10 `multiplicidade_m08.csv` — produtor: P3 (T23); consumido pelo heatmap (T30)

Uma linha por casa não-parede da grade, ordenada por `linha`, `coluna`.

| Coluna | Tipo | Descrição |
|---|---|---|
| `linha`, `coluna` | int | posição |
| `simbolo` | str | caractere da casa |
| `multiplicidade` | int | quantos estados de `G_est` estão nessa casa (0 se inalcançável) |

### 3.11 `comparacao_modelagem.csv` — produtor: P3 (T24)

Uma linha por (mapa, modelagem), para `m02`, `m03`, `m04` (e `m05` em `G_pos`, para a prova
do ciclo negativo).

| Coluna | Tipo | Descrição |
|---|---|---|
| `mapa` | str | nome do mapa |
| `modelagem` | str | `G_pos` ou `G_est` |
| `opcao_porta` | str | `parede` ou `chao` (só `G_pos`; vazio em `G_est`) |
| `ordem`, `tamanho` | int | tamanho do grafo |
| `alcanca_alvo` | bool | existe caminho até `G` |
| `passos_bfs` | int | passos do caminho do BFS (vazio se não houver) |
| `custo_minimo` | número | custo mínimo (vazio se não houver ou se houver ciclo negativo) |
| `solucao_valida` | bool | o caminho respeita as regras do jogo (ex.: não atravessa porta sem chave) |
| `observacao` | str | texto curto |

### 3.12 Arquivos não tabulares

| Arquivo | Produtor | Lê |
|---|---|---|
| `percurso_m03.png`, `percurso_m08.png` | P5 (T28) | `percurso_<mapa>.json` |
| figura da árvore BFS do m02, figura de `G_est` em camadas, heatmap do m08 | P5/P3 (T28, T30) | `arestas_m02.csv`, `camadas.json`, `multiplicidade_m08.csv` |
| `labirinto_interativo.html` | P5 (T20, T31) | `percurso_<mapa>.json`, `armadilhas_<mapa>.csv`, `metricas_global.json` (dados embutidos no HTML pelo Python) |

---

## 4. `out/parte2/`

Dataset: `data/dataset_parte2/soc-sign-bitcoinalpha.csv`, sem cabeçalho, colunas
`origem,destino,nota,timestamp` (nota inteira de −10 a +10, timestamp em segundos Unix). O
arco vai de quem **avalia** (`origem`) para quem é **avaliado** (`destino`). Os vértices são
os ids numéricos do dataset convertidos para `int`.

### 4.1 Recortes

Todo resultado da Parte 2 indica o `recorte` usado: `10`, `50` ou `100` (percentual das
avaliações). O critério de corte (ex.: primeiras N avaliações por `timestamp`) é decidido no
leitor (T18) e registrado em `parte2_report.json` → `dataset.criterio_recorte`.

### 4.2 `parte2_report.json` — produtor: P4 (T26), com casos de P2 (T25)

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
    { "origem": 1, "destino": 2, "recorte": 100, "status": "ok",
      "custo": 0, "passos": 0, "caminho": [1, 2] }
  ],
  "bellman_ford": [
    { "caso": "sem_ciclo_negativo", "fonte": 1, "recorte": 100, "status": "ok",
      "ciclo": [], "custo_ciclo": null },
    { "caso": "com_ciclo_negativo", "fonte": 1, "recorte": 100, "status": "ciclo_negativo",
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

*(números ilustrativos, exceto os totais do dataset que constam no plano)*

Regras:

- `bfs` e `dfs`: uma entrada por fonte (3 fontes) e recorte usado.
- `dijkstra`: uma entrada por par (5 pares). `status` ∈ `ok`, `sem_caminho`,
  `recusado_peso_negativo`; sem caminho → `custo`, `passos` `null` e `caminho` vazio.
- `bellman_ford`: pelo menos os dois casos obrigatórios (`sem_ciclo_negativo` e
  `com_ciclo_negativo`); `ciclo` é fechado (primeiro id repetido no fim).
- Caminhos e ciclos são listas de ids `int`.

### 4.3 `benchmark_parte2.csv` — produtor: P4 (T26); consumido pelos gráficos (T32)

Uma linha por execução medida (5 execuções × algoritmos × 3 recortes).

| Coluna | Tipo | Descrição |
|---|---|---|
| `algoritmo` | str | `BFS`, `DFS`, `DIJKSTRA`, `BELLMAN_FORD` |
| `recorte` | int | 10, 50 ou 100 |
| `vertices`, `arcos` | int | tamanho do grafo no recorte |
| `execucao` | int | 1 a 5 |
| `fonte` | int | vértice de partida usado |
| `tempo_ms` | número | tempo medido (sem leitura do arquivo nem construção do grafo) |

### 4.4 Visualizações AVD

As 4 exploratórias e as 2 explanatórias são gravadas em `out/parte2/` com o padrão
`exp<N>_<assunto>.png` (`exp1_...` a `exp4_...`) e `expl<N>_<assunto>.png`
(`expl1_...`, `expl2_...`). Se uma visualização precisar de uma tabela intermediária, ela vai
ao lado com o mesmo prefixo e extensão `.csv`.

---

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

## 6. Pontos a confirmar na revisão

- Conferir com o enunciado os nomes exatos dos arquivos obrigatórios; os que **não** são
  citados no plano e foram propostos aqui são `multiplicidade_m08.csv`,
  `benchmark_parte2.csv`, `ciclo_negativo_m05_gpos.json` e o padrão de nomes das
  visualizações AVD.
- Os custos de cada tipo de casa (`.`, `,`, `~`, esteiras, `+`, `*`) **não** são definidos aqui:
  seguem o enunciado e são implementados em `estados.py` (P1). Este documento só fixa onde o
  peso aparece.
- Critério de recorte e transformação de pesos da Parte 2 ficam com P4/P2 (T18, T25); aqui só
  se fixa onde eles são registrados.
