from pathlib import Path
from lxml import etree as E
from zipfile import ZipFile
import posixpath, json, re, hashlib

ROOT=Path(__file__).resolve().parent
PPTX=ROOT/'exports/light-theme-refinement_20261015_20261015_233059.pptx'
SOURCE=ROOT.parent/'鱼力无限-鱼搭网站路演-增强版-18页.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships','s':'http://www.w3.org/2000/svg'}
def norm(s):return re.sub(r'\s+','',s)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def target(part,rel):return rel.lstrip('/') if rel.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(part),rel))
def rels(z,part):return E.fromstring(z.read(posixpath.join(posixpath.dirname(part),'_rels',posixpath.basename(part)+'.rels')))

assert SOURCE.read_bytes()==(ROOT/'sources/source.pptx').read_bytes()
pages=[]
with ZipFile(PPTX) as z:
    main='ppt/presentation.xml';pres=E.fromstring(z.read(main));relationships={r.get('Id'):r for r in rels(z,main)}
    ordered=[target(main,relationships[s.get('{'+NS['r']+'}id')].get('Target')) for s in pres.findall('p:sldIdLst/p:sldId',NS)]
    assert len(ordered)==18
    assert len([p for p in z.namelist() if re.fullmatch(r'ppt/notesSlides/[^/]+\.xml',p)])==18
    for i,part in enumerate(ordered,1):
        r=E.fromstring(z.read(part));text=''.join(r.xpath('.//a:t/text()',namespaces=NS))
        svg=E.parse(str(ROOT/'authoring-svg-flat'/f'slide_{i:02}.svg'))
        wanted=''.join(''.join(x.itertext()) for x in svg.findall('.//s:text',NS))
        assert norm(text)==norm(wanted),(i,'text mismatch')
        assert '鱼力无限' in text and '小程序' not in text,(i,'identity')
        notes=[q for q in rels(z,part) if q.get('Type','').endswith('/notesSlide')]
        assert len(notes)==1
        nt=E.fromstring(z.read(target(part,notes[0].get('Target'))))
        note=''.join(nt.xpath('.//a:t/text()',namespaces=NS));assert note.strip()
        if i==5:
            # The replacement screenshot is placed whole, with no srcRect crop.
            assert len(r.findall('.//p:pic',NS))==1
            assert not r.findall('.//p:pic/p:blipFill/a:srcRect',NS)
        if i==6:
            for num in range(1,7):
                runs=[a for a in r.findall('.//a:r',NS) if a.find('a:t',NS) is not None and a.find('a:t',NS).text==str(num)]
                assert len(runs)==1,(i,num,'number run')
                assert runs[0].find('a:rPr/a:solidFill/a:srgbClr',NS).get('val')=='FFFFFF'
        if i==7:
            assert '宣传视频' in text and '演示视频' in text and text.count('视频待插入')==2
            assert not r.findall('.//a:videoFile',NS)
        pages.append({'page':i,'visible_characters':len(text),'text_matches_authoring':True,'notes_characters':len(note)})
    sz=pres.find('p:sldSz',NS)
    cm_per_px=int(sz.get('cx'))/1280/360000

source_copies=[]
for f in (ROOT/'sources').glob('0[1-7]-*.md'):
    original=ROOT.parents[1]/f.name
    assert sha(f)==sha(original)
    source_copies.append({'name':f.name,'sha256':sha(f)})
assert len(source_copies)==7
slots=[]
for x in [64,664]:slots.append({'left_cm':round(x*cm_per_px,3),'top_cm':round(220*cm_per_px,3),'width_cm':round(552*cm_per_px,3),'height_cm':round(310.5*cm_per_px,3),'aspect_ratio':'16:9'})
report={'status':'passed','slides':18,'notes':18,'source_unchanged':True,'source_sha256':sha(SOURCE),'output_sha256':sha(PPTX),'video_placeholders':slots,'copied_sources':source_copies,'pages':pages}
(ROOT/'validation/content-readback.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['pages','copied_sources']},ensure_ascii=False,indent=2))
