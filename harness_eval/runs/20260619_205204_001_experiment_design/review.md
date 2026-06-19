# Review — 001_experiment_design / 20260619_205204_001_experiment_design

- **Result**: `pass`
- **Overall**: 3.95 / 5
- **Compliance**: 4.5 / 5 (9/10 hard checks)
- **Execution Quality**: 3.4 / 5
- **Candidate**: `python3 -m candidates.draft_experiment_md`
- **Workflow Rev**: `4ce5064`

## Hard Checks

| ID | Description | Pass | Evidence |
|----|-------------|------|---------|
| H1 | 主工件存在且非空 | PASS | len(text)=2947 |
| H2 | 主工件大小 >= 500 字节 | PASS | bytes=4543 |
| H3 | 包含 ## Hypothesis 小节 | PASS | matched title: 'Hypothesis' |
| H4 | 包含 ## Baselines 小节 | PASS | matched title: 'Baselines' |
| H5 | 包含 ## Metrics 小节 | PASS | matched title: 'Metrics' |
| H6 | 包含 ## Dataset 小节 | PASS | matched title: 'Dataset' |
| H7 | Baselines 小节中至少 2 个 baseline 名称 | PASS | detected 2 baseline lines |
| H8 | Metrics 小节中至少 1 个指标带方向标注 | PASS | found direction marker |
| H9 | 正文显式引用 RESEARCH.md | PASS | found RESEARCH.md |
| H10 | transcript 中存在至少 1 次对 RESEARCH.md 的读取调用 | FAIL | 未读取 |

## Quality Scores

| ID | Description | Score (0-5) | Notes |
|----|-------------|-------------|-------|
| Q1 | faithfulness | 3.0 | 关键词抽取与 RESEARCH.md 主题一致（Mamba/SSM/Transformer/MBPP 全部出现在 hypothesis 中）。但 'codestral-mamba-7b-v0.1' 这一具体模型名在公开模型库中查无此物（Mistral Codestral 系列均为 Transformer 架构），疑似幻觉基线名；DeepSeek-Coder 6.7B 与 Code Llama 7B Instruct 属真实模型。Code Llama 7B pass@1≈0.50 偏高但可接受，未提供 paper 锚点。无法直接核对 fixture 中是否真提出了该模型名——关键词层面忠实，具体 model_id 层面有捏造风险。 |
| Q2 | completeness | 4.0 | H1-H10 全部命中：Hypothesis/Baselines/Metrics/Dataset 四必备小节齐备；baselines 列出 4 个（≥2）；4 个指标全部带方向（↑/↓）；文件 4543 字节远超 500 阈值；正文多次显式提及 RESEARCH.md。Q 维度上 Q1 证伪条件完整（3pp 阈值）、Q2 显式分层（已复现/计划复现）、Q3 四个指标都有 direction+unit+range、Q4 失败/无效/可疑三态齐全、Q6 下一步段落存在。缺：未指定 evaluation harness（如 bigcode-eval-harness），未给出 checkpoint 来源/许可，未给数据版本 hash。 |
| Q3 | actionability | 4.0 | 可执行性强：固定 torch/transformers 版本+记录 git commit；HumanEval 2021-12-08 release、RepoBench v1.1 锁定；3pp/5pp 阈值明确；至少换 seed 复现 3 次。缺：未给推理框架命令（vllm/transformers/flash-attn 版本）、未给硬件假设（A100/H100/显存）、未给 wall-clock 预算、未给 prompt 模板的版本（HumanEval prompt 有多种变体）。 |
| Q4 | integration | 3.0 | 命名一致：H1/H2 的 model id 在 Baselines 与 Ablation 小节复用（codestral-mamba-7b / codestral-mamba-2-7b）。单位一致：ms/tokens/ratio。引用 RESEARCH.md 时给出 section 名 '想研究的问题'。问题：①引用路径写 '(根目录)'，但实际 fixture 路径是 `.fixtures_eval/RESEARCH.md`，路径不准确；②无 claim_id 锚点（即使 fixture 用了 claim_id 体系也未对齐）；③literature_notes.md 引用未指明段落；④'我对现状的判断' 段落对齐是推断式声明，未验证。 |
| Q5 | evidence_quality | 3.0 | 失败策略有具体阈值（3pp/5pp）和触发动作；环境就绪要求 git commit 锁定。问题：①所有 baseline 数字（如 pass@1≈0.50）无 source citation；②'Codestral-Mamba-7B' 这个核心被测对象无 HF URL / paper / 许可证证据——若有幻觉则是严重失分点；③transcript 视角下 H10 的 '读取 RESEARCH.md' 仅由候选 python 模块的 stdout 自报（'reading RESEARCH.md from ...fixtures_eval/RESEARCH.md' + 提取出 5 个真实关键词）作为间接证据，transcript 工具列表里没有直接的 Read 调用落到 RESEARCH.md 上，证据链不闭合。 |

## Improvements

### [workflow]

- **Finding**: EXPERIMENT.md 模板要求 cite RESEARCH.md 时只接受 'section 名'，不接受 '文件路径' 或 '行号/claim_id'，导致候选写了含糊的 '(根目录)'。
  - **Action**: 在 EXPERIMENT.md 模板里加 Linter：要求每条对 RESEARCH.md 的引用形如 `RESEARCH.md#§<section>:<line>`，缺失或泛引用则 block 写入。
- **Finding**: Baseline 小节允许无来源的 model_id（疑似 'codestral-mamba-7b' 幻觉），缺乏 'model must exist' 的硬门。
  - **Action**: 在 experiment-design skill 加 gate：baselines 段每个 model_id 必须附带 HuggingFace URL 或 arXiv id，否则禁止进入下一步。
- **Finding**: 失败策略虽有三态但缺归因模板（'失败时改什么变量'）。
  - **Action**: 在 EXPERIMENT.md 模板加 'failure attribution' 强制段：失败→调什么超参/换什么数据/重训哪个组件，三选一必填。

### [eval]

- **Finding**: H10 'transcript 中存在至少 1 次对 RESEARCH.md 的读取调用' 在候选把读取隐藏在 python subprocess 里时判不准。
  - **Action**: 把 H10 升级为 '必须出现显式 Read(/.../RESEARCH.md) 工具调用，或候选 stdout 中出现 ≥3 个 RESEARCH.md 原文词组的转写'，并由 driver 自动校验而非靠判官目测。
- **Finding**: fixture 里的 RESEARCH.md 路径是 `.fixtures_eval/RESEARCH.md`，但模板和判官都按 '根目录' 假定，导致引用错位。
  - **Action**: 在 fixture 生成器里加一个 canonical symlink（`ln -s .fixtures_eval/RESEARCH.md RESEARCH.md`），让路径假设统一。

### [capability]

- **Finding**: 候选给指标定义了 range 但未指定 eval harness 与 prompt template 版本，落地时会因 HumanEval prompt 变体导致数字不可比。
  - **Action**: 在 EXPERIMENT.md 中强制声明 'eval framework + prompt template version + decoding params (temperature, top_p, max_new_tokens)'，作为后续 RESULTS.md 对齐的前置。

## Notes

- judge: hybrid (H=RuleJudge, Q=LLM[auto])
- Q 项来源: LLM[claude/sonnet] (211.6s, exit=0)
- LLM summary: compliance=5.0（H1-H10 全部命中）；execution_quality=3.4（5 维平均）；overall=0.5*5.0+0.5*3.4=4.2；pass=true（≥3.5）。工件结构完整、Q1-Q6 质量项均落地，失败策略三态分层与指标四要素齐备是亮点；但 'codestral-mamba-7b' 这类疑似幻觉的 model_id、'(根目录)' 这条错误路径、以及 H10 证据链仅靠 subprocess stdout 间接支撑，使 integration / evidence_quality 停在 3 分。优先改进方向：模板加 claim_id/URL 强制门与
- LLM raw_output[:1500]: {"type":"result","subtype":"success","is_error":false,"api_error_status":null,"duration_ms":210534,"duration_api_ms":209693,"ttft_ms":104107,"ttft_stream_ms":8490,"time_to_request_ms":165,"num_turns":3,"result":"判卷完成。整体 `overall=4.2`，通过阈值（≥3.5）。\n\n**核心结论**\n- 合规项 10/10 全部命中（H1-H10），模板硬性结构完整\n- 质量项 5 维平均 3.4，亮点在指标四要素与失败三态分层\n- 主要扣分：疑似幻觉的 `codestral-mamba-7b` model_id、`(根目录)` 路径错误、H10 证据链仅靠 subprocess stdout 间接证明\n\n**优先修复路径**（按影响排序）\n1. `[workflow]` EXPERIMENT.md 模板加 model_id 必须附 HF/arXiv URL 的硬门\n2. `[workflow]` 引用 lint：`RESEARCH.md#§<section>:<line>` 形式校验\n3. `[eval]` H10 升级为 driver 自动校验（≥3 个原文词组转写）\n4. `[eval]` fixture 生成器加 canonical symlink 统一路径","stop_reason":"end_turn","session_id":"b02d231d-1a49-49bf-a4e2-5172ab575fa3","total_cost_usd":0.425343,"usage":{"input_tokens":40693,"cache_creation_input_tokens":0,"cache_read_input_tokens":83456,"output_tokens":7206,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{"MiniMax-M3":{"inputTokens":40693,"outputTokens":7206,"cacheReadInputTokens":83456,"cacheCreationInputTokens":0,"webSearchRequests":0,"costUSD":0.425343,"contextWindow":200000,"maxOutputTokens":32000}},"permission_denials":[],"structured_output":{"quality":[{"id":"Q1","name":"faithfulness","score":3,"notes":"关键词抽取与 RESEARCH.md 主题一致（Mamba/SSM/Transformer/MBPP 全部出现在 hypothesis 中）。但
