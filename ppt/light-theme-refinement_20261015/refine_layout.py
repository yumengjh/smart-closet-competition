from pathlib import Path
from lxml import etree as E
from copy import deepcopy

ROOT = Path(__file__).resolve().parent
S = 'http://www.w3.org/2000/svg'
NS = {'s': S}
PAPER, WHITE, INK, MUTED = '#F7F8FA', '#FFFFFF', '#25262B', '#666B76'
GREEN, SOFT, LINE = '#1F5C45', '#EEF6F1', '#E8E9EE'
FONT = 'Microsoft YaHei, Arial, PingFang SC, sans-serif'

def tag(s): return f'{{{S}}}{s}'
def el(name, **attrs): return E.Element(tag(name), {k.replace('_','-'):str(v) for k,v in attrs.items()})
def shape(r, n):
    a = r.xpath(f'//*[@id="shape-{n}"]')
    assert len(a)==1, n
    return a[0]
def frame(g,x,y,w,h): g.set('data-pptx-frame', f'{x:g} {y:g} {w:g} {h:g}')
def rectpath(g,x,y,w,h,fill='none',stroke='none',radius=0):
    old = g.find('s:path[@data-pptx-part="geometry"]', NS)
    if old is not None: g.remove(old)
    if radius:
        d=f'M {x+radius} {y} L {x+w-radius} {y} Q {x+w} {y} {x+w} {y+radius} L {x+w} {y+h-radius} Q {x+w} {y+h} {x+w-radius} {y+h} L {x+radius} {y+h} Q {x} {y+h} {x} {y+h-radius} L {x} {y+radius} Q {x} {y} {x+radius} {y} Z'
    else: d=f'M {x} {y} L {x+w} {y} L {x+w} {y+h} L {x} {y+h} Z'
    p=el('path',d=d,fill=fill,stroke=stroke)
    p.set('data-pptx-part','geometry')
    if stroke!='none':p.set('stroke-width','1')
    g.insert(0,p)
    frame(g,x,y,w,h)
def text(g, lines, x,y,w,h,size=22,color=INK,bold=False,anchor='start',baseline=None,leading=None,geom=True):
    if isinstance(lines,str):lines=[lines]
    for t in g.findall('s:text',NS):g.remove(t)
    if geom:rectpath(g,x,y,w,h)
    else:frame(g,x,y,w,h)
    t=el('text',x=x if anchor=='start' else x+w/2 if anchor=='middle' else x+w,
         y=baseline if baseline is not None else y+size*1.1,font_size=size,fill=color,
         font_family=FONT,font_weight='bold' if bold else 'normal',text_anchor=anchor)
    t.set('data-pptx-text-baseline','metrics-v1')
    t.set('{http://www.w3.org/XML/1998/namespace}space','preserve')
    t.text=lines[0]
    for line in lines[1:]:
        sp=el('tspan',x=t.get('x'),dy=leading or size*1.5);sp.text=line;t.append(sp)
    g.append(t)
    return t
def st(r,n,*args,**kw):return text(shape(r,n),*args,**kw)
def surface(r,n,x,y,w,h,fill=WHITE):
    g=shape(r,n);rectpath(g,x,y,w,h,fill,LINE,16)
    g.attrib.pop('transform',None)
    return g
def circle(r,n,x,y,d=48):
    g=shape(r,n)
    for c in list(g):g.remove(c)
    p=el('path',d=f'M {x+d/2} {y} A {d/2} {d/2} 0 1 1 {x+d/2} {y+d} A {d/2} {d/2} 0 1 1 {x+d/2} {y} Z',fill=GREEN,stroke='none')
    p.set('data-pptx-part','geometry');g.append(p);frame(g,x,y,d,d)
def num(r,n,value,x,y,d=48):st(r,n,str(value),x,y,d,d,22,WHITE,True,'middle',baseline=y+32)
def delete(r,n):
    a=shape(r,n);a.getparent().remove(a)
def newgroup(r,name,fr):
    g=el('g',id=name);frame(g,*fr);g.set('data-pptx-bounds',g.get('data-pptx-frame'));r.append(g);return g
def label(r,name,s,x,y,w,h,size=22,color=INK,bold=False,anchor='start'):
    g=newgroup(r,name,(x,y,w,h));text(g,s,x,y,w,h,size,color,bold,anchor,geom=False);return g
def line(r,n,coords):
    g=shape(r,n);g.attrib.pop('transform',None)
    x1,y1,x2,y2=coords
    for c in list(g):g.remove(c)
    p=el('path',d=f'M {x1} {y1} L {x2} {y2}',fill='none',stroke=GREEN,stroke_width=2)
    p.set('marker-end','url(#marrow1)');p.set('data-pptx-part','geometry');g.append(p)
    frame(g,min(x1,x2),min(y1,y2),abs(x2-x1),abs(y2-y1))
def picture(r,n,href,x,y,w,h):
    g=shape(r,n)
    for c in list(g):g.remove(c)
    g.set('data-pptx-object','picture');g.attrib.pop('data-pptx-semantic-object',None)
    frame(g,x,y,w,h)
    im=el('image',href=href,x=x,y=y,width=w,height=h,preserveAspectRatio='xMidYMid meet')
    g.append(im)
def header(r,title_id,sub_id,title,sub):
    st(r,title_id,title,64,62,1152,62,40,INK,True,baseline=106)
    st(r,sub_id,sub,64,128,1152,32,18,GREEN,baseline=150)
def clean(r):
    r.set('font-family',FONT)
    for e in r.iter():
        if e is not r:e.attrib.pop('font-family',None)
        if e.tag==tag('text'):
            e.set('font-family',FONT)
            if ''.join(e.itertext()).strip() not in ['1','2','3','4','5','6'] and e.get('fill','').upper() in [WHITE,'#DCEAE2']:
                e.set('fill',INK if e.get('fill')==WHITE else MUTED)
        if e.get('data-pptx-frame')=='0 0 1280 720':
            for p in e.findall('s:path[@data-pptx-part="geometry"]',NS):
                if p.get('fill') not in [None,'none']:
                    p.set('fill',PAPER);p.attrib.pop('fill-opacity',None)
    for g in r.xpath('//*[@data-pptx-object="shape"]'):
        fs=g.get('data-pptx-frame','').split()
        if len(fs)==4 and float(fs[1])>=664:
            for t in g.findall('s:text',NS):t.set('fill',MUTED)
def recompute(r):
    for g in reversed(r.findall('.//s:g',NS)):
        if g.get('data-pptx-object')!='group':continue
        boxes=[]
        for c in g:
            v=c.get('data-pptx-frame','').split()
            if len(v)==4:boxes.append(list(map(float,v)))
        if boxes:
            x=min(v[0] for v in boxes);y=min(v[1] for v in boxes)
            frame(g,x,y,max(v[0]+v[2] for v in boxes)-x,max(v[1]+v[3] for v in boxes)-y)

for page in range(1,19):
    fn=f'slide_{page:02}.svg'
    t=E.parse(str(ROOT/'reference/authoring-before'/fn));r=t.getroot();clean(r)
    if page==1:
        st(r,3,'AI 数字衣柜 · Web 网站',80,80,550,40,22,GREEN,True)
        st(r,4,'鱼搭',76,170,450,150,116,INK,True)
        st(r,5,['让已有衣物，','成为每天的选择。'],80,356,380,96,32,INK,leading=48)
        st(r,7,['参赛团队：鱼力无限','网页作品路演'],80,528,380,70,20,MUTED,leading=32)
    elif page==2:
        header(r,30,3,'从真实衣柜，到日常选择','路演目录 / 六个问题，讲清鱼搭')
        titles=['为什么做','产品如何工作','创新与算法','技术如何支撑','用户与商业','团队与下一步']
        bodies=['衣柜很满，选择仍难','入柜 · 推荐 · 搭台 · OOTD','本地检索 · 可解释推荐','Web · 模型 · 持久任务','共创验证 · 订阅与额度','鱼力无限 · 作品与规划']
        for k,(ci,ni,ti,bi) in enumerate([(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20),(21,22,23,24),(25,26,27,28)]):
            x=64+(k%2)*600;y=224+(k//2)*132
            circle(r,ci,x,y,56);num(r,ni,k+1,x+4,y+4,48)
            st(r,ti,titles[k],x+88,y,430,42,28,INK,True)
            st(r,bi,bodies[k],x+88,y+50,430,34,20,MUTED)
        delete(r,4)
    elif page==3:
        header(r,3,20,'衣柜很满，选择仍然很难','01 · 需求洞察')
        st(r,4,['照片分散、灵感难落地，','出门前仍然反复选择那几件。'],64,206,550,80,24,MUTED,leading=38)
        shape(r,34).set('transform','translate(-60 -70)')
        delete(r,5)
        for k,(ci,ni,ti,bi) in enumerate([(6,7,8,9),(10,11,12,13),(14,15,16,17)]):
            x=664;y=226+k*130
            circle(r,ci,x,y,48);num(r,ni,k+1,x,y)
            st(r,ti,[['今天，适合穿什么？'],['衣物多，难以记忆和查找'],['有灵感，却难用自己的衣物还原']][k],x+72,y-2,480,42,24,INK,True)
            st(r,bi,['建议有依据','衣柜可搜索','组合可编辑'][k],x+72,y+50,450,35,21,GREEN)
    elif page==4:
        header(r,3,2,'把衣柜，变成决策资源','01 · 项目立意')
        st(r,4,'从真实衣物出发，让每次选择都有依据。',64,198,1120,42,24,MUTED)
        line(r,6,(104,304,1188,304))
        for k,(ci,ti,bi,di) in enumerate([(7,8,9,10),(12,13,14,15),(17,18,19,20),(22,23,24,25)]):
            x=64+k*288
            circle(r,ci,x+28,292,24)
            st(r,ti,['拥有','理解','选择','反馈'][k],x,352,260,50,36,INK,True)
            st(r,bi,['真实衣物','属性与图像','场景 · 天气 · 风格','换件 · 喜好 · 恢复'][k],x,426,270,42,24,INK)
            st(r,di,['库存成为起点','知道适合什么','选择附带理由','影响下一次选择'][k],x,480,260,35,21,MUTED)
        st(r,28,'让更多已有衣物进入日常；实际效果仍需用户验证。',64,580,1152,45,23,GREEN)
    elif page==5:
        header(r,3,7,'拍一件，收一件','02 · 网站功能 / 快速入柜')
        picture(r,10,'../images/quick-intake-complete.png',480,190,720,450)
        st(r,5,'实时网站画面 · 完整操作区',64,608,370,30,17,MUTED)
        for k,(title,body) in enumerate([('拍照或选图','相册多选 · 拖拽 · 粘贴'),('先看到贴纸','后台处理，无需原地等待'),('入柜后可修改','资料、图片仍可继续调整')]):
            y=224+k*120
            g=newgroup(r,f'intake-step-{k+1}',(64,y,368,94))
            g.append(el('circle',cx=84,cy=y+20,r=20,fill=GREEN))
            q=el('text',x=84,y=y+28,font_size=22,font_weight='bold',fill=WHITE,text_anchor='middle');q.text=str(k+1);g.append(q)
            label(r,f'intake-title-{k+1}',title,124,y-1,290,40,26,INK,True)
            label(r,f'intake-body-{k+1}',body,124,y+51,306,32,21,MUTED)
    elif page==6:
        header(r,5,41,'从入柜到出门，一个完整闭环','02 · 六步核心功能')
        rows=[(14,10,11,12,13),(19,15,16,17,18),(24,20,21,22,23),(29,25,26,27,28),(34,30,31,32,33),(39,35,36,37,38)]
        names=['拍照入柜','混合检索','计算推荐','搭台编辑','OOTD 预览','反馈调整']
        desc=[['照片转成衣物资产'],['字段 · 文本 · 图像'],['组合 · 评分 · 理由'],['多画板，自由接手'],['模特 · 动作 · 调整'],['偏好可恢复']]
        pos=[(64,210),(464,210),(864,210),(864,410),(464,410),(64,410)]
        for k,((gi,ci,ni,ti,bi),(x,y)) in enumerate(zip(rows,pos)):
            g=shape(r,gi);card=el('rect',x=x,y=y,width=352,height=140,rx=16,fill=WHITE,stroke=LINE,stroke_width=1);g.insert(0,card)
            circle(r,ci,x+24,y+24);num(r,ni,k+1,x+24,y+24)
            st(r,ti,names[k],x+92,y+24,244,42,26,INK,True)
            st(r,bi,desc[k],x+92,y+81,244,35,20,MUTED)
        line(r,6,(416,280,452,280));line(r,7,(816,280,852,280));line(r,8,(1040,358,1040,398));line(r,9,(864,480,828,480))
        for k,(a,b,c,d) in enumerate([(464,480,428,480),(88,398,88,362)]):
            g=newgroup(r,f'loop-link-{k}',(min(a,c),min(b,d),max(abs(a-c),1),max(abs(b-d),1)))
            g.append(el('line',x1=a,y1=b,x2=c,y2=d,stroke=GREEN,stroke_width=2,marker_end='url(#marrow1)'))
        st(r,2,'OOTD 仅作效果预览；真实合身与细节仍需线下确认。',64,602,1152,35,19,MUTED)
    elif page==7:
        for c in list(r):
            if c.tag==tag('defs'):continue
            if c.get('id') not in ['shape-2','shape-3','shape-44'] and c.get('data-pptx-source-ref'):
                r.remove(c)
            elif c.tag==tag('use'):r.remove(c)
        header(r,23,3,'先看见价值，再看它如何工作','02 · 视频展示 / 素材制作完成后插入')
        for k,(x,title,desc) in enumerate([(64,'宣传视频','从穿搭困境，到鱼搭的日常价值'),(664,'演示视频','入柜 → 推荐 → 搭台 → OOTD')]):
            g=newgroup(r,f'video-slot-{k+1}',(x,220,552,310.5))
            g.append(el('rect',x=x,y=220,width=552,height=310.5,rx=16,fill=SOFT,stroke=GREEN,stroke_width=1.5,stroke_dasharray='8,4'))
            g.append(el('circle',cx=x+276,cy=324,r=35,fill=WHITE))
            g.append(el('polygon',points=f'{x+268},308 {x+268},340 {x+292},324',fill=GREEN))
            label(r,f'video-title-{k+1}',title,x+30,382,492,44,30,INK,True,'middle')
            label(r,f'video-status-{k+1}','视频待插入 · 16:9',x+30,447,492,32,20,GREEN,anchor='middle')
            label(r,f'video-caption-{k+1}',desc,x,558,552,42,22,INK,anchor='middle')
        label(r,'video-note','同一页预留两个独立视频位，保留完整画面比例。',64,617,1152,30,18,MUTED)
    elif page==8:
        header(r,6,3,'从用户问题，到可解释的实现','03 · 创新机制与用户价值')
        for e in r.iter():
            if e.tag not in [tag('text'),tag('tspan')] and e.get('fill') in [INK,GREEN]:e.set('fill',SOFT)
            if e.tag in [tag('text'),tag('tspan')] and e.get('fill')==WHITE:e.set('fill',INK)
        for n,s,x,w in [(25,'维度',112,160),(26,'用户问题',320,390),(27,'鱼搭机制',760,410)]:st(r,n,s,x,190,w,36,22,GREEN,True,anchor='middle')
        vals=[('图片处理','上传后还要原地等待',['持久任务','提交后查看状态']),('输入可靠性','背景复杂，属性难确认',['本地抠图 · 属性证据','用户可核对与修正']),('推荐选择','理由不清楚，结果总重复',['规则解释 · 曝光均衡','反馈可恢复']),('执行与成本','耗时与上游结果不确定',['授权 · 回执 · 额度快照','未知结果不盲目重试'])]
        for k,(a,b,c) in enumerate(vals):
            y=252+k*93.33
            st(r,28+k*3,a,112,y,160,46,20,INK,True,anchor='middle')
            st(r,29+k*3,b,320,y,390,46,20,MUTED,anchor='middle')
            st(r,30+k*3,c,760,y-7,410,76,20,GREEN,anchor='middle',leading=29)
    elif page in [9,10]:
        title='照片入柜，三道可靠性工序' if page==9 else '推荐有依据，变化也可计算'
        sub='03 · 图像处理' if page==9 else '03 · 推荐算法 / 计算推荐不依赖远程大模型决策'
        header(r,23,3,title,sub)
        headings=['图像规整','本地抠图','属性证据'] if page==9 else ['混合召回','规则与风格','曝光与反馈']
        bodies=[['尺寸与方向规整','原图与展示派生分开'],['U²-Net / GrabCut','透明检查与恢复路径'],['确认 · 推测 · 未知 · 冲突','核对后形成衣物资料']] if page==9 else [['字段与关键词约束候选','BGE / 可选 CLIP','补充语义相关性'],['11 维评分 · 18 风格画像','结构底线 + 软评分','每次选择保留理由'],['动态候选 · 曝光均衡','反馈衰减与重新排序','减少反复推荐同几件']]
        for k,(bg,ci,ni,ti,bi) in enumerate([(4,5,6,7,8),(10,11,12,13,14),(16,17,18,19,20)]):
            x=64+k*400;surface(r,bg,x,220,352,300)
            circle(r,ci,x+24,246);num(r,ni,k+1,x+24,246)
            st(r,ti,headings[k],x+96,250,230,42,26,INK,True)
            st(r,bi,bodies[k],x+24,342,304,135,21,MUTED,leading=35)
        line(r,9,(424,370,452,370));line(r,15,(824,370,852,370))
        st(r,21,'后台处理，让用户继续下一件；实际耗时随图片、模型和资源变化。' if page==9 else '复用预训练模型，贡献领域规则、可解释评分、重排与执行协议。',64,574,1152,60,21,GREEN)
    elif page==11:
        header(r,22,3,'网站架构：交互、计算与执行解耦','04 · 四层架构 / 技术与职责分开呈现')
        tech=['Vue 3 · TypeScript · Ant Design Vue · Konva','Java 21 · Spring Boot · Spring Security','ONNX Runtime · U²-Net / BGE / 可选 CLIP · LangGraph','H2 · MyBatis Plus · Flyway · 本地 / S3 图片 · Docker / CI']
        roles=['响应式网页 · 衣柜与组合台 · 任务回执','API 与数据归属 · 推荐规则 · 额度与持久任务','本地推理与对话编排 · CPU / 识别 / 生成分池','数据持久化与版本迁移 · 图片存储 · 可控单机交付']
        tiers=['交互层','服务层','智能与执行','数据与交付']
        for k,(bg,ti,bi) in enumerate([(4,5,6),(8,9,10),(12,13,14),(16,17,18)]):
            y=190+k*104;surface(r,bg,64,y,1152,88)
            st(r,ti,tech[k],270,y+12,920,34,23,INK,True)
            st(r,bi,roles[k],270,y+52,920,28,19,MUTED)
            label(r,f'architecture-tier-{k}',tiers[k],88,y+28,160,34,22,GREEN,True)
        for n,y in [(7,278),(11,382),(15,486)]:line(r,n,(176,y,176,y+12))
        st(r,19,'持久记录 · 网页内查看状态 · 未知结果不自动重发',64,620,1152,30,19,GREEN)
        delete(r,20)
    elif page==12:
        header(r,23,3,'先验证，谁会反复使用','05 · 目标用户与市场验证计划')
        st(r,4,['高校与初入职场人群','衣物不少，日常选择很难'],64,210,520,96,28,INK,True,leading=45)
        st(r,6,'30–50 位共创者',64,382,540,55,36,GREEN,True)
        st(r,7,['计划观察 4 周','采纳 · 穿着覆盖 · 留存 · 付费意愿'],64,464,540,96,23,MUTED,leading=40)
        surface(r,8,664,196,552,424)
        st(r,9,'待验证的三个问题',696,220,480,38,23,GREEN,True)
        for k,(ci,ni,ti,bi) in enumerate([(10,11,12,13),(14,15,16,17),(18,19,20,21)]):
            y=288+k*108;circle(r,ci,696,y);num(r,ni,k+1,696,y)
            st(r,ti,['第一次就能用上','每天愿意再回来','持续价值能收费'][k],768,y-1,420,38,25,INK,True)
            st(r,bi,['入柜后，得到可采纳的搭配','观察真实使用与实际穿着','访谈与小额实验验证意愿'][k],768,y+45,420,34,20,MUTED)
        delete(r,5)
    elif page==13:
        header(r,20,3,'从日常服务，走向可验证的收入','05 · 商业设计 / 计划验证，尚无收费成绩')
        for k,(bg,ci,ni,ti,bi) in enumerate([(4,5,6,7,8),(9,10,11,12,13),(14,15,16,17,18)]):
            x=64+k*400;surface(r,bg,x,206,352,306);circle(r,ci,x+24,230);num(r,ni,k+1,x+24,230)
            st(r,ti,['持续订阅','OOTD 生成额度','未来机构工作台'][k],x+24,310,304,44,26,INK,True)
            st(r,bi,[['基础衣柜与计算推荐作入口','高级管理、长期洞察','探索订阅服务'],['按次或额度包收费','覆盖真实上游生成成本','先核算，再验证付费'],['面向造型与整理服务商','共创授权工作台','用户衣柜数据不出售']][k],x+24,374,304,118,21,MUTED,leading=34)
        st(r,33,'10,000 活跃用户 × 5% × 199 元/年 = 9.95 万元/年',88,566,1104,44,28,GREEN,True)
        st(r,34,'情景演算，非预测或净利润；未扣获客、计算、存储、支持与税费。',88,620,1104,30,18,MUTED)
    elif page==14:
        header(r,23,3,'已实现什么，下一步验证什么','06 · 项目进展')
        for use in list(r.findall('.//s:use',NS)):use.getparent().remove(use)
        for k,(ci,ti,bi,si) in enumerate([(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20)]):
            x=64+k*288
            circle(r,ci,x+20,422,24)
            if k==3:
                for p in shape(r,ci):p.set('fill',MUTED)
            st(r,ti,['Web 网站闭环','搭台与个人 OOTD','工程与管理接入','用户与商业验证'][k],x,244,264,42,24,INK,True)
            st(r,bi,[['衣柜 · 入柜 · 搜索','计算推荐已打通'],['多画板 · 模特 / 动作','生成确认已有实现'],['持久任务 · 数据归属','管理 API 默认关闭'],['共创 · 留存 · 付费','单位成本仍待验证']][k],x,308,264,90,21,MUTED,leading=36)
            st(r,si,['已实现','已实现','已有实现','下一阶段'][k],x,476,264,36,22,GREEN if k<3 else MUTED,True)
        line(r,4,(96,434,960,434))
        label(r,'progress-evidence','实现能力来自项目源码与既有验证材料，用户效果以共创实验继续验证。',64,588,1152,40,21,MUTED)
    elif page==15:
        header(r,21,3,'把“总穿那几件”，变成可测问题','06 · 历史模拟 / 固定意图，连续 28 天')
        vals=[('167 件','仿内测衣柜','实验条件'),('49 → 97 件','进入推荐的衣物','曝光覆盖改善'),('20% → 8%','单品最高占比','降低过度集中'),('待验证','曝光不等于实际穿着','下一步：用户研究')]
        for k,(ci,ti,bi,si) in enumerate([(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20)]):
            x=64+k*288;delete(r,ci)
            st(r,ti,vals[k][0],x,256,272,62,36 if k<3 else 32,GREEN,True)
            st(r,bi,vals[k][1],x,342,272,52,21,INK)
            st(r,si,vals[k][2],x,430,272,36,20,MUTED)
        st(r,37,'支持推荐曝光覆盖改善；真实穿着与消费影响仍需验证。',88,542,1104,46,25,GREEN,True)
        st(r,38,'来源：2026-10-10 审美报告；历史模拟，非本轮重测，并非所有公平指标均改善。',88,602,1104,32,18,MUTED)
    elif page==16:
        header(r,25,3,'鱼力无限，以作品接受评审','06 · 四项能力方向 / 不代表成员人数')
        rows=[(4,5,6,7),(8,9,10,11),(12,13,14,15),(16,17,18,19)]
        names=['前端开发','后端架构','算法与图像处理','产品与设计']
        desc=[['响应式网页','交互与组合画布'],['API · 权限 · 存储','持久任务与调度'],['本地检索与抠图','规则推荐与解释'],['需求与交互','视觉与项目文档']]
        for k,(ci,ni,ti,bi) in enumerate(rows):
            x=64+k*288;circle(r,ci,x,212);num(r,ni,k+1,x,212)
            st(r,ti,names[k],x,292,264,42,24,INK,True)
            st(r,bi,desc[k],x,356,264,84,21,MUTED,leading=36)
        st(r,21,'团队起点与作品证据',64,486,1152,34,20,GREEN)
        st(r,22,'全新团队，第一次参加比赛。',64,536,1152,56,34,INK,True)
        st(r,23,'暂无过往竞赛奖项；以产品闭环、算法依据和工程交付展示实力。',64,612,1152,32,21,MUTED)
        delete(r,20)
    elif page==17:
        header(r,20,3,'下一步，围绕三个验证目标推进','06 · 发展路线')
        for k,(bg,ci,ni,ti,bi) in enumerate([(4,5,6,7,8),(9,10,11,12,13),(14,15,16,17,18)]):
            x=64+k*400;surface(r,bg,x,220,352,350);circle(r,ci,x+24,246);num(r,ni,k+1,x+24,246)
            st(r,ti,['短期 · 打磨体验','中期 · 验证付费','长期 · 共创 B 端'][k],x+24,326,304,46,26,INK,True)
            st(r,bi,[['减少入柜摩擦','记录采纳与实际穿着','完善任务对账与压测'],['试验订阅与生成额度','验证留存与付费意愿','核算单位服务成本'],['与造型 / 整理商共创','验证授权工作台需求','评估数据库与容量扩展']][k],x+24,400,304,132,22,MUTED,leading=40)
    elif page==18:
        for n in [3,4,5]:
            for p in shape(r,n).findall('s:path',NS):p.set('fill',SOFT);p.attrib.pop('fill-opacity',None)
        st(r,6,'鱼力无限 · 鱼搭 AI 数字衣柜网站',128,182,1024,42,22,GREEN,True,anchor='middle')
        st(r,7,['理解衣柜，解释选择。','让已有衣物，重新有机会。'],128,280,1024,160,48,INK,True,anchor='middle',leading=78)
        st(r,9,'欢迎现场体验网站，共创日常穿搭价值。',128,532,1024,45,25,MUTED,anchor='middle')
    if r.xpath('//*[@marker-end="url(#marrow1)"]') and not r.xpath('//*[@id="marrow1"]'):
        defs=r.find('s:defs',NS)
        if defs is None:defs=el('defs');r.insert(0,defs)
        m=el('marker',id='marrow1',viewBox='0 0 10 10',refX=10,refY=5,markerWidth=3.5,markerHeight=3.5,orient='auto',markerUnits='strokeWidth')
        m.append(el('path',d='M 0 0 L 10 5 L 0 10 Z',fill=GREEN));defs.append(m)
    recompute(r)
    t.write(str(ROOT/'authoring-svg-flat'/fn),encoding='utf-8',xml_declaration=True)
    print('refined',fn)

notes={5:'用户可以在网站中拍照、从相册多选，也可以拖拽或粘贴图片。当前快速入柜模式先生成贴纸，资料在后台继续补齐，贴纸做好后自动入柜；用户仍可修改资料和更换图片。这张画面重新截取了完整的操作卡片和说明，展示可运行网站的真实交互。',7:'这一页预留宣传视频和操作演示两个独立的位置。宣传视频将解释日常穿搭困境和鱼搭的价值；演示视频将串起入柜、推荐、组合台与 OOTD 的操作。当前视频仍在制作，页面中的两个框是待插入位置，正式路演前将替换为实际视频。',11:'架构分为四层：交互层由 Vue、TypeScript、Ant Design Vue 和 Konva 承载网站与画布；服务层用 Java、Spring Boot 和 Security 处理 API、数据归属、推荐规则与额度。智能与执行层通过 ONNX 运行本地模型，由 LangGraph 编排对话，并按 CPU、识别和生成资源分别调度。数据与交付层使用 H2、MyBatis Plus、Flyway、本地或 S3 图片、Docker 与持续集成；当前采用可控单机部署。任务持久记录、网页内可查看状态，上游结果未知时不会自动重发。'}
for n,s in notes.items():(ROOT/'notes'/f'slide_{n:02}.md').write_text(s)
(ROOT/'讲稿.md').write_text('\n\n---\n\n'.join(f'# {n:02}\n\n'+(ROOT/'notes'/f'slide_{n:02}.md').read_text().strip() for n in range(1,19)))
