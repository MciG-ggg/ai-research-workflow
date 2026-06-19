# Literature Notes (手记，可信度低，需要 primary 校验)

- **Mamba (Gu & Dao 2023)**: linear-time, 论文报告在 language modeling perplexity 上匹配 Transformer。
  在 Long Range Arena 上比 Transformer 强很多。但 code generation 上没有报告。

- **Mamba-2 (Dao & Gu 2024)**: SSD framework, 训练速度更快；代码任务上还没看到独立复现。

- **Code Llama (Roziere et al. 2023)**: 7B/13B/34B 代码专用 Transformer 基线。

- **DeepSeek-Coder (Guo et al. 2024)**: SOTA 开源代码模型，2B/6.7B/33B 多种规模，HumanEval 上很高。

- **RepoBench (Liu et al. 2023)**: 长上下文代码补全 benchmark。

- **LongCodeArena (Bogomolov et al. 2024)**: 更长上下文（>10k tokens）的代码任务。

- **HumanEval / MBPP**: 短上下文代码生成 baseline benchmark。

## 我对现状的判断

- 在短上下文代码任务上，Transformer 基线已经很强，Mamba 替代的预期收益可能有限。
- 在长上下文代码任务上，可能真的有收益，但需要自己做实验验证。
- 现有 SOTA baseline 应该用 Code Llama 7B + DeepSeek-Coder 6.7B。

## 不确定的地方

- Mamba 代码模型的开源实现成熟度（codestral-mamba? jamba?）
- 长上下文代码评测的数据集版本和 split
- SSM 推理速度 vs Transformer 在 code completion 场景下的真实差距
