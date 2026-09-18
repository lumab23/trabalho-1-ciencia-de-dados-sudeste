# Entrega de Amanda

Trabalho 1 de Ciência de Dados, T326, Universidade de Fortaleza.
Municípios do Sudeste, ES, MG, RJ e SP, com PIB e população de 2020.

## Arquivos principais

- `../../notebooks/contribuicoes/02_amanda.ipynb`: notebook executado, no caminho
  previsto pelo manifesto de integração de Luma.
- `amanda_secao_executada.pdf`: exportação das células, códigos, tabelas, gráfico
  e interpretações do notebook executado.
- `tabelas/`: quatro rankings, estatísticas e tabelas auxiliares em CSV.
- `../figures/amanda_histograma_pib_per_capita.png`: histograma em alta resolução.
- `amanda_introducao_metodologia.pptx`: quatro slides introdutórios editáveis,
  com notas do apresentador e referências documentais.
- `roteiro_dreamshaper.pdf`: roteiro de aproximadamente 2min30s e blocos para revisão.
- `roteiro_dreamshaper.md`: versão editável do mesmo documento em Markdown.
- `conferencia.json`: verificações numéricas, hash da base e versões das bibliotecas.
- `conferencia_slides.json`: verificações estruturais do PowerPoint.
- `entrega_amanda.zip`: pacote de entrega com a estrutura relativa do projeto.

## Tabelas

Os CSVs usam UTF-8, separador vírgula e ponto decimal, sem arredondamento prévio.
Importe `codigo_municipio` como texto. A unidade consta em cada ranking.

| Arquivo | Conteúdo |
|---|---|
| `top5_pib_total_reais.csv` | Cinco maiores PIBs totais |
| `bottom5_pib_total_reais.csv` | Cinco menores PIBs totais |
| `top5_pib_per_capita_reais.csv` | Cinco maiores PIBs per capita |
| `bottom5_pib_per_capita_reais.csv` | Cinco menores PIBs per capita |
| `estatisticas_pib_per_capita.csv` | Contagem, média, mediana, quartis e dispersão |
| `media_municipal_e_regional.csv` | Média municipal, totais e PIB per capita regional |
| `cobertura.csv` | Quantidade de municípios por UF, sem comparação econômica estadual |
| `auditoria_validade.csv` | Ausências, validade e exclusões por variável |
| `exclusoes.csv` | Registros inválidos; apenas cabeçalho nesta execução, pois não houve exclusões |
| `empates_rankings.csv` | Verificação de empates na quinta posição |
| `classes_histograma.csv` | Limites dos intervalos e frequências do histograma |

## Resultados conferidos

Há 1.668 municípios válidos, sem ausências ou exclusões adicionais. Não há empates
na quinta posição de nenhum ranking. A média simples é R$ 30.364,89 por pessoa,
a mediana é R$ 22.531,00 e o PIB per capita regional é R$ 44.406,19. Variância e
desvio padrão são populacionais, com `ddof=0`. O histograma tem 30 classes no
logaritmo decimal e preserva todos os valores válidos, inclusive os extremos.

O notebook passou pela execução sequencial em kernel novo e pela conferência
independente com `statistics`, interpolação de quartis, soma de totais e ordenação
de rankings. CSV e Parquet foram comparados numericamente. A contagem do histograma
fecha com a base e o hash do Parquet permaneceu inalterado. Os arquivos originais
do projeto e de Luma não foram modificados.

Os PDFs foram renderizados e inspecionados. A estrutura do PPTX foi validada e os
quatro slides foram renderizados pelo Quick Look do macOS para inspeção visual.
Não se afirma que houve abertura no Microsoft PowerPoint. A apresentação contém
textos e tabela nativos, não imagens achatadas de slides.

## Integração e reprodução

Luma deve usar `notebooks/contribuicoes/02_amanda.ipynb`, já indicado no
`integracao.json`. Os nomes globais da seção recebem o prefixo `am_` para reduzir
conflitos na integração. Nenhum arquivo original deve ser substituído para usar
a contribuição. O notebook encontra a raiz por caminhos relativos e lê o Parquet.

Além das dependências existentes do projeto, instale `matplotlib`. As versões
efetivamente utilizadas estão em `conferencia.json`. A execução desta entrega usou
Python 3.9.6 em ambiente isolado local; a preparação de Luma não foi reexecutada.

Com o ambiente do projeto ativado, execute a partir da raiz:

```bash
PYTHONPATH=src python -m sudeste.notebook notebooks/contribuicoes/02_amanda.ipynb
```

O executor existente gera `02_amanda_executado.ipynb` e HTML em `outputs/reports/`.
As tabelas e a figura são regravadas apenas nos caminhos de Amanda. O notebook
contém os próprios cálculos e textos e não depende dos scripts de autoria para rodar.
O pacote ZIP deve ser extraído sobre a raiz de uma cópia do projeto que já contenha
a base tratada e seus metadados; ele não duplica os dados de Luma.

## Pendências

- A edição da DTB permanece não identificada.
- Confirmar os campos efetivos e limites de caracteres do Dreamshaper.
- Confirmar ações extensionistas, público, participantes, datas e impactos apenas
  quando houver informações e evidências da equipe.
- Revisar com a equipe e integrar a seção com Luma e os slides com Luís.
- Ensaiar a fala para ajustar as pausas e o tempo real.

Os arquivos brutos e as auditorias intermediárias completas de Luma não estão
nesta cópia do repositório. A descrição da preparação baseia-se nos notebooks,
metadados e relatórios disponíveis. Não houve publicação no Dreamshaper, gravação
de vídeo ou execução das análises de Peter e Luís.
