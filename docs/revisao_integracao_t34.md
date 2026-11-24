# Revisão da integração (T34)

Parecer de Artur Antunes para Ricardo Machado. A primeira revisão foi feita em `f03c80c`. Em 23/11/2026, os casos foram conferidos sobre `833729d`. Em 24/11, a integração foi revista sobre `ff83d6b`.

## Achados

1. **Mapa inválido na CLI · corrigido.** Ricardo tratou erros de validação da grade em `1a5f538`. A revisão de integração estendeu o tratamento às falhas de leitura e à codificação inválida. A CLI informa o nome do mapa e a causa, retorna código 1 e encerra antes de gravar as saídas.
2. **Contagem de armadilhas no painel · corrigida na demonstração.** Na base `833729d`, o painel exibe o número de casas distintas da camada. Estados com o mesmo conjunto de chaves e diferentes bônus consumidos podem compartilhar uma casa. Com o painel revisto, um teste de navegador em mapa sintético confirmou oito estados-armadilha e seis casas realçadas. Desligar o realce remove as marcas da grade e preserva o total do contador.
3. **Custo da fila da BFS · registrado para o benchmark.** `src/graphs/algorithms.py` usa `list.pop(0)`, que desloca os itens restantes da fila. As medições publicadas da T26 correspondem a essa implementação. Em uma revisão futura do algoritmo, uma fila com `collections.deque` permite remover o primeiro elemento em tempo constante.
4. **Origem da implementação · marcação restaurada.** O commit `9c109bf` publicou a implementação inicial e os testes gerados com OpenAI Codex. A marcação foi removida em `bacad13`, restaurada em `0e8586d` e retirada novamente em `1a5f538`. Esta revisão repõe o cabeçalho com a origem da implementação e o registro dos ajustes do grupo.

## Verificações

Na base `833729d`, `python -m pytest -q` passou em 565 testes. A revisão também reproduziu o caso de mapa inválido e executou o HTML revisto em desktop e celular com os mapas do projeto e o mapa sintético.

As 180 medições da T26 foram conferidas com os resumos do JSON e com as sete tabelas regeneradas da T32. O [apoio à comparação](avd/apoio_comparacao.md) descreve os comandos e as condições registradas no benchmark.

## Revisões de Artur previstas no planejamento

| Tarefa | Evidência conferida | Resultado |
|---|---|---|
| T01 | Estrutura, oito mapas fornecidos, configuração do pytest e dependências | `pip check` passou em Python 3.11.15. |
| T04 | Figuras de m02 e do mapa mínimo | As contagens das figuras coincidem com a execução. Elas registram apoio de Claude e conferência por script. O desenho e a contagem manuais previstos no plano seguem sujeitos à comprovação do grupo. |
| T07–T09 | Validação dos mapas, opções de porta em `G_pos` e regras de chaves, bônus, fonte e `ALVO` em `G_est` | Os testes das camadas de leitura e modelagem passaram. O erro de apresentação da CLI está registrado no item 1. |
| T10 | Exportação de arestas | Os dez CSVs publicados coincidem com a reprodução após normalizar as quebras de linha. |
| T16 | Oráculo implementado por Luca | Passaram os 345 casos dedicados. NetworkX aparece apenas na suíte, com grafos sintéticos e `G_pos` como entradas do oráculo. Os testes de integração cobrem `G_est`. |

O comando `python -m pytest -q tests/test_io.py tests/test_estados.py tests/test_oraculo_networkx.py` passou com 441 testes.

<!-- [IA] OpenAI Codex – reprodução das falhas, atualização do parecer e conferência de evidências. -->
