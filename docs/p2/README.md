# P2 - Artur Antunes

Preparação do pacote de algoritmos e testes, conforme a divisão do Plano do Projeto Grafos + AVD recebido em 09/11/2026. O revisor formal do P2 é Ricardo Machado.

## Situação desta contribuição

Este parcial contém orientação e sugestões de testes, com apoio de IA registrado. **Não conclui T02 nem implementa os algoritmos.** Na base conferida, graph.py e algorithms.py estão vazios. Esses arquivos permanecem para implementação autoral, conforme as regras do grupo.

O material do P5 iniciado antes da confirmação da divisão foi interrompido e ficou somente em um rascunho local. Ele não integra esta contribuição.

## O que fazer primeiro: Sprint 0 / T02

Prazo do plano: 09 a 10/11. Dependência: T01, a estrutura inicial que já consta no repositório. Entrega: src/graphs/graph.py com representação dirigida por lista de adjacência, ordem de inserção, pesos, metadados e transposto.

1. Combinar com Ricardo e Luca a API que será consumida por estados, algoritmos e métricas. O plano não fixa nomes ou assinaturas dos métodos; não há uma API acordada nestes arquivos auxiliares.
2. Definir como cadastrar e consultar vértices, inclusive os sem nenhuma aresta.
3. Escrever a inclusão de um arco dirigido, preservando o peso e os metadados recebidos. A criação de um arco não autoriza criar o arco reverso automaticamente.
4. Conferir que os vizinhos são devolvidos na ordem em que foram inseridos. A exploração dos mapas fornecerá N, L, S, O; a estrutura deve preservar essa ordem, sem ordenar alfabeticamente.
5. Escrever o transposto como outro grafo, invertendo origem e destino de cada arco e conservando os vértices, pesos e metadados associados ao arco original. Não mudar o grafo original durante essa operação.
6. Conferir os casos T02 abaixo com a API escrita pelo grupo e registrar as decisões sobre arestas repetidas e tipos de identificadores.
7. Pedir a revisão de Ricardo. Não marcar T02 como concluída apenas por estes exemplos passarem no oráculo.

Uma esteira ou uma porta pertence às regras de estados do P1. O grafo genérico armazena os arcos e seus metadados; não deve decidir se um movimento do jogo é permitido. No transposto usado para busca reversa, inverter um arco não significa inventar um movimento físico permitido no mapa.

## Arquivos de apoio

- tests/fixtures/p2_casos_sinteticos.json: entradas e expectativas independentes de API.
- tests/test_casos_referencia_p2.py: conferência das expectativas usando NetworkX, exclusivamente em tests/.
- docs/p2/CASOS_TESTE.md: explicação dos 11 cenários.
- docs/p2/AGENDA_ARTUR.md: tarefas e dependências do plano.
- [Declaração coletiva de uso de IA](../../README.md#uso-de-ia).

## Executar a conferência dos exemplos

Na raiz do projeto, com as dependências de requirements.txt instaladas:

```powershell
python -m pytest tests/test_casos_referencia_p2.py -q
```

O comando verifica as expectativas dos exemplos com um oráculo externo. **Não importa nem testa src/graphs/graph.py ou algorithms.py.** Portanto, seu resultado não demonstra corretude da implementação do grupo e não substitui os testes obrigatórios de Graph, BFS, DFS, Dijkstra e Bellman-Ford.

Os testes desses módulos devem ser escritos contra a API efetivamente combinada pelo grupo. Quando houver uma primeira versão autoral, ela pode ser depurada com apoio declarado de IA. Não é preciso esperar os labirintos para testar os algoritmos: os pequenos grafos destas fixtures já cobrem os comportamentos importantes.

## Regra de trabalho do grupo

O plano prevê commits pequenos direto na main, sem branches ou PRs, com a própria conta, revisão e pytest antes de cada push. Antes de enviar, atualizar com git pull --rebase. O título de um commit deste material deve indicar preparação de casos, sem afirmar que T02 foi implementada.

## Referências de escopo

Plano do Projeto Grafos + AVD (08/11): páginas 4-5 para T02/T11-T15; página 6 para T25; página 7 para T32/T36; páginas 8-9 para revisão e apoio de IA. O plano proíbe geração de graph.py e algorithms.py por IA; permite dúvidas conceituais, depuração de código dos alunos e sugestões de testes com registro.
