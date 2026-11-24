# Projeto de Grafos + AVD

Projeto final das disciplinas de Teoria dos Grafos e Análise e Visualização de Dados (AVD), semestre 2026.2.

## Objetivo

O projeto reúne duas partes:

1. Modelagem e análise de labirintos com chaves, portas e outros elementos por meio de grafos de estados.
2. Comparação de algoritmos de grafos e análise de um dataset de maior dimensão.

## Requisitos

- Python 3.11 ou superior.
- Dependências listadas em `requirements.txt`.
- Os algoritmos BFS, DFS, Dijkstra e Bellman-Ford ficam em `src/graphs/algorithms.py`. A implementação inicial assistida por IA e os ajustes do grupo estão identificados no código.
- NetworkX é usado como oráculo de testes.

## Instalação

No PowerShell, na raiz do repositório:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Execução

Os resultados publicados estão em [Parte 1](out/parte1/) e [Parte 2](out/parte2/). Os comandos abaixo gravam novas execuções em uma pasta temporária.

```powershell
$repro = Join-Path ([System.IO.Path]::GetTempPath()) ("grafos-avd-" + [guid]::NewGuid())
$parte1 = Join-Path $repro "parte1"
$parte2 = Join-Path $repro "parte2"
```

### Parte 1 — Labirintos

```powershell
python -m src.cli --interactive --fonte-consumivel --out $parte1
python -m src.analises --out $parte1
python -c "from src.graphs.estados import exportar_todos; import sys; exportar_todos('.', sys.argv[1])" $parte1
```

Abra [Rotas possíveis](out/parte1/labirinto_interativo.html) para comparar dois percursos em planta ou relevo. A página [Quatro algoritmos em ação](out/parte1/algoritmos_em_acao.html) mostra BFS, DFS, Dijkstra e Bellman-Ford com o mesmo controle de reprodução. A CLI gera as páginas, os percursos, as soluções e os casos de armadilha. `src.analises` gera as métricas, a comparação de modelagens e as figuras da T30. `exportar_todos` exporta os CSVs de arestas.

Para testar um mapa ao vivo, inicie `python -m src.avd.servidor_bitcoin` e abra `http://127.0.0.1:8765/labirinto_interativo.html#enviar-mapa`. Escolha um `.txt` em UTF-8 que siga as mesmas regras dos mapas da CLI. O mapa analisado aparece na Mesa de rotas e na vista dos quatro algoritmos na mesma aba do navegador.

### Parte 2 — Bitcoin Alpha

O painel [Bitcoin Alpha](out/parte1/bitcoin_alpha.html) organiza grafo, desempenho, caminhos, buscas, método e gráficos em abas. Na aba do grafo, reproduza um algoritmo na rede completa, localize usuários pelo ID ou compare os quatro em paralelo. Na aba **Gráficos**, selecione uma das 12 figuras e baixe o PNG. A CLI gera essa página com `--interactive`.

Na bancada da Parte 2, os cinco pares de três origens ficam disponíveis offline para reprodução das execuções registradas. Para **executar novamente os quatro algoritmos** no dataset completo, rode o serviço local e abra `http://127.0.0.1:8765/bitcoin_alpha.html`.

```powershell
python -m src.avd.servidor_bitcoin
```

O botão **Rodar os quatro** calcula no servidor local e envia os resultados à medida que terminam. Para regenerar os registros offline, use `python -m src.avd.experimentos` e depois execute a CLI com `--interactive`. Essa etapa reexecuta Bellman-Ford para as três fontes e pode levar alguns minutos.

Os casos de algoritmos e as tabelas podem ser reproduzidos com as medições publicadas pelo grupo.

```powershell
$relatorio = Join-Path $parte2 "parte2_report.json"
python -m src.parte2 --out $relatorio
Copy-Item -LiteralPath out/parte2/benchmark.csv -Destination (Join-Path $parte2 "benchmark.csv")
python -m src.avd.comparacao_algoritmos --relatorio $relatorio --benchmark (Join-Path $parte2 "benchmark.csv") --out (Join-Path $parte2 "dados_comparacao_algoritmos")
```

Para medir novamente no seu computador, passe à CLI o caminho do arquivo CSV. O benchmark pode levar vários minutos.

```powershell
python -m src.cli --dataset data/dataset_parte2/soc-sign-bitcoinalpha.csv --benchmark --out $parte2
```

O comando grava `benchmark.csv`. Para incorporar essas medições ao JSON local da T25, rode `python -c "from src.registrar_benchmark import registrar_benchmark; import sys; registrar_benchmark(*sys.argv[1:])" (Join-Path $parte2 "benchmark.csv") $relatorio`. As [figuras publicadas](out/parte2/avd/) incluem os gráficos exploratórios, explanatórios e os de comparação entre algoritmos.

Para regenerar as figuras nos caminhos de entrega, execute:

```powershell
python -m src.avd.visualizacoes
python -m src.avd.visualizacoes_algoritmos
python -m src.avd.visualizacoes_explanatorias
```

## Testes

Para executar os testes automatizados:

```powershell
python -m pytest
```

## Organização do projeto

```text
Projeto-Grafos-AVD/
├── data/
│   ├── mapas/
│   ├── mapas_grupo/
│   └── dataset_parte2/
├── docs/
├── out/
│   ├── parte1/
│   └── parte2/
├── src/
│   └── graphs/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

### Descrição dos diretórios

- `data/mapas/`: mapas fornecidos para a Parte 1.
- `data/mapas_grupo/`: mapas desenvolvidos pelo grupo.
- `data/dataset_parte2/`: dataset utilizado na Parte 2.
- `docs/`: documentação, contratos e declaração de uso de IA.
- `out/parte1/`: resultados e visualizações dos labirintos.
- `out/parte2/`: resultados e visualizações do dataset.
- `src/`: aplicação, grafos, algoritmos e visualizações.
- `tests/`: testes automatizados.

## Equipe e contribuições

O projeto é desenvolvido por:

- Pedro Ferraz
- Ricardo Machado
- Luca Albuquerque
- Artur Antunes
- Victor Uen

As responsabilidades, revisões e contribuições individuais estão no relatório técnico para revisão do G1. [PDF](docs/RELATORIO_TECNICO.pdf) · [Versão editável](docs/RELATORIO_TECNICO.md)

## Uso de IA

O uso de ferramentas de inteligência artificial seguirá as regras estabelecidas no planejamento e no enunciado do projeto.

Os usos permitidos serão registrados, e os trechos de código que receberem apoio de IA serão identificados conforme a orientação do grupo.

A declaração de uso de IA, preenchida e assinada por todos os integrantes, será disponibilizada em:

`docs/DECLARACAO_IA.pdf`

[Documento de trabalho da declaração de uso de IA](https://docs.google.com/document/d/1vJfLOciHPq844Sul8AgRh8vQg1W1JeNT/edit)
