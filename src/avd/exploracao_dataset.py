"""T19: Exploaração do dataset"""

import pandas as pd

COLUNAS = ["origem", "destino","nota", "timestamp"]

def explorar_dataset(caminho):
    df = pd.read_csv(caminho, header=None, names=COLUNAS)

    print("=== ESTRUTURA ===")
    print("Linhas:", len(df))
    print("Colunas:", len(df.columns))
    print("Tipos:")
    print(df.dtypes)
    print("\nPrimeiras linhas:")
    print(df.head())

    print("\n=== VALORES FALTANTES ===")
    print(df.isnull().sum())
    print("Duplicatas exatas:", df.duplicated().sum())

    print("\n=== AVALIAÇÕES ===")
    print("Notas positivas:", (df["nota"] > 0).sum())
    print("Notas negativas:", (df["nota"] < 0).sum())
    print("Notas zero:", (df["nota"] == 0).sum())
    print("Distribuição das notas:")
    print(df["nota"].value_counts().sort_index())
    print("Resumo das notas:")
    print(df["nota"].describe())

    usuarios = pd.concat([df["origem"], df["destino"]]).nunique()
    print("\nUsuários diferentes:", usuarios)

    # Quantidade de avaliações feitas e recebidas por usuário
    feitas = df.groupby("origem").size()
    recebidas = df.groupby("destino").size()

    print("\n=== USUÁRIOS COM MAIS AVALIAÇÕES ===")
    print("Mais avaliações feitas:")
    print(feitas.sort_values(ascending=False).head(5))
    print("Mais avaliações recebidas:")
    print(recebidas.sort_values(ascending=False).head(5))
    print("Resumo das avaliações feitas:")
    print(feitas.describe())
    print("Resumo das avaliações recebidas:")
    print(recebidas.describe())

    # Usa a regra do intervalo interquartil para procurar valores altos.
    q1 = recebidas.quantile(0.25)
    q3 = recebidas.quantile(0.75)
    limite = q3 + 1.5 * (q3 - q1)
    print("\n=== POSSÍVEIS OUTLIERS ===")
    print("Limite de avaliações recebidas:", limite)
    print("Usuários acima do limite:", (recebidas > limite).sum())

    # Transforma o timestamp Unix em data para analisar a evolução da rede.
    df["data"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)
    print("\n=== PERÍODO ===")
    print("Primeira avaliação:", df["data"].min())
    print("Última avaliação:", df["data"].max())

    df["ano"] = df["data"].dt.year
    df["negativa"] = df["nota"] < 0
    print("\n=== RELAÇÕES ENTRE VARIÁVEIS ===")
    print("Avaliações por ano:")
    print(df.groupby("ano").size())
    print("Percentual de avaliações negativas por ano:")
    print((df.groupby("ano")["negativa"].mean() * 100).round(2))

    # Para cada usuário avaliado, compara total recebido com notas negativas.
    por_usuario = df.groupby("destino").agg(
        total=("nota", "size"),
        negativas=("negativa", "sum")
    )
    print("\nUsuários que mais receberam avaliações:")
    print(por_usuario.sort_values("total", ascending=False).head(10))

    return df


if __name__ == "__main__":
    explorar_dataset("data/dataset_parte2/soc-sign-bitcoinalpha.csv")
