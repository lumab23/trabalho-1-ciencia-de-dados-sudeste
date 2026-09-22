# Dicionário da base tratada

Granularidade: um município do Sudeste por ano. Chave: `(codigo_municipio, ano)`.
CSV UTF-8 com separador vírgula e decimal ponto; Parquet com tipos preservados.
Ausência no CSV é campo vazio; no Parquet, nulo. Valores não são formatados como
moeda textual nem arredondados antes do cálculo.

| Variável | Tipo lógico | Unidade / origem / transformação |
|---|---|---|
| `codigo_municipio` | texto, 7 dígitos | `Cód.` no SIDRA e `Código Município Completo` na DTB |
| `municipio` | texto | `Nome_Município` da DTB |
| `codigo_uf` | texto, 2 dígitos | `UF` da DTB |
| `uf` | texto | Sigla derivada do código de UF da DTB |
| `estado` | texto | `Nome_UF` da DTB, validado contra o código |
| `regiao` | texto | Sudeste, segundo as UFs da DTB |
| `ano` | inteiro | Ano comum; 2020 documentado nos nomes originais do PIB e população |
| `pib_total_reais` | real | `PIB (Mil Reais)` × 1.000; reais correntes |
| `populacao` | inteiro | `População (Pessoas)`; pessoas, estimativa residente |
| `pib_per_capita_reais` | real | `pib_total_reais / populacao`; reais/pessoa |
| `impostos_reais` | real | `Impostos (Mil Reais)` × 1.000 |
| `va_agropecuaria_reais` | real | `VA da agropecuária (Mil Reais)` × 1.000 |
| `va_industria_reais` | real | `VA da indústria (Mil Reais)` × 1.000 |
| `va_servicos_reais` | real | `VA dos serviços (Mil Reais)` × 1.000 |
| `va_administracao_publica_reais` | real | `VA da administração pública (Mil Reais)` × 1.000 |

Os cinco campos econômicos auxiliares são preservados quando presentes. Seus
marcadores não numéricos e valores não finitos viram nulos auditados; negativos
permanecem com alerta. Nenhum valor é imputado. Os registros sem PIB/população
válidos para a fórmula são separados em `outputs/reports/registros_excluidos.csv`.

A classificação territorial é obtida da DTB fornecida, cuja edição não é informada.
Nem a quantidade atual de municípios do Brasil nem uma edição territorial distinta
são usadas para completar a base. As regiões geográficas imediatas/intermediárias
da DTB ficam preservadas nos originais e na etapa normalizada, mas não são necessárias
ao contrato de consumo da equipe.

Consulte [SIDRA 5938](https://sidra.ibge.gov.br/tabela/5938) para o conceito detalhado
de impostos e atividades e antes de somar serviços e administração pública. O projeto
mantém a correspondência exata com os rótulos recebidos; não calcula participações
setoriais, que pertencem à análise posterior. Não confunda reais correntes com reais constantes,
nem PIB por habitante com renda individual.
