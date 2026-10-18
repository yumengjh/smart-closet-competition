<!-- ppt-master-schema: design-spec/v1 -->
# 鱼搭竞赛路演 - Design Spec

## I. Project Information

| Item | Value |
| --- | --- |
| Project Name | 鱼搭竞赛路演 |
| Canvas Format | ppt169 — 1280×720 |
| Page Count | 18 |
| Primary Language | zh-CN |
| Target Audience | 竞赛评委、潜在共创伙伴 |
| Communication Intent | 从日常选择困境解释价值，以功能、算法、工程与历史证据证明实现，再展示目标市场和盈利验证路线 |
| Desired Audience Outcome | 理解鱼搭的价值与实现边界，认可开展用户和商业验证 |
| Core Message / Ask / Action | 让已有衣物成为可解释、可反馈的个人穿搭决策资源；邀请首批共创者参与验证 |
| Delivery Context | 主讲约 10 分钟的竞赛现场答辩，次要为会后查阅 |
| Artifact Afterlife | 备注支撑答辩、复用与来源追溯 |
| Reading Mode | balanced |
| Content Strategy | 用户授权「你自己发挥」；材料可重组，事实不扩写为未证实成绩，商业数字标为情景 |
| Design Style | 衣柜新刊，editorial 支持的时尚杂志式原生示意 |
| AI Image Acquisition Path | not applicable |
| Generation Mode | continuous |
| Spec Refinement | disabled |
| Speaker Notes | enabled — delegated final Stage-2 proactive policy |
| Custom Animations | disabled — delegated final Stage-2 proactive policy |
| Narration Audio | disabled — delegated final Stage-2 proactive policy |
| Created Date | 2026-10-13 |

## II. Canvas Specification

| Property | Value |
| --- | --- |
| Format | PPT 16:9 |
| Dimensions | 1280×720 |
| viewBox | `0 0 1280 720` |
| Margins | 64 px；大色域可满版，正文留安全区 |
| Content Area | 64, 64 到 1216, 640 |

## III. Visual Theme

### Theme Style

- **Mode**: custom
- **Mode References**: narrative
- **Mode Behavior**: 从出门前的选择困境进入，产品闭环带来转折；技术与历史模拟提供证据；市场与收费假设展开下一章；结尾邀请共创验证。
- **Visual style**: custom
- **Visual Style References**: editorial
- **Visual Style Behavior**: 用杂志式衬线标题、细线、非对称分栏和大色域组织层级，衣物轮廓成为项目专属视觉母题；深浅页随论点切换，流程和架构由有方向的连线表达，数据使用大数字对比而非卡片铺满。
- **Theme**: 衣柜新刊；衣物轮廓在封面、用户困境、搭配和结尾变换身份，连起已有衣物到决策价值。
- **Tone**: 有时尚产品感，清晰、诚实、自信。

### Color Scheme

| Role | HEX | Purpose |
| --- | --- | --- |
| Background | #F5F1E8 | 奶油白正文场 |
| Secondary background | #E8E1D6 | 浅层与示意布料 |
| Primary | #302238 | 梅紫主场与标题 |
| Accent | #D8F36A | 关键选择与行动 |
| Secondary accent | #BBA4CB | 次层与衣物材质示意 |
| Body text | #302238 | 正文 |
| Secondary text | #6B6071 | 来源与注释 |
| Divider | #C7BECC | 细线 |
| On dark | #F5F1E8 | 深色场正文 |
| Muted dark | #C7BECC | 深色场次层 |

## IV. Typography System

### Font Plan

| Role | Character (Reference) | Primary | English if non-English | Fallback tail |
| --- | --- | --- | --- | --- |
| Title | 杂志衬线、有气质 | SimSun | Georgia | serif |
| Body | 中性清晰 | Microsoft YaHei | Arial | sans-serif |
| Display | 高对比大数字与封面钩子 | Microsoft YaHei | Arial | sans-serif |

- **Title stack**: SimSun, Georgia
- **Body stack**: Microsoft YaHei, Arial
- **Display stack**: Microsoft YaHei, Arial
- **Role rationale**: Display 采用 lining 数字，支持时间、实验与商业数字；support roles 继承正文。

### Font Size Hierarchy

| Purpose | Anchor Size (px) |
| --- | ---: |
| Body | 26 |
| Title | 48 |
| Subtitle | 36 |
| Lead | 32 |
| Annotation | 20 |
| Footnote | 16 |
| Kicker | 18 |
| Display | 88 |
| Hero | 64 |
| Number | 56 |

## V. Layout Principles

### Deck-wide Direction

- **Hierarchy direction**: 一个判断先进入视线，图形与注释支撑其依据。
- **Composition tendency**: 大字与衣物轮廓共构画面，证据页用非对称列，机制页用连线。
- **Cross-page continuity**: 同一套衣物形态在困境、推荐、商业务实和结尾变换关系；结构性细线和栏目标签支持定位。
- **Spacing posture**: 开场与结尾舒展，架构与机制紧凑，中间证据页释放空间。
- **Spacing anchors**: page margin 64；block gap 28；column gutter 32；corner radius 12；body leading 42 px。

## VI. Icon Usage Specification

- **Primary bundled library**: none

| Icon Path | Suitable Scenarios |
| --- | --- |

## VIII. Image Resource List

| Filename | Dimensions | Ratio | Purpose | Type | Image pattern | Crop Policy | Acquire Via | Status | Reference | text_policy | page_role |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

image_usage=none；原生示意承担视觉任务，衣物和界面均是流程示意，不是实测截图；不需要外部图片资源。

## IX. Content Outline

### Part 1: 从衣柜出发

#### Slide 01 - 让衣柜里的每一件重新有机会
- **Audience move**: 初见项目 → 记住已有衣物的价值。
- **Relationships**: 衣物与决策价值 link；日常使用与新机会 link。
- **Composition**: 产品名、两行钩子与大型衣物轮廓共享深色场。
- **Title**: 鱼搭
- **Core message**: 让衣柜里的每一件，重新有机会。
- **Cover impact**: 让衣柜里的每一件，重新有机会；用衣物和选择线呈现新的出场机会。
- **Content**:
  - 可解释 AI 数字衣柜与穿搭决策系统；竞赛路演 2026。
  - 从已有衣物出发，把选择变得有依据。

#### Slide 02 - 衣柜很满，却总穿那几件
- **Audience move**: 模糊需求 → 感知出门前的选择困境。
- **Relationships**: 衣物多与选择难 contrast；找不到、不会配、不敢试 membership 于选择困境。
- **Composition**: 07:50 大时间与被重复选择的衣物形成焦点。
- **Title**: 衣柜很满，却总穿那几件。
- **Core message**: 照片、灵感和衣物存在，但难转成可执行的今天穿什么。
- **Content**:
  - 07:50 为情景时间；找不到：照片分散、属性不清；不会配：灵感无法落到已有衣物；不敢试：缺少理由和预览。
- **Data class**: scenario；07:50 是故事情景，非调查。

#### Slide 03 - 缺的是一套决策过程
- **Audience move**: 想继续买衣服 → 关注理解、选择与反馈。
- **Relationships**: 拥有→理解→选择→反馈 order；反馈与下一次选择 link。
- **Title**: 缺的是一套决策过程。
- **Core message**: 鱼搭把库存变成可理解、可组合、可反馈的决策资源。
- **Content**:
  - 拥有：留下真实衣物；理解：属性与图像；选择：场景、天气、风格；反馈：换件、喜好、恢复。
  - 提高实际穿着率是目标，尚需用户验证。

### Part 2: 产品与技术

#### Slide 04 - 从入柜到出门的闭环
- **Audience move**: 知道概念 → 看见完整用户链路。
- **Relationships**: 拍照入柜→混合检索→计算推荐→搭台编辑→OOTD预览→反馈调整 order；反馈与推荐 link。
- **Title**: 一个从入柜到出门的闭环。
- **Core message**: 多个功能围绕真实衣柜接起来，而不是各自独立。
- **Content**:
  - 拍照入柜·混合检索·计算推荐·搭台编辑·OOTD预览·反馈调整。
  - OOTD 是效果预览，不能保证尺码合身或衣物细节完全一致。

#### Slide 05 - 把衣物变成可用资产
- **Audience move**: 以为只是上传照片 → 理解资产与属性的可靠性。
- **Relationships**: 原图→本地抠图→属性证据→可用衣物 order；人工修正与属性 link。
- **Title**: 拍一张，先变成可用资产。
- **Core message**: 抠图、属性证据和修正把照片变成可靠业务输入。
- **Content**:
  - U²-Net / GrabCut；透明素材；属性分已确认、推测、未知、冲突；用户可修正；复杂背景保留恢复路径。
  - 原图与展示派生分开；衣物图片为原生流程示意。

#### Slide 06 - 推荐给理由，选择由用户接手
- **Audience move**: 接收单一结果 → 能解释与修改。
- **Relationships**: 意图与衣物推荐 link；推荐与理由 link；换件与反馈 link。
- **Title**: 先给你理由，再给你选择。
- **Core message**: 系统解释为什么，也允许用户换一件、换一批、查看未入选理由。
- **Content**:
  - 情景：明天通勤，想精致一些；配色呼应、场景适配、近期曝光参与计算；“换双鞋”重新计算；不是永久讨厌该鞋。
  - 页面推荐和微调零远程大模型决策调用；本地计算仍有成本。
- **Data class**: scenario；衣物与通勤意图为功能示意。

#### Slide 07 - 会聊天，也会把操作做实
- **Audience move**: 只理解聊天 → 理解受控执行与回执。
- **Relationships**: 用户意图→后端授权→浏览器执行→回执确认 order；可编辑搭台与执行 link。
- **Title**: 会聊天，也会把操作做实。
- **Core message**: 完成状态由实际执行结果确认。
- **Content**:
  - LangGraph 对话·Java 权限与工具·SSE 命令·浏览器 ACK / revision；多画板搭台可编辑并接手。
  - OOTD 先确认输入和额度，冻结后进入持久任务；示意界面非实际截图。

#### Slide 08 - 算法负责决策，模型负责表达
- **Audience move**: 把所有能力归为大模型 → 认识自主领域设计与模型分工。
- **Relationships**: 召回→组合→打分→重排 order；计算与识图/对话/生图 contrast。
- **Title**: 算法负责决策，模型负责表达。
- **Core message**: 可计算步骤用可重复的代码，语言和视觉交给适合的模型。
- **Content**:
  - 11 维当前评分；18 风格画像；本地 BGE 语义与可选 CLIP；CIELAB / k-means；曝光债与时间衰减反馈。
  - U²-Net、BGE、CLIP 为预训练技术；领域特征、规则/重排和执行协议是项目工作，未自研基础模型。

#### Slide 09 - 可控单机架构
- **Audience move**: 看到功能清单 → 看到边界与真实选型。
- **Relationships**: Vue 用户端与 Java 主服务 link；Java 与 Agent、ONNX、持久数据、上游服务 link；管理接口属于可选模块 membership。
- **Title**: 为可控的真实产品而建。
- **Core message**: 业务后端掌握数据、权限、成本和任务，Agent 负责语言编排。
- **Content**:
  - Vue 3 / TypeScript / Ant Design Vue / Pinia / Konva；Java 21 / Spring Boot 4.1 / Security；Node.js / TypeScript / LangGraph。
  - ONNX Runtime：U²-Net、BGE、可选CLIP；H2 / Flyway / MyBatis Plus；本地 / S3 图片；持久任务 / 资源池；Docker / GitHub Actions。
  - 管理 API 默认关闭；H2 单机架构，未证明水平扩展与高并发。

#### Slide 10 - 让重复推荐可测
- **Audience move**: 只听到“更好” → 能辨认实验协议和效果边界。
- **Relationships**: 改进前后 contrast；覆盖衣物与最高单品占比是不同指标 membership。
- **Title**: 让“总穿那几件”成为可测问题。
- **Core message**: 历史模拟支持曝光覆盖改善，不等同真实穿着效果。
- **Content**:
  - 167 件仿内测衣柜、固定意图、连续模拟 28 天：进入推荐衣物 49→97 件；单品最高占比 20%→8%。
  - 来源 2026-10-10 审美报告；非本轮重测；非实际穿着率；并非所有公平指标都改善。

### Part 3: 市场与商业

#### Slide 11 - 同赛道，更可解释的切口
- **Audience move**: 怀疑已存在同类 → 理解定位而不误认全球首创。
- **Relationships**: Acloset、Whering、Stylebook membership 于同类平台；公开能力与鱼搭实现特点 contrast。
- **Title**: 同赛道，选择更可解释的切口。
- **Core message**: 基础能力有重叠，鱼搭以可解释与可控实现形成定位。
- **Content**:
  - Acloset：AI整理、天气/场合推荐、虚拟试穿；Whering：规划、社交、穿着统计；Stylebook：画布拼贴、Shuffle、日历。
  - 鱼搭：中文风格线索、理由追踪、曝光均衡、反馈恢复、受控执行。
  - 官方公开资料截至 2026-10-13；未公开不代表竞品没有；无付费实测。

#### Slide 12 - 先切入高频选择场景
- **Audience move**: 泛泛全民市场 → 明确首批可触达的用户假设。
- **Relationships**: 高校/初职、日常通勤、穿搭爱好者 membership 于待验证目标用户；初期与扩展 order。
- **Title**: 先找到“衣服不少、选择很难”的人。
- **Core message**: 优先高频穿搭决策，逐步扩展场景。
- **Content**:
  - 高校与初入职场：首次建立衣柜和场合选择；通勤人群：每天省下决策步骤；穿搭爱好者：复用已有衣物、探索变化。
  - 待验证用户假设；规模、需求与付费尚未证明。

#### Slide 13 - 从首次有效搭配到习惯
- **Audience move**: 只关心获客 → 看到留存和验证机制。
- **Relationships**: 共创招募→首套采纳→四周观察→付费访谈 order；观测与下一次迭代 link。
- **Title**: 获客靠一次有效搭配，留存靠每天能用。
- **Core message**: 先验证真实价值，再扩大用户数量。
- **Content**:
  - 计划招募 30–50 人：校园/社群共创；完成首套可采纳搭配；四周记录使用；观察采纳、实际穿着覆盖、留存和付费意愿。
  - 本页为验证计划，无现有用户规模。
- **Data class**: scenario；30–50 人与四周均为计划。

#### Slide 14 - 持续服务与额度收费
- **Audience move**: 工具没有收入逻辑 → 理解可以测试的服务收费路径。
- **Relationships**: 基础免费、持续订阅、生成额度、机构工作台是分阶段收入路径 membership；用户价值与收入 link。
- **Title**: 第一笔收入，来自持续服务。
- **Core message**: 免费基础建立习惯，按持续价值与生成成本收费。
- **Content**:
  - 基础：衣柜与计算推荐；订阅假设：高级管理、长期洞察与专属服务；生成额度：OOTD 按次/包；未来 B2B：造型/整理服务商授权工作台。
  - 商业方案待验证，高级服务与机构方案尚未上线；不出售衣柜数据；生成不承诺无限量。

#### Slide 15 - 单位经济情景
- **Audience move**: 只听收入想象 → 知道需要验证的转化、价格与成本。
- **Relationships**: 活跃人数→会员人数→年订阅收入 order；收入与成本 contrast。
- **Title**: 先算清一位用户，再放大市场。
- **Core message**: 收费必须覆盖持续成本，生成费用单列核算。
- **Content**:
  - 情景演算：10,000 活跃用户、5% 转化、500 年费会员、199 元/年，对应年订阅收入 99,500 元（9.95万元）。
  - 未扣获客、服务器、存储、支持与税费；不是预测或净利润。
  - 生成额度单列成本；推荐计算无远程模型决策费，但非零成本；验证转化/留存/单位成本后再扩张。
- **Data class**: scenario；本页全部商业数字为示意假设。

### Part 4: 团队与下一步

#### Slide 16 - 新团队，用作品建立信任
- **Audience move**: 按过往奖项判断 → 理解新团队已有作品证据。
- **Relationships**: 首次参赛与现有作品 contrast；产品闭环、算法依据、工程保障 membership 于交付证据。
- **Title**: 新团队，拿作品建立信任。
- **Core message**: 没有过往竞赛奖项；已做出的系统是本次实力依据。
- **Content**:
  - 全新团队·首次参赛·暂无过往竞赛奖项；未补造人数、成员履历或荣誉。
  - 产品闭环：前后端与个人 OOTD；算法依据：领域规则、风格画像、反例与快照；工程保障：持久任务、数据归属、CI/接口契约。
  - 当前证据为实现与既有验证记录，用户与商业验证是下一步。

#### Slide 17 - 从可演示到可复用
- **Audience move**: 以为已商业成熟 → 看清迭代和验收路线。
- **Relationships**: 现有系统→30天共创→90天付费验证→180天合作试点 order。
- **Title**: 下一阶段，把可演示变成可复用。
- **Core message**: 每阶段以证据验收，不以功能数量验收。
- **Content**:
  - 已有：产品/技术闭环；30 天目标：修正录入摩擦、四周行为观察；90 天目标：订阅/额度实验、单位成本核算；180 天目标：机构共创、数据库和容量评估。
  - 时间为路线图示意，非保证；入柜耗时、实际穿着覆盖、留存、付费与成本为验证信号。
- **Data class**: scenario；30/90/180 天为目标。

#### Slide 18 - 共创验证
- **Audience move**: 理解项目 → 记住价值并知道可参与的下一步。
- **Relationships**: 已有衣物与新机会 link；共创参与与验证 link。
- **Composition**: 明亮行动色域承载最后的主张，衣物与封面呼应但形成新的选择。
- **Title**: 给已有衣物，一个新的出场机会。
- **Core message**: 让更多已有衣物真正进入日常选择，邀请首批共创者验证。
- **Closing impact**: 给已有衣物，一个新的出场机会；行动聚焦首批共创验证。
- **Content**:
  - 鱼搭：理解衣柜，解释选择，持续反馈。
  - 下一步：招募首批共创者，共同验证更好用的衣柜；可持续利用为愿景，未量化消费或减排效果。

## X. Speaker Notes Requirements

- **Generation**: enabled
- **Filename**: match each SVG filename under `notes/`
- **Content**: 以最终页面为依据，每页一段讲稿加来源和答辩边界；历史与商业情景分别说明；不虚构团队奖项。
- **Total duration**: 约 10 分钟，按现场节奏可缩短。
- **Notes style**: 中文口语化、事实清楚、解释与转场相接。
- **Presentation purpose**: 解释价值、证明实现、提出市场与收入验证路线。
