# Parte de análises econômicas — Sudeste, 2020

Seção de análises econômicas do Trabalho 1.

## O que abrir

| Arquivo | Para que serve |
| --- | --- |
| [03_analises_economicas.ipynb](../../notebooks/contribuicoes/03_analises_economicas.ipynb) | Código comentado, tabelas, sete gráficos e conclusões parciais para o notebook do grupo. |
| [roteiro_apresentacao.md](roteiro_apresentacao.md) | O que falar em cada slide, em aproximadamente 2min30s, e respostas para possíveis perguntas. |
| [Gráficos](../figures/) | Os sete arquivos PNG, com nomes referentes ao conteúdo de cada gráfico. |

## O que sua parte cobre

- Valores Adicionados de Agropecuária, Indústria, Serviços e Administração Pública.
- Participações dos setores no VA total regional e estadual.
- Comparação de ES, MG, RJ e SP por PIB, população, PIB per capita e composição econômica.
- Matriz de correlação, com interpretação e complemento em log10.
- Dispersão entre PIB e população.
- Conclusões parciais e gráficos dos resultados.

## Como executar o notebook

Use a base Parquet que já existe no repositório. Na raiz do projeto:

```bash
python -m pip install -r requirements.txt -r scripts/analises_economicas/requirements.txt
```

Abra `notebooks/contribuicoes/03_analises_economicas.ipynb` no Jupyter ou VS Code e execute todas as células em ordem. As figuras e tabelas são geradas automaticamente. O arquivo da base não é alterado.

O `integracao.json` do grupo já indica o caminho correto dessa contribuição. A integração completa e a gravação do vídeo continuam sendo etapas coletivas.

## Dois arquivos de apoio

- `scripts/analises_economicas/requirements.txt`: bibliotecas adicionais necessárias para executar a análise.
- `outputs/analises_economicas/fontes/sidra_5938_metadados.json`: definição oficial dos setores usada para conferir que Serviços exclui Administração Pública.

## Conferência e limites

A análise usa 1.668 municípios de 2020. Os totais estaduais foram reconciliados e o PIB per capita estadual foi conferido pela média ponderada por população. Os percentuais setoriais somam 100% do VA total. PIB por habitante não representa renda individual, e correlação não demonstra causalidade.

A matriz logarítmica usa 1.666 municípios, pois Nilópolis/RJ e Águas de São Pedro/SP têm VA agropecuário zero. Eles permanecem nas demais análises. A edição da DTB não foi identificada pelo grupo.

As sete células de código foram executadas em ordem em um processo Python novo via IPython, com saídas registradas. O ambiente bloqueou sockets do kernel externo Jupyter, portanto esse modo de execução não foi testado aqui.

O histograma disponível na seção da estatística descritiva foi revisado: título, unidades, escala logarítmica e legenda estavam legíveis e identificados. A seção de distribuição e síntese ainda não estava na main consultada.
