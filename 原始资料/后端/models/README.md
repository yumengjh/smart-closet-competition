# 模型文件

执行 `bash scripts/download-model.sh` 下载 U²-Net ONNX 权重（约 176 MB）。这是项目数据文件，不安装 Python 或系统软件。服务不会在启动或处理图片时自行联网下载。

- 网络结构与训练项目：https://github.com/xuebinqin/U-2-Net （Apache-2.0）
- ONNX 发布方：https://github.com/danielgatis/rembg/releases/tag/v0.0.0
- 文件：https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx
- 上游完整性校验：MD5 `60024c5c889badc19c04ad937298a77b`，参考 https://github.com/danielgatis/rembg/blob/main/rembg/sessions/u2net.py 。MD5 用来发现损坏，不作为可信签名。
- 经原始发布文件 MD5 核对后记录的 SHA-256：`8d10d2f3bb75ae3b6d527c77944fc5e7dcd94b29809d47a739a7a728a912b491`。下载脚本固定校验此 SHA-256，使用 16 段并行取回原始文件，组装通过后才替换旧模型。
- 输入：RGB，320×320，NCHW，按图像最大通道值缩放，再使用 ImageNet mean/std；输出首个显著性图，做 min/max 归一化。
- 本实现用 Java 双三次重采样；与上游 Pillow Lanczos 不完全相同。
- 这是通用显著物体分割模型，不验证主体一定是衣物，不返回材质或衣物类别。

## 部署：模型后到、不用重启

- 容器只需把宿主机 `./models` 挂到 `/models`（`compose.yaml` 已配置，向量模型路径也已指向 `/models`）。先只跑容器、之后再拉模型完全可以：在宿主机执行 `bash scripts/install-models.sh`（等于依次执行上面两个脚本），**不需要重启容器**。
- 抠图模型：下一次上传或重处理时才加载，之前没有文件时会提示“未安装模型”或改用 GRABCUT。闲置 10 分钟（`CLOSET_SEGMENTATION_IDLE_UNLOAD`，设为 `0` 常驻）后自动释放内存，下次录入时重新加载，多等约 1 秒。
- 向量模型：文件放好并停止写入 5 秒后，服务自动发现并加载（日志出现“本地向量模型已加载”）。后台任务每 30 秒扫描一次，把**所有用户的全部在架衣物**逐批生成向量（每批 200 件，一次任务最多 5000 件），之后新增或修改的衣物同样自动补算。索引完成前搜索与推荐自动降级为字段加关键词，设置页会显示“智能搜索准备中”。
- 更换模型文件（例如 fp32 换 int8）同样不用重启：版本号随文件内容变化，旧向量自动判为过期并重算。
- 半截文件不会被加载：修改时间不足 5 秒的文件视为仍在复制；加载失败的文件对只会被记住一次，换文件后立即重试，否则每 5 分钟重试。

## 本地文本向量

执行 `bash scripts/download-embedding-model.sh` 安装两个精度版本、词表与分词配置（约 120 MB）。服务只加载已有本地文件，启动与请求期间都不联网下载；文件缺失或损坏时语义功能自动降级为字段加关键词，并在日志与接口中说明。

- 原始模型与许可证：[BAAI/bge-small-zh-v1.5](https://huggingface.co/BAAI/bge-small-zh-v1.5)，MIT。词表、分词配置与 `tokenizer.json` 取自该仓库固定提交 `7999e1d3359715c523056ef9478215996d62a620`。
- ONNX 转换：[Xenova/bge-small-zh-v1.5](https://huggingface.co/Xenova/bge-small-zh-v1.5) 固定提交 `75c43b069aac4d136ba6bc1122f995fedcfd2781`（社区常用转换版本）。

| 本地文件 | 来源 | 字节 | SHA-256 |
|---|---|---|---|
| `embedding-fp32.onnx`（默认） | Xenova `onnx/model.onnx` | 94,851,877 | `69a0b846f4f116b5e6aabf9546ea6754d02264f3211a13a1bd69b31b8040749a` |
| `embedding-int8.onnx` | Xenova `onnx/model_quantized.onnx` | 24,010,842 | `15b717c382bcb518ba457b93ea6850ede7f4f1cd8937454aa06972366cd19bcc` |
| `embedding-vocab.txt` | BAAI `vocab.txt` | 109,540 | `45bbac6b341c319adc98a532532882e91a9cefc0329aa57bac9ae761c27b291c` |
| `embedding-tokenizer-config.json` | BAAI `tokenizer_config.json` | 367 | `e6f3b96db926a37d4039995fbf5ad17de158dfb8f6343d607e4dbaad18d75f5a` |
| `embedding-tokenizer.json` | BAAI `tokenizer.json`（只用于生成分词对拍数据） | 439,125 | `48cea5d44424912a6fd1ea647bf4fe50b55ab8b1e5879c3275f80e339e8fae26` |

以上值均于 2026-10-08 实际下载后核对。脚本先校验长度与 SHA-256，全部通过才替换旧文件。权重与词表不进入 Git；分词对拍数据内嵌了 MIT 许可的词表，供无模型的 CI 验证分词一致。

**输入输出**：三个 int64 批量张量 `input_ids`、`attention_mask`、`token_type_ids`；取 `last_hidden_state` 的 CLS 向量并做 L2 归一化，512 维。只对检索查询加前缀 `为这个句子生成表示以用于检索相关文章：`，衣物描述卡不加。官方分词配置 `do_lower_case=false`、`strip_accents=null`，即保留大小写和重音。

**精度选择（本机 Apple Silicon、2 推理线程、50 张描述卡实测）**：

| | 查询编码中位 / P95 | 单张描述卡中位 / P95 | 批量 10 张每张 | 内存中权重 |
|---|---|---|---|---|
| fp32 | 2.4 / 3.0 ms | 1.5 / 2.0 ms | 0.73 ms | 约 90 MB |
| int8 | 3.2 / 7.6 ms | 1.6 / 3.4 ms | 1.58 ms | 约 23 MB |

int8 与 fp32 的向量余弦一致度：描述卡中位 0.992，查询中位 0.990；检索相似度平均绝对误差 0.015。在本机 int8 并不更快，所以默认使用 fp32；内存紧张的部署机可把 `closet.embedding-model-path` 指向 int8（换版本后后台会自动重算向量）。

配置：`closet.embedding-model-path`、`closet.embedding-vocab-path`、`closet.embedding-max-tokens`（2–512）、`closet.semantic-threshold`（默认 0.5）。

复现分词参考数据（30 条，仅开发时需要）：

```bash
uv run --with tokenizers==0.22.1 python scripts/gen-tokenizer-fixtures.py
mvn -o -Dtest=TokenizerParityTest test
```

复现实测：`mvn -o -Dsemantic.benchmark=true -Dtest=EmbeddingBenchmark test`，结果写入 `.planning/recommend-p2-20261008/benchmark-embedding.json`。真实模型测试在文件存在时自动启用。

## 本地图文模型（可选：相似衣物、重复提醒、超级搜索、用文字找图片）

执行 `bash scripts/export-image-model.sh` 生成（约 6 分钟，需要 uv 与约 6 GB 临时磁盘；在 MacBook 上导出后把文件拷到服务器的 `./models` 即可）。没有官方 ONNX 下载，脚本用官方 PyTorch 权重自行导出，并逐个文件与 PyTorch 对拍，全部通过才放进 `./models`。**服务不联网下载**；没有这些文件时相关功能自动回退为颜色、轮廓比对，文字找图片关闭，界面会提示。

- 模型：Chinese-CLIP ViT-B/16（图像塔 ViT-B/16 86M 参数，文本塔 RoBERTa-wwm-Base 102M 参数，512 维共同空间）。项目：https://github.com/OFA-Sys/Chinese-CLIP ，仓库为 MIT 许可证；权重由同一项目发布，未单独声明许可证。商用前请再确认一次。
- 权重来源：`cn_clip==1.6.0` 自带的下载逻辑（ModelScope `AI-ModelScope/chinese-clip-vit-base-patch16` 或 Hugging Face `OFA-Sys/chinese-clip-vit-base-patch16` 的 `clip_cn_vit-b-16.pt`）。导出后文件的 SHA-256 写在 `image-model-manifest.json`（每次导出生成，请保留）。
- 导出所用版本：torch 2.6.0、onnx 1.23.2、onnxruntime 1.31.0、opset 14；int8 为 onnxruntime 动态量化（权重 QInt8）。文本塔按通道量化（issue #15：按张量量化时真实权重最差只有 0.82）；2026-10-10 前导出的 `image-text-model-int8.onnx` 请重新运行导出脚本替换，图像塔文件不变。

| 本地文件 | 用途 | 大小（约） |
|---|---|---|
| `image-model-int8.onnx`（默认） | 图像塔 | 87 MB |
| `image-model-fp32.onnx` | 图像塔（更高精度，内存多约 330 MB） | 345 MB |
| `image-text-model-int8.onnx`（默认） | 文本塔 | 102 MB |
| `image-text-model-fp32.onnx` | 文本塔 | 408 MB |
| `image-text-vocab.txt` | 文本塔词表（与 `embedding-vocab.txt` 相同） | 110 KB |
| `image-model-check.json` / `.png` | PyTorch 对拍数据，供 `ClipRealModelParityTest` 使用 | 100 KB |
| `image-model-manifest.json` | 各文件字节数与 SHA-256 | — |

**输入输出（官方导出约定）**：图像 `image` float `[1,3,224,224]`，Pillow 双三次直接缩放到 224×224（不裁剪），透明像素先合成到白底，CLIP 均值方差归一化 → `unnorm_image_features` `[1,512]`；文本 `text` int64 `[1,52]`，`[CLS]` + WordPiece（小写、去重音）+ `[SEP]`，0 填充 → `unnorm_text_features` `[1,512]`；两边 L2 归一化后用余弦。Java 实现已在真实结构上对拍：fp32 余弦 1.00000，int8 图像 0.9998、文字 0.9993（随机权重）。真实权重（2026-10-10）：int8 图像 0.963，文字 0.970（按通道量化后）。

**加载与内存**：图像塔闲置 10 分钟、文本塔闲置 30 分钟后释放（`CLOSET_IMAGE_MODEL_IDLE_UNLOAD`、`CLOSET_IMAGE_TEXT_MODEL_IDLE_UNLOAD`），推理中不会卸载；加载前检查可用内存（容器内按 cgroup 限额），低于“文件大小 × 1.5 + 256 MB”就不加载并回退（`CLOSET_IMAGE_MODEL_MIN_FREE_MB` 可改为固定值，设很大可模拟内存不足）。放入或替换文件不用重启；换文件后图像向量自动重算。

**切换精度**：`CLOSET_IMAGE_MODEL_PATH=/models/image-model-fp32.onnx`（或文本塔 `CLOSET_IMAGE_TEXT_MODEL_PATH`）。

**核对与评估**：`mvn -o -Dtest=ClipRealModelParityTest test`（对拍）；`mvn -o -Dtest=ImageModelEvaluation -Dimage.eval=<照片文件夹> test`（效果评估），步骤见 [docs/IMAGE_SEARCH_TESTING.md](../docs/IMAGE_SEARCH_TESTING.md)。
