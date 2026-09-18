"""Exporta as células e saídas executadas e o documento de fala para PDF."""
from pathlib import Path
import base64
import io
import re
import textwrap
from html import escape

import nbformat
import mistune
from bs4 import BeautifulSoup
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, Preformatted, PageBreak, KeepTogether,
)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/amanda'
WIDTH = A4[0] - 88
FONT_DIR = Path(matplotlib.get_data_path()) / 'fonts/ttf'
for name, filename in [('Body', 'DejaVuSans.ttf'), ('BodyBold', 'DejaVuSans-Bold.ttf'),
                       ('Mono', 'DejaVuSansMono.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('Body', normal='Body', bold='BodyBold',
                             italic='Body', boldItalic='BodyBold')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('BodyPT', fontName='Body', fontSize=9.2, leading=13.3,
    spaceAfter=7, textColor=colors.HexColor('#222222'), splitLongWords=True))
styles.add(ParagraphStyle('TablePT', parent=styles['BodyPT'], fontSize=7.6,
    leading=10, spaceAfter=0))
styles.add(ParagraphStyle('SmallPT', parent=styles['BodyPT'], fontSize=7.4, leading=10))
for level, size in [(1, 21), (2, 14), (3, 11)]:
    styles.add(ParagraphStyle(f'H{level}PT', fontName='BodyBold', fontSize=size,
        leading=size * 1.25, spaceBefore=12 if level > 1 else 0,
        spaceAfter=9, keepWithNext=True, textColor=colors.HexColor('#155E6A')))
styles.add(ParagraphStyle('CodePT', fontName='Mono', fontSize=6.8, leading=9.4,
    spaceBefore=4, spaceAfter=9, backColor=colors.HexColor('#F2F5F5'),
    borderPadding=5))
markdown = mistune.create_markdown(plugins=['table'])


def inline(node):
    value = ''.join(str(c) for c in node.contents)
    value = re.sub(r'<code>(.*?)</code>', r'<font name="Mono">\1</font>', value, flags=re.S)
    value = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', value, flags=re.S)
    value = value.replace('<strong>', '<b>').replace('</strong>', '</b>')
    value = value.replace('<em>', '<i>').replace('</em>', '</i>')
    return value


def table_from_html(tag):
    rows = []
    for tr in tag.find_all('tr'):
        row = [Paragraph(escape(td.get_text(' ', strip=True)), styles['TablePT'])
               for td in tr.find_all(['th', 'td'])]
        if row:
            rows.append(row)
    n = len(rows[0])
    labels = [cell.get_text(' ', strip=True) for cell in tag.find('tr').find_all(['th', 'td'])]
    if labels == ['Pos.', 'Município', 'UF', 'Valor', 'Unidade']:
        fractions = [.075, .285, .055, .265, .32]
    elif n == 3:
        fractions = [.43, .29, .28]
    elif n == 2:
        fractions = [.48, .52]
    elif n == 6:
        fractions = [.27, .13, .17, .17, .13, .13]
    else:
        fractions = [1 / n] * n
    total = sum(fractions)
    t = Table(rows, colWidths=[WIDTH * f / total for f in fractions],
              repeatRows=1, hAlign='LEFT', splitByRow=0)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DDECEE')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F6F8F8')]),
        ('GRID', (0, 0), (-1, -1), .35, colors.HexColor('#D9D9D9')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6), ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return [t, Spacer(1, 9)]


def html_flow(html):
    soup = BeautifulSoup(html, 'html.parser')
    result = []
    for node in soup.children:
        name = getattr(node, 'name', None)
        if not name:
            continue
        if name == 'table':
            result.extend(table_from_html(node))
        elif name in ['h1', 'h2', 'h3', 'h4']:
            result.append(Paragraph(inline(node), styles[f'H{min(int(name[1]), 3)}PT']))
        elif name in ['ul', 'ol']:
            for li in node.find_all('li', recursive=False):
                result.append(Paragraph('- ' + inline(li), styles['BodyPT']))
        elif name == 'p':
            result.append(Paragraph(inline(node), styles['BodyPT']))
        elif name == 'div':
            result.extend(html_flow(str(node))) if not node.find('div') else None
    return result


def md_flow(text):
    return html_flow(markdown(text))


def footer(canvas, doc):
    canvas.setFont('Body', 7)
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.drawString(44, 25, 'Amanda - T326 - Sudeste - 2020')
    canvas.drawRightString(A4[0] - 44, 25, str(doc.page))


def build_pdf(path, story, title):
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=44, leftMargin=44,
        topMargin=38, bottomMargin=42, title=title, author='Amanda').build(
        story, onFirstPage=footer, onLaterPages=footer)


def export_notebook():
    original = ROOT / 'notebooks/contribuicoes/02_amanda_executado.ipynb'
    notebook = nbformat.read(original, as_version=4)
    nbformat.validate(notebook)
    counts = [c.execution_count for c in notebook.cells if c.cell_type == 'code']
    assert counts == list(range(1, len(counts) + 1))
    assert not any(o.output_type == 'error' for c in notebook.cells
                   for o in c.get('outputs', []))
    # O nome contratado na integração recebe a versão efetivamente executada.
    nbformat.write(notebook, ROOT / 'notebooks/contribuicoes/02_amanda.ipynb')
    story = []
    for cell in notebook.cells:
        if cell.cell_type == 'markdown':
            if cell.source.startswith(('## Estatística', '## Conclusões')):
                story.append(PageBreak())
            if cell.source.startswith('## Referências'):
                story.append(KeepTogether(md_flow(cell.source)))
            else:
                story.extend(md_flow(cell.source))
        elif cell.cell_type == 'code':
            story.append(Paragraph(f'Python - célula executada {cell.execution_count}', styles['SmallPT']))
            wrapped = '\n'.join('\n'.join(textwrap.wrap(line, width=105,
                subsequent_indent='    ', replace_whitespace=False,
                drop_whitespace=False)) if line else '' for line in cell.source.splitlines())
            story.append(Preformatted(wrapped, styles['CodePT']))
            for out in cell.outputs:
                if out.output_type == 'stream':
                    text = out.text
                    # Nenhum stderr é omitido silenciosamente.
                    story.append(Paragraph(escape(text).replace('\n', '<br/>'), styles['SmallPT']))
                elif out.output_type in ['display_data', 'execute_result']:
                    data = out.data
                    if 'text/html' in data:
                        story.extend(html_flow(data['text/html']))
                    elif 'text/markdown' in data:
                        story.extend(md_flow(data['text/markdown']))
                    elif 'image/png' in data:
                        raw = io.BytesIO(base64.b64decode(data['image/png']))
                        picture = Image(raw)
                        ratio = picture.imageHeight / picture.imageWidth
                        picture.drawWidth, picture.drawHeight = WIDTH, WIDTH * ratio
                        story.append(picture)
                        story.append(Spacer(1, 8))
                    elif 'text/plain' in data:
                        story.append(Paragraph(escape(data['text/plain']), styles['SmallPT']))
    build_pdf(OUT / 'amanda_secao_executada.pdf', story,
              'Amanda - Seção executada do Trabalho 1 de Ciência de Dados')


def export_document():
    text = (OUT / 'roteiro_dreamshaper.md').read_text(encoding='utf-8')
    # Mudanças de página deliberadas mantêm o roteiro e os blocos separados.
    parts = re.split(r'(?=^## Blocos adaptáveis|^### Metodologia|^### Informações)', text, flags=re.M)
    story = []
    for i, part in enumerate(parts):
        if i:
            story.append(PageBreak())
        story.extend(md_flow(part))
    build_pdf(OUT / 'roteiro_dreamshaper.pdf', story,
              'Amanda - Roteiro e textos para o Dreamshaper')


if __name__ == '__main__':
    export_notebook()
    export_document()
    print('PDFs exportados a partir do notebook executado e do documento Markdown.')
