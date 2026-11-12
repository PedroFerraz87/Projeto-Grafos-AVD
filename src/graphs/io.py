"""Leitura e validação de mapas .txt (T07).

Linhas que começam com ';' são comentários e linhas em branco são ignoradas.
O resultado é a grade como lista de strings, sem comentários; as coordenadas
(l,c) do restante do projeto são base 0 sobre essa grade (docs/contratos.md).
"""

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
