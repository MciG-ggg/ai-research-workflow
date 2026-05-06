# AI Research Workflow Skill

A Codex/OMX skill that turns vague AI/ML research ideas into artifact-gated research workflows: intake, literature review, falsifiable hypothesis spec, experiment design, implementation, experiment runs, result analysis, reproducibility review, and paper drafting.

## Why

AI research agents are most useful when they do not jump from an idea directly to code. This skill forces separation between:

- `RESEARCH.md`: scientific intent, hypotheses, contribution, success/falsification criteria, non-goals, and claim boundaries.
- `EXPERIMENT.md`: datasets, baselines, metrics, ablations, seeds, commands, logging, statistical tests, and failure policy.

The result is a workflow where evidence controls claims.

## Dependency: oh-my-codex

This skill is designed for Codex sessions running with [oh-my-codex (OMX)](https://github.com/Yeachan-Heo/oh-my-codex), the multi-agent orchestration layer that provides workflow skills such as `$deep-interview --autoresearch`, `$autoresearch`, `$ralplan`, `$ralph`, and `$autopilot`.

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

## What it creates

For a new project, the skill can initialize:

```text
.omx/ai-research/<slug>/
  RESEARCH.md
  LITERATURE.md
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  REPRODUCIBILITY.md
  PAPER_DRAFT.md
```

## Experiment run standards

By default, this skill standardizes how experiments are executed and recorded. Users should not need to request this separately:

- create a dedicated run directory under `.omx/ai-research/<slug>/runs/<run-id>/`
- capture complete stdout/stderr in `logs/combined.log`
- write structured metrics to `data/metrics.jsonl` and `data/summary.json`
- generate figures under `figures/` with a `figures_manifest.json`
- print the absolute log path in the final report

The agent should use the helper script to scaffold a run unless the project already has an equivalent runner:

```bash
python3 skills/ai-research-workflow/scripts/prepare_experiment_run.py <slug> --command "python train.py ..."
```

## Local validation

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/init_research_artifacts.py demo --root /tmp/ai-research-workflow-test --title "Demo Research"
```

## License

MIT
