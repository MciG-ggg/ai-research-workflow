# Rubric：004_branch_confirmation

> **这份文件只有判官能看到。**

## 一、硬性通过项

- [ ] **H1**：工件 `{{project_root}}/.omx/ai-research/{{slug}}/BRANCH_PLAN.md` 存在
- [ ] **H2**：文件大小 ≥ 500 字节
- [ ] **H3**：包含 `branch_name` 字段
- [ ] **H4**：包含 `base_branch` 字段
- [ ] **H5**：branch_name 符合 `feature` / `fix` / `chore` / `refactor` / `exp` / `docs` 前缀
- [ ] **H6**：base_branch 是有效值（`main` / `feat/...` / `exp/...` 等）
- [ ] **H7**：rationale 引用 `git_preflight_policy` 至少 1 个具体章节（`§1` 到 `§6`）
- [ ] **H8**：`depends_on` 至少包含 1 条（EXPERIMENT.md / SCOPE.md / CLAIMS.md / git_preflight_policy 之一）
- [ ] **H9**：`risk` 小节至少包含 1 条具体风险标注
- [ ] **H10**：正文显式引用 `EXPERIMENT.md`（确认已读）
- [ ] **H11**：transcript 中存在对 `git_preflight_policy.md` 的读取调用

## 二、质量项（LLM judge 评 5 维）

- **Q1 faithfulness**：branch_name 与 EXPERIMENT.md 的 scope 一致（不是凭空取名）
- **Q2 completeness**：6 个结构化字段（branch_name / base_branch / worktree_path / depends_on / rationale / risk）**全部**齐备
- **Q3 actionability**：worktree_path 实际可被 git worktree add 接受
- **Q4 integration**：rationale 引用的章节号（§N）真实存在于 fixture 文件里
- **Q5 evidence_quality**：risk 标注具体到可观测现象（不是"可能有风险"）

## 三、典型失分点

- branch_name 用 `test` / `temp` / `tmp` 等不规范前缀
- base_branch 写成 `__eval__*` 临时分支（违反 §3）
- rationale 写"切这个分支方便管理"（空洞，没引用 §5 风险清单）
- risk 写"可能有冲突"（不可观测）
- 没读 git_preflight_policy.md 就开始写（transcript 里能看到）
- 6 个字段缺一（task.md 明确要求全部齐备）

## 四、改进建议归因维度

- `[workflow]`：branch 模板该补的强制项
- `[eval]`：本道题 task / rubric 哪里没说清楚
- `[capability]`：考生通用能力短板

## 五、评分锚点

```text
overall = 0.5 * compliance + 0.5 * execution_quality
pass = overall >= 3.5
```
