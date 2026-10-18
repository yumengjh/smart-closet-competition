# 鱼搭 PWA 设计文档

> 状态：已实现 · 2026-10-07
> 范围：前端仓库 `smart-closet`；后端 `smart-closet-server` 无代码改动，仅通过发布脚本接收新增静态文件。

## 1. 背景与目标

鱼搭此前只能在浏览器标签页中使用。手机用户需要每次打开浏览器、输入或查找地址；电脑用户的衣柜页面混在大量标签页里，也没有独立的图标和窗口。

本次为鱼搭加入 Progressive Web App（PWA）支持：

1. **可安装**：在主流系统与浏览器中可以把鱼搭安装到桌面、程序坞、开始菜单或手机主屏幕，以独立窗口打开。
2. **安装入口统一放在 `/settings`**：新增「安装应用」分类，浏览器支持时提供一键安装按钮，不支持时给出当前设备的手动步骤。
3. **覆盖主流系统的快速指引**：iPhone / iPad、Android、Windows、macOS、Linux、ChromeOS。
4. **弱网可打开**：缓存应用外壳与静态资源，断网时仍能打开界面，而不是浏览器的离线错误页。

### 非目标

- **不做离线数据**：衣物、穿搭、任务等业务数据仍然实时请求接口，不在本地缓存，也不支持离线编辑后同步。
- **不做推送通知、后台同步、文件处理、分享目标**等扩展能力。
- **不引入 `vite-plugin-pwa` / Workbox**：现有缓存需求简单，手写 Service Worker 约 80 行即可覆盖，避免新增依赖和构建期配置。
- **不改变后端**：后端已对非 `/api/**` 路径放行，静态文件可直接访问。

## 2. 总体结构

```
index.html ──────────── <link rel="manifest">、apple-touch-icon、iOS meta
public/
  manifest.webmanifest ─ 应用名称、图标、启动地址、显示模式、快捷方式
  sw.js ─────────────── Service Worker（缓存策略见 §4）
  icons/ ────────────── 由 scripts/generate-pwa-icons.swift 生成
src/
  main.ts ───────────── 启动时调用 installPwa()
  services/pwa.ts ───── 注册 SW、捕获安装事件、暴露安装状态
  domain/install-platform.ts ─ 纯函数：识别系统/浏览器、指引数据、不可安装原因
  views/SettingsPage.vue ───── 新增「安装应用」分类
  views/settings/SettingsInstallSection.vue ─ 安装按钮与各系统指引
scripts/
  generate-pwa-icons.swift ─── 图标生成
  publish-to-server.mjs ────── 发布时一并复制 manifest、sw.js、icons/
tests/install-platform.test.ts ─ 平台识别与指引的单元测试
```

依赖关系是单向的：`domain/install-platform.ts` 不依赖浏览器环境，可在 Node 测试中直接运行；`services/pwa.ts` 负责所有浏览器 API；设置页组件只读状态、调用 `promptInstall()`。

## 3. Web App Manifest

文件：`public/manifest.webmanifest`，在 `index.html` 中通过 `<link rel="manifest" href="/manifest.webmanifest">` 引用。

| 字段 | 取值 | 说明 |
| --- | --- | --- |
| `id` | `/` | 应用身份固定，以后修改 `start_url` 不会被浏览器视为另一个应用 |
| `name` / `short_name` | 鱼搭 · 数字衣柜 / 鱼搭 | 与 `<title>` 一致；主屏图标下显示短名 |
| `start_url` | `/wardrobe` | 直接进入衣柜，避免 `/` 重定向多一跳；未登录时由路由守卫转到 `/login` |
| `scope` | `/` | 全站都在应用窗口内打开 |
| `display` | `standalone` | 独立窗口，无地址栏 |
| `background_color` / `theme_color` | `#f7f8fa` | 与浅色主题的 `--paper` 一致，启动闪屏不跳色 |
| `orientation` | `any` | 画板在平板横屏下也可用 |
| `icons` | 192、512（`any`），512（`maskable`） | 见 §5 |
| `shortcuts` | 录入衣物 `/add`、穿搭 `/outfits` | 长按 / 右键应用图标可直达 |

**未采用 `window-controls-overlay`**：它会让内容延伸到标题栏，需要为顶栏重新处理拖拽区域和安全边距，收益不大，先保持标准独立窗口。

**主题色**：manifest 中的 `theme_color` 是静态的浅色值。运行时 `stores/theme.ts` 已会同步修改 `<meta name="theme-color">`，深色主题下标题栏/状态栏仍会跟随为 `#191c23`。按 AGENTS 约定，默认浅色。

### iOS 补充 meta

iOS Safari 对 manifest 的支持不完整，`index.html` 额外加入：

```html
<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-title" content="鱼搭" />
<meta name="apple-mobile-web-app-status-bar-style" content="default" />
```

状态栏样式选择 `default` 而非 `black-translucent`：后者会让页面顶到状态栏下面，需要给顶栏增加 `env(safe-area-inset-top)` 处理；现有布局只处理了底部安全区（移动端底部导航）。

## 4. Service Worker

文件：`public/sw.js`，注册在根作用域 `/`。

### 4.1 设计原则

1. **业务数据永远不进缓存。** 鱼搭涉及登录 Cookie、CSRF Token、私有图片（`/api/me/private-media/*` 明确声明 `no-store`）和 SSE 流式输出，任何缓存错误都可能造成串号、数据陈旧或流中断。
2. **发布后立刻生效。** 页面入口每次都走网络，不会出现「部署了但用户还在看旧版本」的问题。
3. **只拦截明确认识的请求。** 不认识的请求不调用 `respondWith`，交给浏览器默认处理，行为与没有 Service Worker 时完全一致。

### 4.2 请求分类

| 请求 | 处理 | 缓存 |
| --- | --- | --- |
| 非 `GET`、带 `Range` 头、跨域 | 不拦截 | — |
| `/api/**`、`/workflow/**`、`/studio/**` | 不拦截 | — |
| 页面导航（`request.mode === 'navigate'`） | 网络优先，离线回退 | `yuda-shell-v1` 中的 `/index.html` |
| `/assets/**`（Vite 带哈希产物） | 缓存优先 | `yuda-assets-v1`，最多 160 条 |
| `/icons/**`、`/illustrations/**`、`/person-stickers/**`、`/licenses/**`、`/yuda-logo.png`、`/favicon.svg`、`/manifest.webmanifest` | 先返回缓存，后台更新 | `yuda-static-v1` |
| 其他同源 GET | 不拦截 | — |

### 4.3 各策略细节

**页面导航——网络优先**

- 网络成功且响应为 `text/html` 时，把响应写入 `yuda-shell-v1` 的 `/index.html` 键下，作为离线兜底。所有 SPA 路由（`/wardrobe`、`/garment/:id` 等）返回的都是同一份 `index.html`，因此只存一份。
- 网络失败时返回缓存的 `/index.html`；若从未缓存过，则抛出原始错误，由浏览器展示默认离线页。
- 导航请求的重定向模式为 `manual`，后端若返回重定向，得到的是 `opaqueredirect`，`ok` 为 false，不会被写入缓存，并原样交还浏览器处理。
- 离线时页面能打开，但接口请求会失败，各页面沿用现有的错误与重试提示。

**`/assets/**`——缓存优先**

- Vite 产物文件名带内容哈希，同名即同内容，命中缓存可直接使用。
- 每次写入后按插入顺序裁剪到 160 条，防止多次发布后缓存无限增长。当前构建约几十个文件，160 条可容纳若干个版本的懒加载块。
- 附带收益：旧页面在发布后懒加载已从服务器删除的旧块时（`publish-to-server.mjs` 会清空旧 `assets/`），如果该块曾被缓存，仍可正常加载。

**其他静态资源——先返回缓存，后台更新**

- 这些文件名不带哈希，但很少变化。有缓存时立即返回，同时在 `event.waitUntil` 中刷新，下次访问即为新版本。
- 无缓存时等待网络结果。

### 4.4 生命周期与版本

- `install`：预缓存 `/index.html`、manifest、Logo 与两张主图标，随后 `skipWaiting()`。
- `activate`：删除所有以 `yuda-` 开头但不在当前已知列表中的缓存，然后 `clients.claim()`，首次安装后当前页面即受控。
- **为什么可以直接 `skipWaiting`**：入口页总是走网络，静态产物带哈希，新旧 Service Worker 的缓存行为兼容，不存在「新 SW 配旧页面」导致资源错配的问题。
- **何时需要改版本号**：只有当缓存策略或缓存内容格式变化时，才把 `yuda-*-v1` 改为 `v2`，激活时旧缓存会被自动清理。日常发布无需修改 `sw.js`。
- 浏览器每次导航都会检查 `sw.js` 是否变化（默认最多使用 24 小时 HTTP 缓存），修改后会自动更新。

### 4.5 注册条件

`src/services/pwa.ts` 中的 `installPwa()` 在 `main.ts` 挂载应用前调用，满足以下全部条件时才注册：

- `import.meta.env.PROD` 为真：开发环境不注册，避免缓存干扰 Vite 热更新；
- 浏览器支持 `serviceWorker`；
- `window.isSecureContext`：HTTPS 或 `localhost`。

注册放在 `load` 事件之后，不与首屏资源争抢带宽；注册失败静默忽略，离线能力是增强项，不影响正常使用。

## 5. 图标

源图：`public/yuda-logo.png`（1428 × 1102，透明背景，非正方形）。生成脚本：`scripts/generate-pwa-icons.swift`（使用 macOS 自带 AppKit，无需安装依赖）。

```bash
swift scripts/generate-pwa-icons.swift
```

| 文件 | 尺寸 | Logo 宽度占比 | 背景 | 用途 |
| --- | --- | --- | --- | --- |
| `icon-192.png` | 192 | 86% | 透明 | manifest `any`，Android 启动器、桌面快捷方式 |
| `icon-512.png` | 512 | 86% | 透明 | manifest `any`，安装弹窗、启动闪屏 |
| `maskable-512.png` | 512 | 62% | `#f7f8fa` | manifest `maskable`，Android 自适应图标 |
| `apple-touch-icon.png` | 180 | 72% | `#f7f8fa` | iOS 主屏幕 |

- **maskable 安全区**：系统可能把图标裁成圆形、圆角方形或水滴形，只保证中心直径 80% 的圆内可见。Logo 宽 62%、高约 48%，包围盒半对角线约为边长的 39%，小于安全圆半径 40%，四角不会被裁掉。
- **iOS 必须实底**：iOS 会把透明像素渲染成黑色，因此 `apple-touch-icon` 铺了与浅色主题一致的底色。
- 更换 Logo 后重新运行脚本即可；脚本按源图实际宽高比计算，不依赖固定尺寸。

## 6. 安装流程与状态

### 6.1 状态来源（`src/services/pwa.ts`）

| 导出 | 类型 | 含义 |
| --- | --- | --- |
| `installPlatform` | `{ os, browser }` | 启动时识别一次的当前系统与浏览器 |
| `canPromptInstall` | `ComputedRef<boolean>` | 浏览器是否提供可调用的一键安装弹窗 |
| `appInstalled` | `Readonly<Ref<boolean>>` | 当前是否以已安装应用的方式运行 |
| `promptInstall()` | `Promise<'accepted' \| 'dismissed' \| undefined>` | 唤起原生安装弹窗 |
| `installPwa()` | `void` | 启动时调用：注册监听与 Service Worker |

**为什么在 `main.ts` 中尽早监听**：Chromium 系浏览器满足安装条件后会派发一次 `beforeinstallprompt`，时间点通常在页面加载后不久。如果等用户进入设置页再监听，事件早已错过，按钮将永远不会出现。因此在应用启动时就 `preventDefault()` 并保存事件对象，设置页只读取状态。

**安装状态判断**：
- `display-mode: standalone` 媒体查询命中，或 iOS 的 `navigator.standalone` 为真，即视为已安装；
- 监听该媒体查询的 `change` 事件，以及 `appinstalled` 事件，状态实时更新。

**`promptInstall()` 的约束**：`prompt()` 每个事件只能调用一次，因此调用前先清空保存的事件；用户取消后按钮会暂时消失，直到浏览器再次派发 `beforeinstallprompt`。

### 6.2 平台识别（`src/domain/install-platform.ts`）

`detectInstallPlatform(userAgent, maxTouchPoints)` 是纯函数，便于测试。

**系统判断顺序**（先匹配者优先）：

1. `iPhone|iPad|iPod`，或 `Macintosh` 且 `maxTouchPoints > 1` → `ios`。iPadOS 13 起默认请求桌面版网站，UA 与 Mac 一致，只能用触控点数区分；
2. `Android` → `android`；
3. `CrOS` → `chromeos`（Chromebook UA 含 `X11`，必须先于 Linux 判断）；
4. `Windows` → `windows`；
5. `Macintosh|Mac OS X` → `macos`；
6. 其余 → `linux`。

**浏览器判断顺序**：

1. 应用内置浏览器（微信 `MicroMessenger`、QQ、微博、钉钉、飞书 `Lark`、支付宝、Facebook、Instagram、Line）→ `in-app`。必须最先判断，因为它们的 UA 同时含有 `Chrome` 或 `Safari`；
2. `SamsungBrowser` → `samsung`（UA 含 `Chrome`）；
3. `Edg/`、`EdgA/`、`EdgiOS/` → `edge`（UA 含 `Chrome`）；
4. `Firefox/`、`FxiOS/` → `firefox`；
5. `CriOS/`、`Chrome/` → `chrome`；
6. `Safari/` → `safari`（几乎所有浏览器 UA 都含 `Safari/`，所以放最后）；
7. 其余 → `other`。

UA 识别只用于**默认选中哪份指引**和**是否显示不可安装提示**，不限制任何功能；识别错误时用户仍可手动切换。

### 6.3 不可安装的环境（`installBlocker`）

| 条件 | 提示 |
| --- | --- |
| `in-app` | 当前在应用内置浏览器中，无法安装。请点右上角菜单，选择「在浏览器中打开」后再试。 |
| `firefox` 且系统不是 Android / iOS | Firefox 桌面版暂不支持安装网页应用，请改用 Chrome、Edge 或 Safari 打开。 |
| 非安全上下文（非 HTTPS 且非 localhost，在组件中判断） | 安装需要 HTTPS 连接，请通过 https:// 地址访问后再试。 |

Firefox Android 支持「添加到主屏幕」；iOS 16.4 起第三方浏览器也可通过分享菜单添加到主屏幕，因此这两种情况不提示。

## 7. 设置页交互

### 7.1 入口

`SettingsPage.vue` 的分类列表末尾新增：

| 字段 | 值 |
| --- | --- |
| key | `install` |
| 标签 / 副标题 | 安装应用 / 桌面与主屏幕 |
| 描述 | 把鱼搭安装到电脑或手机，像应用一样独立打开。 |
| 图标 | `DownloadOutlined` |
| 隐藏条件 | 首次登录（需先修改初始密码） |

可通过 `/settings?section=install` 直达，沿用设置页已有的 PC 左右分栏和移动端子页面返回逻辑。便携登录用户也可见：安装与账号权限无关。

### 7.2 「安装到这台设备」卡片

状态从上到下判断：

```
已安装（standalone）
  └─ 成功提示：鱼搭已安装，当前正以应用模式运行。
否则
  ├─ 非安全上下文 → 警告：需要 HTTPS
  ├─ 否则若有 installBlocker → 警告：对应原因
  ├─ 若刚操作过 → 结果提示（已开始安装 / 已取消安装）
  └─ canPromptInstall ?
       ├─ 是 → 主按钮「安装鱼搭」（loading 态防重复点击）
       └─ 否 → 文案：当前浏览器不提供一键安装，请按下方「<当前系统>」步骤手动添加。
```

- 用户确认安装后播放 `success` 音效（`src/services/sound.ts`，尊重全局音效开关）；按钮点击音由全局交互音效统一处理，不重复播放。
- Safari、iOS 上的所有浏览器、Firefox Android 都不提供 `beforeinstallprompt`，会直接显示手动指引文案。

### 7.3 「各系统安装指引」卡片

- `a-segmented` 切换六个系统，默认选中当前设备，并在标签后标注「· 本机」。
- 窄屏下选项自动换行（`:deep(.ant-segmented-group) { flex-wrap: wrap }`），避免横向滚动时选中项被遮挡。
- 每份指引包含：支持的浏览器、编号步骤、可选补充说明。

| 系统 | 支持的浏览器 | 主要步骤 |
| --- | --- | --- |
| iPhone / iPad | Safari（iOS 16.4 起 Chrome、Edge 也可） | 分享 → 添加到主屏幕 → 添加 |
| Android | Chrome、Edge、三星浏览器 | ⋮ 菜单 → 安装应用 / 添加到主屏幕 |
| Windows | Edge、Chrome | 地址栏「安装」图标，或菜单 → 应用 → 安装鱼搭 |
| macOS | Safari 17+、Chrome、Edge | Safari：文件 → 添加到程序坞；Chrome / Edge：地址栏「安装」图标 |
| Linux | Chrome、Edge、Chromium | 地址栏「安装」图标，或菜单 → 投射、保存和分享 → 安装 |
| ChromeOS | Chrome | 同上，安装后在启动器中打开 |

### 7.4 约定遵循

- 所有交互控件使用 Ant Design Vue（`a-button`、`a-alert`、`a-segmented`）；步骤列表是纯展示的 `<ol>`，不涉及交互。
- 样式只使用现有语义变量（`--surface-alt`、`--muted-copy`、`--space-*` 等）和设置页已有的 `.settings-group`、`.settings-hint` 类，深浅主题自动适配。
- 无新增动画，不涉及 `prefers-reduced-motion`。

## 8. 构建与发布

- `public/` 下的文件由 Vite 原样复制到 `dist/`，无需额外配置。
- `scripts/publish-to-server.mjs`（`npm run build:server` / `npm run deploy:local` 使用）新增复制：
  - `manifest.webmanifest`、`sw.js` → 后端 `static/` 根目录；
  - `icons/` → 后端 `static/icons/`。
- 后端 `SecurityConfiguration` 对非 `/api/**`、`/workflow/**`、`/studio/**` 路径 `permitAll`，Spring Boot 默认静态资源处理即可提供这些文件。
- **Service Worker 必须位于站点根路径** `/sw.js`，否则作用域无法覆盖全站；不要把它移入 `assets/`。
- 独立部署（`npm run build:standalone`）时，前端静态站点需同样以根路径提供上述文件。

### 部署后检查

1. 以 HTTPS 打开站点，开发者工具 → Application → Manifest，确认无报错、图标正常显示；
2. Application → Service Workers，确认 `/sw.js` 处于 activated 状态；
3. 访问 `/manifest.webmanifest` 返回 200。Spring 可能不认识 `.webmanifest` 扩展名而返回 `application/octet-stream`，Chrome 不校验该类型，但如需严格合规，可在后端补充 MIME 映射 `application/manifest+json`；
4. Network 面板勾选 Offline 刷新页面，应能看到界面（接口报错属预期）。

## 9. 测试

### 单元测试

`tests/install-platform.test.ts`（`npm test`）：

- 识别 iPhone Safari、伪装成 Mac 的 iPad（`maxTouchPoints = 5`）、真实 Mac（`maxTouchPoints = 0`）、Android Chrome、三星浏览器、Windows Edge、Chromebook、微信内置浏览器；
- 微信与 macOS Firefox 返回对应的不可安装提示，Windows Edge 无提示；
- 六个系统都有非空的安装指引。

### 已完成的手动验证

使用 mock 模式构建（`VITE_USE_MOCKS=true vite build`）并 `vite preview`，在 Chrome 中：

- `/sw.js` 注册成功并处于激活状态，`yuda-shell-v1` 预缓存 5 条，访问页面后 `yuda-assets-v1` 写入产物；
- `/manifest.webmanifest` 返回 200；
- `/settings?section=install` 在桌面 1280 宽、手机 390 宽，浅色与深色主题下布局正常。

### 待真机验证

- Android Chrome、Windows / macOS Chrome 与 Edge 上「安装鱼搭」按钮出现并完成安装（`beforeinstallprompt` 的派发时机由浏览器的参与度规则决定，自动化环境中可能不出现）；
- iOS Safari 添加到主屏幕后图标、名称、状态栏显示；
- Android 自适应图标在圆形遮罩下不被裁切；
- 已安装应用中设置页显示「已安装」状态。

## 10. 风险与后续

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| Service Worker 缓存逻辑出错 | 用户可能长期拿到错误资源 | 入口页始终走网络；业务请求一律不拦截；如需紧急止损，可发布一个只做 `caches.delete` 并 `self.registration.unregister()` 的 `sw.js` |
| `assets` 缓存与服务器不一致 | 理论上无 | 文件名带内容哈希，同名即同内容 |
| UA 识别不准 | 默认指引选错 | 仅影响默认选中项，用户可手动切换 |
| iOS 独立窗口中 Cookie 与 Safari 不共享 | 安装后需重新登录一次 | 属系统行为；便携登录链接可帮助在新环境登录 |

后续可选方向：

- 新版本可用时提示刷新（监听 `registration.waiting`，当前因 `skipWaiting` 与网络优先策略暂不需要）；
- 在 manifest 中补充 `screenshots`，让 Android / 桌面 Chrome 显示更丰富的安装弹窗；
- 接入 Web Share Target，从系统分享菜单直接收录衣物照片。
