# Harness Eval — 量化脚手架设计

> 参考自《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》
> 落地在 ai-research-workflow（claude 分支）上的 v1 架构（hybrid judge + 4 道题）。

## 我们在量化什么

`ai-research-workflow` 本身就是一个 **Harness 工作流**：

```text
用户问题 -> RESEARCH.md -> LITERATURE.md -> EXPERIMENT.md
          -> scripts/ + runs/ -> RUNS.md -> RESULTS.md -> CLAIMS.md
          -> REPRODUCIBILITY.md -> 论文/报告
```

每一步都是一个"概率程序"——靠 LLM + skill + rules + context 共同决定输出。
改一条 rule、补一段 rubric、换一段 prompt，蝴蝶效应可能让下一版完全跑偏。

这篇文章的核心命题适用于这里：

> **任何不可量化的东西都不可优化。**

我们要给这个工作流搭一个"考试系统"，让它从"主观 vibes 驱动开发"变成
"数据驱动回归"。

## 三个不可妥协的原则

来自文章，我们原样保留作为设计的北极星：

1. **可重复 > 精确**。一道题跑 N 次，看分布趋势，不追单次满分。
2. **可归因 > 高分**。失败必须能告诉你"为什么失败"——工作流漏洞 / 题目歧义 / 模型短板。
3. **闭环 > 单向**。跑完评测直接喂回到下一轮迭代，不是出一份成绩单就完事。

## v0 → v1 演进

| 维度 | v0 (2026-06-19 上午) | v1 (现在) | 关键变化 |
|---|---|---|---|
| 判官 | 纯 RuleJudge（启发式） | HybridJudge（H=Rule + Q=LLM） | 质量项从"看感觉的启发式"升级到 LLM 多维评分 |
| LLM judge | 占位 `NotImplementedError` | `ClaudeCodeJudge` 走 `claude -p` + JSON schema | 真实可用，零 API key 依赖（复用 Claude Code 鉴权） |
| Fallback | 无 | LLM 失败 → RuleJudge Q；整条 pipeline 不破 | |
| rubric 解析 | 001/002 题目 hardcode 在 judge.py | 自动从 rubric.md 解析 H3+，启发式覆盖 6 种模式 | 新题不用改 judge.py |
| 题库 | 2 道（波次 1） | 4 道（波次 1+2） | 加了 scope_locking（HARD GATE）和 branch_confirmation（BRANCH GATE） |
| 改进建议 | 题目 specific 启发式 | LLM 多维（faithfulness / completeness / actionability / integration / evidence_quality）| 能抓"自承不存在却未删引用"这种诚信偏差 |
| worktree 清理 | 只清 sandbox，残留 `__eval__*` 分支 | `ws.cleanup()` 也删临时分支 | 避免 git 堆积 |
| JSON 解析 | 单一 json.loads | 平衡大括号优先（避免 non-greedy regex 误吃嵌套 JSON）| LLM 输出 robustness 提升 |

## 判官架构决策（v1 hybrid）

文章原方案只提"独立 LLM 进程"，没说 H/Q 分不分。

我们的判断：

- **H 项**（硬性项：文件存在、必填小节、必填字段、关键词命中、§N 引用）本质是"是否做了"的 binary 判定
  - 启发式 + keyword + regex 完全够用
  - 零成本、零延迟、确定性强（同一道题跑两次结果一致）
  - LLM 给的话可能不一致（"5.0 还是 4.8"），且慢且贵
- **Q 项**（质量项：是否"做得好"）本质是品味判断
  - 启发式给不出"自承不存在却未删引用 — 诚信偏差"这种细致判断
  - LLM 的多维评分（faithfulness / completeness / actionability / integration / evidence_quality）远超任何固定启发式
  - 慢且贵但物有所值

**所以 v1 默认 `hybrid`：H=RuleJudge, Q=LLMJudge**。这让"硬性失败"确定可复现，让"质量批评"细致有营养。

**Fallback 链**（按顺序）：
1. LLM CLI 不可用（claude/codex 不在 PATH）→ RuleJudge Q
2. LLM 超时（300s 默认）→ RuleJudge Q
3. LLM JSON 解析失败（含 markdown 包装 / 嵌套 JSON）→ RuleJudge Q
4. LLM 输出 quality 数组为空 → RuleJudge Q

所有 fallback 都在 `verdict.notes` 里显式标注（"Q 项来源: RuleJudge[fallback]（LLM 调用失败: ...）"），不会 silent degrade。

## LLM judge 调什么 / 怎么调

```bash
# 默认：检测本地可用 CLI（claude 优先，codex 备选）
python3 -m harness_eval.runner.cli run 003_scope_locking --judge hybrid

# 强制 claude
python3 -m harness_eval.runner.cli run 003_scope_locking --judge claude

# 强制 codex
python3 -m harness_eval.runner.cli run 003_scope_locking --judge codex
```

底层调用：

```bash
claude -p "<rubric + 工件 + transcript 摘要>" \
    --output-format json \
    --json-schema '<5 维 quality + improvements schema>' \
    --model sonnet
```

**为什么是 CLI 而不是直接调 Anthropic API？**

- 用户的 ai-research-workflow 主要在 Claude Code 里跑，复用 Claude Code 的鉴权
- 不需要单独管理 ANTHROPIC_API_KEY
- codex 作为等价 fallback，行为可对比
- 切到 codex 0 改动（只是 argv_template 换）

**成本**：单题 ~$0.30（5 维评分 + 改进建议），全 4 题 batch ~$1.20
**延迟**：单题 ~60-120 秒

**5 维评分 schema**（跨题目复用，rubric.md 的 Q 项可与之映射）：

| 维度 | 含义 | 关注点 |
|---|---|---|
| faithfulness | 忠实于源材料 | 不凭空捏造引用、数字、结论 |
| completeness | 覆盖完整度 | 是否回应 task.md 的每条要求 |
| actionability | 可执行性 | 描述/范围/触发条件可操作，不是空洞口号 |
| integration | 集成一致性 | 与上下游 artifact 的引用、单位、命名、claim_id 保持一致 |
| evidence_quality | 证据链质量 | 失败有归因、结论有 run_id / claim_id 锚点、不粉饰 |

## rubric.md 自动解析（v1 新增）

`RuleJudge._check_hard_from_rubric` 从 rubric.md 的 `## 一、硬性通过项` 区段解析 H3+，启发式覆盖 6 种描述模式：

| 模式 | 例子 |
|---|---|
| 包含 X 小节 | "包含 `in_scope` 小节" |
| X 小节 至少 N 条 | "`in_scope` 小节至少包含 2 条列表项" |
| 每条 X 含 N 个 KEY 关键词 | "每条 `out_of_scope` 含 1 个拒绝理由关键词" |
| 包含 X 字段 | "包含 `branch_name` 字段" |
| X 符合 A / B / C 前缀 | "branch_name 符合 `feature` / `fix` 前缀" |
| X 是有效值 | "base_branch 是有效值（`main` / `feat/...`）" |
| X 引用 Y 至少 1 章节 | "rationale 引用 §1 到 §6 至少 1 项" |
| 引用 FILE | "正文显式引用 `RESEARCH.md` |
| transcript 中存在读 X | "transcript 中存在对 `git_preflight_policy.md` 的读取" |

**找不到模式 → 显式标 `RuleJudge[unevaluable]: ...` + 提示需 LLM judge 补判**。
不静默 pass（避免 v0 那种"启发式没识别 = 算 pass"的 false negative 陷阱）。

## 系统全景（v1）

```text
items/                  题库：每个题目一个目录，4 文件
  _template/            新题模板（meta/task/rubric/env）
  001_experiment_design/   波次 1 — 实验设计
  002_run_distillation/    波次 1 — 跑分蒸馏
  003_scope_locking/       波次 2 — scope 锁定（HARD GATE）
  004_branch_confirmation/ 波次 2 — branch 确认（BRANCH GATE）

runner/                 执行引擎（Python）
  loader.py             题目加载 + 模板变量
  workspace.py          git worktree 沙箱（自动清理 __eval__ 分支）
  driver.py             编排：跑考生 + 抓 transcript
  transcript.py         记录 transcript.jsonl
  judge.py              RuleJudge（v0 + v1 rubric 解析 + field extractor）
  judge_llm.py          LLM judge（v1 新增，claude/codex，含 JSON 解析 robustness）
  scoring.py            写 score.yaml / review.md
  aggregate.py          聚合 latest.md / score-history.yaml / batch-insights.md
  cli.py                CLI 入口（--judge rule/hybrid/llm/claude/codex）

candidates/             示例考生实现
  draft_experiment_md.py     001 candidate
  distill_run_to_results.py  002 candidate
  scope_lock.py              003 candidate
  plan_branch.py             004 candidate
```

## 闭环怎么形成

```text
一次跑题
  -> score.yaml 记录 pass/fail + 2 维分数（compliance + execution_quality）
  -> review.md 记录 evidence + improvements
  -> improvements 按 [workflow] / [eval] / [capability] 三维分类
     [workflow] -> 直接喂回 ai-research-workflow 的 skill 更新
     [eval]     -> 直接喂回题库 rubric/task 修订
     [capability] -> 提示换模型 / 换工具 / 加 guard

一批跑题（多道题 × 多次）
  -> latest.md / latest-stats.yaml 汇总本批
  -> score-history.yaml 扁平记录全历史（带 workflow_rev 字段）
  -> batch-insights.md 跨题聚合改进建议
```

`workflow_rev` 字段绑定 git commit，让你 6 个月后问
"v0.4 通过率从 0.4 跳到 0.8 到底改了什么"时，可以直接定位到那次 commit。

## 跑一道题会发生什么（v1 hybrid）

```text
1. workspace.py 准备 git worktree 沙箱（创建 __eval__<run_id> 临时分支）
2. driver.py 把 fixtures 复制到 .fixtures_eval/ + harness_eval 复制到沙箱
3. 跑 env.yaml.setup 的 check 命令
4. 启动考生命令（cwd=sandbox, env=item.env.env overrides）
5. transcript.py 记录所有 IO 到 transcript.jsonl（stdout/stderr/tool_call/file_read/file_write/exit）
6. 收集工件（env.yaml.outputs 路径）
7. 调 HybridJudge.judge()：
   a. RuleJudge.judge() → verdict.hard_checks（H 项确定性评估）
   b. _resolve_provider() → 检测本地 claude/codex
   c. 拼 prompt（rubric + 工件 + transcript 摘要）+ JSON schema
   d. _call_llm() → subprocess.run(claude -p ...) 或 codex exec ...
   e. _parse_stringy_result() → 平衡大括号提取（避免 non-greedy regex 误吃嵌套 JSON）
   f. _parse_llm_result() → QualityScore / Improvement 列表
   g. 任意步骤失败 → fallback 到 RuleJudge 的 Q 项，notes 标注
8. scoring.py 写 score.yaml + review.md
9. aggregate.py 更新 score-history.yaml
10. ws.cleanup() 拆 worktree + 删 __eval__<run_id> 临时分支

总耗时：v1 hybrid 单题预计 90-180s（含一次 LLM 调用），一次跑批 4 题 ≈ 10-15min
成本：v1 hybrid 单题 ~$0.30，4 题 batch ~$1.20
```

## 题目分层（v1 已铺 2 波次 4 道题）

文章建议 5 波次分层：

| 波次 | 主题 | v1 状态 | 题号 |
|---|---|---|---|
| 1 | 主干闭环：研究问题 → 实验 → 跑分 → 蒸馏 | ✅ 2 道 | 001 / 002 |
| 2 | 状态机 & 门禁（scope / branch） | ✅ 2 道 | 003 / 004 |
| 3 | 知识库闭环 | 待铺 | — |
| 4 | 周边 skill | 待铺 | — |
| 5 | 韧性场景（失败修复、Critical 拦截） | 待铺 | — |

## 评判标准（pass/fail + 二维分数）

```yaml
result: pass | fail                    # 二元结论（overall >= pass_threshold）
compliance: 1-5                        # 流程遵循度：rubric 硬性项通过率 * 5
execution_quality: 1-5                 # 执行质量：LLM 5 维平均分
overall: 1-5                           # 综合分：0.5 * compliance + 0.5 * quality
hard_checks:                           # 来自 RuleJudge（H=确定性）
  - id: H1..H11
    description: "..."
    passed: true|false
    evidence: "..."
quality_scores:                        # 来自 LLM judge（Q=5 维）
  - id: Q1..Q5
    name: faithfulness|completeness|...
    score: 0-5
    notes: "..."
improvements:                          # 来自 LLM judge，强制 [workflow]/[eval]/[capability] 三维归因
  - dimension: workflow|eval|capability
    finding: "..."
    action: "..."
```

## 下一步（v1 跑通后）

- [ ] 扩题库到波次 3（知识库闭环）
- [ ] 加 sensitivity / regression 看板（按 workflow_rev 对比 pass rate 趋势）
- [ ] LLM judge cache（同 item_id + main_text hash 不重复调 LLM）
- [ ] 引入"考官"角色做多轮交互题
- [ ] 接入真实 Cursor/Codebuddy CLI 作为考生
- [ ] 加 symlink 替换工作流快照（多候选人同题对比）

## 参考

- 文章：《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》
- 核心哲学：可重复 > 精确 / 可归因 > 高分 / 闭环 > 单向
