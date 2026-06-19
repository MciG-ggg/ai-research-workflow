"""示例考生：001_experiment_design

根据 RESEARCH.md + literature_notes.md 起草一份合规的 EXPERIMENT.md。

这个 candidate 是 demo 用的"理想考生"——产生明显 pass 的工件，
目的是验证整套评测骨架（驱动 + 判卷 + 落盘）能跑通。

要看"工作流退化"是什么样的，把这个 candidate 替换成"故意有缺陷"的版本即可。
"""
from __future__ import annotations

import os
from pathlib import Path


def _read(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def _extract_keywords(text: str, n: int = 5) -> list[str]:
    """从 RESEARCH.md 抽几个高频词作为 hypothesis 的锚点（演示用）。"""
    import re
    # 简单启发式：找名词性短语
    candidates = re.findall(r"\b[A-Z][a-z]+(?:[- ][A-Z][a-z]+)*\b|\b[A-Z]{2,}\b", text)
    seen: list[str] = []
    for c in candidates:
        if c not in seen and len(c) > 2:
            seen.append(c)
        if len(seen) >= n:
            break
    return seen


def main() -> int:
    research_path = os.environ.get("HARNESS_EVAL_RESEARCH_MD")
    lit_path = os.environ.get("HARNESS_EVAL_LITERATURE_NOTES")
    project_root = Path(os.environ["HARNESS_EVAL_PROJECT_ROOT"])
    slug = os.environ.get("HARNESS_EVAL_SLUG", "eval_demo")

    out_dir = project_root / ".omx" / "ai-research" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "EXPERIMENT.md"

    research = _read(research_path)
    lit = _read(lit_path)
    keywords = _extract_keywords(research)

    # ---- 故意在 transcript 里留下读 RESEARCH.md 的痕迹（满足 H10）----
    print(f"[candidate] reading RESEARCH.md from {research_path}")
    print(f"[candidate] extracted keywords: {keywords}")
    if lit_path:
        print(f"[candidate] reading literature notes from {lit_path}")

    body = f"""# EXPERIMENT — {slug}

> 由 harness_eval candidate `draft_experiment_md` 自动起草。
> 本文件结构按 ai-research-workflow 的 EXPERIMENT 模板生成。

参考依据：见 `RESEARCH.md`（根目录）。
文献综述：见 `literature_notes.md`（手记，待 primary 校验）。

## Hypothesis

基于 RESEARCH.md 的研究方向（关键词：{', '.join(keywords[:5]) if keywords else 'N/A'}），
我们提出以下**可证伪**假设：

> **H1**：在 HumanEval 这种"短上下文代码任务"上，同等参数量的
> Mamba SSM 模型（codestral-mamba-7b）的 pass@1 **不低于**
> Transformer 基线（codellama-7b-instruct）。

**证伪条件**：如果 codestral-mamba-7b 的 pass@1 在 HumanEval 上
显著低于 codellama-7b-instruct（差距 ≥ 3pp），则 H1 不成立。

> **H2**：在 RepoBench 长上下文（≥ 8k tokens）场景下，
> Mamba 在推理延迟上**优于** Transformer 同规模基线。

**证伪条件**：Mamba 在 8k 上下文上的 avg_latency_ms ≥ Transformer 同规模基线。

（这两个假设直接对应 RESEARCH.md 中"想研究的问题"小节。）

## Baselines

我们对比两类 baseline：

1. **弱基线（已复现 / weak）**：Code Llama 7B Instruct — 主流开源代码 Transformer 基线，
   pass@1 ≈ 0.50 on HumanEval。
2. **强基线（计划复现 / strong）**：DeepSeek-Coder 6.7B Instruct — 当前 SOTA 开源代码模型。

> **Baseline 分层**：上表中"已复现"指跑过完整 HumanEval；
> "计划复现"指仅在 paper 数字中见过，独立复现还没做。

补充基线（来自 literature_notes.md）：
- Mamba (Gu & Dao 2023)：论文报告在 language modeling 上匹配 Transformer，
  代码任务上暂无独立复现结果。
- Mamba-2 (Dao & Gu 2024)：SSD framework，训练更快，待评估。

## Metrics

| Metric | Direction | Unit | Range | 说明 |
|--------|-----------|------|-------|------|
| pass@1 | ↑ 越大越好 | ratio | [0, 1] | HumanEval/RepoBench 单样本通过率 |
| pass@10 | ↑ 越大越好 | ratio | [0, 1] | 多样本 k=10 通过率 |
| avg_latency_ms | ↓ 越小越好 | ms | >0 | 单样本平均推理延迟 |
| context_length_used | ↑ 越大越好（覆盖度） | tokens | [512, 32768] | 实际使用的上下文长度 |

**指标的合理性说明**：pass@1 反映单次生成质量；avg_latency_ms 反映工程可用性；
context_length_used 反映模型对长上下文的实际利用度。

## Dataset

| Dataset | Split | 上下文长度 | 用途 |
|---------|-------|-----------|------|
| HumanEval | test | ~1k tokens | 短上下文代码生成 baseline |
| RepoBench | test_long_8k | 8k tokens | 长上下文代码补全 |
| MBPP | test | ~1k tokens | 补充基线（计划） |

数据来源：HuggingFace `openai_humaneval`、`microsoft/repo-bench`。
版本锁定：HumanEval 2021-12-08 release；RepoBench v1.1。

## 失败策略

**什么算"失败"**：
- 若 H1 不成立（Mamba 短上下文 ≤ baseline - 3pp）—— 停止"短上下文评估"这条线，
  把资源全压到长上下文实验
- 若 H2 不成立（Mamba 长上下文延迟 ≥ Transformer）—— 重新评估 SSM 替代
  Transformer 的工程价值，可能降级为"仅作学术对照"

**什么算"无效"**：
- 评测集本身有数据泄漏（检查 prompt 是否在 train set 出现过）
- 推理框架 bug 导致延迟不准（如 KV cache 没启）

**什么算"可疑，需复现"**：
- 单次 run 与 paper 报告差距 ≥ 5pp —— 至少换 seed 复现 3 次取均值

## 实验流程

1. **环境就绪**：固定 torch / transformers 版本，记录 git commit。
2. **Baseline 复现**：先跑 codellama-7b-instruct on HumanEval，与 paper 对照。
3. **主实验**：codestral-mamba-7b-v0.1 on HumanEval + RepoBench test_long_8k。
4. **Ablation**：换成 codestral-mamba-2-7b 验证 SSD 改进。
5. **结果蒸馏**：写 RESULTS.md，对齐 RESEARCH.md 的 claim。

## 引用一致性

本文档 Hypothesis 小节**显式引用**了 `RESEARCH.md` 的"想研究的问题"小节
（关键词锚点：{', '.join(keywords[:3]) if keywords else 'N/A'}）。
Baselines 小节引用了 `literature_notes.md` 中的 Mamba / Code Llama 段落。
Metrics 的方向标注符合 RESEARCH.md 中"指标定义"小节未明确提出但 lit notes 中
"我对现状的判断"段落的隐含预期。

## 下一步

- 跑通 baseline 复现，与 paper 对照
- 启 8k 长上下文实验
- 在 [workflow] 改进点：把"方向标注"和"已复现/计划复现"作为 EXPERIMENT.md 模板的强制项
"""

    out_path.write_text(body, encoding="utf-8")
    print(f"[candidate] wrote {out_path} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
