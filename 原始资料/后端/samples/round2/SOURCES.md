# 第二轮原图与筛选记录

固定日期：2026-09-27。先查看原图并固定清单，再运行任何分割算法；没有根据分割结果增删样本。

## 来源与许可

- 数据集：[aRTF Clothes Dataset](https://github.com/tlpss/aRTF-Clothes-dataset)，[Zenodo DOI 10.5281/zenodo.10875542](https://doi.org/10.5281/zenodo.10875542)。
- 作者：Thomas Lips、Victor-Louis De Gusseme、Francis wyffels。
- 数据许可：[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)。许可针对数据，仓库代码的 MIT 许可不能替代图片许可。
- 作者指定引用：Lips et al., *Learning Keypoints for Robotic Cloth Manipulation using Synthetic Data*, 2024，[论文](https://arxiv.org/abs/2401.01734)。这里使用的 aRTF 图片为真实拍摄。
- 图片取自原始 `aRTFClothes-rgb.zip` 的 test 部分，未裁剪、缩放、重画或修改原图。归档内完整路径、原始尺寸、SHA-256 与参考多边形均保存在 [manifest.json](manifest.json)。
- 参考轮廓来自作者发布的 [tshirts-test.xml](https://github.com/tlpss/aRTF-Clothes-dataset/blob/main/data/aRTFClothes/tshirts-test.xml)，属于借助 Segment Anything 制作的半自动标注，并非逐像素人工真值。
- 报告中的透明图、蒙版与拼图是本项目由这些原图产生的衍生结果。原作者未对本项目背书。

## 固定样本

主对照共 12 张：7 张床单、2 张沙发、2 张木桌、1 张木条桌。床上包含 7 件不同颜色/花纹的上衣；紫色和绿色两件同时出现在其他场景，所以 12 张不等于 12 件不同衣服。

| 编号 | 场景/衣物 | 原图观察 |
| --- | --- | --- |
| 200 | 床单、紫色 | 完整单件，有褶皱 |
| 208 | 床单、黑橙花纹 | 无袖上衣，花纹复杂 |
| 216 | 床单、浅灰 | 完整单件，有褶皱 |
| 228 | 床单、酒红 | 完整单件，肩部起伏 |
| 240 | 床单、绿色 | 斜放，有阴影 |
| 248 | 床单、蓝色 | 与床单颜色相近，保留为困难样例 |
| 260 | 床单、橙红 | 倒置，颈肩有皱折 |
| 100 | 木条桌、绿色 | 桌面接缝、斑点、设备影子 |
| 120 | 沙发、紫色 | 靠垫、扶手在旁，未遮挡 |
| 140 | 沙发、绿色 | 有自然褶皱 |
| 280 | 木桌、紫色 | 靠近桌边，衣物仍完整入镜 |
| 320 | 木桌、绿色 | 衣身皱折明显 |

## 未纳入主对照的候选

原 16 张候选和额外 5 张分别保留在 `../round2-candidates/` 与 `../round2-additional/`，可复核选图。以下决定在算法运行前作出：

- 000、020、360：袖子或衣身明显内折/堆叠，不适合主平铺条件。
- 080：下摆距图像底边约 6 像素，留白不足，保留为边界样例；不武断认定它一定缺失衣物。
- 040、060、160、180、380：优先把有限比较量用于床单及不同衣物，因此本轮未纳入；并非判定它们都不合格。

## 复现

项目已有图片时不需要下载。需要恢复原图时，在根目录运行：

```bash
python3 scripts/fetch-artf-samples.py samples/round2/manifest.json --output samples/round2
```

脚本只使用已有 Python 标准库与 curl，不安装软件，按 HTTP Range 读取所需 ZIP 条目；完整条目进行 ZIP CRC 校验，比较测试再核对固定的 SHA-256。下载缓存位于 `target/artf-ranges/`，不下载整个 7 GB 压缩包。

## 局限

这是一小批人工筛选的探索性样本，不是随机抽样评测。床单只有一种蓝色波点背景，衣物以短袖/无袖上衣为主；白衣白床单、蕾丝、肩带、黑衣黑背景、裤装等还未覆盖。不能把本轮数字当通用准确率。
