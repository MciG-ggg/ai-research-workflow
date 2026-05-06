# AI Research Workflow Skill

A Codex/OMX framework skill that turns vague AI/ML research ideas into artifact-gated research workflows: intake, literature review, falsifiable hypothesis spec, experiment design, implementation, experiment runs, result analysis, reproducibility review, and paper drafting.

## Why

AI research agents are most useful when they do not jump from an idea directly to code. This skill forces separation between:

- `RESEARCH.md`: scientific intent, hypotheses, contribution, success/falsification criteria, non-goals, and claim boundaries.
- `EXPERIMENT.md`: datasets, baselines, metrics, ablations, seeds, commands, logging, statistical tests, and failure policy.

The result is a workflow where evidence controls claims.

## Dependency: oh-my-codex

This skill is designed for Codex sessions running with [oh-my-codex (OMX)](https://github.com/Yeachan-Heo/oh-my-codex), the multi-agent orchestration layer that provides workflow skills such as `$deep-interview --autoresearch`, `$autoresearch`, `$ralplan`, `$ralph`, `$team`, and `$autopilot`.

- GitHub: <https://github.com/Yeachan-Heo/oh-my-codex>
- Documentation/homepage: <https://yeachan-heo.github.io/oh-my-codex>

Install and initialize OMX before using the OMX handoff paths in this skill:

```bash
npm install -g oh-my-codex
omx setup
omx doctor
```

## Install

Clone the repo and copy the skill folder into your Codex skills directory:

```bash
git clone https://github.com/MciG-ggg/ai-research-workflow.git
mkdir -p ~/.codex/skills
cp -R ai-research-workflow/skills/ai-research-workflow ~/.codex/skills/
```

Then invoke it explicitly:

```text
$ai-research-workflow turn this paper idea into a research plan and experiment workflow
```

## Framework layout

For each research project, the skill asks the agent to create or maintain a project-local research workspace:

```text
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

The skill intentionally does **not** ship universal experiment runner scripts. Different research projects use different training stacks, config systems, clusters, notebooks, plotting tools, and logging conventions. Instead, it defines where project-local scripts should live and how they should be named and documented.

## Experiment run standards

By default, this skill standardizes how experiments are executed, monitored, recorded, and published. Users should not need to request this separately:

- long runs should launch in detached tmux when available
- independent lanes may run via OMX `$team` or native subagents when useful
- every run gets a dedicated directory under `.omx/ai-research/<slug>/runs/<run-id>/`
- stdout/stderr are captured in a complete log file
- metrics and summaries are written to structured files
- figures are generated for numeric/comparative results when appropriate
- final reports include tmux/status/log/metrics/summary/figure paths
- settled results and conclusions are mirrored into project-root `docs/ai-research/<slug>/` with MkDocs config when safe

Project-local scripts should be recorded in:

```text
.omx/ai-research/<slug>/SCRIPT_REGISTRY.md
.omx/ai-research/<slug>/scripts/
```

Typical script names:

```text
run_<experiment>.sh
monitor_<experiment>.sh
collect_metrics_<experiment>.<ext>
plot_<experiment>.<ext>
publish_docs_<experiment>.sh
```

## Local validation

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
```

## License

MIT
