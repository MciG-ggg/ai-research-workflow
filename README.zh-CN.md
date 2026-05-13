# AI Research Workflow Skill

[English README](README.md)

这是一个面向 Codex/OMX 的 AI/ML 科研工作流 skill，用来把模糊 idea、论文、baseline 和实验计划推进成有证据约束的研究 artifact，而不是从想法直接跳到代码。

核心原则很简单：

- `RESEARCH.md` 记录研究问题、假设、范围和 claim 边界。
- `EXPERIMENT.md` 记录数据集、baseline、指标、实验运行和失败策略。
- `RUNS.md`、`RESULTS.md`、`CLAIMS.md`、`REPRODUCIBILITY.md` 把证据和结论分开。

这个 skill 是工作流和 artifact 框架，不内置通用实验 runner。项目里的真实代码、配置、训练脚本、评估脚本应该放在目标研究仓库里。

## 依赖

这个 skill 设计给使用 [oh-my-codex (OMX)](https://github.com/Yeachan-Heo/oh-my-codex) 的 Codex 会话。

```bash
npm install -g oh-my-codex
omx setup
omx doctor
```

## 安装

```bash
git clone https://github.com/MciG-ggg/ai-research-workflow.git
mkdir -p ~/.codex/skills
cp -R ai-research-workflow/skills/ai-research-workflow ~/.codex/skills/
```

仓库更新后同步 skill：

```bash
cd ai-research-workflow
./skills/ai-research-workflow/scripts/update_installed_skill.sh
```

本地开发时不拉取远端：

```bash
./skills/ai-research-workflow/scripts/update_installed_skill.sh --no-pull
```

## 典型使用流程

```text
1. 从一个 idea、论文、baseline 或实验问题开始。
2. 可选地先做 idea / paper 调研：
   - IDEA_SCOUTING.md 记录候选研究想法
   - PAPERS.md 维护 SOTA/baseline 论文列表
3. 新开 workstream 前先走：
   $deep-interview --autoresearch -> $ralplan -> $autoresearch
4. 为一个具体方向创建或复用 .omx/ai-research/<slug>/。
5. 选择 workstream 类型：
   - paper-reproduction：复现一篇论文/baseline/claim，使用 REPRODUCTION.md
   - experiment-campaign：围绕假设、消融、benchmark 或方法评估跑一组实验
6. 项目代码写在目标仓库里，不放进 .omx/ai-research/。
7. 记录 runs、scripts、metrics、summary 和失败情况。
8. 把稳定证据蒸馏到 RESULTS.md、CLAIMS.md、REPRODUCIBILITY.md。
9. workstream 完成后，先生成 closeout/report-before-merge plan，再合并、推送或清理 worktree。
```

## 常用命令

需要确定路由时，显式调用 skill：

```text
$ai-research-workflow scout            # 候选 idea 调研
$ai-research-workflow papers           # 查找/维护 SOTA 和 baseline 论文列表
$ai-research-workflow reproduce-paper  # 准备单篇论文复现 workstream
$ai-research-workflow experiment       # 准备 experiment-campaign workstream
$ai-research-workflow new-workstream   # 新建 gated 小方向
$ai-research-workflow handoff          # 收尾已完成的 runs/scripts/results
$ai-research-workflow summarize        # 汇总 portfolio/workstream 状态
$ai-research-workflow score            # 启发式 artifact 质量检查
$ai-research-workflow closeout         # 生成 report-before-merge plan
$ai-research-workflow negative-result  # 保存失败/无显著/不确定结果
$ai-research-workflow draft            # 生成论文或报告 outline
```

本地 CLI helper：

```bash
python3 skills/ai-research-workflow/scripts/ai_research.py help
python3 skills/ai-research-workflow/scripts/ai_research.py resolve <project-root> --prompt "这个实验做完了，整理落盘"
python3 skills/ai-research-workflow/scripts/ai_research.py summarize <project-root>
python3 skills/ai-research-workflow/scripts/ai_research.py score <project-root>
python3 skills/ai-research-workflow/scripts/ai_research.py schema <project-root>
```

## Artifact 目录

```text
.omx/ai-research/
  IDEA_SCOUTING.md   # 可选候选 idea 调研
  PAPERS.md          # 可选 SOTA/baseline 论文池
  RESEARCH.md        # 整体研究总览
  INDEX.md           # workstream 索引

.omx/ai-research/<slug>/
  STATE.json
  RESEARCH.md
  LITERATURE.md
  REPRODUCTION.md    # paper-reproduction workstream 必需
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  CLAIMS.md
  REPRODUCIBILITY.md
  SCRIPT_REGISTRY.md
  CLOSEOUT.md
  scripts/
  runs/
```

## 注意事项

- 新 workstream 需要 gate evidence，不应该自动创建。
- merge、push、删除 worktree、删除 branch 前，需要 report-before-merge 确认。
- `runs/` 存原始证据，稳定结论要蒸馏回 markdown artifacts。
- bundled scripts 只做 framework guardrail，不是用户实验 runner。

## 验证

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/run_e2e_scenarios.py
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
```
