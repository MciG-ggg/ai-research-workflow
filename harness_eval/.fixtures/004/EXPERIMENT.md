# EXPERIMENT — Mamba-1 vs Mamba-2 长上下文代码生成

> 引用 RESEARCH.md "想研究的问题"第 2 条 + "范围"小节 SSM 架构变体

## Hypothesis

> **H1**：在 RepoBench 8k 长上下文代码补全场景下，codestral-mamba-2-7b 的
> pass@1 **不低于** codestral-mamba-7b-v0.1（同参数量的 Mamba-1）。

**证伪条件**：Mamba-2 在 RepoBench 8k pass@1 显著低于 Mamba-1（差距 ≥ 2pp）。

> **H2**：Mamba-2 的推理延迟（chunked inference）在 8k 上下文上**优于** Mamba-1 的 recurrent state 显存增长。

**证伪条件**：Mamba-2 在 8k 上下文 avg_latency_ms ≥ Mamba-1 短上下文 Mamba-1 延迟的 2x。

## Baselines

1. **强基线（已复现 / reproduced）**：codestral-mamba-7b-v0.1 — Mamba-1，7B 参数
2. **强基线（计划复现 / planned）**：codestral-mamba-2-7b — Mamba-2 SSD 实现，7B 参数
3. **对照基线（已复现）**：codellama-7b-instruct — Transformer 代码基线（7B）

## Metrics

| Metric | Direction | Unit | Range | 说明 |
|--------|-----------|------|-------|------|
| pass@1 | ↑ 越大越好 | ratio | [0, 1] | RepoBench 8k 上下文单样本通过率 |
| pass@10 | ↑ 越大越好 | ratio | [0, 1] | 多样本 k=10 通过率 |
| avg_latency_ms | ↓ 越小越好 | ms | >0 | 8k 上下文单样本推理延迟 |
| peak_memory_gb | ↓ 越小越好 | GB | (0, 24] | 推理峰值显存 |
| context_length_used | ↑ 越大越好 | tokens | [512, 32768] | 实际使用的上下文长度 |

## Dataset

| Dataset | Split | 上下文长度 | 用途 |
|---------|-------|-----------|------|
| RepoBench | test_long_8k | 8k tokens | 长上下文代码补全（主实验） |
| HumanEval | test | ~1k tokens | 短上下文 baseline |
| MBPP | test | ~1k tokens | 补充 baseline |

数据来源：HuggingFace `microsoft/repo-bench`、`openai_humaneval`。
版本锁定：RepoBench v1.1、HumanEval 2021-12-08。

## 失败策略

- H1 不成立（Mamba-2 ≤ Mamba-1 - 2pp）：停止 Mamba 方向，资源全压到 chunked inference 工程化
- H2 不成立（Mamba-2 延迟 ≥ Mamba-1 短上下文 2x）：降级为仅学术对照
- 评测集数据泄漏：换数据集
- 单次 run 与预期差距 ≥ 5pp：换 seed 复现 3 次

## 实验流程

1. 启动 `worktree` 沙箱
2. 先复现 run_001（Mamba-1 + HumanEval）与 paper 对照
3. 跑 Mamba-2 + HumanEval（H3 验证）
4. 跑 RepoBench 8k + Mamba-1（run_003 预期会 OOM）
5. 跑 RepoBench 8k + Mamba-2（run_004 验证 SSD 显存）
6. 写 RESULTS.md，对齐 RESEARCH.md claim
