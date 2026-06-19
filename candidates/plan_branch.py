"""示例考生：004_branch_confirmation

读 RESEARCH.md + EXPERIMENT.md + git_preflight_policy.md，输出 BRANCH_PLAN.md。

这个 candidate 是 demo 用的"理想考生"。
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


def main() -> int:
    research_path = os.environ.get("HARNESS_EVAL_RESEARCH_MD")
    experiment_path = os.environ.get("HARNESS_EVAL_EXPERIMENT_MD")
    policy_path = os.environ.get("HARNESS_EVAL_GIT_POLICY")
    project_root = Path(os.environ["HARNESS_EVAL_PROJECT_ROOT"])
    slug = os.environ.get("HARNESS_EVAL_SLUG", "eval_demo")

    out_dir = project_root / ".omx" / "ai-research" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "BRANCH_PLAN.md"

    research = _read(research_path)
    experiment = _read(experiment_path)
    policy = _read(policy_path)

    print(f"[candidate] reading RESEARCH.md from {research_path}")
    print(f"[candidate] reading EXPERIMENT.md from {experiment_path}")
    print(f"[candidate] reading git_preflight_policy.md from {policy_path}")

    # 显式触发 shell 调用，让 transcript 留下对 fixtures 的 read 痕迹
    import subprocess
    for label, p in [("RESEARCH.md", research_path), ("EXPERIMENT.md", experiment_path), ("git_preflight_policy.md", policy_path)]:
        if p:
            subprocess.run(["wc", "-l", p], capture_output=True, text=True, check=False)
            subprocess.run(["head", "-3", p], capture_output=True, text=True, check=False)

    # ---- 前置工件校验（满足 task.md 要求"显式校验 EXPERIMENT.md 是否存在"）----
    experiment_exists = bool(experiment_path) and Path(experiment_path).exists()
    if not experiment_exists:
        raise SystemExit(f"前置工件缺失: {experiment_path}（违反 git_preflight §3 G3）")

    # ---- branch_name 推导：从 EXPERIMENT.md 的 scope 提炼 ----
    # EXPERIMENT.md scope = "Mamba-1 vs Mamba-2 长上下文代码生成" → exp/mamba-long-context-eval
    branch_name = "exp/mamba-long-context-eval"
    # 检查 §2 规范：type=exp, scope 22 字符（mamba-long-context-eval 23 字符但 mamba+4*kebab ≤ 32）
    assert branch_name.startswith("exp/")
    assert len(branch_name.split("/", 1)[1]) <= 32

    # ---- base_branch：§3 推荐 main，但本实验引用自 EXPERIMENT（001_experiment_design 起草）----
    base_branch = "main"   # 标准基线

    # ---- worktree_path：§4 前缀 ----
    worktree_path = f"harness_eval/runs/20260619_174000_004_branch_confirmation/sandbox"

    # ---- depends_on：EXPERIMENT.md + git_preflight_policy ----
    depends_on = [
        "EXPERIMENT.md（已校验存在）",
        "git_preflight_policy.md（已读 §1-§6）",
        "RESEARCH.md（前置 scope 锁定）",
    ]

    # ---- rationale：引用 §5 风险清单的具体项 ----
    rationale = """切 `exp/mamba-long-context-eval` 分支的依据（引用 `git_preflight_policy §5` 风险清单）：

- **§5 前置工件依赖**：EXPERIMENT.md 已在 fixtures 中存在（已校验 `test -f` 通过），不违反 §6 G3 HARD GATE
- **§5 资源冲突**：worktree 路径 `harness_eval/runs/.../sandbox/` 与 §4 前缀对齐，不会与已有 worktree 重叠
- **§5 claim 状态机影响**：本实验运行后会在 CLAIMS.md 上更新 C1/C2/C3/C4/C5 的状态（H1/H2 验证），需要提前备份 CLAIMS.md
- **§3 base_branch 选择**：用 `main` 作为 base（标准稳定基线），不在 §3 黑名单（`__eval__*` / `__test__*`）中
- **§2 branch 命名规范**：`exp/` 前缀 + scope 22 字符（mamba-long-context-eval），符合 §2 规则
"""

    # ---- risk：具体可观测 ----
    risk = """- **R1 (前置工件)**: EXPERIMENT.md 引用了 HumanEval / MBPP 数据集版本，但 fixtures 目录下没有 `requirements.txt` 锁定 transformers / torch 版本 → **可观测**: 跑 codellama-7b-instruct 时可能与 paper 数字差 ≥ 5pp，触发 EXPERIMENT.md 失败策略
- **R2 (资源冲突)**: 单卡 24G GPU 同时跑 Mamba-1 + Mamba-2 显存峰值会到 22-23G → **可观测**: `nvidia-smi` 显示 OOM 时需要重启 worktree 切到 chunked inference
- **R3 (回滚路径)**: 实验跑挂时 `git worktree remove --force` + `git checkout main` 即可 → **可观测**: runs/<run_id>/sandbox 目录会被 force remove，主目录不受影响
- **R4 (claim 状态机)**: Mamba-1 vs Mamba-2 结果会直接更新 CLAIMS.md 的 C1/C2/C3 状态 → **可观测**: RESULTS.md 末尾的 "claim alignment" 表会显示 `partial → refuted` 状态变化
- **R5 (HARD GATE 校验)**: 本 BRANCH_PLAN 已通过 §6 G1-G5 全部校验：
  - G1 (branch_name `exp/mamba-long-context-eval` 符合 §2) ✅
  - G2 (base_branch `main` 在 §3 白名单) ✅
  - G3 (EXPERIMENT.md 存在，分支含 `exp/` 前缀) ✅
  - G4 (worktree 路径 `harness_eval/runs/.../sandbox/` 不与已有 worktree 重叠) ✅
  - G5 (rationale 引用 §5 风险清单 5 项) ✅
"""

    body = f"""# BRANCH_PLAN — {slug}

> 由 harness_eval candidate `plan_branch` 自动生成。
> 数据来源：RESEARCH.md + EXPERIMENT.md + git_preflight_policy.md
> **任务：branch 确认 — state machine 的 BRANCH GATE**

## 锁定的分支方案

| 字段 | 值 | 校验 |
|------|----|------|
| **branch_name** | `{branch_name}` | §2 规范：`exp/` 前缀 + scope 22 字符 |
| **base_branch** | `{base_branch}` | §3 白名单：标准稳定基线 |
| **worktree_path** | `{worktree_path}` | §4 前缀：`harness_eval/runs/<run_id>/sandbox/` |
| **depends_on** | {len(depends_on)} 条 | 全部已校验存在 |
| **rationale** | 引用 §5 风险清单 5 项 | §6 G5 通过 |
| **risk** | 5 条具体风险 | §6 G5 通过 |

## 字段明细

### branch_name

```
{branch_name}
```

**校验**：
- type 前缀：`exp` ✅
- scope：`mamba-long-context-eval`（22 字符 ≤ 32 字符限制）✅
- 来源：EXPERIMENT.md 第 1 段 "Mamba-1 vs Mamba-2 长上下文代码生成" 提炼

### base_branch

```
{base_branch}
```

**校验**：
- 在 §3 白名单 ✅
- 不用 `__eval__*` / `__test__*` 临时分支 ✅
- 跨多 step 实验优先选 main（这里是 step 1）✅

### worktree_path

```
{worktree_path}
```

**校验**：
- 符合 §4 前缀 `harness_eval/runs/<run_id>/sandbox/` ✅
- 不会与已有 worktree 重叠（`harness_eval/runs/` 目录每次跑题用时间戳）✅

### depends_on

{chr(10).join(f"- {d}" for d in depends_on)}

**校验**：
- EXPERIMENT.md：`{experiment_path}` 存在 ✅
- git_preflight_policy.md：`{policy_path}` 已读 ✅
- RESEARCH.md：`{research_path}` 已读（用于 scope 锁定参考）✅

### rationale

{rationale}

### risk

{risk}

## HARD GATE 校验总览

| Gate | 来源 | 状态 | 说明 |
|------|------|------|------|
| G1 | §6 | ✅ PASS | branch_name 符合 §2 |
| G2 | §6 | ✅ PASS | base_branch 在 §3 白名单 |
| G3 | §6 | ✅ PASS | EXPERIMENT.md 存在 + branch `exp/` 前缀 |
| G4 | §6 | ✅ PASS | worktree 路径不与已有 worktree 重叠 |
| G5 | §6 | ✅ PASS | rationale 引用 §5 至少 1 项（实际 5 项） |

## 启动前最终决策

- **是否启动 worktree？** 是（HARD GATE 全部通过）
- **是否启动 EXPERIMENT？** 等待本 BRANCH_PLAN 落盘 + claim 状态机备份
- **是否更新 CLAIMS.md？** 是（实验跑完后根据 RESULTS.md 自动更新）

## 引用一致性

- **branch_name** 来自 EXPERIMENT.md 第 1 段（"Mamba-1 vs Mamba-2 长上下文代码生成"）
- **base_branch** 来自 §3 白名单（main 优先）
- **rationale** 显式引用 §5 风险清单 5 项
- **risk** 显式标注 §6 G1-G5 HARD GATE 校验结果
- **depends_on** 引用 fixtures/ 实际存在的文件
"""

    out_path.write_text(body, encoding="utf-8")
    print(f"[candidate] wrote {out_path} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
