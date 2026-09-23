# Distribuição e síntese

Esta pasta contém `metricas_distribuicao.csv`, com assimetria e curtose de Fisher
para PIB total, população e PIB per capita nas escalas original e logarítmica.

O notebook correspondente é
`notebooks/contribuicoes/04_distribuicao_sintese.ipynb`. Os boxplots são gravados
em `outputs/figures/boxplots_distribuicao.png` e
`outputs/figures/boxplot_pib_per_capita_por_uf.png`.

Para recriar o notebook-fonte:

```bash
python scripts/distribuicao_sintese/criar_notebook.py
```
