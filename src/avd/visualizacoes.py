
# [IA] Apoio do ChatGPT na implementação das visualizações da T27.

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

COLUNAS = ["origem", "destino", "nota", "timestamp"]


def carregar_dados(caminho):
    df = pd.read_csv(caminho, header=None, names=COLUNAS)

    df["data"] = pd.to_datetime(
        df["timestamp"], unit="s", utc=True
    )

    df["negativa"] = df["nota"] < 0

    df["data"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)

    df["ano"] = df["data"].dt.year
    df["mes"] = df["data"].dt.month
    df["dia"] = df["data"].dt.day

    return df

#Gráfico 1

def grafico_notas(df, pasta_saida):
    contagem = df["nota"].value_counts().sort_index()

    plt.figure(figsize=(10, 5))
    plt.bar(contagem.index, contagem.values)

    plt.title("Distribuição das notas")
    plt.xlabel("Nota")
    plt.ylabel("Quantidade de avaliações")
    plt.xticks(range(-10, 11))
    plt.tight_layout()

    plt.savefig(pasta_saida / "01_distribuicao_notas.png", dpi=150)
    plt.close()


#Gráfico 2


def grafico_avaliacoes_usuario(df, pasta_saida):
    feitas = df.groupby("origem").size()

    faixas = [
        (feitas <= 10).sum(),
        ((feitas > 10) & (feitas <= 25)).sum(),
        ((feitas > 25) & (feitas <= 50)).sum(),
        ((feitas > 50) & (feitas <= 100)).sum(),
        (feitas > 100).sum()
    ]

    nomes = ["1–10", "11–25", "26–50", "51–100", "Mais de 100"]

    plt.figure(figsize=(10, 5))
    plt.bar(nomes, faixas, edgecolor="black")

    plt.title("Quantidade de avaliações feitas por usuário")
    plt.xlabel("Faixas de avaliações feitas")
    plt.ylabel("Quantidade de usuários")
    plt.tight_layout()

    plt.savefig(pasta_saida / "02_avaliacoes_usuario.png", dpi=150)
    plt.close()

#Gráfico 3


def grafico_evolucao(df, pasta_saida):
    avaliacoes_ano = df.groupby(df["data"].dt.year).size()

    plt.figure(figsize=(10, 5))
    plt.plot(
        avaliacoes_ano.index,
        avaliacoes_ano.values,
        marker="o"
    )

    plt.title("Evolução temporal das avaliações")
    plt.xlabel("Ano")
    plt.ylabel("Quantidade de avaliações")
    plt.xticks(avaliacoes_ano.index)
    plt.tight_layout()

    plt.savefig(pasta_saida / "03_evolucao_temporal.png", dpi=150)
    plt.close()

#Gráfico 4


def grafico_recebidas_negativas(df, pasta_saida):
    por_usuario = df.groupby("destino").agg(
        total=("nota", "size"),
        negativas=("negativa", "sum")
    )

    plt.figure(figsize=(10, 5))
    plt.scatter(
        por_usuario["total"],
        por_usuario["negativas"],
        alpha=0.5
    )

    plt.title("Avaliações recebidas e avaliações negativas")
    plt.xlabel("Total de avaliações recebidas")
    plt.ylabel("Avaliações negativas recebidas")
    plt.tight_layout()

    plt.savefig(pasta_saida / "04_recebidas_negativas.png", dpi=150)
    plt.close()


#Gráfico 5


def grafico_evolucao_mensal(df, pasta_saida):

    avaliacoes_mes = (
        df.set_index("data")
        .resample("MS")
        .size()
    )

    fig, ax = plt.subplots(figsize=(15, 6))

    ax.plot(
        avaliacoes_mes.index,
        avaliacoes_mes.values,
        marker="o",
        markersize=3,
        linewidth=1.5
    )

    ax.xaxis.set_major_locator(
        mdates.MonthLocator(interval=3)
    )

    ax.xaxis.set_major_formatter(
        mdates.DateFormatter("%m/%Y")
    )

    plt.setp(
        ax.get_xticklabels(),
        rotation=45,
        ha="right"
    )

    ax.set_title("Evolução mensal das avaliações")
    ax.set_xlabel("Mês/Ano")
    ax.set_ylabel("Quantidade de avaliações")

    ax.grid(axis="both", alpha=0.3)

    plt.tight_layout()

    plt.savefig(
        pasta_saida / "05_evolucao_mensal.png",
        dpi=150
    )

    plt.close()


#Gráfico 6

def grafico_boxplot_notas(df, pasta_saida):
    negativas = df.loc[df["nota"] < 0, "nota"]
    positivas = df.loc[df["nota"] > 0, "nota"]

    plt.figure(figsize=(9, 5))

    plt.boxplot(
        [negativas, positivas],
        tick_labels=["Negativas", "Positivas"],
        patch_artist=True,
        showmeans=True
    )

    plt.title("Distribuição das notas positivas e negativas")
    plt.xlabel("Tipo de avaliação")
    plt.ylabel("Nota")
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        pasta_saida / "06_boxplot_notas.png",
        dpi=150
    )

    plt.close()




def gerar_visualizacoes(
    caminho="data/dataset_parte2/soc-sign-bitcoinalpha.csv",
    saida="out/parte2/avd"
):
    pasta_saida = Path(saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    df = carregar_dados(caminho)

    grafico_notas(df, pasta_saida)
    grafico_avaliacoes_usuario(df, pasta_saida)
    grafico_evolucao(df, pasta_saida)
    grafico_recebidas_negativas(df, pasta_saida)
    grafico_evolucao_mensal(df, pasta_saida)
    grafico_boxplot_notas(df, pasta_saida)

    print("Seis gráficos gerados em:", pasta_saida)


if __name__ == "__main__":
    gerar_visualizacoes()