# [IA] OpenAI Codex – agrupamento visual, cores de sinal e valores próximos aos dados.
from pathlib import Path

import pandas as pd

from .estilo_graficos import NEGATIVA, POSITIVA, TINTA, formatar_eixo, numero, prancha, salvar
from .visualizacoes import FONTE, carregar_dados


def grafico_confianca_por_ano(df, pasta_saida):
    tipos = df["negativa"].map({True: "Negativa", False: "Positiva"})
    contagem = pd.crosstab(df["ano"], tipos).reindex(columns=["Positiva", "Negativa"], fill_value=0)
    percentuais = contagem.div(contagem.sum(axis=1), axis=0)*100
    fig, ax = prancha("Sinal das avaliações por ano", "Cada barra soma 100% das notas registradas naquele ano. Os rótulos mostram a parcela negativa.",
                      "Ano", "Proporção das avaliações")
    anos = percentuais.index
    ax.bar(anos, percentuais["Positiva"], color=POSITIVA, width=.63, label="Positivas")
    ax.bar(anos, percentuais["Negativa"], bottom=percentuais["Positiva"], color=NEGATIVA,
           width=.63, label="Negativas")
    for ano, porcentagem in percentuais["Negativa"].items():
        ax.text(ano, 102.4, numero(porcentagem, 2)+"%", ha="center", va="bottom",
                color=NEGATIVA, weight="bold", size=9.25)
    ax.set(ylim=(0,112), xticks=anos, yticks=[0,25,50,75,100])
    formatar_eixo(ax.yaxis, unidade="%")
    fig.legend(loc="upper right", bbox_to_anchor=(.955,.8), ncol=2, frameon=False, labelcolor=TINTA)
    salvar(fig, pasta_saida / "proporcao_confianca_por_ano.png", FONTE, "2010 e 2016 têm cobertura parcial")
    print("\nProporção de avaliações por ano (%):")
    print(percentuais.round(2).to_string())


def grafico_conectividade_desconfianca(df, pasta_saida):
    por_usuario = df.groupby("destino").agg(total_recebidas=("nota", "size"),
                                             negativas_recebidas=("negativa", "sum"))
    por_usuario["grupo"] = por_usuario["negativas_recebidas"].gt(0).map({False: "Sem negativas",
                                                                        True: "Com negativas"})
    grupos = por_usuario.groupby("grupo")["total_recebidas"].agg(["mean", "size"])
    grupos = grupos.reindex(["Sem negativas", "Com negativas"], fill_value=0)
    fig, ax = prancha("Avaliações recebidas por grupo", "Entre usuários que receberam ao menos uma avaliação.",
                      "Média de avaliações recebidas", grade="x", esquerda=.215)
    rotulos = [f"{nome}\n(n={numero(n)})" for nome, n in grupos["size"].items()]
    barras = ax.barh(rotulos, grupos["mean"], height=.45, color=[POSITIVA, NEGATIVA])
    ax.bar_label(barras, labels=[numero(valor, 2) for valor in grupos["mean"]],
                 padding=7, color=TINTA, weight="bold", size=12)
    ax.set_xlim(0, max(grupos["mean"].max()*1.24,1))
    ax.invert_yaxis()
    formatar_eixo(ax.xaxis)
    salvar(fig, pasta_saida / "conectividade_desconfianca.png", FONTE, "Agrupado pela presença de nota negativa")
    print("\nMédia recebida e usuários por grupo:")
    print(grupos.round(2).to_string())


def gerar_visualizacoes(caminho="data/dataset_parte2/soc-sign-bitcoinalpha.csv",
                        saida="out/parte2/avd/visualizacoes_explanatorias"):
    pasta_saida = Path(saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    df = carregar_dados(caminho)
    grafico_confianca_por_ano(df, pasta_saida)
    grafico_conectividade_desconfianca(df, pasta_saida)
    print("\nGráficos gerados em:", pasta_saida)


if __name__ == "__main__":
    gerar_visualizacoes()
