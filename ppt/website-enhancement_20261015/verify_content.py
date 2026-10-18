from pathlib import Path
from lxml import etree as ET
from zipfile import ZipFile
import hashlib
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parent
PPTX = ROOT / 'exports/website-enhancement_20261015_20261015_222739.pptx'
ORIGINAL = Path('/Users/yaopinxin/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_ajtjclpz12ut22_f42a/msg/file/2026-10/鱼搭 · AI电子衣橱小程序项目路演(3).pptx')
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'rel': 'http://schemas.openxmlformats.org/package/2006/relationships',
      'svg': 'http://www.w3.org/2000/svg'}

def normalized(s):
    return re.sub(r'\s+', '', s)

def resolve(part, target):
    return target.lstrip('/') if target.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part), target))

def relationships(z, part):
    name = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    return ET.fromstring(z.read(name)) if name in z.namelist() else []

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

plan = json.loads((ROOT / 'page_plan.json').read_text())['pages']
results = []
with ZipFile(PPTX) as z:
    pres_part = 'ppt/presentation.xml'
    pres = ET.fromstring(z.read(pres_part))
    rels = {r.get('Id'): r for r in relationships(z, pres_part)}
    ordered_parts = [resolve(pres_part, rels[s.get('{'+NS['r']+'}id')].get('Target'))
                     for s in pres.findall('p:sldIdLst/p:sldId', NS)]
    notes_parts = [p for p in z.namelist() if re.fullmatch(r'ppt/notesSlides/[^/]+\.xml', p)]
    assert len(ordered_parts) == len(plan) == len(notes_parts) == 18
    for i, (part, page) in enumerate(zip(ordered_parts, plan), 1):
        svg_name = page.get('svg', f"slide_{page['source_slide']:02}.svg")
        svg = ET.parse(str(ROOT / 'authoring-svg-flat' / svg_name))
        expected = normalized(''.join(''.join(t.itertext()) for t in svg.findall('.//svg:text', NS)))
        slide = ET.fromstring(z.read(part))
        actual = normalized(''.join(slide.xpath('.//a:t/text()', namespaces=NS)))
        note_rels = [r for r in relationships(z, part) if r.get('Type', '').endswith('/notesSlide')]
        assert len(note_rels) == 1, (i, 'missing notes relationship')
        note_part = resolve(part, note_rels[0].get('Target'))
        note = ET.fromstring(z.read(note_part))
        note_text = ''.join(note.xpath('.//a:t/text()', namespaces=NS))
        assert note_text.strip(), (i, 'empty notes')
        assert actual == expected, (i, 'visible text differs', expected, actual)
        assert '鱼力无限' in actual, (i, 'team not found')
        assert '小程序' not in actual, (i, 'old product positioning in slide')
        assert '小程序' not in note_text.replace('不是小程序或概念界面', ''), (i, 'old product positioning in notes')
        assert '鱼搭开发组' not in actual + note_text, (i, 'old team name')
        results.append({'page': i, 'slide_part': part, 'authoring_svg': svg_name,
                        'text_matches_authoring': True, 'notes_part': note_part,
                        'notes_characters': len(note_text), 'visible_text': actual})

original_hash = sha(ORIGINAL)
assert original_hash == sha(ROOT / 'sources/source.pptx'), 'Original PPT differs from source copy'
source_docs = []
for copy in (ROOT / 'sources').glob('*.md'):
    matches = list((ROOT.parents[1]).glob(copy.name))
    assert len(matches) == 1, ('source not found', copy.name, matches)
    assert sha(copy) == sha(matches[0]), ('source copy differs', copy.name)
    source_docs.append({'name': copy.name, 'sha256': sha(copy), 'copy_verified': True})

report = {'status': 'passed', 'slide_count': len(results), 'notes_count': len(results),
          'source_original_unchanged': True, 'source_pptx_sha256': original_hash,
          'output_sha256': sha(PPTX), 'copied_documents': source_docs, 'pages': results}
(ROOT / 'validation/content-readback.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print(json.dumps({k: v for k, v in report.items() if k != 'pages'}, ensure_ascii=False, indent=2))
