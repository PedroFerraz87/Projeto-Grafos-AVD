# Casos sintéticos sugeridos para P2

Todos os exemplos estão em tests/fixtures/p2_casos_sinteticos.json. São sugestões de teste, a conferir pelo grupo; não são soluções dos mapas fornecidos nem resultados do Bitcoin Alpha. As arestas aparecem na ordem de inserção.

Os campos distancias_finitas, inalcancaveis e afetados distinguem resposta finita, falta de caminho e ausência de mínimo por ciclo negativo. Essa notação das fixtures não impõe o formato de retorno da implementação.

| Caso | O que conferir |
| --- | --- |
| T02_ordem_direcao_metadados | S recebe quatro saídas, inseridas como N/L/S/O. A lista deve conservar essa ordem; não há arcos reversos automáticos. Pesos 1, 3, 5 e -4 e metadados são conservados. I é isolado e deve continuar existindo no transposto. |
| T02_vertices_isolados | Dois vértices e nenhum arco. Cadastrar um vértice não exige criar ligação; o transposto conserva ambos. S alcança apenas S. |
| T11_passos_diferem_de_custo | BFS chega a T em dois arcos por S-A-T. Dijkstra chega por S-B-A-T em três arcos e custo 4. O vértice I é inalcançável. Não confundir número de passos com soma dos pesos. |
| T12_quatro_classes | DFS a partir de A descobre A, B, C e D. Arcos de árvore: A-B, B-C, A-D; retorno: C-A; avanço: A-C; cruzamento: D-C. A ordem de adjacência é parte do exemplo. |
| T12_sem_ciclo_na_componente_alcancavel | S alcança apenas T; o ciclo X-Y está desconectado da fonte. Uma DFS a partir de S não deve declarar que encontrou esse ciclo. |
| T13_zero_e_rejeicao_global | Um arco de peso zero é aceito pela estrutura. O arco negativo X-Y, mesmo inacessível de S, exige recusa de Dijkstra segundo a regra do projeto. |
| T14_negativos_sem_ciclo | Bellman-Ford deve obter S=0, A=4, B=2, T=5; I inalcançável. O caminho até T é S-A-B-T. Há negativo, mas não ciclo negativo. |
| T14_ciclo_negativo_alcancavel | O ciclo A-B-A soma -2. A, B e T ficam afetados; S mantém distância finita e I continua inalcançável. |
| T14_ciclo_negativo_inalcancavel | O ciclo X-Y-X soma -2, mas não é alcançável de S. Bellman-Ford da fonte S tem T=5 e não deve atribuir a esse caso um ciclo negativo alcançável. Dijkstra ainda deve recusar o grafo inteiro. |
| T14_ciclo_nao_afeta_destino_finito | S chega ao ciclo A-B-A, mas ele não leva a T. T continua com mínimo 4 por S-T; A e B não têm mínimo finito. Distinguir ciclo alcançável de ciclo capaz de atingir o destino consultado. |
| T15_armadilha_tem_saida_mas_nao_alcanca_alvo | A e B formam uma região sem acesso a ALVO, embora tenham saída um para o outro. São armadilhas alcançáveis. I é isolado e inacessível de S: não faz parte desse conjunto. G liga ao ALVO virtual com custo zero. |

## Cuidados ao transformar em testes da implementação

- Comparar também os estados inalcançáveis; não contar todos os vértices cadastrados como visitados.
- Conferir o caminho retornado arco a arco e a soma dos pesos.
- Conferir pais e níveis do BFS, além de um único caminho até o destino.
- Os valores absolutos dos tempos de descoberta/finalização da DFS dependem da convenção do relógio. Conferir a ordenação e os intervalos, e registrar a convenção escolhida pelo grupo.
- Um ciclo negativo pode ser retornado começando por qualquer vértice do mesmo ciclo. Não exigir a mesma rotação do exemplo: exigir fechamento, arcos dirigidos existentes e soma negativa.
- Grafo transposto é uma cópia com direções invertidas para busca; não altera o original e não gera regra de movimento do labirinto.
- A recusa de negativos por Dijkstra é uma exigência do projeto. O teste do oráculo não pressupõe que o NetworkX imponha a mesma política.
- O formato público das funções, o tratamento de arestas repetidas e a representação de infinito precisam ser definidos pelos alunos antes de adaptar os asserts.

## Como ler a conferência automática

O arquivo test_casos_referencia_p2.py usa algoritmos prontos apenas como oráculo dentro de tests/, conforme a exceção do enunciado. Ele confere que os valores sugeridos acima são consistentes. A implementação de produção continua sendo responsabilidade do P2 e não é chamada nessa conferência.
