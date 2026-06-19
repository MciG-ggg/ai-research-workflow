# Claims Registry

> **所有 claim 必须有 evidence 才能升级或保留。**

## C1 — Mamba 在短上下文代码任务上不输 Transformer 基线

- **状态**：partial
- **预测**：codestral-mamba-7b pass@1 ≥ codellama-7b pass@1 在 HumanEval 上
- **证据要求**：HumanEval 上两者对比 run（run_001 vs run_002）

## C2 — Mamba 在长上下文代码任务上明显优于 Transformer 基线

- **状态**：unverified
- **预测**：Mamba 在 RepoBench long-context 上 pass@1 应超过 Transformer 同规模基线
- **证据要求**：8k+ 上下文 RepoBench run

## C3 — Mamba-2 在代码任务上优于 Mamba-1

- **状态**：unverified
- **预测**：Mamba-2 pass@1 ≥ Mamba-1 pass@1 in HumanEval
- **证据要求**：Mamba-2 ablation run（run_004）

## C4 — Mamba 长上下文推理延迟低于 Transformer

- **状态**：unverified
- **预测**：Mamba 在 8k context 下 avg_latency_ms 应低于 Transformer 同规模基线
- **证据要求**：8k+ 上下文下两者对比 run

## C5 — Mamba 显存占用与上下文长度线性增长（而非 O(n²)）

- **状态**：broken
- **原预测**：Mamba 显存 O(n) 增长
- **现状**：run_003 在 8k 上下文 OOM（24G GPU），实测不是真正的 O(n)
