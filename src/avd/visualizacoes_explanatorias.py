
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .visualizacoes import carregar_dados


# Gráfico 1 - Evolução da confiança e desconfiança

def grafico_confianca_por_ano(df, pasta_saida):
    dados = df.copy()

    dados["tipo"] = "Positiva"
    dados.loc[dados["nota"] < 0, "tipo"] = "Negativa"

    # Conta as avaliações por ano e tipo.
    contagem = pd.crosstab(dados["ano"], dados["tipo"])

    contagem = contagem.reindex(
        columns=["Positiva", "Negativa"],
        fill_value=0
    )

    # Converte a contagem em porcentagem.
    percentuais = contagem.div(
        contagem.sum(axis=1), axis=0
    ) * 100

    ax = percentuais.plot(
        kind="bar",
        stacked=True,
        figsize=(11, 6),
        color=["#3A9D75", "#D96C60"]
    )

    ax.set_title("Proporção de confiança e desconfiança por ano")
    ax.set_xlabel("Ano")
    ax.set_ylabel("Percentual de avaliações (%)")
    ax.set_ylim(0, 100)
    ax.legend(title="Tipo de avaliação")

    plt.xticks(rotation=0)
    plt.tight_layout()

    plt.savefig(
        pasta_saida / "proporcao_confianca_por_ano.png",
        dpi=150
    )
    plt.close()

    print("\nProporção de avaliações por ano (%):")
    print(percentuais.round(2).to_string())


# Gráfico 2 - Conectividade e desconfiança

def grafico_conectividade_desconfianca(df, pasta_saida):
    # Cada destino representa um usuário que recebeu avaliações.
    por_usuario = df.groupby("destino").agg(
        total_recebidas=("nota", "size"),
        negativas_recebidas=("negativa", "sum")
    )

    # Separa usuários com e sem avaliações negativas.
    por_usuario["grupo"] = "Sem negativas"

    por_usuario.loc[
        por_usuario["negativas_recebidas"] > 0,
        "grupo"
    ] = "Com negativas"

    # Calcula a média de avaliações recebidas em cada grupo.
    medias = por_usuario.groupby("grupo")[
        "total_recebidas"
    ].mean()

    ordem = ["Sem negativas", "Com negativas"]
    medias = medias.reindex(ordem, fill_value=0)

    fig, ax = plt.subplots(figsize=(9, 6))

    barras = ax.bar(
        medias.index,
        medias.values,
        color=["#3A9D75", "#D96C60"],
        edgecolor="black"
    )

    ax.set_title(
        "Conectividade de entrada e avaliações negativas"
    )
    ax.set_xlabel("Grupo de usuários")
    ax.set_ylabel("Média de avaliações recebidas")
    ax.set_ylim(0, max(medias.max() * 1.2, 1))

    # Mostra os valores acima das barras.
    for barra in barras:
        altura = barra.get_height()

        ax.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            f"{altura:.2f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()

    plt.savefig(
        pasta_saida / "conectividade_desconfianca.png",
        dpi=150
    )
    plt.close()

    print("\nMédia de avaliações recebidas por grupo:")
    print(medias.round(2).to_string())

    print("\nQuantidade de usuários por grupo:")
    print(
        por_usuario["grupo"]
        .value_counts()
        .reindex(ordem, fill_value=0)
        .to_string()
    )


def gerar_visualizacoes():
    dataset = Path(
        "data/dataset_parte2/soc-sign-bitcoinalpha.csv"
    )

    pasta_saida = Path(
        "out/parte2/avd/visualizacoes_explanatorias"
    )

    pasta_saida.mkdir(parents=True, exist_ok=True)

    df = carregar_dados(dataset)

    grafico_confianca_por_ano(df, pasta_saida)
    grafico_conectividade_desconfianca(df, pasta_saida)

    print("\nGráficos gerados em:", pasta_saida)


if __name__ == "__main__":
    gerar_visualizacoes()
