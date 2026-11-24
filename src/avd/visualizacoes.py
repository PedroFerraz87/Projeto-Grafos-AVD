# [IA] Apoio do ChatGPT na implementação das visualizações da T27.
# [IA] OpenAI Codex – hierarquia, agrupamento e anotações para a leitura das figuras.
from pathlib import Path

import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import pandas as pd

from .estilo_graficos import MUTED, NEGATIVA, POSITIVA, SUAVE, TINTA, formatar_eixo, numero, prancha, salvar

COLUNAS = ["origem", "destino", "nota", "timestamp"]
FONTE = "Fonte: Bitcoin Alpha (SNAP) · CSV do projeto"


def carregar_dados(caminho):
    dados = pd.read_csv(caminho, header=None, names=COLUNAS)
    dados["data"] = pd.to_datetime(dados["timestamp"], unit="s", utc=True)
    dados["negativa"] = dados["nota"] < 0
    dados["ano"] = dados["data"].dt.year
    dados["mes"] = dados["data"].dt.month
    dados["dia"] = dados["data"].dt.day
    return dados


def grafico_notas(df, pasta_saida):
    notas = df["nota"].value_counts().sort_index()
    fig, ax = prancha("Distribuição das notas", "Uma barra por nota observada. A cor indica o sinal.",
                      "Nota atribuída", "Avaliações")
    ax.axvspan(-10.6, -.45, color=NEGATIVA, alpha=.06, linewidth=0)
    ax.axvspan(.45, 10.6, color=POSITIVA, alpha=.06, linewidth=0)
    ax.bar(notas.index, notas, width=.7, color=[NEGATIVA if n < 0 else POSITIVA for n in notas.index])
    ax.set(xlim=(-10.6, 10.6), xticks=[-10, -8, -6, -4, -2, 0, 1, 2, 4, 6, 8, 10])
    ax.set_ylim(0, notas.max()*1.22)
    formatar_eixo(ax.yaxis)
    for sinal, lado, cor in ((-1, -9.9, NEGATIVA), (1, 9.9, POSITIVA)):
        n = int((df["nota"] * sinal > 0).sum())
        ax.text(lado, notas.max()*1.1, f"{numero(n)} {'negativas' if sinal < 0 else 'positivas'}",
                color=cor, weight="bold", va="bottom", ha="left" if sinal < 0 else "right")
    dominante = notas.idxmax()
    ax.text(dominante, notas.max()*1.026, numero(notas.max()), color=TINTA, ha="center", va="bottom", weight="bold")
    salvar(fig, pasta_saida / "01_distribuicao_notas.png", FONTE, f"{numero(len(df))} avaliações")


def grafico_avaliacoes_usuario(df, pasta_saida):
    feitas = df.groupby("origem").size()
    limites = [(1, 10), (11, 25), (26, 50), (51, 100), (101, float("inf"))]
    faixas = [int(feitas.between(inicio, fim).sum()) for inicio, fim in limites]
    nomes = ["1–10", "11–25", "26–50", "51–100", "Mais de 100"]
    fig, ax = prancha("Avaliações feitas por usuário", "Usuários agrupados pela quantidade de avaliações que enviaram.",
                      "Usuários", "Faixa de avaliações", grade="x", esquerda=.19)
    barras = ax.barh(nomes, faixas, height=.55, color=[POSITIVA, *[SUAVE]*4])
    ax.bar_label(barras, labels=[numero(n) for n in faixas], padding=6, color=TINTA, weight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, max(faixas)*1.19)
    formatar_eixo(ax.xaxis)
    salvar(fig, pasta_saida / "02_avaliacoes_usuario.png", FONTE, f"{numero(len(feitas))} usuários que avaliaram")


def grafico_evolucao(df, pasta_saida):
    anos = df.groupby("ano").size()
    fig, ax = prancha("Avaliações por ano", "O primeiro e o último ano cobrem apenas parte do calendário.",
                      "Ano", "Avaliações")
    ax.plot(anos.index, anos, color=POSITIVA, marker="o", markersize=5, linewidth=2.1)
    ax.fill_between(anos.index, anos, color=POSITIVA, alpha=.08)
    ano_maximo = anos.idxmax()
    ax.scatter([ano_maximo], [anos.max()], color=POSITIVA, s=67, edgecolors="white", zorder=4)
    ax.annotate(f"{ano_maximo} · {numero(anos.max())} avaliações", (ano_maximo, anos.max()),
                xytext=(0, 12), textcoords="offset points", ha="center", color=TINTA, weight="bold")
    ax.set(ylim=(0, anos.max()*1.21), xticks=anos.index)
    formatar_eixo(ax.yaxis)
    periodo = f"{df['data'].min():%m/%Y} a {df['data'].max():%m/%Y}"
    salvar(fig, pasta_saida / "03_evolucao_temporal.png", FONTE, periodo)


def grafico_recebidas_negativas(df, pasta_saida):
    por_usuario = df.groupby("destino").agg(total=("nota", "size"), negativas=("negativa", "sum"))
    fig, ax = prancha("Avaliações recebidas e negativas", "Cada ponto é um usuário com ao menos uma avaliação recebida.",
                      "Total de avaliações recebidas", "Avaliações negativas recebidas")
    sem_negativas = por_usuario[por_usuario["negativas"] == 0]
    com_negativas = por_usuario[por_usuario["negativas"] > 0]
    ax.scatter(sem_negativas["total"], sem_negativas["negativas"], s=21, color=POSITIVA,
               alpha=.32, linewidths=0, label="Sem negativas")
    ax.scatter(com_negativas["total"], com_negativas["negativas"], s=20, color=NEGATIVA,
               alpha=.46, linewidths=0, label="Com negativas")
    ax.set_ylim(bottom=-por_usuario["negativas"].max()*.04)
    formatar_eixo(ax.xaxis)
    formatar_eixo(ax.yaxis)
    ax.legend(loc="upper right", frameon=False, labelcolor=TINTA)
    salvar(fig, pasta_saida / "04_recebidas_negativas.png", FONTE, f"{numero(len(por_usuario))} usuários avaliados")


def grafico_evolucao_mensal(df, pasta_saida):
    meses = df.set_index("data").resample("MS").size()
    fig, ax = prancha("Avaliações por mês", "A linha liga os meses consecutivos do intervalo observado.",
                      "Ano", "Avaliações por mês")
    ax.plot(meses.index, meses, color=POSITIVA, linewidth=1.8)
    ax.fill_between(meses.index, meses, color=POSITIVA, alpha=.09)
    pico = meses.idxmax()
    ax.scatter([pico], [meses.max()], s=58, color=POSITIVA, edgecolors="white", zorder=3)
    ax.annotate(f"{pico:%m/%Y} · {numero(meses.max())}", (pico, meses.max()),
                xytext=(9, 13), textcoords="offset points", color=TINTA, weight="bold")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set(ylim=(0, meses.max()*1.21), xlim=(meses.index[0], meses.index[-1]))
    formatar_eixo(ax.yaxis)
    salvar(fig, pasta_saida / "05_evolucao_mensal.png", FONTE, f"{len(meses)} meses")


def grafico_boxplot_notas(df, pasta_saida):
    negativas = df.loc[df["nota"] < 0, "nota"]
    positivas = df.loc[df["nota"] > 0, "nota"]
    fig, ax = prancha("Notas negativas e positivas", "As caixas representam os 50% centrais das notas de cada grupo.",
                      y="Nota")
    caixa = ax.boxplot([negativas, positivas], widths=.32, patch_artist=True, showmeans=True,
                      medianprops={"color": TINTA, "linewidth": 2},
                      meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": TINTA, "markersize": 6},
                      flierprops={"marker": ".", "markeredgecolor": MUTED, "markersize": 4})
    for item, cor in zip(caixa["boxes"], [NEGATIVA, POSITIVA]):
        item.set_facecolor(cor)
        item.set_alpha(.55)
        item.set_edgecolor(TINTA)
    ax.axhline(0, color="#8d9cb0", linewidth=1, linestyle="--")
    ax.set_xticks([1, 2], [f"Negativas · n={numero(len(negativas))}", f"Positivas · n={numero(len(positivas))}"])
    ax.set(ylim=(-11, 11), yticks=range(-10, 11, 2))
    ax.legend(handles=[
        Line2D([], [], color=TINTA, linewidth=2, label="Mediana"),
        Line2D([], [], color=TINTA, marker="o", markerfacecolor="white", linestyle="none", label="Média"),
    ], loc="upper left", frameon=False, labelcolor=TINTA)
    salvar(fig, pasta_saida / "06_boxplot_notas.png", FONTE, "Bigodes: critério de 1,5 × IIQ")


def gerar_visualizacoes(caminho="data/dataset_parte2/soc-sign-bitcoinalpha.csv", saida="out/parte2/avd"):
    pasta_saida = Path(saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    df = carregar_dados(caminho)
    for grafico in (grafico_notas, grafico_avaliacoes_usuario, grafico_evolucao, grafico_recebidas_negativas,
                    grafico_evolucao_mensal, grafico_boxplot_notas):
        grafico(df, pasta_saida)
    print("Seis gráficos gerados em:", pasta_saida)


if __name__ == "__main__":
    gerar_visualizacoes()
