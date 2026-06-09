# AI Research Workflow Skill (OMC)

[English README](README.md)

这是一个面向 Claude Code / oh-my-claudecode (OMC) 的 AI/ML 科研工作流 skill，用来把模糊 idea、论文、baseline 和实验计划推进成有证据约束的研究 artifact，而不是从想法直接跳到代码。

核心原则很简单：

- `RESEARCH.md` 记录研究问题、falsifiable hypothesis、范围和 claim 边界。
- `EXPERIMENT.md` 记录数据集、baseline、指标、实验运行和失败策略。
- `RUNS.md`、`RESULTS.md`、`CLAIMS.md` 和 `REPRODUCIBILITY.md` 把证据和结论分开。

这个 skill 是工作流和 artifact 框架，**不**内置通用实验 runner。项目里的真实代码、配置、训练脚本、评估脚本应该放在目标 AI research project 里。bundled 的脚本只做 framework guardrail，**不**用于跑用户实验。

这个 skill 是 Codex/OMX `ai-research-workflow` 的 OMC 版本，artifact contract 和 Python guardrail 脚本共用，但 workflow gate 走 [oh-my-claudecode (OMC)](https://github.com/MciG-ggg/oh-my-claudecode) slash 命令（`/oh-my-claudecode:deep-interview`、`/oh-my-claudecode:ralplan`、`/oh-my-claudecode:autoresearch`、`/oh-my-claudecode:ralph`、`/oh-my-claudecode:autopilot`、`/oh-my-claudecode:ultrawork`、`/oh-my-claudecode:team`），portfolio/workstream control plane 放在 `.omc/ai-research/`。

## 依赖

```bash
# 安装 oh-my-claudecode 插件
# 参见：https://github.com/MciG-ggg/oh-my-claudecode
omc setup
omc doctor
```

## 安装

```bash
git clone https://github.com/MciG-ggg/ai-research-workflow.git
mkdir -p ~/.claude/skills
cp -R ai-research-workflow/skills/ai-research-workflow-omc ~/.claude/skills/
```

仓库更新后同步 skill：

```bash
cd ai-research-workflow
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh
```

本地开发时不拉取远端：

```bash
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --no-pull
```

Updater 支持的 flag：`--no-pull`、`--symlink`、`--dry-run`、`--keep-backups N`、`--dest DIR`。Updater 会做 `git pull --ff-only`、跑 `validate_framework_contract.py` 校验源码，再做 staging `rsync -a --delete` 同步到 install dest，然后再次校验安装副本。

## 典型使用流程

This skill is a workflow, not just a logging template. 默认 workflow：

```text
optional idea scouting when no clear research question exists
  -> optional SOTA/baseline paper registry when requested
  -> optional paper-reproduction scouting when explicitly requested
  -> /oh-my-claudecode:deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
  -> literature / research artifact drafting
  -> /oh-my-claudecode:ralplan for implementation and validation shape
  -> task worktree execution in the target repo
  -> /oh-my-claudecode:autoresearch for validator-gated research loop
  -> run experiments / reproduce baselines / evaluate method
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Method implementation 和 baseline reproduction 写在目标 AI research project 的代码目录里，不放进 `.omc/ai-research/`。

```text
1. 从一个 idea、论文、baseline 或实验问题开始。
2. 可选地先做 idea / paper 调研：
   - IDEA_SCOUTING.md 记录候选研究想法
   - PAPERS.md 维护 SOTA/baseline 论文列表
3. 新开 workstream 前先走：
   /oh-my-claudecode:deep-interview --autoresearch -> /oh-my-claudecode:ralplan -> /oh-my-claudecode:autoresearch
4. 为一个具体方向创建或复用 .omc/ai-research/<slug>/。
5. 选择 workstream 类型：
   - paper-reproduction：复现一篇论文/baseline/claim，使用 REPRODUCTION.md
   - experiment-campaign：围绕假设、消融、benchmark 或方法评估跑一组实验
6. 项目代码写在目标 AI research project 里，不放进 .omc/ai-research/。
7. 记录 runs、scripts、metrics、summary 和失败情况。
8. 把稳定证据蒸馏到 RESULTS.md、CLAIMS.md、REPRODUCIBILITY.md。
9. workstream 完成后，先生成 closeout/report-before-merge plan，再合并、推送或清理 worktree。
```

## 常用命令

需要确定路由时，显式调用 skill：

```text
/oh-my-claudecode:ai-research-workflow scout            # 候选 idea 调研
/oh-my-claudecode:ai-research-workflow papers           # 查找/维护 SOTA 和 baseline 论文列表
/oh-my-claudecode:ai-research-workflow reproduce-paper  # 准备单篇论文复现 workstream
/oh-my-claudecode:ai-research-workflow experiment       # 准备 experiment-campaign workstream
/oh-my-claudecode:ai-research-workflow new-workstream   # 新建 gated 小方向
/oh-my-claudecode:ai-research-workflow handoff          # 收尾已完成的 runs/scripts/results
/oh-my-claudecode:ai-research-workflow qa               # 回答并捕获 Q&A（需启用 qa_capture）
/oh-my-claudecode:ai-research-workflow summarize        # 汇总 portfolio/workstream 状态
/oh-my-claudecode:ai-research-workflow score            # 启发式 artifact quality score
/oh-my-claudecode:ai-research-workflow closeout         # 生成 report-before-merge plan
/oh-my-claudecode:ai-research-workflow negative-result  # 保存失败/无显著/不确定结果
/oh-my-claudecode:ai-research-workflow draft            # 生成论文或报告 outline
```

If you want X, say Y:

- Generate/rank candidate ideas -> `/oh-my-claudecode:ai-research-workflow scout`。
- Find and maintain SOTA/baseline papers -> `/oh-my-claudecode:ai-research-workflow papers`。
- Reproduce one paper to find ideas -> `/oh-my-claudecode:ai-research-workflow reproduce-paper`。
- Open an experiment campaign -> `/oh-my-claudecode:ai-research-workflow experiment`。
- Start a new small direction -> `/oh-my-claudecode:ai-research-workflow new-workstream` 并完成 deep-interview/ralplan/autoresearch gate。
- Finish the current experiment -> `/oh-my-claudecode:ai-research-workflow handoff` 或 "current experiment is done"。
- Preserve a failed/null result -> `/oh-my-claudecode:ai-research-workflow negative-result`。
- Record a durable question/answer -> 启用 `--qa-capture` 或 `qa_capture: research`，先回答再记录。
- Check artifact quality before drafting -> `/oh-my-claudecode:ai-research-workflow score` + `validate_research_schema.py` + `build_evidence_graph.py`。

本地 CLI helper：

```bash
python3 skills/ai-research-workflow-omc/scripts/ai_research.py help
python3 skills/ai-research-workflow-omc/scripts/ai_research.py resolve <project-root> --prompt "这个实验做完了，整理落盘"
python3 skills/ai-research-workflow-omc/scripts/ai_research.py summarize <project-root>
python3 skills/ai-research-workflow-omc/scripts/ai_research.py score <project-root>
python3 skills/ai-research-workflow-omc/scripts/ai_research.py schema <project-root>
```

## Artifact 目录

promotion gate 提升 candidate 到正式 intake 时需要：falsifiable hypothesis、evaluation metric/baseline、lightweight evidence、novelty risk、feasibility budget、user-goal fit。

```text
.omc/ai-research/
  IDEA_SCOUTING.md   # 可选候选 idea 调研
  PAPERS.md          # 可选 SOTA/baseline 论文池
  RESEARCH.md        # 整体研究总览
  INDEX.md           # workstream 索引
  CONFIG.md          # 可选 workflow preset / mode flags
  QUESTIONS.md       # 启用 qa_capture 时可选

.omc/ai-research/<slug>/
  STATE.json
  RESEARCH.md
  LITERATURE.md
  REPRODUCTION.md    # paper-reproduction workstream 必需
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  CLAIMS.md
  REPRODUCIBILITY.md
  PAPER_DRAFT.md
  SCRIPT_REGISTRY.md
  CLOSEOUT.md
  PAPER_OUTLINE.md
  QUESTIONS.md       # 启用 qa_capture 时可选
  scripts/
  runs/
```

## 可选 feedback memory、Q&A capture 和 growth review

Research Feedback Memory、Question Capture 和 Researcher Growth Review 默认都是关闭的。除非当前调用或项目配置显式打开，否则不要创建或更新这些 feedback artifact。

调用 flag：

- `/oh-my-claudecode:ai-research-workflow --feedback-memory`：本次启用 Research Feedback Memory。
- `/oh-my-claudecode:ai-research-workflow --qa-capture`：本次启用 Q&A capture。
- `/oh-my-claudecode:ai-research-workflow --growth-review`：本次启用 Researcher Growth Review。
- `/oh-my-claudecode:ai-research-workflow --no-feedback`：本次强制关闭 feedback memory、Q&A capture、growth review。

可选项目配置在 `.omc/ai-research/CONFIG.md`：

```yaml
schema_version: 1
workflow_preset: conservative | guided | autonomous
idea_scouting: auto | off | on
completion_handoff: auto | off
worktree_closeout: off | report-before-merge
feedback_memory: off | lite | full
qa_capture: off | research | all
growth_review: off | milestone | always
```

Resolution precedence：`--no-feedback`、显式 enable flag、`.omc/ai-research/CONFIG.md`、默认 off。仅在对应模式启用时才使用 `assets/templates/CONFIG.md`、`QUESTIONS.md`、`LEARNINGS.md`、`ISSUES.md`、`DECISIONS.md`、`SKILL_GROWTH.md`、`DESIGN.md`、`NOTES.md` 和 `REVIEW.md`。

Feedback memory 记录蒸馏后的知识，不存原始日志。raw logs and run outputs stay under `runs/`，只链入或总结它们。

## 新 workstream gate

Before creating a new slug，先看 portfolio `RESEARCH.md`、root `INDEX.md` 和现有 workstream 目录。如果任务在同一个子问题上延续，reuse 或更新现有 workstream。

新 workstream 创建是 gated transition。`.omc/ai-research/<slug>/`、implementation、experiment launch、docs publishing 在下面三个 gate 全部完成、`INDEX.md` 记录了对应的 evidence 路径前都不能执行：

```text
/oh-my-claudecode:deep-interview --autoresearch
  -> /oh-my-claudecode:ralplan
  -> /oh-my-claudecode:autoresearch
```

Required gate evidence：

- `/oh-my-claudecode:deep-interview --autoresearch`：validator-ready mission/intake artifact，优先放在 `.omc/specs/autoresearch-<slug>/mission.md`、`sandbox.md` 和 `result.json`（autoresearch state/completion artifact），并 draft workstream `RESEARCH.md` 链回 portfolio。
- `/oh-my-claudecode:ralplan`：consensus planning output + `.omc/plans/prd-<slug>.md`（ralplan PRD/test spec）+ `.omc/plans/test-spec-<slug>.md`。
- `/oh-my-claudecode:autoresearch`：persisted autoresearch state with `completion_artifact_path` + 上述 autoresearch state/completion artifact。

## Task worktrees

这个 skill 在目标 AI research project 做实质性 AI research 改动时，先 inspect local git status 再开 worktree。如果主 worktree 有 local 改动，先按 semantic Lore-format commits 拆分保留；不要把无关改动合到同一个 checkpoint。主 worktree 干净后，fetch/pull primary branch，open an isolated git worktree before editing，create the task worktree from the latest commit，validation 和必要的 report-before-merge 确认之后，把完成的 branch 或合并后的 main branch 推到 remote。

优先用 `<repo>/.omc/worktrees/<scope>/`；写不了就用可写 fallback 并记录绝对路径。在目标 AI research project 维护 `.omc/worktrees/REGISTRY.md`，记录 worktree path、branch、scope、own files/areas、status。use one worktree per logical task or lane，merge worktree 时按顺序串行 merge，validation 通过后清理。

多 seed 实验：assign one seed per subagent/team lane 和 explicit idle GPU/device 或 scheduler slot，把 seed-to-device 分配表写到 `RUNS.md`。

只对 read-only 分析、快速查询、非常小的安全编辑跳过 worktree。Task worktree rule 管的是目标项目里的研究工作，不是 skill 自身的安装/维护。

## Run distillation 和 experiment completion handoff

Run directories are raw evidence。每次 terminal run 之后，从 `runs/<run-id>/` 里蒸馏出可复用知识：

1. 更新 `RUNS.md` 写 command、seed/device/resource、status、log path、metrics path、summary path、failure notes。
2. 更新 `SCRIPT_REGISTRY.md` 写用过、改过、validated、deprecated、用户要求的 script/native command。
3. 证据影响科学结论时更新 `RESULTS.md` 和 `REPRODUCIBILITY.md`。
4. 更新 `CLAIMS.md` 并保留 negative/inconclusive 结果。
5. 把用户要求的输出、可复用命令、决策、next-step TODO 持久化到 stable artifacts 或 project-root docs。As part of experiment completion handoff, persist valuable or user-requested content 到稳定 artifact，不要只留在 chat。
6. portfolio `RESEARCH.md` 和 root `INDEX.md` 在整体 synthesis、workstream 状态、next priority 变化时同步更新。
7. 如果用了 task worktree，先生成 report-before-merge closeout plan；merge、push、删除 worktree、删除 branch 都要用户确认后再执行。

`EXPERIMENT.md` 里的 `baseline fairness checklist` 和 `negative/inconclusive result policy` 是强制的：每次 experiment design 必须区分 environment failure、implementation bug、underpowered result、hypothesis failure。

## Git tracking policy

This repository tracks the skill framework itself：

- commit `README.md`、`README.zh-CN.md`、`skills/ai-research-workflow-omc/**` 以及验证本 framework 的 maintenance-only 脚本。
- keep `.omc/` ignored（本地 runtime state、logs、临时 worktree 数据）。
- 在下游 research project 里，只 version 控制稳定的 research document 和 experiment contract，原始 run 输出不直接进 git。

## Update this skill

```bash
cd ai-research-workflow
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh             # git pull + sync
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --no-pull   # local-only sync
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --symlink    # dev: symlink install
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --dry-run    # preview only
```

Updater 会做 `git pull --ff-only`、validate source、staging `rsync -a --delete`、再 validate install 副本。

## Framework guardrail helpers

```bash
# 确定性 workflow 路由
python3 skills/ai-research-workflow-omc/scripts/resolve_workflow.py <project-root> --prompt "<user prompt>"

# portfolio / workstream scaffolding
python3 skills/ai-research-workflow-omc/scripts/init_research_workspace.py <project-root> --preset guided
python3 skills/ai-research-workflow-omc/scripts/init_workstream.py <project-root> <slug> --title "..." --question "..." --deep-interview <path> --ralplan-prd <path> --ralplan-test-spec <path> --autoresearch-result <path>
python3 skills/ai-research-workflow-omc/scripts/update_workstream_state.py <project-root> <slug> --phase experiment-design --next-action "..."

# 只读 review
python3 skills/ai-research-workflow-omc/scripts/summarize_research_state.py <project-root>
python3 skills/ai-research-workflow-omc/scripts/score_research_artifacts.py <project-root>            # 启发式 artifact quality score

# Q&A capture
python3 skills/ai-research-workflow-omc/scripts/capture_question.py <project-root> --question "..." --answer-summary "..."
python3 skills/ai-research-workflow-omc/scripts/question_capture_hook.py --stage submit --project-root <project-root> --prompt "..."
python3 skills/ai-research-workflow-omc/scripts/question_capture_hook.py --stage answer --project-root <project-root> --answer-summary "..."

# closeout、negative result、report outline
python3 skills/ai-research-workflow-omc/scripts/prepare_workstream_closeout.py <project-root> <slug> --write
python3 skills/ai-research-workflow-omc/scripts/preserve_negative_result.py <project-root> <slug> --finding "..." --evidence <path> --interpretation "..." --claim-update "..."
python3 skills/ai-research-workflow-omc/scripts/generate_report_outline.py <project-root> <slug> --kind paper-outline --write

# schema、evidence graph、migration
python3 skills/ai-research-workflow-omc/scripts/validate_research_schema.py <project-root>
python3 skills/ai-research-workflow-omc/scripts/build_evidence_graph.py <project-root> <slug> --json
python3 skills/ai-research-workflow-omc/scripts/migrate_research_workspace.py <project-root> --write

# update / maintenance
python3 skills/ai-research-workflow-omc/scripts/check_skill_update.py
python3 skills/ai-research-workflow-omc/scripts/run_e2e_scenarios.py

# worktree closeout
python3 skills/ai-research-workflow-omc/scripts/prepare_worktree_closeout.py <task-worktree> --base main

# phase validators
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase idea-scouting
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase paper-scouting
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase paper-reproduction --workstream <slug>
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase new-workstream --workstream <slug>
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase completion-handoff --workstream <slug> --check-paths

# maintenance：contract + fixtures
python3 skills/ai-research-workflow-omc/scripts/check_regression_fixtures.py
python3 skills/ai-research-workflow-omc/scripts/validate_framework_contract.py skills/ai-research-workflow-omc
```

## 注意事项

- 新 workstream 需要 gate evidence，不应该自动创建。
- merge、push、删除 worktree、删除 branch 前，需要 report-before-merge 确认。
- `runs/` 存原始证据，稳定结论要蒸馏回 markdown artifacts。
- bundled scripts 只做 framework guardrail，不是用户实验 runner。
- framework 的 portfolio control plane 在 `.omc/ai-research/`，`INDEX.md`（root `INDEX.md`）是 workstream registry。
- `assets/templates/`、`assets/schemas/`、`assets/VERSION`、`assets/hooks/question-capture.example.json` 是 skill 自带的初始 scaffold。

## 验证

```bash
python3 skills/ai-research-workflow-omc/scripts/validate_framework_contract.py skills/ai-research-workflow-omc
python3 skills/ai-research-workflow-omc/scripts/run_e2e_scenarios.py
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root>
```

## 另见

- [Codex/OMX sibling skill](../ai-research-workflow/) — 同一份 artifact contract，不同的 workflow 路由面。
- [oh-my-claudecode (OMC)](https://github.com/MciG-ggg/oh-my-claudecode) — 提供 `/oh-my-claudecode:deep-interview`、`/oh-my-claudecode:ralplan`、`/oh-my-claudecode:autoresearch`、`/oh-my-claudecode:ralph`、`/oh-my-claudecode:autopilot`、`/oh-my-claudecode:ultrawork`、`/oh-my-claudecode:team` 的 OMC framework。
- `references/workflow-orchestration.md` — 完整 OMC workflow 序列和路由 helper。
- `references/artifact-contracts.md` — control-plane artifact 形状。
- `references/research-quality-gates.md` — phase gate 和 confirmation boundary。
