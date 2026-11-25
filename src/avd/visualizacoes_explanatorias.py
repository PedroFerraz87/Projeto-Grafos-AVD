from pathlib import Path
import pandas as pd
from .estilo_graficos import NEGATIVA, POSITIVA, TINTA, MUTED, formatar_eixo, numero, prancha, salvar
from .visualizacoes import FONTE, carregar_dados


def grafico_intensidade_notas(df, pasta_saida):
    positivas = df.loc[df['nota'] > 0, 'nota']
    negativas = df.loc[df['nota'] < 0, 'nota'].abs()
    intensidade = range(1, 11)
    p = positivas.value_counts(normalize=True).reindex(intensidade, fill_value=0) * 100
    n = negativas.value_counts(normalize=True).reindex(intensidade, fill_value=0) * 100
    fig, ax = prancha('+1 domina as positivas; −10 domina as negativas',
                      f'Percentuais dentro de cada sinal: {numero(len(positivas))} positivas e {numero(len(negativas))} negativas.',
                      'Intensidade da nota (valor absoluto)', 'Percentual dentro do grupo', altura=6)
    for i in intensidade:
        ax.bar(i-.19, p[i], width=.36, color=POSITIVA, alpha=1 if i == 1 else .45)
        ax.bar(i+.19, n[i], width=.36, color=NEGATIVA, alpha=1 if i in (1,10) else .45)
    for x, valor, rotulo, cor in [( .81,p[1],'+1',POSITIVA),(1.19,n[1],'-1',NEGATIVA),(10.19,n[10],'-10',NEGATIVA)]:
        ax.annotate(f'{rotulo}: {numero(valor,1)}%', (x,valor), xytext=(0,7), textcoords='offset points', ha='center', color=cor, weight='bold', fontsize=10)
    ax.set(xticks=list(intensidade), xlim=(.15,10.85), ylim=(0,max(p.max(),n.max())*1.23))
    formatar_eixo(ax.yaxis, unidade='%')
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=POSITIVA,label='Positivas (+)'),Patch(color=NEGATIVA,label='Negativas (−)')], frameon=False, loc='upper center', ncol=2)
    salvar(fig, pasta_saida / 'intensidade_confianca_desconfianca.png', FONTE, 'Cada grupo soma 100%')
    print(pd.DataFrame({'Positivas (%)':p,'Negativas (%)':n}).round(2).to_string())


def resumir_avaliacoes_por_faixa(df):
    usuarios = df.groupby('destino').agg(total=('nota', 'size'), negativas=('negativa', 'sum'))
    usuarios['com_negativas'] = usuarios.negativas.gt(0)
    usuarios['faixa'] = pd.cut(usuarios.total, [0, 10, 25, 50, 100, float('inf')],
                               labels=['1–10', '11–25', '26–50', '51–100', '>100'])
    faixas = usuarios.groupby('faixa', observed=False).com_negativas.agg(['size', 'sum'])
    faixas['percentual'] = 100 * faixas['sum'] / faixas['size']
    return usuarios, faixas


def grafico_conectividade_desconfianca(df, pasta_saida):
    usuarios, faixas = resumir_avaliacoes_por_faixa(df)
    faixas = faixas.loc[faixas['size'] > 0]
    fig, ax = prancha('Históricos com negativas são mais comuns entre os mais avaliados',
                      'Cada faixa soma 100% dos usuários avaliados; n indica o tamanho do grupo.',
                      'Percentual de usuários', grade='x', esquerda=.22, altura=6.2)
    fig.texts[0].set_fontsize(18)
    rotulos = [f'{f} avaliações\n(n = {numero(n)})' for f, n in faixas['size'].items()]
    negativas = faixas.percentual
    ax.barh(rotulos, negativas, color=NEGATIVA, height=.62, label='Com negativas')
    ax.barh(rotulos, 100-negativas, left=negativas, color=POSITIVA, height=.62, label='Sem negativas')
    for i, v in enumerate(negativas):
        for inicio, largura in [(0, v), (v, 100-v)]:
            if largura >= 9:
                ax.text(inicio+largura/2, i, numero(largura,1)+'%', ha='center', va='center', color='white', weight='bold', fontsize=10)
    ax.set(xlim=(0,100), xticks=[0,25,50,75,100]); ax.invert_yaxis()
    formatar_eixo(ax.xaxis, unidade='%')
    ax.legend(loc='lower center', bbox_to_anchor=(.5,1.01), ncol=2, frameon=False)
    salvar(fig, pasta_saida / 'conectividade_desconfianca.png', FONTE, 'Mais avaliações implicam mais oportunidades de receber negativas')
    print(faixas.round(2).to_string())


def gerar_visualizacoes(caminho='data/dataset_parte2/soc-sign-bitcoinalpha.csv', saida='out/parte2/avd/visualizacoes_explanatorias'):
    pasta_saida = Path(saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    df = carregar_dados(caminho)
    grafico_intensidade_notas(df,pasta_saida)
    grafico_conectividade_desconfianca(df,pasta_saida)
    print('Gráficos gerados em:',pasta_saida)


if __name__ == '__main__':
    gerar_visualizacoes()
