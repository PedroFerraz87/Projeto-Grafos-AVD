# Revisão da integração (T34)

Base revisada: `f03c80c802e79b306f9eb82759102550a028f88c`. O registro abaixo é uma revisão técnica assistida com OpenAI Codex para Artur conferir com Ricardo e Pedro.

## Achados

1. **Tratamento de mapa inválido na CLI.** `python -m src.cli --mapa .gitignore` termina com código 1 e traceback de `MapaInvalido`. O tratamento atual em `src/cli.py` cobre a localização do arquivo. A análise posterior precisa tratar `MapaInvalido` e erros de leitura com uma mensagem que identifique o mapa inválido. Esse caso interessa à demonstração com mapa surpresa.
2. **Contagem de armadilhas no painel.** Em `src/templates/labirinto_interativo.html`, a quantidade exibida usa posições únicas. Com bônus já consumidos e não consumidos, estados distintos podem ocupar a mesma posição na mesma camada. Um mapa sintético de teste produziu sete estados-armadilha em quatro casas. Se o painel informar quantidade de estados, deve contar os estados antes de agregar suas posições para o destaque visual.
3. **Custo da fila da BFS no benchmark.** `src/graphs/algorithms.py` usa `list.pop(0)`, que desloca os itens restantes da fila. A comparação de escalabilidade deve considerar esse custo no código atual. Uma fila com `collections.deque` mantém a remoção da frente em tempo constante.
4. **Origem da implementação.** A revisão encontrou a marcação de IA dos algoritmos no commit `9c109bf` e confirmou sua retirada em `bacad13`. A marcação foi reposta nesta cópia, com referência ao commit de origem e aos ajustes posteriores feitos no repositório do grupo.

## Verificações

Na base, `python -m pytest -q` passou em 561 testes, incluindo a CLI da Parte 1 e a produção de HTML em diretórios temporários. O caso da CLI com mapa inválido foi reproduzido separadamente. A contagem do painel foi conferida por leitura do código e com um mapa sintético. A revisão não incluiu teste visual no navegador.

Os pontos 1 e 2 ficam para conferência dos responsáveis pela CLI e pela visualização. As medições da T26 ainda são necessárias para a comparação de desempenho da T32.
