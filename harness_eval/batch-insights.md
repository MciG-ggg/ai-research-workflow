# Batch Insights — `demo_v1_pypackage_v2`

> 把本批所有改进建议按维度聚合。`[workflow]` 直接喂回 skill 迭代。

## [workflow]

### `001_experiment_design`

- EXPERIMENT.md 模板要求 cite RESEARCH.md 时只接受 'section 名'，不接受 '文件路径' 或 '行号/claim_id'，导致候选写了含糊的 '(根目录)'。
- Baseline 小节允许无来源的 model_id（疑似 'codestral-mamba-7b' 幻觉），缺乏 'model must exist' 的硬门。
- 失败策略虽有三态但缺归因模板（'失败时改什么变量'）。

### `002_run_distillation`

- run_003 的失败归因 (gpu_model/batch_size/context_length/error_type) 是从外部知识重构的，不是从 run log 自动抽取的字段

### `003_scope_locking`

- candidate 在 '锁定后下一步' 第 4 条提到要新建 watchlist.md，但当前 SCOPE 模板未强制把 deferred 触发条件抽成可机读 watch list

### `004_branch_confirmation`

- BRANCH_PLAN.md 模板把 worktree_path 写死为示例 run_id（`20260619_174000`），与真实 run 目录（`20260619_205913`）脱节，落地时 git worktree add 会因父目录缺失而失败。

## [eval]

### `001_experiment_design`

- H10 'transcript 中存在至少 1 次对 RESEARCH.md 的读取调用' 在候选把读取隐藏在 python subprocess 里时判不准。
- fixture 里的 RESEARCH.md 路径是 `.fixtures_eval/RESEARCH.md`，但模板和判官都按 '根目录' 假定，导致引用错位。

### `002_run_distillation`

- rubric H8 只要求 claim_id 对齐但不验证 claim_id 命名格式是否与 CLAIMS.md 完全一致 (C1 vs claim_001)

### `003_scope_locking`

- rubric 未规定 '隐藏需求' (源自 RESEARCH 而非 NEW_REQUEST) 的标注格式，candidate 用了 '隐藏需求' 字样但未引用具体 NEW_REQUEST 项号
- SCOPE.md 中 '引用一致性' 小节是 candidate 的元评论而非锁定产物，可能让 reader 混淆 '锁定' vs '审计'

### `004_branch_confirmation`

- Rubric H/Q 项没有显式要求 candidate 跑 `git worktree add --dry-run` 或 `test -d $(dirname worktree_path)` 来证明 path 实际可达，导致模板硬编码 bug 无法被机械化拦截。

## [capability]

### `001_experiment_design`

- 候选给指标定义了 range 但未指定 eval harness 与 prompt template 版本，落地时会因 HumanEval prompt 变体导致数字不可比。

### `002_run_distillation`

- run_005 表格中 pass@10 写 '—'，但结论中未区分是 '未测' 还是 '数据缺失'

### `004_branch_confirmation`

- transcript 中 candidate 脚本先写 3938 bytes 再被 Write 覆写为 5289 bytes，但中间没有任何 'I am extending because...' 的说明，artifact 与 candidate 原始输出混在一起，溯源不清。
