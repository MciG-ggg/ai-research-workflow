# Research: 用 Mamba SSM 替代 Transformer 做长上下文代码生成

> 草稿状态——只探索了 2 天，还没定 hypothesis 和实验方案。

## 动机

最近在长上下文代码补全上，Transformer 的 O(n²) attention cost 是明显瓶颈。
看到 Mamba 这类 selective state space model（SSM）在长序列建模上有 O(n) 复杂度，
理论上很适合"几千 token 的代码上下文"这个场景。

但我不确定它在**代码任务**上的实际效果——Mamba 主要在 language modeling 上被验证。

## 想研究的问题

- Mamba 在 HumanEval / MBPP 这种"短上下文"代码任务上能不能打过同参数量 Transformer？
- Mamba 在 RepoBench / LongCodeArena 这种"长上下文"代码任务上的优势有多大？
- 不同 SSM 参数化（Mamba-1 / Mamba-2 / H3）对结果影响如何？

## 已知相关工作（手记，详见 literature_notes.md）

- Mamba (Gu & Dao 2023): linear-time sequence modeling
- Mamba-2 (Dao & Gu 2024): structured state space duality
- Code Llama / DeepSeek-Coder: Transformer 代码基线
- 长上下文代码评测：RepoBench, LongCodeArena

## 范围

**当前在范围内的方向**：

- 代码任务（HumanEval / MBPP / RepoBench / LongCodeArena）
- 文本代码生成 + 代码补全
- SSM 架构变体（Mamba-1 / Mamba-2 / H3）
- 模型规模 1B - 13B（GPU 预算：单卡 24G）

**明确不做的方向**：

- 视觉任务 / 多模态
- 通用语言建模（除 code 以外的 perplexity 评测）
- 训练阶段的优化（仅做推理评测）
- 100B+ 规模（硬件不可行）

## 我目前的状态

- 没跑过任何实验
- 数据集和 baseline 都还没定
- 想知道这个方向值不值得花 1-2 周做下去
- 单卡 24G GPU（4090 / A5000），无多机资源
- 评估时间预算：2 周全职
