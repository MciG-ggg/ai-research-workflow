"""示例考生：003_scope_locking

读 RESEARCH.md + NEW_REQUEST.md，输出 SCOPE.md（in_scope / out_of_scope / deferred）。

这个 candidate 是 demo 用的"理想考生"。
"""
from __future__ import annotations

import os
import re
from pathlib import Path


def _read(path: str | None) -> str:
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def _extract_research_constraints(research: str) -> dict[str, str]:
    """从 RESEARCH.md 抽出关键约束。"""
    return {
        "in_scope_section": _section_block(research, "范围") or "",
        "status_section": _section_block(research, "我目前的状态") or "",
        "questions_section": _section_block(research, "想研究的问题") or "",
    }


def _section_block(text: str, title: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_block = False
    title_rank = 0
    for line in lines:
        m = re.match(r"^(#{1,3})\s+(.+)$", line)
        if m:
            current_rank = len(m.group(1))
            current_title = m.group(2).strip()
            if in_block and current_rank <= title_rank:
                break
            if current_title == title:
                in_block = True
                title_rank = current_rank
                continue
        if in_block:
            out.append(line)
    return "\n".join(out)


def main() -> int:
    research_path = os.environ.get("HARNESS_EVAL_RESEARCH_MD")
    request_path = os.environ.get("HARNESS_EVAL_NEW_REQUEST")
    project_root = Path(os.environ["HARNESS_EVAL_PROJECT_ROOT"])
    slug = os.environ.get("HARNESS_EVAL_SLUG", "eval_demo")

    out_dir = project_root / ".ai-research-workflow" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "SCOPE.md"

    research = _read(research_path)
    request = _read(request_path)

    print(f"[candidate] reading RESEARCH.md from {research_path}")
    print(f"[candidate] reading NEW_REQUEST.md from {request_path}")

    constraints = _extract_research_constraints(research)

    # ---- in_scope: 从 NEW_REQUEST 里挑能对得上 RESEARCH "范围"小节的 ----
    in_scope = """## in_scope

> 接下来 1-2 周会做。**每条都引用 RESEARCH.md 的"范围"或"想研究的问题"小节**作为依据。

- **Mamba-2 vs Mamba-1 长上下文对比**（NEW_REQUEST 需求 2）— 对应 RESEARCH.md "想研究的问题"小节
  第 2 条 "Mamba 在 RepoBench / LongCodeArena 这种'长上下文'代码任务上的优势有多大？"
  以及 "范围"小节的 "SSM 架构变体（Mamba-1 / Mamba-2 / H3）"。是 RESEARCH 的核心 hypothesis 之一。
- **HumanEval + RepoBench 双场景 baseline 复现**（NEW_REQUEST 需求 2 的前置）— 对应 RESEARCH.md
  "范围"小节的 "代码任务（HumanEval / MBPP / RepoBench / LongCodeArena）" 与 "想研究的问题"小节第 1 条
  "Mamba 在 HumanEval / MBPP 这种'短上下文'代码任务上能不能打过同参数量 Transformer"。
  必须在跑 Mamba-2 长上下文对比前，先建立 Transformer 基线 + 跑通 Mamba-1 短上下文数据。
- **明确做"已复现 vs 计划复现"的 baseline 分层**（隐藏需求，源自 RESEARCH.md "范围"小节
  "SSM 架构变体" 与 EXPERIMENT 模板）— 区分 Code Llama 7B（已复现）与 DeepSeek-Coder 6.7B（计划复现）。
- **记录失败 run**（隐藏需求，源自 RESEARCH.md "我目前的状态"小节 "单卡 24G GPU" 的资源约束，
  预期 8k 上下文会有 OOM）— 把 OOM 失败的 run 也写进 RESULTS.md，不偷偷删除。"""

    # ---- out_of_scope: 拒绝 NEW_REQUEST 里明显超范围的 ----
    out_of_scope = """## out_of_scope

> **明确不做**。每条说明拒绝理由（追溯到 RESEARCH.md 的具体约束）。

- **视觉理解 / 图像分类**（NEW_REQUEST 需求 1）— **因为** RESEARCH.md "范围"小节**明确写**
  "明确不做的方向：视觉任务 / 多模态"。在范围内白名单外，资源冲突。优先级排在代码任务之后。
- **Mamba 训练加速研究（perplexity vs wall-clock）**（NEW_REQUEST 需求 3）— **因为** RESEARCH.md
  "范围"小节**明确写** "训练阶段的优化（仅做推理评测）"。本工作只做推理评测，不碰 pretraining 加速。
- **支持 100B 规模**（NEW_REQUEST 需求 4）— **因为** RESEARCH.md "我目前的状态"小节
  明确硬件约束 "单卡 24G GPU（4090 / A5000），无多机资源"。tensor parallel / ring attention
  超出硬件可行性，不在当前阶段的预算内。
- **H3 / Hyena / RetNet 完整 ablation**（NEW_REQUEST 需求 5）— **资源**不允许。
  RESEARCH.md "想研究的问题"小节第 3 条只提了 "不同 SSM 参数化（Mamba-1 / Mamba-2 / H3）"，
  没说要做完整 ablation；Mamba-1 vs Mamba-2 才是核心对比，H3/Hyena/RetNet 是次级 sweep。
  H3 留到 deferred（看主实验结果），Hyena/RetNet 直接砍（与 H3 同质，无新增 insight）。"""

    # ---- deferred: 推迟 + 触发条件 ----
    deferred = """## deferred

> **推迟到后续阶段**。每条写明**可观测的触发条件**。

- **H3 完整 ablation** — **当** Mamba-2 vs Mamba-1 在 HumanEval + RepoBench 两个 benchmark 上
  的差距 ≥ 2pp 时，**触发**对 H3 的同等评测；**如果**差距 < 2pp，**则** H3 ablation 不再启动，
  资源全压到 Mamba-2 的工程化。
- **跨语言代码评测（HumanEval-X）** — **当** Mamba 在 Python HumanEval 上的实验**完成后**且
  主实验结果**达成**预期（pass@1 差距在 H1 证伪条件 ±2pp 范围内），**再次**评估启动 HumanEval-X
  的 ROI；**如果** Python 都没跑通，跳过跨语言。
- **完整 ablation：Mamba-1 / Mamba-2 / Mamba-2 + chunked inference 三向对比** — **当**
  8k 上下文长上下文实验**触发** Mamba-1 OOM 但 Mamba-2 不 OOM 的现象被复现 ≥ 1 次，**则**启动
  三向对比以判断 chunked inference 的具体开销；**恢复**标准是"主实验的 C2 claim 状态从 unverified
  升级为 partial 或 confirmed"。"""

    body = f"""# SCOPE — {slug}

> 由 harness_eval candidate `scope_lock` 自动生成。
> 数据来源：RESEARCH.md（研究方向草稿）+ NEW_REQUEST.md（产品方 6 条新需求）
> **任务：scope 锁定 — state machine 的 HARD GATE**

## 锁定原则

1. **以 RESEARCH.md 的"范围"和"我目前的状态"为唯一依据**
2. **NEW_REQUEST 的每条新需求都要被判定**（in_scope / out_of_scope / deferred 三选一）
3. **拒绝要有理由，推迟要有触发条件**（避免"以后再说"和"因为重要"这种空话）

## 锁定的范围摘要

| 类别 | 数量 | 说明 |
|------|------|------|
| in_scope | 4 | 主实验 + baseline 复现 + baseline 分层 + 失败保留 |
| out_of_scope | 4 | 视觉 / 训练加速 / 100B / H3 Hyena RetNet 完整 ablation |
| deferred | 3 | H3 ablation / 跨语言 / 三向对比（都有触发条件） |

{in_scope}

{out_of_scope}

{deferred}

## 引用一致性

- **in_scope 第 1、2 条**直接引用 RESEARCH.md "想研究的问题"小节的具体条目
- **in_scope 第 3、4 条**引用 RESEARCH.md "范围"小节与 "我目前的状态"小节
- **out_of_scope 第 1、2 条**直接引用 RESEARCH.md "范围"小节里"明确不做的方向"白名单
- **out_of_scope 第 3 条**引用 RESEARCH.md "我目前的状态"小节硬件约束
- **out_of_scope 第 4 条**引用 RESEARCH.md "想研究的问题"小节（第 3 条没说要完整 ablation）
- **deferred 第 1 条**触发条件引用 EXPERIMENT.md H1 证伪阈值
- **deferred 第 2 条**触发条件引用主实验 claim 状态机
- **deferred 第 3 条**触发条件引用 8k 上下文 OOM 现象的复现次数

## 锁定后下一步

1. 把 in_scope 第 2 条（baseline 复现）作为 P0 启动
2. 启动 EXPERIMENT.md 起草（in_scope 第 1 条对应的实验）
3. 同步在 README.md 标注 "out_of_scope: 视觉 / 训练加速 / 100B" 防止后续再被提起
4. 把 deferred 的 3 条触发条件做成 watch list，写到 .ai-research-workflow/{slug}/watchlist.md
"""

    out_path.write_text(body, encoding="utf-8")
    print(f"[candidate] wrote {out_path} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
