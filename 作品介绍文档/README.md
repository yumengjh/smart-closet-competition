# 作品介绍文档

- 正文：[鱼搭作品介绍文档.md](鱼搭作品介绍文档.md)
- 配图：`images/`（`fig-*` 为图表，`shot-*` 为真实界面截图，`cover-illustration.jpeg` 取自团队原 PPT）
- 图表源文件：`figures-src/*.html`。修改后进入 `figures-src`，首次执行 `npm i playwright`，再运行 `node render.mjs fig-xxx.html`，PNG 输出到 `images/`。浏览器路径（本机 `~/Library/Caches/ms-playwright/chromium-1228`）写在 render.mjs 顶部，可按需修改。

## 转 PDF 前请注意

1. 封面「所属学校 / 指导老师 / 团队成员」为【待填写】。
2. 公式使用 `$$…$$`，需转换器开启数学公式（Typora 默认支持；pandoc 加 `--mathjax` 或 `--pdf-engine` 配合 LaTeX）。
3. 分页使用 `<div style="page-break-after: always;"></div>`，Typora / 浏览器打印均可识别。
4. 第 6.4 节的 3 项后端失败用例是 2026-10-18 本机运行结果，复核后请同步修改数字。
5. 部分截图早于 10-16 之后的界面更新（图注已标明），若重拍可直接替换同名文件。

## 正式版在思源笔记

2026-10-18 起正式版写在思源「草稿板 / 项目介绍文档」（ID `20261018225009-eoetkgf`），使用思源原生语法（提示块、超级块、公式块、块引用目录、分页样式），在思源中导出 PDF。本目录的 Markdown 为早期草稿；`images/` 中的界面截图已于 10-18 用真实账号重拍，与思源文档一致。
