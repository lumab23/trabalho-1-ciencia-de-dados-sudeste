// Exportador alternativo local: o runtime @oai/artifact-tool não está disponível.
import pptxgen from '/private/tmp/estatistica_descritiva-slides-build/node_modules/pptxgenjs/dist/pptxgen.cjs.js';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out = path.join(root, 'outputs/estatistica_descritiva');
const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'estatística descritiva';
pptx.subject = 'Introdução e metodologia - Trabalho 1 de Ciência de Dados';
pptx.title = 'O Brasil é um país desigual? - Municípios do Sudeste';
pptx.company = 'Universidade de Fortaleza';
pptx.lang = 'pt-BR';
pptx.theme = { headFontFace: 'Arial', bodyFontFace: 'Arial', lang: 'pt-BR' };
const C = { ink: '222A2C', teal: '146D7A', plum: '873D5F', grey: '526065', light: 'E5EFF0' };
const audit = [];

function text(slide, content, x, y, w, h, size = 22, extra = {}) {
  const opt = { x, y, w, h, fontFace: 'Arial', fontSize: size, color: C.ink,
    margin: 0, breakLine: false, valign: 'top', paraSpaceAfterPt: 8,
    ...extra };
  slide.addText(content, opt);
  audit.push({ slide: pptx._slides.length, text: content, ...opt });
}
function slide(title, number) {
  const s = pptx.addSlide();
  s.background = { color: 'FFFFFF' };
  text(s, title, .7, .5, 11.9, .95, 30, { bold: true, color: C.teal });
  text(s, `estatística descritiva · Trabalho 1 de Ciência de Dados · Sudeste, 2020`, .7, 7.02, 11.2, .2, 10, {color:C.grey});
  text(s, String(number), 12.15, 7.02, .4, .2, 10, {color:C.grey, align:'right'});
  return s;
}

let s = slide('O Brasil é um país desigual?', 1);
text(s, 'Diferenças econômicas entre os municípios do Sudeste', .7, 1.6, 11.5, 1.0, 32,
  { bold: true });
text(s, 'ES, MG, RJ e SP\nPIB e população de 2020', .7, 2.95, 10.9, .9, 25, {color:C.plum});
text(s, 'Objetivo', .7, 4.3, 10.9, .4, 20, {bold:true, color:C.teal});
text(s, 'Descrever diferenças de produção e de produção por habitante,\ncom dados públicos e estatística descritiva.', .7, 4.85, 11.7, .9, 23);
text(s, 'Finalidade social: contribuir para a leitura crítica das disparidades territoriais.',
  .7, 6.12, 11.7, .55, 18, {color:C.grey});
s.addNotes('Fala: 0:00 a 0:35. Apresentar a pergunta e o objetivo social como finalidade educativa, sem afirmar ação extensionista realizada. Fonte: README.md e documento de divisão de tarefas fornecido. O recorte não responde sozinho pelo Brasil inteiro.');

s = slide('Recorte e fontes dos dados', 2);
text(s, '1.668 municípios', .7, 1.62, 6, .6, 34, {bold:true});
text(s, 'ES 78     MG 853     RJ 92     SP 645', .7, 2.42, 11.9, .42, 23, {color:C.plum});
const rows = [
  ['Fonte IBGE', 'Informação utilizada', 'Referência'],
  ['SIDRA 5938', 'PIB municipal', '2020'],
  ['SIDRA 6579', 'População estimada', '2020'],
  ['DTB', 'Código, nome e UF', 'Edição não informada'],
];
s.addTable(rows, { x:.7, y:3.15, w:11.9, h:2.0, colW:[3.5,4.8,3.6], rowH:.5,
  fontFace:'Arial', fontSize:19, color:C.ink, margin:10,
  border:{type:'solid',color:'D9D9D9',pt:.6},
  autoPage:false, bold:false, fill:'FFFFFF',
  rowColor:['FFFFFF','FFFFFF','FFFFFF','FFFFFF'] });
text(s, 'Unidade de análise: um município em 2020.\nValores monetários em reais correntes de 2020.',
  .7, 5.65, 11.9, .9, 22);
s.addNotes('Fala: 0:35 a 1:15. Fonte: data/processed/metadados.json; outputs/reports/qualidade.md; notebooks/01_preparacao_dados_executado.ipynb. PIB: tabela5938_2020.csv.xz. População: tabela6579_2020.csv.xz. DTB: RELATORIO_DTB_BRASIL_MUNICIPIO.csv, edição desconhecida. Ano econômico e populacional identificado nos nomes originais por preparação dos dados. Referências institucionais: https://sidra.ibge.gov.br/tabela/5938 e https://sidra.ibge.gov.br/tabela/6579. Os arquivos não foram substituídos por versões atuais.');

s = slide('Da base preparada à análise descritiva', 3);
text(s, 'Preparação dos dados', .7, 1.65, 5.65, .45, 23, {bold:true,color:C.teal});
text(s, 'Cruzamento por código IBGE\nRecorte ES, MG, RJ e SP\nConversão de mil reais para reais\nPIB per capita = PIB ÷ população',
  .7, 2.38, 5.65, 2.1, 21, {breakLine:false, paraSpaceAfterPt:16});
text(s, 'Análises de estatística descritiva', 7.0, 1.65, 5.63, .45, 23, {bold:true,color:C.plum});
text(s, 'Medidas descritivas\nTop 5 e Bottom 5\nHistograma em escala logarítmica\nInterpretação e limites',
  7.0, 2.38, 5.63, 2.1, 21, {paraSpaceAfterPt:16});
text(s, 'Variância e desvio padrão populacionais: divisor N.\nMédia municipal: pesos iguais. PIB per capita regional: PIB total ÷ população total.',
  .7, 5.2, 11.9, 1.2, 20, {color:C.grey});
s.addNotes('Fala: 1:15 a 2:00. Preparação atribuída a preparação dos dados. A documentação registra 1.668 municípios e nenhuma perda ou ausência na base final. estatística descritiva mantém a base original e confere a fórmula. Quantis com interpolação linear; ddof=0 descreve a população municipal coberta. Rankings sobre valores sem arredondamento e desempate por código IBGE crescente. Extremos preservados. Histograma: Freedman-Diaconis no log10, 30 classes, 1.668 valores positivos, zero exclusões para o log. Fonte: notebooks/contribuicoes/02_estatistica_descritiva.ipynb e outputs/estatistica_descritiva/conferencia.json.');

s = slide('Limites da interpretação', 4);
const limits = [
  ['PIB total', 'Expressa o volume da produção econômica municipal.'],
  ['PIB per capita', 'Expressa produção por habitante. Não equivale à renda individual\nnem revela sozinho a desigualdade dentro do município.'],
  ['Alcance territorial e temporal', 'Resultados do Sudeste em 2020. A conclusão sobre todo o Brasil\nexige evidências adicionais. A edição da DTB permanece desconhecida.'],
];
let yy = 1.65;
for (const [label, detail] of limits) {
  text(s, label, .7, yy, 11.9, .42, 22, {bold:true,color:C.teal});
  text(s, detail, .7, yy+.57, 11.9, .9, 21);
  yy += 1.65;
}
s.addNotes('Fala: 2:00 a 2:30. Destacar que a desigualdade entre municípios é distinta da desigualdade entre pessoas. A base não informa a distribuição da renda dos moradores. Não inferir causas. Um único ano não permite estudar evolução temporal. Edição desconhecida da DTB é uma limitação de compatibilidade histórica. Encerrar passando a fala para preparação dos dados, conforme sequência sugerida no planejamento. Fonte: dicionário, metadados e seção de limitações do notebook de estatística descritiva.');

await pptx.writeFile({fileName:path.join(out,'introducao_metodologia.pptx')});
fs.mkdirSync(path.join(root,'tmp/estatistica_descritiva'), {recursive:true});
fs.writeFileSync(path.join(root,'tmp/estatistica_descritiva/slides_geometry.json'), JSON.stringify(audit,null,2));
console.log('PowerPoint exportado: 4 slides com texto e tabela editáveis.');
