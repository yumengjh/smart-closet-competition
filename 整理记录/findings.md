# 扫描发现

扫描日期：2026-10-13。事实以本轮文件核对为准。

- 后端 pom 声明 Java 21、Spring Boot 4.1.1、MyBatis Plus 3.5.17、H2、Flyway、JDBC Session、ONNX Runtime 1.30.0、JavaCPP/OpenCV。
- 用户端声明 Vue 3、TypeScript、Vite、Pinia、Vue Router、Ant Design Vue、Konva、Foley；build:server 经脚本发布到后端 static。
- Agent 是独立 Node.js / TypeScript / LangGraph / LangChain / Zod 运行时；声明 Node >=22。
- 仓库已有未提交业务及文档改动，整理任务仅新增 competition 文件。
- 尚未发现可用的个人写作检索工具；遵循当前中文任务与明确表达偏好，不宣称已匹配历史写作样本。

- 当前版本：后端 02bc6bf0849c1432dbe56334f9416e35e9cff124；用户端 6ff54017df4a808ce741d2c4cc81ffb4fd16392c，双方均有未提交改动。
- 后端有 108 个 *Test.java 测试类、用户端有 93 个 Vue 文件；数量仅为源文件盘点，不代表本轮通过数。
- 推荐引擎源码已核对：按位置召回、自由组合与已审核搭法两条路径、统一打分、多样化与曝光均衡；当前为 v4，历史 P1 七维已扩展为审美维度。
- 本地文本向量、Chinese-CLIP 和 U²-Net 均复用现成预训练模型，不宜宣称自研基础模型。推荐主引擎纯计算，搜索可有本地编码推理；聊天、识图、生图仍会调用上游。
- P1 报告字符数降幅 94%–96%，并非 token/费用实测；审美报告的 49→97 件来自 167 件仿内测衣柜连续 28 天模拟，不是现实穿着率。
- 官方竞品核查：Acloset 已公开推荐、AI聊天、入柜和虚拟试穿；Whering 有日常建议与社交衣柜；Stylebook 有搭配拼贴、规划和统计。不能宣称这些基础功能是鱼搭独有。
- 原文旧分支及待合并状态是历史记录，不用于判断当前 HEAD 是否含有实现。
- 路由文件实际为 ../smart-closet/src/router.ts，首次按 index.ts 读取失败已纠正。

- 当前规则资源：11 个评分维度、24 个风格画像、74 条搭法资源条目、105 格颜色对/78 格材质对；74 条不等于 74 条线上生效，仍受审核叠加状态影响。
- 当前后端有 V1–V27 共 27 个 H2 迁移文件，V27 属于现有未跟踪改动；不宣称当前数据库已应用 V27。
- 文本向量默认 fp32，CLIP 默认 int8；本机存在七个 ONNX 文件，仅核对存在和字节数，本轮未验证推理、加载或完整性。
- 源码组织差异：recommend 引擎直接 import agent.OutfitRules，不能沿用原设计“推荐包完全不依赖 agent 包”的表述；其计算过程不调用远程模型。
- GitHub Actions 后端包主动排除本地 SPA 与测试前端夹具；同源本地发布和独立容器部署要分别说明。
- 个人 OOTD 是生成式效果预览，不是服装尺寸/物理合身模拟；姿势关节坐标由识图估计，以文字进入生图，不是专业姿态检测网络。
- 前端 CI 文件实际为 .github/workflows/frontend.yml（Node 24）；Agent CI 使用 Node 22。首读 ci.yml 失败已纠正。
