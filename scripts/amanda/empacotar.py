"""Valida os artefatos finais e empacota a contribuição, sem copiar a base de Luma."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import re
import sys
import nbformat
import pandas as pd
import fitz
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/amanda'
nb = nbformat.read(ROOT / 'notebooks/contribuicoes/02_amanda.ipynb', 4)
nbformat.validate(nb)
code = [c for c in nb.cells if c.cell_type == 'code']
assert [c.execution_count for c in code] == list(range(1, len(code) + 1))
assert not any(o.output_type == 'error' for c in code for o in c.outputs)
assert sum('image/png' in o.get('data', {}) for c in code for o in c.outputs) == 1
report = json.loads((OUT / 'conferencia.json').read_text())
assert report['status'] == 'aprovado' and report['n'] == 1668
assert hashlib.sha256((ROOT / 'data/processed/sudeste_municipios.parquet').read_bytes()).hexdigest() == report['sha256_base_parquet']
for name in ['top5_pib_total_reais', 'bottom5_pib_total_reais',
             'top5_pib_per_capita_reais', 'bottom5_pib_per_capita_reais']:
    table = pd.read_csv(OUT / 'tabelas' / (name + '.csv'))
    assert len(table) == 5
    assert not table[['municipio', 'uf', 'valor', 'unidade']].isna().any().any()
pdf = fitz.open(OUT / 'amanda_secao_executada.pdf')
pdf_text = '\n'.join(p.get_text() for p in pdf)
for expected in ['30.364,89', '22.531,00', '44.406,19', '101,62',
                 'Louveira', 'Francisco Badaró', 'Serra da Saudade',
                 'Top 5: PIB total', 'Bottom 5: PIB total', 'Top 5: PIB per capita',
                 'Bottom 5: PIB per capita', 'Conferências aprovadas']:
    assert expected in pdf_text, expected
assert sum(len(p.get_images()) for p in pdf) >= 1
# A imagem e cada bloco textual devem permanecer dentro da página.
for page in pdf:
    for block in page.get_text('dict')['blocks']:
        rect = fitz.Rect(block['bbox'])
        assert rect.x0 >= 0 and rect.y0 >= 0
        assert rect.x1 <= page.rect.width + 1 and rect.y1 <= page.rect.height + 1

with ZipFile(OUT / 'amanda_introducao_metodologia.pptx') as z:
    slides = [n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]
    assert len(slides) == 4
    for name in z.namelist():
        if name.endswith('.xml') or name.endswith('.rels'):
            etree.fromstring(z.read(name))

final = {'status': 'aprovado', 'python': sys.version.split()[0],
    'celulas_codigo_executadas': len(code), 'erros_notebook': 0,
    'paginas_pdf_secao': len(pdf),
    'paginas_pdf_roteiro': len(fitz.open(OUT / 'roteiro_dreamshaper.pdf')),
    'slides_editaveis': 4, 'tabelas_csv': len(list((OUT / 'tabelas').glob('*.csv'))),
    'pdf_contem_resultados_e_histograma': True,
    'renderizador_slides': 'Quick Look do macOS; inspeção visual dos 4 slides',
    'renderizador_pdf': 'PyMuPDF; inspeção visual de todas as páginas',
    'publicado_no_dreamshaper': False}
(OUT / 'validacao_final.json').write_text(json.dumps(final, ensure_ascii=False, indent=2))
files = [p for p in OUT.rglob('*') if p.is_file() and p.suffix != '.zip'
         and p.name != 'manifesto_sha256.json']
files += [ROOT / 'notebooks/contribuicoes/02_amanda.ipynb',
          ROOT / 'outputs/figures/amanda_histograma_pib_per_capita.png',
          ROOT / 'scripts/amanda/requirements-analise.txt']
manifest = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(files)}
(OUT / 'manifesto_sha256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
files.append(OUT / 'manifesto_sha256.json')
with ZipFile(OUT / 'entrega_amanda.zip', 'w', ZIP_DEFLATED) as z:
    for p in sorted(files):
        z.write(p, str(p.relative_to(ROOT)))
with ZipFile(OUT / 'entrega_amanda.zip') as z:
    assert z.testzip() is None
    for p, checksum in manifest.items():
        assert hashlib.sha256(z.read(p)).hexdigest() == checksum
print(json.dumps(final, ensure_ascii=False, indent=2))
print('ZIP validado:', len(files), 'arquivos')
