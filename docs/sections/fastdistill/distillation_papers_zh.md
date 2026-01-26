# 蒸馏论文清单（精选）

面向 FastDistill 的阅读列表。每篇论文给出方法解读与“是否能在本项目中落地优化”的判断。

**可行性标准**
- **高**：可直接并入现有数据管线，或仅需小改动。
- **中**：需要额外产物（logprobs、偏好对等）或自托管教师。
- **低**：依赖隐藏层/梯度或重训练循环改造。

## 基础 KD

| 论文 | 方法解读 | FastDistill 优化路径 | 可行性 | 链接 |
| :-- | :-- | :-- | :-- | :-- |
| Distilling the Knowledge in a Neural Network | 通过温度化软目标迁移教师分布。 | 生成阶段捕获 logprobs 入库；训练时用 KL 贴合软目标。 | 中 | https://arxiv.org/abs/1503.02531 |
| FitNets: Hints for Thin Deep Nets | 对齐中间层表征“提示”。 | 仅在自托管教师下可获取隐藏层并对齐。 | 低 | https://arxiv.org/abs/1412.6550 |
| Born Again Neural Networks | 自蒸馏：学生成为下一轮教师。 | 将迭代蒸馏做成标准流程（run_id 串联 + 教师替换）。 | 高 | https://proceedings.mlr.press/v80/furlanello18a.html |
| LIT: Block-wise Intermediate Representation Training | 分块级中间表示对齐。 | 需要教师暴露 block 输出，仅适用于自托管模型。 | 低 | https://arxiv.org/abs/1810.01937 |

## Transformer KD

| 论文 | 方法解读 | FastDistill 优化路径 | 可行性 | 链接 |
| :-- | :-- | :-- | :-- | :-- |
| DistilBERT | 预训练阶段的 MLM + KD + 余弦对齐。 | 可作为学生预训练配方；需教师隐藏层。 | 中 | https://arxiv.org/abs/1910.01108 |
| Patient KD for BERT | 多层中间表示蒸馏（PKD-Last/PKD-Skip）。 | 自托管教师下可做多层对齐。 | 中 | https://arxiv.org/abs/1908.09355 |
| TinyBERT | 预训练 + 任务阶段蒸馏结合。 | 训练配方可复用；需要注意力/隐藏层。 | 中 | https://arxiv.org/abs/1909.10351 |
| MiniLM | 蒸馏自注意力关系（QK/Value）。 | 训练栈能拿到 attention 时可实现。 | 中 | https://arxiv.org/abs/2002.10957 |
| MiniLMv2 | 多头关系蒸馏，头数更灵活。 | 与 MiniLM 类似但更兼容不同头数。 | 中 | https://arxiv.org/abs/2012.15828 |

## LLM KD

| 论文 | 方法解读 | FastDistill 优化路径 | 可行性 | 链接 |
| :-- | :-- | :-- | :-- | :-- |
| Distilling Step-by-Step! | 用推理链作为额外监督信号。 | 加入“推理链生成 + 质检”，训练时多任务使用。 | 高 | https://aclanthology.org/2023.findings-acl.507/ |
| MiniLLM | 生成式 LLM 的 Reverse-KL 蒸馏。 | 捕获教师 logprobs，训练时做 reverse-KL。 | 中 | https://arxiv.org/abs/2306.08543 |
| DistiLLM | Skew-KL + 自适应 off-policy 采样。 | 加入学生 off-policy 输出并与教师样本混训。 | 中 | https://arxiv.org/abs/2402.03898 |
| Direct Preference KD | 基于偏好信号的 KD（隐式奖励 + reverse-KL）。 | 复用 judge/reward 输出构造偏好对。 | 中 | https://arxiv.org/abs/2406.19774 |

## 数据集蒸馏 / 数据蒸馏

| 论文 | 方法解读 | FastDistill 优化路径 | 可行性 | 链接 |
| :-- | :-- | :-- | :-- | :-- |
| Data Distillation | 多增强伪标注的自训练。 | 对无标注数据做多提示/多解码伪标注。 | 高 | https://arxiv.org/abs/1712.04440 |
| Dataset Distillation | 通过梯度匹配优化合成数据。 | 需要可微训练环；黑盒教师不适用。 | 低 | https://arxiv.org/abs/1811.10959 |
| Matching Training Trajectories | 通过轨迹匹配蒸馏数据。 | 需存训练轨迹，训练改造重。 | 低 | https://arxiv.org/abs/2203.11932 |
| Deep Generative Prior | 生成先验辅助蒸馏合成数据。 | 偏视觉任务，文本管线适配度低。 | 低 | https://arxiv.org/abs/2305.01649 |
| DiLM: Dataset Distillation with Language Models | 训练 LM 生成蒸馏后的文本样本。 | 训练小生成器 + 数据合成步骤融合。 | 中 | https://aclanthology.org/2024.findings-naacl.199/ |

## 综述（用作评测清单）

| 论文 | 可复用内容 | 可行性 | 链接 |
| :-- | :-- | :-- | :-- |
| A Survey on KD of LLMs | 评测维度与失败模式清单。 | 高 | https://arxiv.org/abs/2402.13116 |
| Survey on KD for LLMs | 方法谱系与评测任务整理。 | 高 | https://arxiv.org/abs/2407.01885 |
