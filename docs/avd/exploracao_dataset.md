
# T19 - Exploração do dataset Bitcoin Alpha

## Estrutura e tipos

- O dataset tem 24.186 linhas 

- 4 colunas: 'origem' , 'destino', 'nota' e 'timestamp'. Todas são do tipo int.

- 'origem' e 'destino' identificam os usuários, 'nota' representa a avaliação e, 'timestamp' informa quando a avaliação aconteceu.

- Existem 3.783 usuários diferentes.

## Valores faltantes

- Não há valores faltantes em nenhuma das quatro colunas. Por isso, não foi necessário remover ou preencher dados.

- Também não foram encontradas linhas completamente duplicadas.

## Distribuição das avaliações

- Existem 22.650 notas positivas e 1.536 negativas.

- Não há como dar nota zero. 

- A nota mais comum é '+1', com 13.760 ocorrências.

- A média é aproximadamente 1,46 e a mediana é 1.

- A menor nota é -10 e a maior é +10.

## Outliers

### Alguns usuários concentram muitas avaliações.

- O usuário 1 fez 490 avaliações e recebeu 398.

- Entre os usuários que receberam pelo menos uma avaliação, a mediana é 2 avaliações recebidas.

- Pelo critério do intervalo interquartil, mais de 11 avaliações recebidas é um valor alto, e 442 usuários passam desse limite.

- *Isso não significa que os dados estão errados, apenas que alguns usuários são mais avaliados que outros.

## Relações entre variáveis

- As avaliações vão de novembro de 2010 a janeiro de 2016.

- Em 2011, 1,95% das avaliações foram negativas; em 2014, foram 15,25%.

- Isso mostra que a proporção de notas negativas varia com o tempo (não explica o motivo da mudança).

- Também comparamos o total de avaliações recebidas por usuário com a quantidade de notas negativas recebidas.

- Por exemplo, o usuário 1 recebeu 398 avaliações, nenhuma negativa, enquanto o usuário 177 recebeu 198 avaliações, sendo 42 negativas. Ou seja, ter muitas avaliações não significa necessariamente receber muitas avaliações negativas.

## Conclusão

- A rede tem muito mais avaliações positivas do que negativas, e alguns usuários concentram mais avaliações que outros.

- Esses resultados ajudam a entender os dados antes de estudar conectividade, caminhos e ciclos negativos com os algoritmos de grafos.
