# Registro da entrega — 08/09/2026

Pasta: `/Users/lbca/Documents/Projects/trabalho-1-ciencia-de-dados-sudeste`.
Sistema identificado: macOS (Darwin), conta `/Users/lbca`; pasta real encontrada:
`Documents/Projects`. Nenhuma pasta de projeto existente foi sobrescrita.

## Executado

- Ambiente virtual local instalado com Python 3.14.6. Versões em `requirements-lock.txt`.
- Download dos três IDs do professor via gdown; originais preservados, com hashes e histórico.
- Inspeção do conteúdo CSV/XZ e dos nomes originais do Drive.
- Pipeline com dados reais de 2020; CSV e Parquet exportados e relidos.
- Suíte pytest: **43 aprovados, 0 falhas, 0 erros, 0 ignorados**, conforme `testes.xml`.
- Notebook: **9 células de código executadas, 0 saídas de erro**, formato nbformat validado.
- HTML do notebook executado gerado para leitura.
- `pip check`: `No broken requirements found.`
- Repositório Git inicializado localmente, sem remoto e sem publicação.

## Dados efetivamente utilizados

| Fonte | Nome original | Referência |
|---|---|---|
| PIB | tabela5938_2020.csv.xz | 2020, nome confirmado no Drive |
| População | tabela6579_2020.csv.xz | 2020, nome confirmado no Drive |
| DTB | RELATORIO_DTB_BRASIL_MUNICIPIO.csv | Edição não informada |

Todos os arquivos têm 5.570 registros. O recorte fornecido pela DTB tem 1.668
municípios, todos presentes na saída: ES 78, MG 853, RJ 92, SP 645. Não houve
perdas de cruzamento, exclusões por cálculo inválido, duplicidades, divergências
de nomes ou valores ausentes na base final.

## Impedimentos resolvidos e limitação persistente

A instalação e o download inicialmente falharam por DNS no ambiente restrito;
a repetição com acesso autorizado funcionou. O kernel Jupyter inicialmente não
pôde abrir portas locais (`PermissionError: Operation not permitted`); a execução
com permissão adequada funcionou. O runner também encerra explicitamente o kernel.

A edição da DTB continua desconhecida. Não se atribuiu 2020 a ela, não se
substituíram fontes e não se inferiu equivalência histórica de limites municipais.

## Pendências da equipe

Amanda, Peter e Luís ainda precisam entregar suas análises e notebooks reais.
`integracao.json` e `src/sudeste/integracao.py` preparam a reunião posterior das
contribuições. O procedimento foi testado com fixtures explicitamente artificiais,
sem criar resultados econômicos. Não há notebook final da equipe, slides, vídeo
ou PDF final. Luma deverá revisar a integração e executar o conjunto completo após
receber as contribuições.
