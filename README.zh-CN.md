# AI Research Workflow Skill

[English README](README.md)

这是一个面向 Codex/OMX 的 AI 科研工作流 skill，用来把模糊的 AI/ML 研究想法推进成有 artifact gate 的研究流程：研究 intake、文献综述、可证伪假设、实验设计、方法实现、实验运行、结果分析、可复现性审查和论文/报告草稿。

## 为什么需要它

AI 科研 agent 最大的问题不是不会写代码，而是太容易从一个模糊想法直接跳到实现。这个 skill 强制把科学意图和执行细节拆开：

- `RESEARCH.md`：研究问题、假设、贡献类型、成功/证伪标准、非目标和 claim 边界。
- `EXPERIMENT.md`：数据集、baseline、指标、消融、随机种子、命令、日志、统计检验和失败策略。

最终目标是让证据控制结论，而不是让代码产出倒推科研 claim。

## 依赖：oh-my-codex

这个 skill 设计给运行 [oh-my-codex (OMX)](https://github.com/Yeachan-Heo/oh-my-codex) 的 Codex 会话使用。OMX 提供 `$deep-interview --autoresearch`、`$ralplan`、`$autoresearch`、`$ralph`、`$team`、`$autopilot` 等工作流能力。

- GitHub: <https://github.com/Yeachan-Heo/oh-my-codex>
- 文档/主页: <https://yeachan-heo.github.io/oh-my-codex>

安装并初始化 OMX：

```bash
npm install -g oh-my-codex
omx setup
omx doctor
```

## 安装

克隆仓库并复制 skill 到 Codex skills 目录：

```bash
git clone https://github.com/MciG-ggg/ai-research-workflow.git
mkdir -p ~/.codex/skills
cp -R ai-research-workflow/skills/ai-research-workflow ~/.codex/skills/
```

显式调用：

```text
$ai-research-workflow turn this paper idea into a research plan and experiment workflow
```

## 工作流

这个 skill 是一个完整工作流，不只是日志模板。

默认序列：

```text
$deep-interview --autoresearch
  -> 检查总览 RESEARCH.md / INDEX.md
  -> 文献和研究 artifacts
  -> $ralplan 规划实现和验证形状
  -> 目标项目仓库中的 task worktree
  -> $autoresearch validator-gated loop
  -> 方法实现 / baseline 复现 / 实验
  -> 将运行结果蒸馏到 RUNS.md / RESULTS.md / 项目根目录产物
  -> 可复现性审查
  -> 论文或报告草稿
```

`.omx/ai-research/RESEARCH.md` 和 `.omx/ai-research/INDEX.md` 是整个研究工作的 portfolio control plane。每个 `.omx/ai-research/<slug>/` 是一个具体方向的 workstream。真实的方法实现、baseline 复现、配置、测试和项目原生实验代码，应该放在目标项目仓库根目录或该仓库已有约定的位置，而不是放到 `.omx/ai-research/` 下面。

## 更新这个 skill

如果你从本仓库安装，更新 clone 并同步到 Codex：

```bash
cd ai-research-workflow
git pull --ff-only
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
rsync -a --delete skills/ai-research-workflow/ ~/.codex/skills/ai-research-workflow/
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/ai-research-workflow
```

如果你维护的是这个 skill 仓库本身，发布或同步前先跑框架校验。下面的 task worktree 策略描述的是 skill 在目标 AI 科研项目仓库中的行为，不是编辑这个 skill 仓库的安装要求。

## 框架目录

每个研究项目会创建或复用一个项目本地研究总览和若干 workstream 工作区：

```text
.omx/ai-research/
  RESEARCH.md
  INDEX.md
.omx/ai-research/<slug>/
  RESEARCH.md
  LITERATURE.md
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  REPRODUCIBILITY.md
  PAPER_DRAFT.md
  SCRIPT_REGISTRY.md
  scripts/
  runs/
```

根目录 `RESEARCH.md` 记录整体研究目标、中心问题、north-star hypotheses、claim 边界、当前综合判断、活跃 workstreams 和下一步优先级。根目录 `INDEX.md` 记录每个 slug 的子问题、状态、artifact 链接、最新证据和下一步。创建新 slug 前，agent 应先检查这两个文件和已有 workstream；只有当新任务确实有独立研究问题或验证边界时才创建新 slug。

这个 skill 不内置通用实验 runner。不同研究项目会使用不同训练栈、配置系统、集群、notebook、绘图工具和日志约定。因此它只规定项目本地脚本应该放在哪里、如何命名、如何登记。

运行目录是原始证据。每次运行终止后，把稳定结论蒸馏回 `RUNS.md`、`RESULTS.md`、`REPRODUCIBILITY.md`，并在结果可复用时同步到项目根目录的 docs、报告、代码、配置或测试。

当用户说“当前实验做完了”“这个实验结束了”或要求收尾时，agent 应进入 experiment completion handoff：先整理 `runs/` 和 `scripts/`，更新 `RUNS.md` 和 `SCRIPT_REGISTRY.md`，再把有价值或用户明确要求保留的内容写入 `RESULTS.md`、`REPRODUCIBILITY.md` 或项目根目录文档，最后报告写入的路径。

## bundled scripts 只用于维护

`skills/ai-research-workflow/scripts/` 下的脚本只用于维护和验证这个 framework。它们不能用作用户研究项目的实验 runner、指标收集器、绘图脚本或研究文档发布器。

用户研究脚本应放在目标项目工作区：

```text
.omx/ai-research/<slug>/scripts/
.omx/ai-research/<slug>/SCRIPT_REGISTRY.md
```

## Task worktrees

当这个 skill 被用于目标 AI 科研项目仓库中的实质性工作时，编辑前先开隔离 git worktree：

```text
.omx/worktrees/<scope>/
.omx/worktrees/REGISTRY.md
```

在 `REGISTRY.md` 记录每个 worktree 的路径、分支、用途、负责的文件/区域和状态。如果 `.omx/worktrees/` 不可写，使用 `~/omx-worktrees/<repo-name>/<scope>` 这类可写 fallback，并记录绝对路径。

开 worktree 之前，先检查本地 git 状态。如果主 worktree 有修改，先按语义拆分成 Lore-format commit，再基于最新 commit 创建 task worktree。验证通过后，把 task 分支或合并后的 main 分支推送到远端。

冲突策略：

- 按不重叠的文件/区域拆分任务
- 每个逻辑任务或 lane 使用一个 worktree
- 除非某个 worktree 是明确的 integrator，否则避免并发编辑同一文件
- 最终验证前，把每个 worktree rebase 到 `main`
- 串行合并 worktree，每合并一次就验证一次
- 重复冲突模式较多时启用 `git rerere`
- merge-back 前，把 worker 自动 checkpoint commit 改写或 squash 成 Lore-format commit

维护辅助命令：

```bash
python3 skills/ai-research-workflow/scripts/check_worktree_registry.py .
```

详情见 `skills/ai-research-workflow/references/worktree-development.md`。

该规则适用于目标项目的代码、文档、实验设置、重构和结果包装。只读分析或非常小的安全修改可以跳过。

## Git 跟踪策略

本仓库跟踪 skill framework 本身：

- 跟踪 `README.md`、`README.zh-CN.md`、`skills/ai-research-workflow/**` 和维护脚本
- 保持 `.omx/` ignored，因为它记录本地 runtime 状态、日志和临时 worktree 数据
- 在下游研究项目中，只选择性版本化稳定研究文档和实验 contract

下游项目中适合进入 git 历史的文件：

- 根目录 `RESEARCH.md`
- 根目录 `INDEX.md`
- `RESEARCH.md`
- `LITERATURE.md`
- `EXPERIMENT.md`
- `RUNS.md`
- `RESULTS.md`
- `REPRODUCIBILITY.md`
- `PAPER_DRAFT.md`
- `SCRIPT_REGISTRY.md`

通常保持本地：

- `.omx/**/runs/`
- `.omx/**/logs/`
- `.omx/state/`
- `.omx/worktrees/`

## 实验运行标准

默认情况下，这个 skill 会规范实验如何执行、监控、记录和发布。用户不需要额外要求日志、指标、进度或图表。

- 长实验默认使用 detached tmux
- 独立 lane 可在有收益时通过 OMX `$team` 或 native subagents 并行
- 每次运行都有独立目录 `.omx/ai-research/<slug>/runs/<run-id>/`
- stdout/stderr 必须捕获到完整日志
- metrics 和 summary 写入结构化文件
- 数值/对比结果需要合适的 figures
- 最终报告包含 tmux/status/log/metrics/summary/figure 路径
- 稳定结果和结论同步到项目根目录 `docs/ai-research/<slug>/`，安全时配置 MkDocs
- 多 seed 实验可以每个 seed 一个 subagent/team lane，并给每个 lane 分配明确的空闲 GPU/device 或 scheduler slot
- 方法实现和 baseline 复现发生在目标项目根目录，不放在 `.omx/ai-research/`

项目本地脚本应登记在：

```text
.omx/ai-research/<slug>/SCRIPT_REGISTRY.md
.omx/ai-research/<slug>/scripts/
```

常见脚本名：

```text
run_<experiment>.sh
monitor_<experiment>.sh
collect_metrics_<experiment>.<ext>
plot_<experiment>.<ext>
publish_docs_<experiment>.sh
```

## 本地验证

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/check_worktree_registry.py .
```

## License

MIT
