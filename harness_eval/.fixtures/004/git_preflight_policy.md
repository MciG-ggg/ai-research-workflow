# Git Pre-flight Policy（worktree / branch 规则摘要）

> 本文件是项目里 `.omx/git-preflight` skill 的简版规则。
> 完整版本见 `skills/git-preflight/SKILL.md`。

## 一、什么时候必须跑 preflight

启动任何 `worktree` 操作前，必须：

1. 确认**前置工件**已存在
2. 确认**目标分支**命名符合规范
3. 确认**不会与现有 worktree 冲突**

## 二、branch 命名规范

- 格式：`<type>/<scope>[-<detail>]`
- 允许的 type：`feature` / `fix` / `chore` / `refactor` / `exp` / `docs`
- scope：1-3 个 kebab-case 词，**不超过 32 字符**
- 示例：
  - `feature/mamba-long-context-eval`
  - `exp/repobench-mamba-ablation`
  - `fix/humaneval-oom-mamba`

## 三、base_branch 选择

- 优先选 `main`（稳定基线）
- 如果是基于某个未合入的 feature，base = `feat/<that-feature>`
- **禁止**从 `__eval__*` 或 `__test__*` 临时分支切
- 跨多 step 的实验，base = 上一步的输出分支

## 四、worktree 路径

- 路径前缀：`harness_eval/runs/<run_id>/sandbox/`
- 沙箱内是**隔离的 git checkout**，与主目录互不污染
- 沙箱跑完后必须 `worktree remove --force` 清理

## 五、风险标注必须项

任何 `BRANCH_PLAN.md` 必须显式列出 ≥ 1 个风险点，至少覆盖：

- [ ] **前置工件依赖**：EXPERIMENT.md / SCOPE.md / CLAIMS.md 是否存在？
- [ ] **资源冲突**：是否与已存在的 worktree 冲突？
- [ ] **回滚路径**：如果实验跑挂，怎么回到 base_branch？
- [ ] **claim 状态机影响**：会不会污染 CLAIMS.md 的已有状态？

## 六、HARD GATE

- **G1**：branch_name 不符合 §2 → 拒绝
- **G2**：base_branch 不在 §3 白名单 → 拒绝
- **G3**：EXPERIMENT.md 不存在但 branch 含 `exp/` 前缀 → 拒绝
- **G4**：worktree 路径与已存在 worktree 重叠 → 拒绝
- **G5**：rationale 不引用 §5 风险清单任意 1 项 → 拒绝
