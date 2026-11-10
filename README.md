# Projeto de Grafos + AVD

Projeto final das disciplinas de Teoria dos Grafos e Análise e Visualização de Dados (AVD), semestre 2026.2.

## Objetivo

O projeto reúne duas partes:

1. Modelagem e análise de labirintos com chaves, portas e outros elementos por meio de grafos de estados.
2. Comparação de algoritmos de grafos e análise de um dataset de maior dimensão.

O projeto está em desenvolvimento. Os resultados e comandos serão atualizados conforme a integração e validação das entregas.

## Requisitos

- Python 3.11 ou superior.
- Dependências listadas em `requirements.txt`.
- Os algoritmos BFS, DFS, Dijkstra e Bellman-Ford são implementados pelo grupo.
- Bibliotecas de algoritmos prontos não devem ser utilizadas na aplicação.

## Instalação

No PowerShell, na raiz do repositório:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Execução

Os comandos abaixo representam exemplos previstos para a execução do projeto. Devem ser conferidos após a integração e validação da CLI.

### Parte 1 — Labirintos

```powershell
python -m src.cli --mapa .\data\mapas\m03_tres_chaves.txt --alg BFS --out .\out\parte1
```

```powershell
python -m src.cli --mapa .\data\mapas\m05_bonus.txt --alg BELLMAN_FORD --out .\out\parte1
```

### Parte 2 — Dataset

```powershell
python -m src.cli --dataset .\data\dataset_parte2 --benchmark --out .\out\parte2
```

Os parâmetros e comandos definitivos serão documentados após a integração da CLI.

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

As responsabilidades, revisões e contribuições individuais serão detalhadas no relatório técnico, com evidências dos commits realizados.

## Uso de IA

O uso de ferramentas de inteligência artificial seguirá as regras estabelecidas no planejamento e no enunciado do projeto.

Os usos permitidos serão registrados, e os trechos de código que receberem apoio de IA serão identificados conforme a orientação do grupo.

A declaração de uso de IA, preenchida e assinada por todos os integrantes, será disponibilizada em:

`docs/DECLARACAO_IA.pdf`

[Documento de trabalho da declaração de uso de IA](https://docs.google.com/document/d/1vJfLOciHPq844Sul8AgRh8vQg1W1JeNT/edit)