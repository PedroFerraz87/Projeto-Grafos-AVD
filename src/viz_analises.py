from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import ConnectionPatch, Patch, Rectangle

from .graphs import metricas

SUPERFICIE = "#fcfcfb"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
PAREDE_CLARA = "#e4e3df"
PAREDE_ESCURA = "#3d3d3a"
NEUTRO = "#f0efec"
ARCO = "#b5b4ae"
CORES_CAMADAS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
RAMPA_AZUL = ["#b7d3f6", "#6da7ec", "#3987e5", "#1c5cab", "#0d366b"]
ESPECIAIS = set("SGabcdABCD")

def _salvar(fig, caminho):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=160, bbox_inches="tight", facecolor=SUPERFICIE)
    plt.close(fig)
    return caminho

def _nome_camada(nome):
    return "sem chaves" if nome == "-" else f"chaves {nome}"

def gerar_camadas_png(analise, caminho_saida):
    g, grade = analise["g"], analise["grade"]
    por_camada = metricas.camadas(g)
    resumo = {item["camada"]: item for item in metricas.metricas_camadas(g)}
    em_g = metricas.estados_em_g(g)
    altura, largura = len(grade), len(grade[0])

    fig, eixos = plt.subplots(len(por_camada), 1, squeeze=False,
                              figsize=(max(7, largura * 0.55), (altura * 0.55 + 0.9) * len(por_camada)))
    fig.patch.set_facecolor(SUPERFICIE)
    eixo_da_camada = {}

    for i, (nome, estados) in enumerate(por_camada.items()):
        eixo, cor = eixos[i][0], CORES_CAMADAS[i % len(CORES_CAMADAS)]
        eixo_da_camada[nome] = (eixo, cor)
        eixo.set_facecolor(SUPERFICIE)
        for l, texto in enumerate(grade):
            for c, s in enumerate(texto):
                eixo.add_patch(Rectangle((c - 0.5, -l - 0.5), 1, 1, linewidth=0,
                                         facecolor=PAREDE_CLARA if s == "#" else SUPERFICIE))
                if s in ESPECIAIS:
                    eixo.text(c - 0.42, -l + 0.42, s, fontsize=7, color=TEXTO_2, ha="left", va="top")

        conjunto = set(estados)
        ja_desenhados = set()
        for a in g.arcos():
            if a.origem in conjunto and a.destino in conjunto:
                par = frozenset((a.origem, a.destino))
                if par in ja_desenhados:
                    continue
                ja_desenhados.add(par)
                (l1, c1), (l2, c2) = metricas.posicao(a.origem), metricas.posicao(a.destino)
                eixo.plot([c1, c2], [-l1, -l2], color=ARCO, linewidth=1, zorder=1)

        xs = [metricas.posicao(v)[1] for v in estados]
        ys = [-metricas.posicao(v)[0] for v in estados]
        eixo.scatter(xs, ys, s=46, color=cor, edgecolor=SUPERFICIE, linewidth=1.5, zorder=2)
        for v in estados:
            l, c = metricas.posicao(v)
            if v == analise["inicio"]:
                eixo.annotate("início", (c, -l), xytext=(0, -11), textcoords="offset points",
                              ha="center", va="top", fontsize=8, color=TEXTO)
            if v in em_g:
                eixo.annotate("→ ALVO", (c, -l), xytext=(-22, -12), textcoords="offset points",
                              ha="right", va="top", fontsize=8, color=TEXTO)

        r = resumo[nome]
        eixo.set_title(f"Camada {nome} ({_nome_camada(nome)}): {r['ordem']} estados, {r['tamanho']} arcos",
                       loc="left", fontsize=10, color=TEXTO)
        eixo.set_xlim(-0.6, largura - 0.4)
        eixo.set_ylim(-altura + 0.4, 0.6)
        eixo.set_aspect("equal")
        eixo.axis("off")

    trocas = 0
    for a in g.arcos():
        if a.destino == "ALVO" or a.origem == "ALVO":
            continue
        de, para = metricas.camada(a.origem), metricas.camada(a.destino)
        if de == para:
            continue
        trocas += 1
        (l1, c1), (l2, c2) = metricas.posicao(a.origem), metricas.posicao(a.destino)
        eixo_de, _ = eixo_da_camada[de]
        eixo_para, cor_para = eixo_da_camada[para]
        fig.add_artist(ConnectionPatch((c1, -l1), (c2, -l2), "data", "data", axesA=eixo_de, axesB=eixo_para,
                                       arrowstyle="-|>", mutation_scale=12, color=cor_para, linewidth=2,
                                       zorder=5))
        eixo_para.annotate(f"pega a chave {a.metadados['casa_destino']}", (c2, -l2), xytext=(-10, -12),
                           textcoords="offset points", ha="right", va="top", fontsize=8, color=TEXTO)

    fig.suptitle(f"G_est do {analise['curto']} em camadas: {analise['ordem']} estados, "
                 f"{trocas} {'arco' if trocas == 1 else 'arcos'} entre camadas",
                 x=0.02, ha="left", fontsize=12, color=TEXTO)
    fig.tight_layout()
    return _salvar(fig, caminho_saida)


def gerar_heatmap_multiplicidade_png(analise, caminho_saida):
    grade = analise["grade"]
    mult = metricas.multiplicidade(analise["g"])
    maximo = max(mult.values())
    rampa = RAMPA_AZUL[-maximo:] if maximo <= len(RAMPA_AZUL) else RAMPA_AZUL
    matriz = [[-1 if s == "#" else mult.get((l, c), 0) for c, s in enumerate(texto)]
              for l, texto in enumerate(grade)]
    cores = [PAREDE_ESCURA, NEUTRO] + rampa
    norma = BoundaryNorm([v - 0.5 for v in range(-1, len(rampa) + 2)], len(cores))

    altura, largura = len(grade), len(grade[0])
    fig, eixo = plt.subplots(figsize=(max(8, largura * 0.24), altura * 0.24 + 1.6))
    fig.patch.set_facecolor(SUPERFICIE)
    eixo.imshow(matriz, cmap=ListedColormap(cores), norm=norma, interpolation="nearest")

    for l, texto in enumerate(grade):
        for c, s in enumerate(texto):
            if s in ESPECIAIS:
                fundo_escuro = mult.get((l, c), 0) >= 3
                eixo.text(c, l, s, ha="center", va="center", fontsize=6.5, fontweight="bold",
                          color=SUPERFICIE if fundo_escuro else TEXTO)

    no_max = sum(1 for m in mult.values() if m == maximo)
    eixo.set_title(f"Multiplicidade do G_est por casa: {analise['nome']} "
                   f"(máximo {maximo} estados, em {no_max} casas)", loc="left", fontsize=11, color=TEXTO)
    eixo.axis("off")

    legenda = [Patch(facecolor=PAREDE_ESCURA, label="parede")]
    if any(0 in linha for linha in matriz):
        legenda.append(Patch(facecolor=NEUTRO, label="0 (inalcançável)"))
    legenda += [Patch(facecolor=cor, label=f"{i} estado" + ("s" if i > 1 else ""))
                for i, cor in enumerate(rampa, start=1)]
    eixo.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=len(legenda),
                frameon=False, fontsize=8, labelcolor=TEXTO_2, handlelength=1.2)
    fig.tight_layout()
    return _salvar(fig, caminho_saida)


def gerar_figuras_t30(analises, pasta_saida):
    por_nome = {a["curto"]: a for a in analises}
    pasta_saida, gerados = Path(pasta_saida), []
    if "m02" in por_nome:
        gerados.append(gerar_camadas_png(por_nome["m02"], pasta_saida / "g_est_camadas_m02.png"))
    if "m08" in por_nome:
        gerados.append(gerar_heatmap_multiplicidade_png(por_nome["m08"],
                                                        pasta_saida / "heatmap_multiplicidade_m08.png"))
    return gerados
