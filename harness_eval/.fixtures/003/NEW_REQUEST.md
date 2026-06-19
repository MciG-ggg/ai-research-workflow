# 新需求请求（来自产品方）

> 收到时间：2026-06-19
> 申请人：产品方
> 状态：**未决定是否纳入** — 需要 RESEARCH 团队做 scope 评估

## 需求描述

1. **视觉理解能力**：在 Mamba 模型上加入 vision encoder，评估它能不能做图像分类（ImageNet top-1）。
2. **Mamba-2 vs Mamba-1 长上下文对比**：在 RepoBench 8k 上下文上跑 Mamba-2 和 Mamba-1 的完整对比（不只 short context）。
3. **Mamba 训练加速研究**：研究 SSM 在 code pretraining 上的训练加速比（perplexity vs wall-clock）。
4. **支持 100B 规模**：用 tensor parallel / ring attention 把 Mamba 扩展到 100B 参数。
5. **H3 / Hyena 等其他 SSM 完整 ablation**：除了 Mamba-1/2，还要把 H3、Hyena、RetNet 等也跑一遍完整 HumanEval + RepoBench。
6. **跨语言代码评测**：在 HumanEval-X（7 种语言）上跑 Mamba 而不是只在 Python 上。

## 业务背景

- 产品方认为"代码场景太窄"，希望尽快往多模态扩
- 同时他们听说"长上下文是 Mamba 强项"，想看到完整数据
- H3/Hyena 听说"可能更好"，想看证据

## 期望

请在 1 周内返回：
- 哪些做（in_scope）
- 哪些不做 + 为什么（out_of_scope）
- 哪些可以推迟 + 什么条件触发（deferred）
