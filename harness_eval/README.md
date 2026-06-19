# Harness Eval — 量化脚手架

> 给 ai-research-workflow 跑"考试"的脚手架。
> 设计灵感来自《你的 Harness 工作流真的在进步吗？》（腾讯团队）。

## 一句话总结

**任何不可量化的东西都不可优化。**
这套脚手架给 ai-research-workflow 这个 Harness 工作流建立
"可重复、可归因、闭环"的评测系统——让你改一条 rule / 补一段 rubric
时能回答"v0.4 通过率从 0.4 跳到 0.8 到底改了什么"。

## 状态

v1（混合判官 + 4 道题）：

- [x] 4 文件题库模板（meta / task / rubric / env）
- [x] **4 道题** — 波次 1 (实验设计 / 跑分蒸馏) + 波次 2 (scope 锁定 / branch 确认)
- [x] Python 执行引擎（worktree 沙箱 + driver + transcript 录像）
- [x] **Hybrid judge** — H 项用 RuleJudge（确定性，零成本），Q 项用 LLM judge（多维度、挑剔）
- [x] **LLM judge** 走 `claude -p` / `codex` CLI（无 API key 依赖，复用 Claude Code 鉴权）
- [x] **Fallback 链** — LLM 不可用 / JSON 解析失败 → 自动回退到 RuleJudge 的 Q 项
- [x] **Rubric 自动解析** — H 项描述从 `rubric.md` 自动启发式评估（支持 section/field/keyword/§N 引用等模式）
- [x] 评分产物（score.yaml + review.md + batch-insights.md）
- [x] 改进建议强制归因到 [workflow] / [eval] / [capability] 三维
- [x] demo 4 题 100% pass, avg overall 4.66
- [ ] 引入"考官"角色做多轮交互
- [ ] 接入 Cursor / Codebuddy CLI 作为真实考生
- [ ] 加 symlink 工作流快照隔离
- [ ] 扩题库到波次 3-5

## 5 分钟上手

```bash
# 1. 自检题目 4 文件 + 模板变量
python3 -m harness_eval.runner.cli check 003_scope_locking
python3 -m harness_eval.runner.cli check 004_branch_confirmation

# 2. 跑一道题（默认 hybrid judge，H=Rule + Q=LLM）
python3 -m harness_eval.runner.cli run 003_scope_locking

# 3. 跑所有 4 道题
python3 -m harness_eval.runner.cli batch \
    001_experiment_design 002_run_distillation \
    003_scope_locking 004_branch_confirmation \
    --batch demo_v1

# 4. 聚合 + 看 insights
python3 -m harness_eval.runner.cli aggregate --batch demo_v1
cat harness_eval/latest.md
cat harness_eval/batch-insights.md   # 改进建议直接喂回 skill

# 5. 切换 judge 模式
python3 -m harness_eval.runner.cli run 003_scope_locking --judge rule     # 纯规则
python3 -m harness_eval.runner.cli run 003_scope_locking --judge hybrid   # H=rule + Q=LLM
python3 -m harness_eval.runner.cli run 003_scope_locking --judge claude   # 强制 claude provider
python3 -m harness_eval.runner.cli run 003_scope_locking --judge codex    # 强制 codex provider

# 6. 看历史
python3 -m harness_eval.runner.cli history
python3 -m harness_eval.runner.cli history --batch demo_v1
```

## 判官架构（v1）

```
┌─────────────────────────────────────────────────────────────┐
│  HybridJudge（默认 v1）                                      │
│  ┌────────────────────┐    ┌──────────────────────────────┐ │
│  │ RuleJudge           │    │ LLM judge (ClaudeCodeJudge) │ │
│  │                     │    │                              │ │
│  │ H 项：确定性         │    │ Q 项：5 维度多维评分          │ │
│  │ - 文件存在          │    │ - faithfulness               │ │
│  │ - 必填小节          │    │ - completeness               │ │
│  │ - 必填字段          │    │ - actionability              │ │
│  │ - 关键词命中         │    │ - integration                │ │
│  │ - 引用 §N 章节       │    │ - evidence_quality           │ │
│  │ - transcript 读 X    │    │                              │ │
│  │ 0 外部依赖，0 成本    │    │ 走 `claude -p --json-schema` │ │
│  └────────────────────┘    │ fallback → RuleJudge 的 Q 项  │ │
│                             └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**为什么 H=Rule + Q=LLM？**

- **H 项**是"是否做了"的硬性问题，**确定性比灵活性更重要** — 用 regex/keyword 启发式，零成本且可复现
- **Q 项**是"做得怎么样"的品味问题，**LLM 的多维判断远超启发式** — 能抓"指标定义小节自承不存在却未删引用"这种诚信偏差
- LLM 不可用 / JSON 解析失败 → 自动回退到 RuleJudge 的 Q 项，整个 pipeline 不破

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

**成本**：单题 ~$0.30（5 维评分 + 改进建议），全 4 题 batch ~$1.20
**延迟**：单题 ~60-120 秒

## 工作流改进怎么形成闭环

每次跑题，判官会输出三类改进建议（强制归因）：

- **`[workflow]`**：ai-research-workflow skill 该补什么 gate / rule / 模板
- **`[eval]`**：题库本身有什么问题（rubric 模糊 / task 误导）
- **`[capability]`**：考生暴露的通用能力短板

`batch-insights.md` 会按维度聚合，**直接对应到下一轮 skill 迭代**。
`score-history.yaml` 绑定 `workflow_rev`（git commit），让你回头定位
"v0.4 通过率提升是哪个 commit 的功劳"。

## 新增一道题

```bash
# 复制模板
cp -R harness_eval/items/_template harness_eval/items/005_<your_slug>

# 编辑 4 个文件（按文件内注释填）
$EDITOR harness_eval/items/005_<your_slug>/meta.yaml      # id / wave / difficulty / target_skill
$EDITOR harness_eval/items/005_<your_slug>/task.md        # 考生看到的题面
$EDITOR harness_eval/items/005_<your_slug>/rubric.md      # 硬性项 + 质量维度（v1 LLM 自动评 5 维）
$EDITOR harness_eval/items/005_<your_slug>/env.yaml       # setup / env / outputs / timeout

# 准备 fixtures
mkdir -p harness_eval/.fixtures/005
# 放 RESEARCH.md / EXPERIMENT.md / 其他输入材料

# 自检 + 跑
python3 -m harness_eval.runner.cli check 005_<your_slug>
python3 -m harness_eval.runner.cli run 005_<your_slug>
```

## rubric.md 写作约定（v1 自动解析）

`RuleJudge` 会从 `rubric.md` 的 `## 一、硬性通过项` 区段自动解析 H 项。

支持的 H 项描述模式：

| 模式 | 例子 | RuleJudge 行为 |
|------|------|----------------|
| 包含 X 小节 | "包含 `in_scope` 小节" | 找 `## in_scope` |
| X 小节至少 N 条 | "`in_scope` 小节至少包含 2 条列表项" | 数 `## in_scope` 块下的 `- ` |
| 每条 X 至少 N 个 KEY | "每条 `out_of_scope` 含 1 个拒绝理由关键词" | 数 `## out_of_scope` 块下命中关键词的列表项 |
| 包含 X 字段 | "包含 `branch_name` 字段" | 找 markdown 表格 / `**field**:` |
| X 符合 A / B / C 前缀 | "branch_name 符合 `feature` / `fix` 前缀" | 找字段值，匹配前缀 |
| X 是有效值 | "base_branch 是有效值（`main` / `feat/...`）" | 找字段值，匹配允许集合 |
| X 引用 Y 至少 1 章节 | "rationale 引用 §1 到 §6 至少 1 项" | 找字段值，匹配 `§N` |
| 引用 FILE | "正文显式引用 `RESEARCH.md`" | 找文件名出现 |
| transcript 中存在读 X | "transcript 中存在对 `git_preflight_policy.md` 的读取" | 找 transcript tool_call 含 X |

**找不到模式 → 标 `unevaluable`（fail）+ evidence 提示需 LLM judge 补判**。
这强制 rubric 写标准化（不要花式描述），否则 LLM judge 是唯一裁决。

## 自定义考生

题目 `meta.yaml` 里 `default_candidate` 指定默认命令。你可以用 `--candidate` 覆盖：

```bash
# 跑同一个题，但换成不同的"考生实现"，对比质量差异
python3 -m harness_eval.runner.cli run 001_experiment_design \
    --candidate "python3 -m harness_eval.candidates.draft_experiment_md_v2"
```

后续会接入 Cursor / Codebuddy CLI 作为真实考生。

## 目录结构

```text
harness_eval/
  DESIGN.md                  # 设计决策（对齐文章原文）
  README.md                  # 本文件
  items/                     # 题库
    _template/               # 4 文件模板
    001_experiment_design/   # 波次 1 — 实验设计
    002_run_distillation/    # 波次 1 — 跑分蒸馏
    003_scope_locking/       # 波次 2 — scope 锁定（HARD GATE）
    004_branch_confirmation/ # 波次 2 — branch 确认（BRANCH GATE）
  runner/                    # 执行引擎
    loader.py                # 题目加载 + 模板变量
    workspace.py             # git worktree 沙箱（自动清理 __eval__ 分支）
    driver.py                # 编排：跑考生 + 抓 transcript
    transcript.py            # 记录 transcript.jsonl
    judge.py                 # RuleJudge（v0 + v1 rubric 解析）
    judge_llm.py             # LLM judge（v1 新增，claude/codex）
    scoring.py               # 写 score.yaml / review.md
    aggregate.py             # 写 latest.md / score-history.yaml / batch-insights.md
    cli.py                   # CLI 入口
  candidates/                # 示例考生实现
    draft_experiment_md.py   # 001 candidate
    distill_run_to_results.py # 002 candidate
    scope_lock.py            # 003 candidate
    plan_branch.py           # 004 candidate
  .fixtures/                 # 题目输入数据（git 跟踪）
    001/ 002/ 003/ 004/
  runs/                      # 历史跑分（git 只跟踪 score.yaml/review.md）
    <run_id>_<item>/
      score.yaml
      review.md
      transcript.jsonl       # ignored
      artifacts/             # 考生产物副本
  latest.md                  # 本批汇总（人读）
  latest-stats.yaml          # 本批汇总（结构化）
  batch-insights.md          # 改进建议聚合（[workflow]/[eval]/[capability]）
  score-history.yaml         # 全历史扁平记录（带 workflow_rev）
```

## 参考

- 原文：《你的 Harness 工作流真的在进步吗？我们用一场考试撕掉了遮羞布》
- `harness_eval/DESIGN.md` — 完整设计决策与文章原文的对照
- `ai-research-workflow` SKILL.md — 这个评测脚手架服务的目标工作流
