import pandas as pd

from src.graphs.graph import Graph

# chão, parede, início, saída, lama, água, chaves, portas, esteiras, bônus, fonte
SIMBOLOS = set("#.SG,~abcdABCD><^v+*")


class MapaInvalido(ValueError):
    pass


def ler_mapa(caminho):
    grade, numeros = [], []

    f = open(caminho, encoding="utf-8-sig")

    quant_linhas = enumerate(f, start=1)

    for n, linha in quant_linhas:
                linha = linha.rstrip("\r\n")
                if linha.startswith(";") or not linha.strip():
                    continue
                grade.append(linha)
                numeros.append(n)

    f.close()

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

COLUNAS_DATASET = ["origem", "destino", "nota", "timestamp"]

class DatasetInvalido(ValueError):
    pass

def ler_dataset(caminho, recorte=100):
    if recorte not in (10, 50, 100):
        raise DatasetInvalido("O recorte deve ser 10, 50 ou 100.")

    df = pd.read_csv(caminho, header=None)

    if df.shape[1] != 4:
        raise DatasetInvalido("O dataset deve ter 4 colunas.")

    df.columns = COLUNAS_DATASET

    df = df.sort_values("timestamp", kind="stable")

    quantidade = int(len(df) * recorte / 100)
    df = df.head(quantidade)

    grafo = Graph()

    for linha in df.itertuples(index=False):
        grafo.adicionar_arco(
            int(linha.origem),
            int(linha.destino),
            int(linha.nota),
            {"timestamp": int(linha.timestamp)}
        )

    return grafo
