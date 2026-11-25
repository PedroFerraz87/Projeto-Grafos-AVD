# Visualizações explanatórias — Bitcoin Alpha
Pergunta de pesquisa
Como os usuários do Bitcoin Alpha expressam confiança e desconfiança, e de que maneira a presença de avaliações negativas está associada ao volume de avaliações recebidas?
Pensar como designer
A identidade visual reutiliza estilo_graficos.py: azul para avaliações positivas ou ausência de negativas, vermelho para presença de negativas, fundo discreto e títulos orientados às descobertas. Similaridade agrupa categorias; proximidade associa rótulos aos dados; continuidade organiza intensidades e faixas; figura e fundo destacam as evidências. Valores escritos, sinais e legendas reduzem a dependência da cor.

## Visualização 1 — Intensidade das notas

Barras agrupadas por intensidade absoluta, com percentuais calculados separadamente por sinal. Entre as 22.650 positivas, 60,75% são +1; entre as 1.536 negativas, 52,86% são −10 e 27,93% são −1. A confiança concentra-se em baixa intensidade; a desconfiança tem concentração no extremo máximo, mas também no mínimo.

## Visualização 2 — Presença de negativas por volume recebido

Barras empilhadas de 100%, com usuários agrupados por total recebido. A proporção com pelo menos uma negativa é 11,85% (1–10), 48,04% (11–25), 53,64% (26–50), 48,98% (51–100) e 59,09% (>100). Os grupos maiores têm poucos usuários. Entre os 3.754 usuários avaliados, os 630 com negativas recebem em média 15,63 avaliações, contra 4,59 dos 3.124 sem negativas. Maior exposição também aumenta a oportunidade de receber uma negativa.

## Big Idea

No Bitcoin Alpha, a confiança concentra-se em notas de baixa intensidade, enquanto a desconfiança frequentemente aparece no extremo da escala e é mais comum no histórico dos usuários mais avaliados.

## Storytelling — 3-Minute Story

Será que confiança e desconfiança são expressas da mesma maneira? A nota +1 predomina entre as positivas, enquanto −10 predomina entre as negativas. Ao agrupar usuários pelo volume recebido, observamos que a presença de negativas passa de cerca de 12% na faixa de 1 a 10 avaliações para 48% na faixa de 11 a 25. Nas demais faixas, permanece acima da primeira, sem crescimento contínuo. Assim, a intensidade das notas e a presença de negativas revelam padrões distintos de avaliação.

## Conclusão

Os resultados são descritivos, não causais. Mais avaliações aumentam as oportunidades de receber uma negativa; receber uma negativa não comprova comportamento inadequado. Os experimentos de caminhos e ciclos permanecem como análises complementares de grafos.
