# Roteiro e textos para o Dreamshaper

Amanda - Trabalho 1 de Ciência de Dados - Universidade de Fortaleza

Este documento reúne a fala introdutória e os blocos de contextualização, objetivos,
metodologia e contribuições para revisão da equipe. Os textos usam o recorte municipal
do Sudeste em 2020 e a base preparada por Luma. Não foram publicados no Dreamshaper.

## Roteiro de aproximadamente 2 minutos e 30 segundos

Sugestão de ritmo: cerca de 135 palavras por minuto, com pausas nas trocas de slide.
O tempo é uma estimativa de leitura e deve ser ajustado em ensaio. Os marcadores de
tempo e os títulos dos blocos não fazem parte da fala.

### Slide 1 — Problema e objetivo — 0:00 a 0:35

Olá, eu sou a Amanda. Nosso trabalho parte da pergunta: “O Brasil é um país desigual?”.
Para investigar uma dimensão dessa questão, analisamos as diferenças de produção
econômica entre os municípios do Sudeste. O objetivo social é tornar os dados públicos
mais compreensíveis e contribuir para uma discussão informada sobre desigualdades
territoriais. Nesta etapa, observamos o tamanho da produção e a produção por habitante,
sem assumir que esses indicadores expliquem todas as condições de vida da população.

### Slide 2 — Recorte e fontes — 0:35 a 1:15

Nossa unidade de análise é o município. A base reúne mil seiscentos e sessenta e oito
municípios de Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo. O período
comum do PIB e da população é dois mil e vinte. Utilizamos os dados de PIB dos
Municípios, da tabela cinco mil novecentos e trinta e oito do SIDRA, e as estimativas
populacionais, da tabela seis mil quinhentos e setenta e nove. A Divisão Territorial
Brasileira fornece a identificação dos municípios. Todas essas fontes são do IBGE.

### Slide 3 — Preparação e método — 1:15 a 2:00

A Luma preparou a base utilizada nas análises. Ela padronizou os campos, cruzou os
arquivos pelos códigos municipais, selecionou o Sudeste e conferiu a compatibilidade
dos anos. Também converteu o PIB de mil reais para reais e calculou o PIB per capita,
dividindo o PIB municipal pela população. A documentação não registra perdas no
recorte nem valores ausentes na base final. Na minha seção, utilizo medidas
descritivas, rankings e um histograma. A variância e o desvio padrão usam divisor
populacional, pois descrevemos todos os municípios cobertos pela base. A média
simples dá o mesmo peso a cada município. Já o PIB per capita regional divide o
PIB total pela população total.

### Slide 4 — Limites da interpretação — 2:00 a 2:30

Precisamos manter alguns cuidados. O PIB per capita representa produção por habitante,
não a renda recebida por cada pessoa, e não revela sozinho a desigualdade dentro das
cidades. A edição da base territorial não foi identificada, o que permanece como
limitação. Além disso, nossos resultados se referem ao Sudeste em dois mil e vinte e
não permitem concluir, isoladamente, sobre todo o Brasil. A seguir, a Luma detalha
a preparação dos dados.

## Blocos adaptáveis para o Dreamshaper

Os nomes exatos dos campos e seus limites de caracteres não foram disponibilizados.
Os blocos abaixo podem ser adaptados após a conferência desses campos. Informações
sobre extensão dependem de confirmação e não devem ser preenchidas como fatos
com base apenas na análise de dados.

### Contextualização

O projeto parte da pergunta “O Brasil é um país desigual?” e investiga uma dimensão
econômica e territorial dessa questão por meio de dados municipais do Sudeste.
O recorte abrange Espírito Santo, Minas Gerais, Rio de Janeiro e São Paulo, com
PIB e estimativas populacionais de 2020. A análise de dados públicos permite
descrever diferenças no volume de produção e na produção por habitante, apoiando
uma discussão informada sobre disparidades entre municípios. O PIB per capita não
equivale à renda individual nem informa, sozinho, como os recursos se distribuem
entre moradores. As evidências produzidas dizem respeito ao recorte estudado, sem
generalização automática para o Brasil inteiro.

### Objetivo geral

Descrever as diferenças de PIB total e PIB per capita entre os municípios do
Sudeste em 2020, utilizando dados do IBGE e estatística descritiva, para contribuir
para a compreensão de uma dimensão territorial da desigualdade econômica.

### Objetivos específicos da contribuição de Amanda

- Contextualizar a pergunta-guia e explicitar fontes, período, unidades e limites.
- Calcular e interpretar medidas de tendência central e dispersão do PIB per capita.
- Identificar os cinco maiores e menores valores de PIB total e PIB per capita.
- Visualizar a distribuição municipal em histograma, preservando extremos válidos.
- Distinguir a média simples municipal do PIB per capita agregado do Sudeste.
- Comunicar os resultados e suas limitações em materiais acadêmicos acessíveis.

### Objetivo social

Favorecer a compreensão de indicadores públicos e a leitura crítica de disparidades
econômicas entre municípios. Este objetivo expressa a finalidade educativa do
trabalho. Sua realização junto a uma comunidade e eventuais efeitos sociais
dependem da confirmação de atividades e evidências pela equipe.

### Metodologia

Estudo quantitativo, descritivo e transversal, baseado em dados secundários do IBGE.
A unidade de análise é o município em 2020. A base tratada por Luma contém 1.668
municípios do Sudeste: 78 no Espírito Santo, 853 em Minas Gerais, 92 no Rio de
Janeiro e 645 em São Paulo. As fontes documentadas são as tabelas SIDRA 5938,
para PIB municipal, e 6579, para estimativas populacionais, além da DTB, para
identificação territorial. O ano de PIB e população foi identificado nos nomes
originais dos arquivos. A edição da DTB permanece desconhecida.

Luma realizou a padronização e os cruzamentos pelo código IBGE completo, converteu
valores monetários de mil reais para reais e calculou PIB per capita como PIB total
dividido pela população do mesmo ano. A documentação registra cobertura integral
do recorte fornecido, sem exclusões por cálculo inválido ou valores ausentes na
base final. A contribuição de Amanda utiliza essa base preservada e confere sua
cobertura e consistência antes das análises.

As estatísticas municipais atribuem peso igual a cada município. Variância e desvio
padrão são populacionais, com divisor N, e os quartis usam interpolação linear.
O PIB per capita regional é a soma dos PIBs dividida pela soma das populações.
Os rankings ordenam valores sem arredondamento prévio e usam código IBGE crescente
para desempates, mantendo cinco linhas por tabela. O histograma utiliza classes
definidas pela regra de Freedman-Diaconis aplicada ao logaritmo decimal dos valores
positivos, com eixo rotulado em reais por pessoa. Valores extremos válidos são
mantidos. Nesta base, não há exclusões adicionais nem valores não positivos fora
do histograma. As análises não permitem inferir causalidade nem medir, isoladamente,
a desigualdade de renda dentro dos municípios.

### Minhas contribuições

Minha contribuição nesta entrega reúne a contextualização da pergunta-guia, a
descrição das fontes e da metodologia e a análise descritiva do PIB per capita
municipal. A partir da base preparada por Luma, foram produzidas as medidas
estatísticas, quatro rankings e um histograma, acompanhados de interpretações e
conclusões parciais. A seção também diferencia a média simples dos municípios do
PIB per capita regional e explicita as limitações dos indicadores. Integram a
entrega o notebook executado, sua versão em PDF, tabelas em CSV, o gráfico em PNG,
slides introdutórios e este roteiro. A preparação dos dados e a integração do
trabalho são atribuições de Luma. Os textos para o Dreamshaper estão preparados
para revisão, sem publicação.

### Informações que dependem de confirmação

- Campos efetivos do Dreamshaper e respectivos limites de caracteres.
- Comunidade ou instituição parceira, quando houver, e problema identificado com ela.
- Público efetivamente atendido e critérios utilizados para identificá-lo.
- Atividades extensionistas realmente realizadas, locais, datas e duração.
- Participantes envolvidos e responsabilidades efetivamente desempenhadas.
- Evidências das atividades, retorno do público e resultados ou impactos observados.
- Edição da DTB, caso a informação possa ser recuperada na fonte fornecida.
- Revisão da equipe, prazo final, gravação e integração à apresentação completa.

Não há, nos arquivos consultados, evidências suficientes para afirmar que houve
ação extensionista, atendimento de público ou impacto social. O objetivo social
e os produtos acadêmicos não devem ser apresentados como comprovação dessas ações.
Nenhuma publicação ou gravação é afirmada nesta entrega.

## Base documental

Notebooks de preparação de Luma e arquivos do projeto: `data/processed/metadados.json`,
`docs/dicionario_dados.md`, `outputs/reports/qualidade.md` e `qualidade.json`.
Resultados conferidos em `notebooks/contribuicoes/02_amanda.ipynb`.
O documento de divisão de tarefas fornecido por Amanda orienta a distribuição
de responsabilidades da equipe.
