# Review — 003_scope_locking / 20260619_205745_003_scope_locking

- **Result**: `pass`
- **Overall**: 5.0 / 5
- **Compliance**: 5.0 / 5 (11/11 hard checks)
- **Execution Quality**: 5.0 / 5
- **Candidate**: `python3 -m candidates.scope_lock`
- **Workflow Rev**: `4ce5064`

## Hard Checks

| ID | Description | Pass | Evidence |
|----|-------------|------|---------|
| H1 | 主工件存在且非空 | PASS | len(text)=3526 |
| H2 | 主工件大小 >= 500 字节 | PASS | bytes=5725 |
| H3 | 包含 `in_scope` 小节 | PASS | matched section: 'in_scope' |
| H4 | 包含 `out_of_scope` 小节 | PASS | matched section: 'out_of_scope' |
| H5 | 包含 `deferred` 小节 | PASS | matched section: 'deferred' |
| H6 | `in_scope` 小节至少包含 2 条列表项 | PASS | detected 4 list items in 'in_scope' (need ≥2) |
| H7 | `out_of_scope` 小节至少包含 1 条列表项 | PASS | detected 4 list items in 'out_of_scope' (need ≥1) |
| H8 | `deferred` 小节至少包含 1 条列表项 | PASS | detected 3 list items in 'deferred' (need ≥1) |
| H9 | 正文显式引用 `RESEARCH.md`（不止一次） | PASS | found RESEARCH.md |
| H10 | `out_of_scope` 小节里的列表项，每条至少含 1 个拒绝理由关键词（`因为` / `优先级` / `范围外` / `资源` / `冲突` / `不在范围内`） | PASS | 4/4 条列表项命中关键词: ['因为', '优先级', '范围外'] |
| H11 | `deferred` 小节里的列表项，每条至少含 1 个触发条件关键词（`当` / `如果` / `触发` / `再次` / `恢复` / `达成` / `完成后`） | PASS | 3/3 条列表项命中关键词: ['当', '如果', '触发'] |

## Quality Scores

| ID | Description | Score (0-5) | Notes |
|----|-------------|-------------|-------|
| Q1 | faithfulness | 5.0 | SCOPE.md 第 13-26 行 (in_scope) 全部指向 RESEARCH.md '想研究的问题'小节 第 1/2 条与 '范围'小节的具体条目；引用结构与 Mamba/SSM 研究上下文一致，未见捏造的数字或 hypothesis。 |
| Q2 | completeness | 5.0 | 6 条 NEW_REQUEST 需求逐一判定：需求 1(视觉)→out_of_scope #1、需求 2(Mamba-2 vs Mamba-1)→in_scope #1、需求 3(训练加速)→out_of_scope #2、需求 4(100B)→out_of_scope #3、需求 5(H3/Hyena/RetNet)→拆分为 out_of_scope #4 + deferred #1、需求 6(跨语言 HumanEval-X)→deferred #2。另识别 2 条隐藏需求（baseline 分层、失败 run 记录），覆盖面优于门槛。 |
| Q3 | actionability | 5.0 | deferred 三条触发条件全部可观测：差距 ≥ 2pp + pass@1 在 H1 ±2pp 范围内 + 8k OOM 现象复现 ≥ 1 次 + C2 claim 从 unverified 升级为 partial/confirmed。引用了具体的 claim 状态机和量化阈值，无 '以后再说' 类空话。 |
| Q4 | integration | 5.0 | out_of_scope 拒绝理由均回溯到 RESEARCH.md 具体小节：视觉→'明确不做的方向：视觉任务 / 多模态'、训练加速→'训练阶段的优化（仅做推理评测）'、100B→'单卡 24G GPU' 硬件约束、H3→'想研究的问题第 3 条没说要完整 ablation'。deferred 触发条件引用 EXPERIMENT.md H1 证伪阈值与主实验 claim 状态机，跨 artifact 命名一致。 |
| Q5 | evidence_quality | 5.0 | NEW_REQUEST 需求 1（视觉）被显式拒绝并引用 RESEARCH.md 明确白名单外条款，未偷入 in_scope；in_scope #4 '记录失败 run' 明确要求保留 OOM 失败结果到 RESULTS.md，体现反 cherry-picking 原则。所有判定均有 RESEARCH.md 段落或 claim_id 锚点。 |

## Improvements

### [workflow]

- **Finding**: candidate 在 '锁定后下一步' 第 4 条提到要新建 watchlist.md，但当前 SCOPE 模板未强制把 deferred 触发条件抽成可机读 watch list
  - **Action**: 在 SCOPE 模板新增 ## Watch List 小节，把每条 deferred 的触发条件固化为可由自动化 cron 扫描的结构化字段（threshold, condition, action）

### [eval]

- **Finding**: rubric 未规定 '隐藏需求' (源自 RESEARCH 而非 NEW_REQUEST) 的标注格式，candidate 用了 '隐藏需求' 字样但未引用具体 NEW_REQUEST 项号
  - **Action**: 在 task.md 增加 'RESEARCH-derived requirements' 标签规则，要求 candidate 显式注明隐藏需求的 RESEARCH.md 来源小节行号
- **Finding**: SCOPE.md 中 '引用一致性' 小节是 candidate 的元评论而非锁定产物，可能让 reader 混淆 '锁定' vs '审计'
  - **Action**: 将 '引用一致性' 从 SCOPE.md 拆到独立 AUDIT.md，避免 scope 锁定工件混入审计性元数据

## Notes

- judge: hybrid (H=RuleJudge, Q=LLM[auto])
- Q 项来源: LLM[claude/sonnet] (87.2s, exit=0)
- LLM summary: compliance=11/11 (H1-H11 全部通过)；execution_quality=5.0 (Q1-Q5 全部满分，'因为'/'当...则' 等触发关键词命中，引用一致性小节体现元审计意识，in_scope 包含 baseline 分层与失败 run 记录两条隐藏需求属加分项)。overall = 0.5*5 + 0.5*5 = 5.0，pass=true。工件在典型失分点（视觉偷入 in_scope / deferred 写'以后再说' / 自循环引用）均未踩雷。
- LLM raw_output[:1500]: {"type":"result","subtype":"success","is_error":false,"api_error_status":null,"duration_ms":86295,"duration_api_ms":85447,"ttft_ms":60783,"ttft_stream_ms":11585,"time_to_request_ms":183,"num_turns":3,"result":"判卷完成。`003_scope_locking` 工件通过所有 11 项硬性门槛（H1-H11），Q1-Q5 质量维度均给 5 分。**overall = 5.0，pass = true**。\n\n主要亮点：\n- 6 条 NEW_REQUEST 需求全部显式判定（无遗漏、无偷纳入）\n- deferred 三条触发条件全部可观测（量化阈值 + claim 状态机锚点）\n- 视觉需求显式拒绝并引用 RESEARCH.md 白名单条款\n- 主动识别 2 条隐藏需求（baseline 分层、失败 run 记录），体现反 cherry-picking 意识\n\n改进建议集中在 [eval]（隐藏需求标签规则、引用一致性元评论应拆出 SCOPE 工件）和 [workflow]（deferred 触发条件应固化为可机读 Watch List 字段）。","stop_reason":"end_turn","session_id":"23db4632-358b-49b3-9d7e-c3a82871667d","total_cost_usd":0.393568,"usage":{"input_tokens":38951,"cache_creation_input_tokens":0,"cache_read_input_tokens":85376,"output_tokens":6245,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{"MiniMax-M3":{"inputTokens":38951,"outputTokens":6245,"cacheReadInputTokens":85376,"cacheCreationInputTokens":0,"webSearchRequests":0,"costUSD":0.393568,"contextWindow":200000,"maxOutputTokens":32000}},"permission_denials":[],"structured_output":{"quality":[{"id":"Q1","name":"faithfulness","score":5,"notes":"SCOPE.md 第 13-26 行 (in_scope) 全部指向 RESEARCH.md '想研究的问题'小节 第 1/2 条与 '范围'小节的具体条目；引用结构与 Mamba/SSM 研究上下文一致，未见捏造的数字或 hypothesis。"},{"id":"Q2","na
