# 题面：分支确认（state machine BRANCH GATE）

> **给考生看的所有信息都在这里。**

## 背景

ai-research-workflow 的分支确认阶段是一个 **BRANCH GATE**：
- 启动任何 `worktree` 之前必须先做 BRANCH_PLAN
- 错误的分支命名或缺前置工件依赖，会导致后续 EXPERIMENT / run 阶段全部污染
- 风险点必须**显式标注**，不能事后补

## 你的任务

我手头有：
- `RESEARCH.md`：研究方向草稿
- `EXPERIMENT.md`：刚起草的实验草案（Mamba-1 vs Mamba-2 长上下文对比）
- `git_preflight_policy.md`：本项目的 worktree / branch 规则摘要（含 §1-§6 章节）

请你基于这三份材料，输出一份 **`BRANCH_PLAN.md`** 到
`{{project_root}}/.ai-research-workflow/{{slug}}/BRANCH_PLAN.md`。

## BRANCH_PLAN.md 必须包含 6 个结构化字段

| 字段 | 含义 | 校验规则 |
|------|------|---------|
| `branch_name` | 目标分支名 | 必须符合 `git_preflight_policy §2`：`feature` / `fix` / `chore` / `refactor` / `exp` / `docs` 前缀，scope ≤ 32 字符 |
| `base_branch` | 从哪个分支切 | 必须在 `git_preflight_policy §3` 白名单内（main / feat/...） |
| `worktree_path` | 沙箱路径 | 必须以 `harness_eval/runs/` 前缀 |
| `depends_on` | 前置工件 | 至少 1 条：EXPERIMENT.md / SCOPE.md / CLAIMS.md / git_preflight_policy 之一 |
| `rationale` | 为什么这样切 | 必须引用 `git_preflight_policy §5` 风险清单的至少 1 项 |
| `risk` | 风险点 | 至少 1 个具体的 risk（不是"可能有风险"） |

## 输入材料

- `fixtures/RESEARCH.md`
- `fixtures/EXPERIMENT.md`
- `fixtures/git_preflight_policy.md`（**核心参考**）

## 输出要求

1. `{{project_root}}/.ai-research-workflow/{{slug}}/BRANCH_PLAN.md`

## 约束

- 不得修改 fixtures/ 下的任何文件
- 不得联网
- 120 秒内完成
- 必须**显式**引用 `git_preflight_policy` 的具体章节（§1-§6）
- 必须在 BRANCH_PLAN 里**显式校验**前置工件 EXPERIMENT.md 是否存在
- 如果发现 `git_preflight_policy` 的 HARD GATE（G1-G5）有任一违反，必须在 BRANCH_PLAN 里**显式说明并决策**

## 提示

- 看 `harness_eval/candidates/` 下的样例候选实现
- 不要忘了 transcript 里的 read 调用要包含 `git_preflight_policy` 和 `EXPERIMENT.md`

---

**剧本（仅给 runner 看）**

考生进程会收到环境变量：
- `HARNESS_EVAL_RESEARCH_MD`
- `HARNESS_EVAL_EXPERIMENT_MD`
- `HARNESS_EVAL_GIT_POLICY`
- `HARNESS_EVAL_PROJECT_ROOT`
- `HARNESS_EVAL_SLUG`
- `HARNESS_EVAL_TIMEOUT`
