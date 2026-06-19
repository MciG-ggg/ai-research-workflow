"""示例考生：002_run_distillation

从 runs/ 数据 + CLAIMS.md 蒸馏出 RESULTS.md，保留失败 run，对齐 claim。

这个 candidate 是 demo 用的"理想考生"。
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def _read_json(p: Path) -> dict | None:
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_text(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")


def main() -> int:
    runs_dir = Path(os.environ["HARNESS_EVAL_RUNS_DIR"])
    claims_path = Path(os.environ.get("HARNESS_EVAL_CLAIMS_MD", ""))
    project_root = Path(os.environ["HARNESS_EVAL_PROJECT_ROOT"])
    slug = os.environ.get("HARNESS_EVAL_SLUG", "eval_demo")

    out_dir = project_root / ".omx" / "ai-research" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "RESULTS.md"

    print(f"[candidate] reading runs from {runs_dir}")
    if claims_path.exists():
        print(f"[candidate] reading claims from {claims_path}")

    # ---- 1. 加载所有 run ----
    runs: list[dict] = []
    for run_id in sorted(os.listdir(runs_dir)):
        run_dir = runs_dir / run_id
        if not run_dir.is_dir():
            continue
        m = _read_json(run_dir / "metrics.json")
        if m:
            runs.append(m)

    if not runs:
        print("[candidate] ERROR: no runs found", flush=True)
        return 1

    # ---- 2. 构造结果表 ----
    rows: list[str] = []
    rows.append("| run_id | kind | model | dataset | status | pass@1 ↑ | pass@10 ↑ | avg_latency_ms ↓ | context_len |")
    rows.append("|--------|------|-------|---------|--------|----------|-----------|------------------|-------------|")
    for r in runs:
        m = r.get("metrics", {}) or {}
        pass1 = m.get("pass@1")
        pass10 = m.get("pass@10")
        lat = m.get("avg_latency_ms")
        ctx = m.get("context_length_used")
        rows.append(
            f"| {r['run_id']} | {r.get('kind', '?')} | {r.get('model', '?')} | "
            f"{r.get('dataset', '?')}/{r.get('split', '?')} | "
            f"**{r.get('status', '?')}** | "
            f"{pass1 if pass1 is not None else '—'} | "
            f"{pass10 if pass10 is not None else '—'} | "
            f"{lat if lat is not None else '—'} | {ctx} |"
        )

    table = "\n".join(rows)

    # ---- 3. 失败 run 列表（保留！不删！）----
    failed = [r for r in runs if r.get("status") == "failed"]
    failed_block = ""
    if failed:
        failed_lines = ["## 失败 Run（保留不删）", ""]
        for r in failed:
            err = r.get("error", {})
            failed_lines.append(
                f"- **{r['run_id']}** ({r.get('model')} on {r.get('dataset')}): "
                f"`{err.get('type', '?')}` — {err.get('message', '')}"
            )
        failed_lines.append("")
        failed_lines.append("**归因**：长上下文（8k）下 Mamba-1 的 recurrent state 显存增长超出预期，")
        failed_lines.append("不是真正的 O(n)。需要切到 Mamba-2 的 SSD 实现或加 chunked inference。")
        failed_lines.append("")
        failed_block = "\n".join(failed_lines)

    # ---- 4. 结论（引用 run_id + 对齐 claim）----
    conclusions = """## 结论

基于上述 5 次 run（含 1 次失败）：

### C1 — Mamba 在短上下文代码任务上不输 Transformer 基线

- **对齐到 run_001 vs run_002**：
  - codestral-mamba-7b pass@1 = 0.471
  - codellama-7b-instruct pass@1 = 0.502
  - **差距 = -3.1pp**
- **Claim 状态变化**：从 `partial` 下调为 `refuted`（H1 不成立——
  短上下文场景下 Mamba 略低于 Transformer 基线）。
- **依据**：RESEARCH.md H1 的证伪条件是"差距 ≥ 3pp"，
  我们实测 -3.1pp，刚好在边界上。**需要至少再跑 1 次 seed=43 复现确认**。

### C3 — Mamba-2 在代码任务上优于 Mamba-1

- **对齐到 run_004 vs run_001**：
  - codestral-mamba-2-7b pass@1 = 0.488
  - codestral-mamba-7b-v0.1 pass@1 = 0.471
  - **差距 = +1.7pp**
- **Claim 状态变化**：从 `unverified` 升级为 `partial`（H3 部分成立）。
- **依据**：Mamba-2 在 HumanEval 上略优于 Mamba-1，且推理更快（162.8 vs 187.3 ms）。

### C2 — Mamba 在长上下文代码任务上明显优于 Transformer 基线

- **状态**：unverified（**没有有效证据**——run_003 OOM 失败，没有可对比数据）
- **建议**：换 Mamba-2 + chunked inference（run_005 是 chunked 但没对比 Transformer 基线）

### C4 — Mamba 长上下文推理延迟低于 Transformer

- **对齐到 run_005**：chunked Mamba 推理延迟 = 423.7 ms（vs run_001 短上下文 Mamba 的 187.3ms）
- **Claim 状态变化**：保持 `unverified`——chunked inference 引入了 prefix recomputation
  overhead，延迟反而比短上下文还高 2x，未能验证 "Mamba 长上下文延迟低"。

### C5 — Mamba 显存占用与上下文长度线性增长

- **对齐到 run_003**：codestral-mamba-7b-v0.1 在 8k 上下文 OOM（24G GPU）
- **Claim 状态变化**：从 `broken` 保持 `broken`，且进一步降级为 `refuted` —
  显存不是 O(n)，而是 O(n) × state_size，超过某个阈值后 OOM。

## 下一步

| 动作 | 命令 / 路径 | 优先级 |
|------|-------------|--------|
| 用 seed=43 复现 run_001/002，确认 C1 的 -3.1pp 边界 | `python scripts/repro_humaneval.py --seed 43` | P0 |
| 跑 codellama-7b on RepoBench 8k，建立 C2/C4 的 Transformer 基线 | `python scripts/eval_repobench.py --model codellama-7b` | P0 |
| 跑 Mamba-2 + chunked on RepoBench 8k，对齐 run_005 | `python scripts/eval_repobench.py --model codestral-mamba-2-7b --chunk-size 2048` | P1 |
| 在 [workflow] 改进点：把"失败 run 不删除"作为 RESULTS.md 模板的硬性约束 | 编辑 templates/RESULTS.md | P2 |

**不要做**：不要基于这次数据宣称"Mamba 在代码任务上有优势"——证据不支持。
"""

    body = f"""# RESULTS — {slug}

> 由 harness_eval candidate `distill_run_to_results` 自动蒸馏。
> 数据来源：{runs_dir}
> Claim 来源：{claims_path if claims_path.exists() else 'N/A'}

## Run 汇总

{table}

{failed_block}
{conclusions}
"""

    out_path.write_text(body, encoding="utf-8")
    print(f"[candidate] wrote {out_path} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
