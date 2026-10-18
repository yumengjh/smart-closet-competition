# 服务商实测 · 2026-09-28

服务商：https://api.yumg.cn/ 。使用用户提供的密钥；密钥不包含在此报告或版本管理中。

## 上游更新后的最新结果 · 17:09–17:13

重新读取 `/v1/models`，模型数从 20 增至 26。新生图 ID 为 `gpt-image-2.5-flare` 和 `gpt-image-2.5-sunburst`；另新增 gpt-6、gpt-6-astra、gpt-6-luna、gpt-6-sol，未将其作为生图模型测试。

| 模型 | 本次路径 | 结果 | 生图步骤耗时 |
| --- | --- | --- | --- |
| gpt-image-2.5-flare | 文生图 `/v1/images/generations` → U2Net → 贴纸 | 三步成功 | 36.87 秒 |
| gpt-image-2.5-sunburst | 图生图 `/v1/images/edits` | 服务商 HTTP 504，后续步骤跳过 | 60.26 秒 |

两次均使用 size=1024x1024、quality=low、output_format=png、n=1。flare 请求仅使用文字；sunburst 使用现有公开样图 artf-260 的校正照片，没有使用用户上传的私人图片。无自动重试。

flare 实际返回 **1312×1199**，未遵守本次请求的 1024×1024 尺寸；本地贴纸按既有规则输出 1024×1024。目视确认生成了完整的蓝色短袖衣物。usage 为 input_tokens=48、output_tokens=829、total_tokens=877，没有返回金额。

sunburst 的失败是服务商返回 HTTP 504，约 60 秒时发生，早于本地 180 秒超时。不能据此断言该模型完全不可用，也尚未验证其文生图。flare 的图生图本轮未测；不将单次文生图成功扩展为所有能力均可用。

本机默认模型更新为 **gpt-image-2.5-flare**。详细结果见 [upstream-refresh-results.json](upstream-refresh-results.json)。

- [flare 生图](flare-generate.png)
- [flare 抠图](flare-segment.png)
- [flare 贴纸](flare-sticker.png)

## 上游更新前的记录

`GET /v1/models` 返回 HTTP 200，共 20 个模型。生图候选为 `gpt-image-1`、`gpt-image-1.5`、`gpt-image-2`。服务商识别 OpenAI Images 路径，但本轮 **0 张生成成功**，暂不能将任何一个候选称为已验证可用。

| 请求 | 参数 | HTTP | 耗时 | 服务商错误 |
| --- | --- | --- | --- | --- |
| gpt-image-1 | n=1, 1024x1024, low | 502 | 1.8 秒 | Upstream request failed |
| gpt-image-1.5 | n=1, 1024x1024, low | 502 | 1.3 秒 | Upstream request failed |
| gpt-image-2 | n=1, 1024x1024, low | 502 | 1.1 秒 | Upstream request failed |
| gpt-image-1.5 最小参数 | 仅 model + prompt | 503 | 0.1 秒 | No available compatible accounts |

前三次请求提示词为单件蓝色 T 恤、完整平铺、白底，无用户图片。最小请求用于排查可选参数影响。所有调用均为 `/v1/images/generations`，没有自动重试。

用户已表示检查密钥分组和上游，因此暂停追加远程生图测试。图生图 `/v1/images/edits` 和 Gemini 原生接口仅通过本地模拟协议测试，尚未在此服务商成功实测。未上传用户照片。没有费用查询数据，无法断言失败请求是否计费。

## 上游恢复后的验证

1. 在 `/workflow/index.html` 选择“文字 → AI 生图 → 抠图 → 贴纸”，确认能下载真实图片。
2. 再用公开样图选择“照片 → AI 整理 → 抠图 → 贴纸”，验证 multipart 编辑接口。
3. 对照原图检查颜色、款式、图案、领口与袖子；接口成功只验证连通性。
4. 成功的模型及参数组合再作为常用配置，不依据候选名单自动切换模型或付费重试。

机器可读记录：`provider-check.json`。
