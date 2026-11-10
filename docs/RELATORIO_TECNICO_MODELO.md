# Relatório Técnico — Projeto de Grafos + AVD

**CESAR School — Grafos e Análise e Visualização de Dados**  
**Turma:** 5B — 2026.2  
**Projeto:** Projeto de Grafos + AVD

**Integrantes:** Pedro Ferraz, Ricardo Machado, Luca Albuquerque, Artur Antunes e Victor Uen.

---

## 1. Repositório, execução e contribuições

### 1.1 Organização do projeto

| Pasta/arquivo | Conteúdo |
|---|---|
| `data/mapas/` | Mapas de m01 a m08 utilizados na Parte 1 |
| `data/mapas_grupo/` | Dois mapas desenvolvidos pelo grupo |
| `data/dataset_parte2/` | Dataset utilizado na Parte 2 |
| `src/` | Aplicação, CLI, solução, visualizações e módulos de grafos |
| `tests/` | Testes automatizados e fixtures |
| `out/parte1/` | Resultados, tabelas e visualizações dos labirintos |
| `out/parte2/` | Relatórios e visualizações do dataset |
| `docs/` | Contratos, registros, declaração e documentação |
| `README.md` | Instruções de instalação, execução e organização |
| `requirements.txt` | Dependências do projeto |

### 1.2 Como reproduzir

Registrar a versão do Python, os procedimentos de instalação, os comandos executados e a localização dos resultados gerados.

Os comandos apresentados devem corresponder à CLI integrada e validada pelo grupo.

### 1.3 Equipe e contribuições

| Integrante | Pacote(s) | Entregas realizadas | Revisões realizadas | Evidências de commits |
|---|---|---|---|---|
| Pedro Ferraz | P5 e contribuições em outro pacote | [Preencher] | [Preencher] | [Preencher] |
| Ricardo Machado | P1 e contribuições em outro pacote | [Preencher] | [Preencher] | [Preencher] |
| Luca Albuquerque | P3 e contribuições em outro pacote | [Preencher] | [Preencher] | [Preencher] |
| Artur Antunes | P2 e contribuições em outro pacote | [Preencher] | [Preencher] | [Preencher] |
| Victor Uen | P4 e contribuições em outro pacote | [Preencher] | [Preencher] | [Preencher] |

### 1.4 Uso de ferramentas e declaração de IA

Descrever os usos de inteligência artificial efetivamente realizados durante o desenvolvimento, indicando as ferramentas utilizadas e suas finalidades.

Anexar a declaração de uso de IA preenchida e assinada por todos os integrantes em `docs/DECLARACAO_IA.pdf`.

---

## 2. Parte 1 — Labirintos

### 2.1 Regras e representação

Descrever as regras implementadas para representar os labirintos e os elementos presentes nos mapas, incluindo paredes, terrenos, chaves, portas, esteiras, bônus e fontes.

Apresentar a diferença entre o grafo de posições e o grafo de estados.

### 2.2 Construção e validação dos grafos

Documentar a leitura e validação dos mapas, a exploração a partir do estado inicial e os resultados dos testes realizados.

Arquivos relacionados:

- `src/graphs/io.py`
- `src/graphs/estados.py`
- `tests/test_io.py`
- `tests/test_estados.py`

### 2.3 Arestas, métricas e camadas

Apresentar os resultados produzidos em `out/parte1/`:

- `arestas_<mapa>.csv`, incluindo o m08;
- `metricas_global.json`;
- `camadas.json`;
- `graus_<mapa>.csv`.

Interpretar os resultados referentes à ordem, tamanho, densidade, ocupação do teto teórico, graus, multiplicidades, becos e arcos entre camadas.

### 2.4 Comparação de modelagens e pesos negativos

Apresentar os resultados de `comparacao_modelagem.csv`, considerando as modelagens dos mapas m02, m03 e m04.

Registrar a demonstração do ciclo negativo em m05 no grafo de posições e a justificativa para seu comportamento no grafo de estados.

Documentar também a correção opcional da fonte em m06 e os resultados obtidos.

### 2.5 Caminhos e algoritmos

Documentar as implementações e os resultados gerados em `out/parte1/`.

Arquivos relacionados:

- `solucoes.csv`;
- `percurso_m03.json`;
- `ciclo_negativo_m06.json`;
- `armadilhas_m04.csv`;
- `armadilhas_m07.csv`;
- `dfs_classificacao.csv`.

Relatar os resultados de BFS, DFS, Dijkstra e Bellman-Ford, incluindo recusas de Dijkstra, detecção e extração de ciclos negativos, estados-armadilha e casos sem solução.

### 2.6 Mapas criados pelo grupo

Indicar os arquivos desenvolvidos em `data/mapas_grupo/` e os resultados de suas validações.

| Mapa | Estados | Arcos | Passos (BFS) | Custo mínimo | Percentual de estados-armadilha |
|---|---:|---:|---:|---:|---:|
| Mapa com chaves, esteiras e bônus | | | | | |
| Mapa armadilha | | | | | |

### 2.7 Visualizações e aplicação interativa

Referenciar as figuras e o HTML gerados em `out/parte1/`, incluindo:

- `percurso_m03.png`;
- `percurso_m08.png`;
- Visualização do grafo de estados de m02 em camadas;
- Árvore BFS de m02;
- Heatmap de multiplicidade de m08;
- `labirinto_interativo.html`.

Para cada figura, apresentar título, legenda, rótulos e interpretação.

Descrever o funcionamento da aplicação interativa, incluindo a seleção de mapa e algoritmo e o acompanhamento do percurso.

---

## 3. Parte 2 — Dataset

### 3.1 Fonte e pergunta de pesquisa

- Dataset utilizado:
- Fonte e licença:
- Unidade de observação:
- Atributos utilizados:
- Número de vértices:
- Número de arestas:
- Pergunta de pesquisa aprovada:

### 3.2 Preparação e qualidade dos dados

Documentar o tratamento realizado pelo leitor de dados, incluindo:

- Tipos de dados;
- Valores faltantes;
- Mecanismo de ausência;
- Inconsistências;
- Outliers;
- Estratégias de tratamento e justificativas.

### 3.3 Modelagem do grafo e pesos

Explicar a direção dos arcos, o significado dos pesos no domínio, as transformações realizadas, os recortes utilizados e as limitações da modelagem.

### 3.4 Exploração e experimentos com algoritmos

Descrever a exploração estrutural, distribucional, relacional e de outliers, assim como os experimentos realizados com BFS, DFS, Dijkstra e Bellman-Ford.

Citar os comandos executados e os resultados armazenados em `out/parte2/`.

### 3.5 Desempenho e escalabilidade

Registrar o ambiente utilizado, o método de medição, as cinco ou mais execuções realizadas, os tamanhos dos grafos, os resultados obtidos e a comparação com as complexidades teóricas.

### 3.6 Visualizações exploratórias

Referenciar as visualizações produzidas em `out/parte2/`.

Para cada uma, apresentar o que mostra, o insight observado e a justificativa da escolha do gráfico.

1. Exploratória 1 — arquivo:
2. Exploratória 2 — arquivo:
3. Exploratória 3 — arquivo:
4. Exploratória 4 — arquivo:

### 3.7 Visualizações explanatórias

Para cada visualização, registrar o achado exploratório que a motivou, a mensagem principal, o público-alvo, os elementos visuais utilizados e a interpretação.

Pelo menos uma visualização deverá responder à pergunta de pesquisa.

1. Explanatória 1 — arquivo:
2. Explanatória 2 — arquivo:

### 3.8 Relatório de resultados

Descrever os campos e resultados de `out/parte2/parte2_report.json`, apontando também as tabelas e figuras geradas no diretório.

---

## 4. Testes e evidências

Informar os comandos executados, os resultados dos testes e as funcionalidades validadas.

Relacionar cada teste à funcionalidade correspondente.

- `test_graph.py`:
- `test_bfs.py`:
- `test_dfs.py`:
- `test_dijkstra.py`:
- `test_bellman_ford.py`:
- `test_estados.py`:
- `test_io.py`:
- Outros testes e fixtures:

---

## 5. Conclusão

Sintetizar os resultados obtidos, as respostas à pergunta de pesquisa, as limitações identificadas e as principais dificuldades encontradas durante o desenvolvimento.

---

## Referências

Listar as fontes de dados, licenças, documentações, artigos e demais materiais efetivamente utilizados.

---

## Apêndices

- Comandos para reproduzir os resultados;
- Tabelas e resultados adicionais de `out/`;
- Evidências do mapa mínimo e da validação manual;
- Outros materiais relevantes armazenados em `docs/`.