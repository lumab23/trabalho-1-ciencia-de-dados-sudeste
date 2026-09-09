# Entrega das contribuições reais

Ainda não há notebooks de Amanda, Peter ou Luís. Este diretório é o ponto de entrega:

- Amanda: `02_amanda.ipynb`.
- Peter: `03_peter.ipynb`.
- Luís: `04_luis.ipynb`.

Cada notebook deve carregar `data/processed/sudeste_municipios.parquet` por caminho
relativo à raiz, usar somente variáveis documentadas e declarar dependências novas.
Deve conter objetivo, código, explicações e resultados realmente executados; não
usar caminhos pessoais nem depender de células executadas fora de ordem. Não
modificar a base tratada no arquivo; faça cópias em memória quando necessário.
Salve figuras sob `outputs/figures/` com nomes distintos para cada integrante.

Luma deve revisar as contribuições, ajustar a ordem editorial em `integracao.json`,
executar `python -m sudeste.integracao`, resolver eventuais conflitos e rodar
`python -m sudeste.notebook notebooks/00_trabalho_integrado.ipynb` em kernel novo.
O script remove saídas antigas no consolidado; resultados só reaparecem com execução.
Se um arquivo faltar, a consolidação para com uma mensagem e não gera um notebook
parcial com seções fictícias. Se o consolidado já existir, escolha outro destino
no manifesto para preservar a versão anterior. Revise texto, gráficos, fontes e
conclusões antes da exportação final para PDF. Slides e vídeo dependem de Luís.
