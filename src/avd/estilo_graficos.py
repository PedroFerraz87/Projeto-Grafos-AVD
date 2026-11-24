# [IA] OpenAI Codex – convenções de leitura e hierarquia visual dos gráficos da Parte 2.
"""Estilo comum para as figuras do Bitcoin Alpha."""
from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

PAPEL = "#f5f2e9"
CAMPO = "#fbf9f1"
TINTA = "#16283d"
MUTED = "#45566a"
GRADE = "#d9dfdf"
POSITIVA = "#1849b8"
NEGATIVA = "#ad3d28"
SUAVE = "#8ca8d7"
ALGORITMOS = {
    "BFS": ("BFS", "#00647f", "o"),
    "DFS": ("DFS", "#8743aa", "s"),
    "DIJKSTRA": ("Dijkstra", "#aa4226", "^"),
    "BELLMAN_FORD": ("Bellman-Ford", "#246046", "D"),
}


def numero(valor, casas=0):
    return f"{valor:,.{casas}f}".translate(str.maketrans(".,", ",."))


def prancha(titulo, descricao, x="", y="", *, grade="y", esquerda=.118, altura=5.45):
    fig, ax = plt.subplots(figsize=(11.2, altura), facecolor=PAPEL)
    fig.subplots_adjust(left=esquerda, right=.954, top=.765, bottom=.187)
    fig.text(.052, .922, titulo, color=TINTA, size=22, weight="bold", va="top")
    fig.text(.052, .842, descricao, color=MUTED, size=10.6, va="top")
    ax.set_facecolor(CAMPO)
    ax.set_axisbelow(True)
    ax.grid(axis=grade, color=GRADE, linewidth=.8)
    ax.tick_params(axis="both", which="both", length=0, colors=MUTED, labelsize=10, pad=6)
    for nome, borda in ax.spines.items():
        borda.set_visible(nome in {"bottom", "left"})
        borda.set_color("#a0afbd")
    ax.set_xlabel(x, color=MUTED, size=10, labelpad=6)
    ax.set_ylabel(y, color=MUTED, size=10, labelpad=8)
    return fig, ax


def formatar_eixo(eixo, casas=0, unidade=""):
    eixo.set_major_formatter(FuncFormatter(lambda valor, _: numero(valor, casas) + unidade))


def salvar(fig, destino, fonte, nota=""):
    fig.text(.052, .053, fonte, size=8.4, color=MUTED, va="center")
    if nota:
        fig.text(.954, .053, nota, size=8.4, color=MUTED, va="center", ha="right")
    fig.savefig(destino, dpi=170, facecolor=PAPEL)
    plt.close(fig)
