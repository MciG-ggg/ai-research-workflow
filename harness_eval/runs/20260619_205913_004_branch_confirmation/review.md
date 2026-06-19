# Review — 004_branch_confirmation / 20260619_205913_004_branch_confirmation

- **Result**: `pass`
- **Overall**: 4.7 / 5
- **Compliance**: 5.0 / 5 (11/11 hard checks)
- **Execution Quality**: 4.4 / 5
- **Candidate**: `python3 -m candidates.plan_branch`
- **Workflow Rev**: `4ce5064`

## Hard Checks

| ID | Description | Pass | Evidence |
|----|-------------|------|---------|
| H1 | 主工件存在且非空 | PASS | len(text)=3938 |
| H2 | 主工件大小 >= 500 字节 | PASS | bytes=5289 |
| H3 | 包含 `branch_name` 字段 | PASS | matched field: 'branch_name' |
| H4 | 包含 `base_branch` 字段 | PASS | matched field: 'base_branch' |
| H5 | branch_name 符合 `feature` / `fix` / `chore` / `refactor` / `exp` / `docs` 前缀 | PASS | branch_name='exp/mamba-long-context-eval' 前缀匹配 ['feature', 'fix', 'chore', 'refactor', 'exp', 'docs'] |
| H6 | base_branch 是有效值（`main` / `feat/...` / `exp/...` 等） | PASS | base_branch='main' 匹配 'main' |
| H7 | rationale 引用 `git_preflight_policy` 至少 1 个具体章节（`§1` 到 `§6`） | PASS | rationale 引用了 1/2 章节: §['1', '6'] |
| H8 | `depends_on` 至少包含 1 条（EXPERIMENT.md / SCOPE.md / CLAIMS.md / git_preflight_policy 之一） | PASS | depends_on='3 条' 命中 3/4 候选: ['EXPERIMENT.md', 'SCOPE.md', 'CLAIMS.md'] |
| H9 | `risk` 小节至少包含 1 条具体风险标注 | PASS | detected 10 list items in 'risk' 小节 (need ≥1) |
| H10 | 正文显式引用 `EXPERIMENT.md`（确认已读） | PASS | found EXPERIMENT.md |
| H11 | transcript 中存在对 `git_preflight_policy.md` 的读取调用 | PASS | transcript 中找到 |

## Quality Scores

| ID | Description | Score (0-5) | Notes |
|----|-------------|-------------|-------|
| Q1 | faithfulness | 4.0 | branch_name `exp/mamba-long-context-eval` 明确从 EXPERIMENT.md 第 1 段 ('Mamba-1 vs Mamba-2 长上下文代码生成') 提炼，scope 22 字符 ≤ 32 字符限制有理有据（BRANCH_PLAN.md: 'branch_name' 段）。rationale 中没有凭空捏造 claim_id（C1/C2/C3/C4/C5 来自 CLAIMS.md 状态机），数字（5pp、22-23G、24G）都锚定到可观测指标。扣 1 分：worktree_path 用 `20260619_174000_004_branch_confirmation` 而实际 run 是 `20260619_205913_004_branch_confirmation`，run_id 不一致是模板硬编码痕迹，transcript 中 candidate 脚本输出 '[candidate] wrote BRANCH_PLAN.md (3938 bytes)' 后又被 Write 成 5289 bytes，存在双重写入链路但解释不清。 |
| Q2 | completeness | 5.0 | 6 个结构化字段全部齐备且各自有详细校验段：branch_name（§2 校验）、base_branch（§3 白名单校验）、worktree_path（§4 前缀校验）、depends_on（3 条全部 '已校验存在'）、rationale（引用 §5 风险清单 5 项）、risk（R1-R5 五条具体风险）。额外增加了 HARD GATE 校验总览表（G1-G5 PASS）、启动前最终决策段、引用一致性段。Rubric H1-H11 全部命中（transcript 显示读了 fixtures 三个文件 + read BRANCH_PLAN.md + exec candidate script）。 |
| Q3 | actionability | 3.0 | 路径格式 `harness_eval/runs/<run_id>/sandbox/` 符合 §4 前缀要求，`git worktree add harness_eval/runs/20260619_174000_004_branch_confirmation/sandbox exp/mamba-long-context-eval` 在语法层面可执行。但关键问题：worktree_path 的 run_id (`20260619_174000`) 与当前 sandbox 的实际 run_id (`20260619_205913`) 不一致——这是模板硬编码的产物，落到真实环境会 git worktree add 失败（父目录不存在）。R3 给出的回滚命令 `git worktree remove --force` + `git checkout main` 是可执行命令，但 R1 提到的 'codellama-7b-instruct 5pp 阈值'、R2 的 'nvidia-smi OOM 检测' 都是 prompt-level 描述而非落地的诊断脚本。 |
| Q4 | integration | 5.0 | rationale 显式引用 §2/§3/§4/§5/§6，与 fixture 文件结构对齐（rubric 标注 §1-§6 存在）。depends_on 三条全部用绝对路径交叉引用 fixtures 实际文件路径：`/Users/mcig/Projects/ai-research-workflow/harness_eval/runs/20260619_205913_004_branch_confirmation/sandbox/.fixtures_eval/{EXPERIMENT.md,RESEARCH.md,git_preflight_policy.md}`。HARD GATE G3 明确要求 'EXPERIMENT.md 存在 + branch exp/ 前缀'，与 §2/§3 交叉验证一致。claim_id (C1-C5) 在 R4 中锚定到 CLAIMS.md 状态机，符合 §5 claim 状态机影响条款。 |
| Q5 | evidence_quality | 5.0 | 5 条 risk 每条都标注了具体可观测信号：R1 (`nvidia-smi` OOM + 与 paper 数字差 ≥ 5pp)、R2 (单卡 24G 显存峰值 22-23G → nvidia-smi 显示 OOM)、R3 (`git worktree remove --force` 命令)、R4 (RESULTS.md 'claim alignment' 表 partial → refuted)、R5 (G1-G5 全部 PASS)。每条 risk 都给出回滚/检测方法而非空洞的'可能有冲突'。transcript 中可看到 candidate 脚本运行后实际读取了三个 fixtures 文件并 test -f 校验存在，证据链完整。 |

## Improvements

### [workflow]

- **Finding**: BRANCH_PLAN.md 模板把 worktree_path 写死为示例 run_id（`20260619_174000`），与真实 run 目录（`20260619_205913`）脱节，落地时 git worktree add 会因父目录缺失而失败。
  - **Action**: 在 `candidates/plan_branch` 注入 `{run_id}` 模板变量，渲染前用 `Path(__file__).parents[2].name` 或环境变量 `EVAL_RUN_ID` 动态替换，并加 G4 HARD GATE 自动断言 `worktree_path.parent.exists()`。

### [eval]

- **Finding**: Rubric H/Q 项没有显式要求 candidate 跑 `git worktree add --dry-run` 或 `test -d $(dirname worktree_path)` 来证明 path 实际可达，导致模板硬编码 bug 无法被机械化拦截。
  - **Action**: 在 rubric 加 H12：'worktree_path 父目录必须在 transcript 中被 test -d 验证存在'，并把 Q3 的 actionability 拆成 syntax_valid 和 runtime_exists 两个子项。

### [capability]

- **Finding**: transcript 中 candidate 脚本先写 3938 bytes 再被 Write 覆写为 5289 bytes，但中间没有任何 'I am extending because...' 的说明，artifact 与 candidate 原始输出混在一起，溯源不清。
  - **Action**: 考生/agent 应在 BRANCH_PLAN.md 顶部加 'Generation Trace' 段：列出 candidate 脚本版本、覆写原因、增量 diff 行数，让评审可区分机器生成与人工/agent 后处理。

## Notes

- judge: hybrid (H=RuleJudge, Q=LLM[auto])
- Q 项来源: LLM[claude/sonnet] (77.8s, exit=0)
- LLM summary: 工件整体质量优秀：11 条硬性通过项全部命中（H1-H11：文件 5289 字节、字段齐全、§2-§6 多处引用、风险 5 条具体可观测、transcript 显示读取三个 fixtures + 执行 candidate 脚本），6 个结构化字段齐备且各自有校验段，质量 5 维平均 4.4。唯一显著扣分点是 Q3 actionability：worktree_path 模板硬编码了与实际 run_id 不一致的路径，落到真实 git worktree add 会失败；建议工作流侧加 G4 父目录存在性断言并动态注入 run_id。overall = 0.5*5.0 + 0.5*4.4 = 4.
- LLM raw_output[:1500]: {"type":"result","subtype":"success","is_error":false,"api_error_status":null,"duration_ms":76888,"duration_api_ms":76051,"ttft_ms":31227,"ttft_stream_ms":4000,"time_to_request_ms":166,"num_turns":3,"result":"判卷完成。`004_branch_confirmation` 评估结果：\n\n- **合规性**：11/11 硬性通过项全部命中\n- **质量 5 维**：Q1=4, Q2=5, Q3=3, Q4=5, Q5=5，平均 4.4\n- **overall**：0.5×5.0 + 0.5×4.4 = **4.7** → **PASS** (≥ 3.5)\n- **关键扣分**：Q3 actionability — worktree_path 用硬编码 `20260619_174000` 而实际 run_id 是 `20260619_205913`，父目录在真实环境不存在，`git worktree add` 会失败\n- **3 条改进建议**：1 条 `[workflow]`（模板动态注入 run_id + G4 父目录断言）、1 条 `[eval]`（rubric 加 H12 强制 test -d 校验）、1 条 `[capability]`（artifact 顶部加 Generation Trace 段区分脚本生成 vs 后处理）","stop_reason":"end_turn","session_id":"dd27649b-1d34-4a0c-9c2e-fd6a2fed1fa5","total_cost_usd":0.4063125,"usage":{"input_tokens":43085,"cache_creation_input_tokens":0,"cache_read_input_tokens":80375,"output_tokens":6028,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{"MiniMax-M3":{"inputTokens":43085,"outputTokens":6028,"cacheReadInputTokens":80375,"cacheCreationInputTokens":0,"webSearchRequests":0,"costUSD":0.4063125,"contextWindow":200000,"maxOutputTokens":32000}},"permission_denials":[],"structured_output":{"quality":[{"id":"Q1","name":"faithfulness","score":4,"notes":"branch_name `exp/mamba-long-context-eval` 明
