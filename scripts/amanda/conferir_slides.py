"""Confere PPTX e prepara cópias de um slide para renderização pelo Quick Look."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import io
import json
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
PPTX = ROOT / 'outputs/amanda/amanda_introducao_metodologia.pptx'
BUILD = ROOT / 'tmp/amanda/slides_qa'
BUILD.mkdir(parents=True, exist_ok=True)
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

with ZipFile(PPTX) as z:
    parts = {n: z.read(n) for n in z.namelist()}
types = etree.fromstring(parts['[Content_Types].xml'])
# PptxGenJS lista masters não emitidos: remover somente declarações órfãs.
removed = []
for element in list(types):
    name = element.get('PartName')
    if name and name.lstrip('/') not in parts:
        removed.append(name)
        types.remove(element)
parts['[Content_Types].xml'] = etree.tostring(types, xml_declaration=True, encoding='UTF-8', standalone=True)


def save(path, content):
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in content.items():
            z.writestr(name, data)


save(PPTX, parts)
presentation = etree.fromstring(parts['ppt/presentation.xml'])
ids = presentation.find('p:sldIdLst', NS)
assert len(ids) == 4
evidence = {'slides': 4, 'orphan_content_types_removed': removed,
            'native_text_shapes': 0, 'native_tables': 0, 'notes': 0}
for index in range(1, 5):
    slide = etree.fromstring(parts[f'ppt/slides/slide{index}.xml'])
    evidence['native_text_shapes'] += len(slide.findall('.//p:sp/p:txBody', NS))
    evidence['native_tables'] += len(slide.findall('.//a:tbl', NS))
    assert f'ppt/notesSlides/notesSlide{index}.xml' in parts
    evidence['notes'] += 1
    # A prévia usa o mesmo XML do slide final, sem redesenhar o conteúdo.
    single = dict(parts)
    pres = etree.fromstring(parts['ppt/presentation.xml'])
    seq = pres.find('p:sldIdLst', NS)
    for i, element in enumerate(list(seq)):
        if i != index - 1:
            seq.remove(element)
    single['ppt/presentation.xml'] = etree.tostring(pres, xml_declaration=True,
        encoding='UTF-8', standalone=True)
    save(BUILD / f'slide_{index}.pptx', single)

geometry = json.loads((ROOT / 'tmp/amanda/slides_geometry.json').read_text())
assert all(g['x'] >= 0 and g['y'] >= 0 and g['x'] + g['w'] <= 13.334
           and g['y'] + g['h'] <= 7.5 for g in geometry)
evidence['text_boxes_inside_slide'] = True
(ROOT / 'outputs/amanda/conferencia_slides.json').write_text(
    json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(evidence, ensure_ascii=False))
