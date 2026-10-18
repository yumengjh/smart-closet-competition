"""Apply the user-confirmed native-deck revision; immutable source.pptx is untouched."""
from pathlib import Path
import copy,json,shutil
import xml.etree.ElementTree as E
from PIL import Image

ROOT=Path(__file__).resolve().parent
SVGS=ROOT/'authoring-svg-flat'
S='http://www.w3.org/2000/svg'
E.register_namespace('',S)
NS={'s':S}
FAMILY='Microsoft YaHei, Arial, PingFang SC, sans-serif'
COLORS={
 '#EFF6FF':'#F7F8FA','#1E3A8A':'#25262B','#2563EB':'#1F5C45',
 '#60A5FA':'#1F5C45','#93C5FD':'#DCEAE2','#BFDBFE':'#DCEAE2',
 '#94A3B8':'#666B76','#64748B':'#666B76','#475569':'#666B76',
 '#6B7280':'#666B76','#FB7185':'#1F5C45','#FBBF24':'#EEF6F1',
 '#34D399':'#EEF6F1','#A855F7':'#1F5C45','#F97316':'#1F5C45',
 '#3B5CAA':'#626774','#DEE0E3':'#E8E9EE','#1D4ED8':'#1F5C45',
 '#DBEAFE':'#DCEAE2','#000000':'#25262B','#767171':'#666B76',
 '#4472C4':'#1F5C45','#ED7D31':'#1F5C45','#70AD47':'#666B76',
 '#B4C7E7':'#F7F8FA','#5B9BD5':'#666B76','#595959':'#666B76',
 '#404040':'#25262B','#B48C14':'#956516',
}

def tag(n):return '{'+S+'}'+n
def load(n):return E.parse(SVGS/f'slide_{n:02}.svg').getroot()
def group(root,id):
 x=root.find(f'.//s:g[@id="{id}"]',NS)
 if x is None:raise ValueError(id)
 return x
def txt(root,id,words,size=None,fill=None):
 g=group(root,id);t=g.find('.//s:text',NS)
 if t is None:raise ValueError(id+' no text')
 for c in list(t):t.remove(c)
 t.text=None
 for k in ('data-pptx-text-model','data-paragraph-line-height'):t.attrib.pop(k,None)
 if size:t.set('font-size',str(size))
 if fill:t.set('fill',fill)
 if isinstance(words,str):t.text=words
 else:
  fs=float(t.get('font-size','20'));frame=g.get('data-pptx-frame')
  y=float(frame.split()[1])+fs*1.1 if frame else float(t.get('y'))
  t.set('y',str(round(y,3)))
  for i,line in enumerate(words):
   E.SubElement(t,tag('tspan'),{'x':t.get('x'),'y':str(round(y+i*fs*1.5,3))}).text=line
 return t
def replace_picture(root,id,name):
 g=group(root,id);x,y,w,h=map(float,g.get('data-pptx-frame').split())
 for child in list(g):g.remove(child)
 E.SubElement(g,tag('image'),{'href':'../images/'+name,'x':str(x),'y':str(y),'width':str(w),'height':str(h),'preserveAspectRatio':'xMidYMid slice'})
def remove(root,id):
 target=group(root,id)
 for p in root.iter():
  if target in list(p):p.remove(target);return
def new_group(root,id,x,y,w,h):return E.SubElement(root,tag('g'),{'id':id,'data-pptx-bounds':f'{x} {y} {w} {h}'})
def native_text(g,x,y,text,size=20,fill='#25262B',weight=None):
 a={'x':str(x),'y':str(y),'font-size':str(size),'fill':fill}
 if weight:a['font-weight']=weight
 E.SubElement(g,tag('text'),a).text=text
def footer(root,num,source=''):
 if num==4:
  txt(root,'shape-30','鱼力无限 / 项目立意',size=16)
  txt(root,'shape-31','04',size=16)
  return
 g=new_group(root,'yuda-footer',64,671,1152,32)
 E.SubElement(g,tag('line'),{'x1':'64','y1':'672','x2':'1216','y2':'672','stroke':'#E8E9EE','stroke-width':'1'})
 native_text(g,64,696,'鱼力无限 / 鱼搭 · AI 数字衣柜网站',14,'#666B76')
 if source:native_text(g,474,696,source,14,'#666B76')
 native_text(g,1184,696,f'{num:02}',14,'#666B76')
def theme(root,page):
 root.set('font-family',FAMILY)
 for e in root.iter():
  for k in ('fill','stroke','stop-color','data-pptx-fg','data-pptx-bg'):
   v=e.get(k)
   if v in COLORS:e.set(k,COLORS[v])
  if 'font-family' in e.attrib:e.set('font-family',FAMILY)
 if page==4:
  for e in list(root):
   if e.tag==tag('image'):root.remove(e)
  root.insert(1,E.Element(tag('rect'),{'x':'0','y':'0','width':'1280','height':'720','fill':'#F7F8FA'}))
  for e in root.findall('.//s:text',NS):
   e.set('fill','#25262B' if float(e.get('font-size','20'))>=26 else '#666B76')
  for id in ('shape-2','shape-28'):
   group(root,id).find('.//s:text',NS).set('fill','#1F5C45')
  remove(root,'shape-33')
 if page==6:
  for e in list(root):
   if e.tag==tag('rect') and e.get('width')=='1280':e.set('fill','#F7F8FA')
  # An imported page background may be a raster/pattern. A native opaque field wins.
  pos=1 if len(root) and root[0].tag==tag('defs') else 0
  root.insert(pos,E.Element(tag('rect'),{'x':'0','y':'0','width':'1280','height':'720','fill':'#F7F8FA'}))
  for t in root.findall('.//s:text',NS):t.set('fill','#25262B' if float(t.get('font-size','20'))>=24 else '#666B76')

# Archive the seven inputs by copying, never moving.
for p in ROOT.parents[1].glob('0[1-7]-*.md'):shutil.copy2(p,ROOT/'sources'/p.name)
approval=ROOT/'修订方案.md'
approval.write_text(approval.read_text().replace('（待确认）','（已确认）')+'\n确认记录：用户于本轮回复「按这个方案直接完成」。\n')

# Screenshot derivatives only crop the private sidebar out; originals stay in reference/.
for source,dest in [('website-wardrobe-desktop.png','web-wardrobe.png'),('website-workspace-desktop.png','web-workspace.png')]:
 im=Image.open(ROOT/'reference'/source)
 im.crop((224,64,im.width,im.height)).save(ROOT/'images'/dest)

pages={n:load(n) for n in range(1,17)}
for n,r in pages.items():theme(r,n)

r=pages[1]
txt(r,'shape-3','AI 数字衣柜 · Web 网站')
txt(r,'shape-5',['让已有衣物，','成为每天的选择。'],size=28)
txt(r,'shape-7','参赛团队：鱼力无限　|　网页作品路演')
# Use the website's own public login illustration as the cover asset.
art=Path('/Users/yaopinxin/project/smart-closet/public/illustrations/yuda-login-light.svg')
shutil.copy2(art,ROOT/'images'/'website-login-illustration.svg')
replace_picture(r,'shape-2','website-login-illustration.svg')

r=pages[2]
for id,words in {'shape-8':'照片分散 · 缺少决策依据','shape-12':'入柜 · 推荐 · 组合台 · OOTD','shape-16':'可解释推荐 · 本地检索','shape-20':'Web · 本地模型 · 持久任务','shape-24':'用户验证 · 订阅与额度','shape-28':'鱼力无限 · 作品与规划'}.items():txt(r,id,words)

r=pages[3]
txt(r,'shape-4',['照片分散、灵感难落地，','出门前仍然反复选择那几件。'],size=22,fill='#DCEAE2')
txt(r,'shape-8',['今天的场合和天气，','适合穿什么？'])
txt(r,'shape-12',['衣物多，难以记忆、','查找和整理。'])
txt(r,'shape-16',['收藏了穿搭灵感，','却难用自己的衣物还原。'])

r=pages[4]
txt(r,'shape-3','把衣柜变成决策资源。',size=42)
txt(r,'shape-4','从真实衣物出发，让每次选择都有依据。',size=24)
txt(r,'shape-28','让更多已有衣物进入日常；效果仍需用户验证。',size=24,fill='#1F5C45')

r=pages[5]
txt(r,'shape-3',['拍照入柜，','在网站里管理自己的衣橱'],size=44)
replace_picture(r,'shape-4','web-wardrobe.png')
txt(r,'shape-5','批量上传 → 后台处理 → 核对入柜 → 进入真实衣柜',size=20)
group(r,'shape-5').set('transform','translate(0 -35)')

r=pages[6]
txt(r,'shape-2','OOTD 为效果预览，不承诺真实尺码合身或衣物细节完全一致。',size=18)

r=pages[7]
txt(r,'shape-2','浏览器里，把衣柜用起来')
txt(r,'shape-5','我的衣柜：字段、语义与图像检索',size=18)
txt(r,'shape-7','组合台：推荐、编辑与保存搭配',size=18)
txt(r,'shape-21','网站实际页面截图 · 2026-10-15 · 已裁去账户栏',size=16)
replace_picture(r,'shape-4','web-wardrobe.png')
replace_picture(r,'shape-6','web-workspace.png')

r=pages[8]
txt(r,'shape-2','从用户问题，到可解释的实现')
txt(r,'shape-3','03 · 创新设计 / 机制与用户价值')
texts=r.findall('.//s:g[@id="shape-4"]/s:text',NS)
cells=['维度','用户遇到的问题','鱼搭的实现机制','图片处理','上传与耗时处理混在一起','持久任务，提交后查看状态','图像可靠性','复杂背景、属性猜测难确认','本地抠图 + 属性证据与人工核对','推荐选择','不知道为什么，也总是重复','规则解释 + 曝光均衡 + 可恢复反馈','执行与成本','耗时任务与生成结果不确定','授权/回执/额度快照，未知不盲重试']
assert len(texts)==len(cells)
for t,words in zip(texts,cells):t.text=words
icon=ROOT/'icons/imported/flat_slide_08_ill01.svg'
it=E.parse(icon)
for e in it.getroot().iter():
 for k in ('fill','stroke'):
  if e.get(k) in COLORS:e.set(k,COLORS[e.get(k)])
it.write(icon,encoding='utf-8',xml_declaration=True)

r=pages[9]
txt(r,'shape-2','照片入柜的三道可靠性工序')
txt(r,'shape-7','图像规整')
txt(r,'shape-8',['尺寸与方向规整，','原图与展示派生分开。'],size=20)
txt(r,'shape-13','本地抠图')
txt(r,'shape-14',['U²-Net / GrabCut；','透明检查与恢复路径。'],size=20)
txt(r,'shape-19','属性证据')
txt(r,'shape-20',['已确认 / 推测 / 未知 / 冲突；','由用户核对后入柜。'],size=20)
txt(r,'shape-21','耗时任务在后台运行；耗时随图片、模型与资源变化，不承诺固定秒数。',size=20)

r=pages[10]
txt(r,'shape-2','网站架构：交互、计算与执行解耦',size=36)
txt(r,'shape-5','Vue 3 / TypeScript / Ant Design Vue / Konva',size=19)
txt(r,'shape-6','浏览器响应式界面 · 衣柜、组合台与执行回执',size=18)
txt(r,'shape-9','Java 21 / Spring Boot / Spring Security',size=19)
txt(r,'shape-10','API、归属与权限 · 推荐规则 · 额度与持久任务',size=18)
txt(r,'shape-13','本地推理 + Agent + 统一任务执行器',size=20)
txt(r,'shape-14',['ONNX：U²-Net / BGE / 可选 CLIP；LangGraph 对话编排；','CPU / 识别 / 生成分池，公平调度与保守恢复。'],size=18)
txt(r,'shape-17','H2 / Flyway / MyBatis Plus · 本地或 S3 图片',size=19)
txt(r,'shape-18','默认可控单机部署；Docker / CI；管理 API 可插拔且默认关闭',size=17)
txt(r,'shape-19','明确的运行边界',size=20)
txt(r,'shape-20',['任务有持久记录','网页内查看状态与通知','UNKNOWN 不自动重发','PWA 缓存应用外壳'],size=19)

r=pages[11]
txt(r,'shape-2','先验证谁会反复使用')
txt(r,'shape-3','05 · 目标用户与进入市场')
txt(r,'shape-4',['衣物不少、选择很难的高校与初入职场人群。','先从高频通勤与日常搭配任务验证价值。'],size=22)
txt(r,'shape-6','切入点：校园与穿搭社群共创',size=20)
txt(r,'shape-7',['计划招募 30–50 位共创者，观察四周；','记录采纳、实际穿着覆盖、留存和付费意愿。'],size=18)
txt(r,'shape-9','待验证的市场假设',size=18)
txt(r,'shape-12','第一次就能用上')
txt(r,'shape-13','入柜并完成一套可采纳搭配')
txt(r,'shape-16','每天愿意再回来')
txt(r,'shape-17','观察真实使用，不拿曝光当穿着')
txt(r,'shape-20','持续价值能收费')
txt(r,'shape-21','访谈与小额实验验证付费意愿')

r=pages[12]
txt(r,'shape-2','从日常服务，走向可验证的收入')
txt(r,'shape-3','05 · 商业设计 / 待验证，未形成付费成绩')
txt(r,'shape-7','持续订阅')
txt(r,'shape-8',['基础衣柜与计算推荐作为入口；','高级管理、长期洞察与','专属服务探索订阅。'],size=18)
txt(r,'shape-12','OOTD 生成额度')
txt(r,'shape-13',['按次或额度包收费，','覆盖真实上游生成成本；','不承诺无限生成。'],size=18)
txt(r,'shape-17','未来机构工作台')
txt(r,'shape-18',['与造型、衣柜整理服务商','共创授权工作台；','不出售用户衣柜数据。'],size=18)
remove(r,'shape-19');remove(r,'shape-25')
for id in ('shape-4','shape-9','shape-14'):
 g=group(r,id);g.set('transform','translate(0 16) scale(1 0.84)')
 for e in list(g):
  # geometry-only carriers may scale; source text lives in independent sibling slots
  pass
g=new_group(r,'commercial-scenario',93,565,1094,87)
E.SubElement(g,tag('rect'),{'x':'93','y':'565','width':'1094','height':'87','rx':'12','fill':'#EEF6F1'})
native_text(g,114,600,'情景演算：10,000 活跃用户 × 5% 转化 × 199 元/人/年 = 9.95 万元/年',22,'#1F5C45','bold')
native_text(g,114,636,'仅演算年订阅收入；未扣获客、计算、存储、支持与税费，不是预测或净利润。',17,'#666B76')

r=pages[13]
txt(r,'shape-6','Web 网站闭环')
txt(r,'shape-7',['衣柜、入柜、搜索与推荐','已在源码中打通。'],size=18)
txt(r,'shape-10','搭台与个人 OOTD')
txt(r,'shape-11',['多画板、模特/动作与','生成确认已有实现。'],size=18)
txt(r,'shape-14','工程与管理接入')
txt(r,'shape-15',['持久任务、归属控制；','管理 API 默认关闭。'],size=18)
txt(r,'shape-16','已有实现')
txt(r,'shape-18','真实用户与付费')
txt(r,'shape-19',['共创、留存与单位成本，','仍需下一阶段验证。'],size=18)
txt(r,'shape-20','下一步验证')
replace_picture(r,'shape-21','web-workspace.png')

r=pages[14]
txt(r,'shape-2','参赛团队：鱼力无限')
txt(r,'shape-3','06 · 四项能力方向 / 不代表成员人数')
txt(r,'shape-7','网站界面、响应式交互与画布')
txt(r,'shape-11','API、任务执行、权限与存储')
txt(r,'shape-15','规则推荐、本地检索与图像处理')
txt(r,'shape-21','团队起点与作品证据')
txt(r,'shape-22','全新团队，第一次参加比赛。')
txt(r,'shape-23','暂无过往竞赛奖项；用产品闭环、算法依据和工程交付接受评审。',size=20)

r=pages[15]
txt(r,'shape-8',['修正入柜摩擦与图片质量','记录采纳和实际穿着覆盖','完善未知任务对账与压测'],size=19)
txt(r,'shape-13',['在已有推荐上验证留存','试验订阅与生成额度','核算真实单位服务成本'],size=19)
txt(r,'shape-18',['与造型/整理服务商共创','验证授权工作台的需求','评估数据库与容量扩展'],size=19)

r=pages[16]
txt(r,'shape-6','鱼力无限 · 鱼搭 AI 数字衣柜网站')
txt(r,'shape-7',['理解衣柜，解释选择。','让已有衣物，重新有机会。'],size=48)
txt(r,'shape-9','欢迎现场体验网站 · 共创验证日常穿搭价值',size=22)

# Two explicitly planned new copies, each keeping its source's native skeleton.
algo=copy.deepcopy(pages[9])
txt(algo,'shape-2','推荐有依据，变化也可计算')
txt(algo,'shape-3','03 · 核心算法 / 计算推荐不依赖远程大模型决策')
txt(algo,'shape-7','混合召回')
txt(algo,'shape-8',['字段与关键词先约束，','BGE / 可选 CLIP 补充相关性。'],size=19)
txt(algo,'shape-13','规则与风格')
txt(algo,'shape-14',['11 维当前评分、18 风格画像；','底线约束 + 可解释软评分。'],size=19)
txt(algo,'shape-19','曝光与反馈')
txt(algo,'shape-20',['动态候选、曝光均衡与重排；','时间衰减，让偏好可恢复。'],size=19)
txt(algo,'shape-21','复用预训练模型；项目贡献在领域特征、规则、重排和业务执行协议。',size=20)

evidence=copy.deepcopy(pages[13])
txt(evidence,'shape-2','把“总穿那几件”变成可测问题')
txt(evidence,'shape-3','06 · 历史实验 / 固定意图，连续模拟 28 天')
for id,words in {'shape-6':'167 件','shape-7':'仿内测衣柜','shape-8':'实验条件','shape-10':'49 → 97 件','shape-11':'进入推荐的衣物','shape-12':'曝光覆盖改善','shape-14':'20% → 8%','shape-15':'单品最高占比','shape-16':'降低过度集中','shape-18':'仍需真实验证','shape-19':'曝光不等于实际穿着','shape-20':'下一步：用户研究'}.items():txt(evidence,id,words,size=26 if id in ('shape-6','shape-10','shape-14') else None)
remove(evidence,'shape-21')
g=new_group(evidence,'experiment-qualification',93,520,1094,116)
E.SubElement(g,tag('rect'),{'x':'93','y':'520','width':'1094','height':'116','rx':'12','fill':'#EEF6F1'})
native_text(g,116,558,'支持推荐曝光覆盖改善，不等同真实穿着率或消费减少。',24,'#1F5C45','bold')
native_text(g,116,598,'来源：2026-10-10 审美报告；历史模拟，非本轮重测；并非所有公平指标都改善。',17,'#666B76')

order=[(n,f'slide_{n:02}.svg',pages[n]) for n in range(1,10)]
order += [(9,'recommendation_algorithm.svg',algo),(10,'slide_10.svg',pages[10]),(11,'slide_11.svg',pages[11]),(12,'slide_12.svg',pages[12]),(13,'slide_13.svg',pages[13]),(13,'evidence_simulation.svg',evidence),(14,'slide_14.svg',pages[14]),(15,'slide_15.svg',pages[15]),(16,'slide_16.svg',pages[16])]
plan=[]
for output,(source,name,root) in enumerate(order,1):
 footer(root,output,'历史模拟，非实际穿着' if name=='evidence_simulation.svg' else '')
 E.ElementTree(root).write(SVGS/name,encoding='utf-8',xml_declaration=True)
 plan.append({'source_slide':source,**({'svg':name} if not name.startswith('slide_') else {})})
(ROOT/'page_plan.json').write_text(json.dumps({'schema':'ppt-master.roundtrip-page-plan.v1','pages':plan},ensure_ascii=False,indent=2))
print('Edited 16 source pages and 2 planned copies; original source package unchanged.')
