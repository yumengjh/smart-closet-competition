# 鱼搭 · 数字衣柜

Vue 3、TypeScript、Vite、Vue Router、Pinia 和 Ant Design Vue 4 构成的数字衣柜界面。项目按手机与桌面同时设计，包含登录/首次改密、衣柜、录入、待确认、衣物详情、任务、组合台、平台级鱼搭助手、个人基准人物、OOTD、我的和回收站。

登录页与应用内支持浅色/深色主题切换，选择保存在当前浏览器。穿搭画板导出的图片不受界面主题影响。

[衣物入库最新完整设计](https://github.com/yumengjh/smart-closet-server/blob/main/docs/design/衣物入库最新设计.md) · [平台级鱼搭与个人 OOTD 设计](https://github.com/yumengjh/smart-closet-server/blob/main/docs/design/2026-10-06-平台级鱼搭助手与个人OOTD设计.md) · [页面流程与状态说明](docs/INTERACTION.md) · [后端运行与接口文档](https://github.com/yumengjh/smart-closet-server/blob/main/docs/CLOSET_PRODUCT.md) · [299 项体验清单](https://github.com/yumengjh/smart-closet-server/blob/main/docs/testing/2026-10-07-平台级鱼搭与个人OOTD完整手工体验清单.md)。

前后端为两个私有仓库。需要同源本地发布时，将它们分别检出为相邻的 `smart-closet` 与 `smart-closet-server`；独立前端测试和构建不要求存在后端目录。

## 启动真实界面

```sh
npm ci
npm run dev
```

默认使用真实 API，Vite 将 `/api` 代理到 `127.0.0.1:8080`。登录受邀账号后上传照片，提交成功进入衣物工作台。

流程为：上传照片 → 服务端排队/识别/生成/本地处理 → 查看原图与结果 → 选择展示图并核对信息 → 确认入柜。

- 进度、模型调用和步骤耗时来自服务端；没有结果图时展示明确的等待状态。
- 只识别模式保留原图；AI 失败时保留照片，允许填写信息入柜；问题照片要求重新上传。
- 透明背景需要检查时贴纸步骤会暂停；可检查原图与现有处理结果，选择可用图片入柜。
- 任务终态停止轮询，查询失败退避；刷新页面读取已提交任务，不自动重试付费请求。

后端首次创建管理员：

```sh
CLOSET_BOOTSTRAP_USERNAME=admin CLOSET_BOOTSTRAP_PASSWORD='请替换为至少12位的初始密码' mvn spring-boot:run
```

首次登录先进入“设置新密码”，完成后才加载衣柜与任务。直接打开业务页面和刷新也会先检查会话；改密前不查询业务接口或任务计数。遇到 `401` 会返回登录，`403 PASSWORD_CHANGE_REQUIRED` 会返回密码设置。云端处理沿用后端 `.local/generation.yml` 中的服务商及模型配置。

## 可选界面演示

只有显式设置 `VITE_USE_MOCKS=true npm run dev` 才会使用浏览器示例数据。演示模式会全程标注，禁止提交/重试 AI，不通过定时器伪造完成状态或识别值。正常运行无需设置此变量。

## 构建并由 Spring Boot 同源提供

```sh
npm run build:server
cd ../smart-closet-server
mvn spring-boot:run
```

后端 `src/main/resources/static/assets/` 为忽略的构建产物，不进入 Git；干净检出必须先执行此构建再打包后端。

`build:server` 固定以 `VITE_USE_MOCKS=false` 构建，并发布静态文件到后端 `src/main/resources/static/`。Spring Boot 会在 `/` 和 Vue 页面地址提供应用，API、会话 Cookie 与页面保持同源。正式本地或局域网使用此方式时，不要从另一台电脑启用 Vite 模拟模式。

绑定局域网网卡时使用 `SERVER_ADDRESS=0.0.0.0`，其他设备通过运行服务电脑的局域网 IP 和端口访问；默认地址 `127.0.0.1` 仅供本机。

## 版本号

设置页导航底部显示「前端 v… · 提交号」和「服务端 v… · 提交号」，用来确认线上跑的是哪一版。

- 前端：构建时注入。打 `v*` 标签部署时用标签（`v1.2.0` → `v1.2.0`），否则用 `package.json` 的 `version`；提交号来自 CI 的 `GITHUB_SHA` 或本地 `git rev-parse`。也可用 `CLOSET_APP_VERSION`、`CLOSET_APP_COMMIT` 手动指定。
- 服务端：读公开的 `/api/health`（`version`、`commit`），由后端镜像构建时写入；本地运行显示 `dev`。

## 邀请账号与旧数据

管理员账号由本机命令创建，不开放注册。先停止正在运行的后端，再执行这些命令；它们会更新同一份 H2 文件库，不会启动第二个图片处理 worker：

```sh
mvn spring-boot:run -Dspring-boot.run.arguments="--closet-command=create-user,--username=alice,--initial-password=请替换为至少12位密码"
mvn spring-boot:run -Dspring-boot.run.arguments="--closet-command=reset-password,--username=alice,--initial-password=请替换为至少12位密码"
mvn spring-boot:run -Dspring-boot.run.arguments="--closet-command=disable-user,--username=alice"
mvn spring-boot:run -Dspring-boot.run.arguments="--closet-command=enable-user,--username=alice"
```

管理员可用 `create-admin` 创建另一位管理员。旧单人数据默认保持未归属，先确认目标账号后再执行一次认领：

```sh
mvn spring-boot:run -Dspring-boot.run.arguments="--closet-command=claim-legacy,--username=admin"
```

该命令把未归属的衣物、任务和独立分割结果交给指定账号；旧衣物进入待确认。请先备份数据库文件和 `data/` 图片目录。

## 检查

本机验证使用 Node.js 24.18.0 / npm 11.16.0。测试命令使用 Node 的 `--experimental-strip-types`，需支持该选项的 Node 版本。

```sh
npm run typecheck
npm test
npm run build
```

后端回归检查：在 `smart-closet-server` 执行 `mvn test`。界面关键操作使用受控 API 服务 `src/services/api.ts` 与 `src/services/platform.ts`；模拟模式没有真实登录、云端处理或服务端隔离能力。

GitHub Actions 的 `Frontend checks` 使用 Node.js 24，在干净检出中运行 `npm ci`、测试、类型检查和关闭模拟的构建；不会调用真实 AI 或发布页面。[当前平台功能进度](.planning/platform-agent-ootd/progress.md)。
