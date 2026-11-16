"""Leitura e validação de mapas .txt (T07).

Linhas que começam com ';' são comentários e linhas em branco são ignoradas.
O resultado é a grade como lista de strings, sem comentários; as coordenadas
(l,c) do restante do projeto são base 0 sobre essa grade (docs/contratos.md).
"""

import pandas as pd

from src.graphs.graph import Graph

# chão, parede, início, saída, lama, água, chaves, portas, esteiras, bônus, fonte
SIMBOLOS = set("#.SG,~abcdABCD><^v+*")


class MapaInvalido(ValueError):
    pass


def ler_mapa(caminho):
    """Lê o mapa em `caminho` e devolve a grade (lista de str).

    Levanta MapaInvalido se o mapa estiver vazio, não for retangular, tiver
    símbolo desconhecido, não tiver exatamente um S ou não tiver nenhum G.
    """
    grade, numeros = [], []
    # utf-8-sig: aceita arquivo salvo com BOM por editores do Windows
    with open(caminho, encoding="utf-8-sig") as f:
        for n, linha in enumerate(f, start=1):
            linha = linha.rstrip("\r\n")
            if linha.startswith(";") or not linha.strip():
                continue
            grade.append(linha)
            numeros.append(n)

    if not grade:
        raise MapaInvalido(f"{caminho}: mapa vazio")

    largura = len(grade[0])
    for linha, n in zip(grade, numeros):
        if len(linha) != largura:
            raise MapaInvalido(f"{caminho}: linha {n} tem {len(linha)} colunas, esperado {largura}")
        for j, simbolo in enumerate(linha):
            if simbolo not in SIMBOLOS:
                raise MapaInvalido(f"{caminho}: símbolo desconhecido {simbolo!r} na linha {n}, coluna {j + 1}")

    texto = "".join(grade)
    if texto.count("S") != 1:
        raise MapaInvalido(f"{caminho}: esperado exatamente um S, encontrado {texto.count('S')}")
    if "G" not in texto:
        raise MapaInvalido(f"{caminho}: o mapa não tem nenhum G")
    return grade

##Parte 02 - Victor

COLUNAS_DATASET = ["origem", "destino", "nota", "timestamp"]


class DatasetInvalido(ValueError):
    pass

def ler_dataset(caminho, recorte=100):
    """Lê o dataset Bitcoin Alpha e devolve um grafo.

    O recorte pode ser 10, 50 ou 100.
    Os dados são ordenados pelo timestamp antes do recorte.
    """

    # Verifica se o recorte é válido
    if recorte not in (10, 50, 100):
        raise DatasetInvalido("O recorte deve ser 10, 50 ou 100.")

    # Lê o CSV sem cabeçalho
    df = pd.read_csv(caminho, header=None)

    # Verifica a quantidade de colunas
    if df.shape[1] != 4:
        raise DatasetInvalido("O dataset deve ter 4 colunas.")

    # Coloca os nomes nas colunas
    df.columns = COLUNAS_DATASET

    # Ordena pelo timestamp
    df = df.sort_values("timestamp", kind="stable")

    # Aplica o recorte
    quantidade = int(len(df) * recorte / 100)
    df = df.head(quantidade)

    # Cria o grafo vazio
    grafo = Graph()

    # Adiciona as avaliações como arcos
    for linha in df.itertuples(index=False):
        grafo.adicionar_arco(
            int(linha.origem),
            int(linha.destino),
            int(linha.nota),
            {"timestamp": int(linha.timestamp)}
        )

    return grafo
