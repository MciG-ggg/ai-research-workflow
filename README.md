# AI Research Workflow Skill

[中文文档](README.zh-CN.md)

A Codex/OMX framework skill that turns vague AI/ML research ideas into artifact-gated research workflows: optional idea scouting/generation, intake, literature review, falsifiable hypothesis spec, experiment design, implementation, experiment runs, result analysis, reproducibility review, and paper drafting.

## Why

AI research agents are most useful when they do not jump from an idea directly to code. This skill forces separation between:

- `RESEARCH.md`: scientific intent, hypotheses, contribution, success/falsification criteria, non-goals, and claim boundaries.
- `EXPERIMENT.md`: datasets, baselines, metrics, ablations, seeds, commands, logging, statistical tests, and failure policy.

The result is a workflow where evidence controls claims.

## Dependency: oh-my-codex

This skill is designed for Codex sessions running with [oh-my-codex (OMX)](https://github.com/Yeachan-Heo/oh-my-codex), the multi-agent orchestration layer that provides workflow skills such as `$deep-interview --autoresearch`, `$ralplan`, `$autoresearch`, `$ralph`, `$team`, and `$autopilot`.

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

## Workflow

This skill is a workflow, not just a logging template.

Default sequence:

```text
optional IDEA_SCOUTING.md when no clear research question exists
  -> $deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
  -> literature and research artifacts
  -> $ralplan for implementation and validation shape
  -> task worktree in the target repo
  -> $autoresearch for a validator-gated loop
  -> implementation / baseline reproduction / experiments
  -> run distillation into RUNS.md / RESULTS.md / project-root outputs
  -> reproducibility review
  -> paper/report drafting
```

`.omx/ai-research/RESEARCH.md` and `.omx/ai-research/INDEX.md` are the portfolio control plane for the whole research program. Each `.omx/ai-research/<slug>/` directory is a workstream for one concrete direction. Actual method implementation, baseline reproduction, configs, tests, and project-native experiment code belong in the target repository root or its existing conventions, not under `.omx/ai-research/`.

## Update this skill

If you installed from this repository, use the safe updater:

```bash
cd ai-research-workflow
./skills/ai-research-workflow/scripts/update_installed_skill.sh
```

The updater runs `git pull --ff-only`, source validation, staged `rsync -a --delete`, and installed-copy validation. For local development, skip pulling with `--no-pull`.

Developer symlink mode is available when you want repo edits to be picked up immediately:

```bash
./skills/ai-research-workflow/scripts/update_installed_skill.sh --symlink --no-pull
```

If you are maintaining this repository, validate the skill framework before syncing or publishing changes. The task-worktree policy below describes how the skill should operate inside a target AI research project, not an installation requirement for editing this skill repository.

## Framework layout

For each research project, the skill asks the agent to create or maintain a project-local research portfolio plus workstream workspaces:

```text
.omx/ai-research/
  IDEA_SCOUTING.md # optional before a clear research question exists
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

The optional root `IDEA_SCOUTING.md` captures idea generation, lightweight evidence, novelty risk, feasibility budget, and user-goal fit before a formal research question exists. The root `RESEARCH.md` captures the overall research program: central question, north-star hypotheses, claim boundaries, current synthesis, active workstreams, and next priorities. The root `INDEX.md` maps each slug to its subquestion, status, artifact links, latest evidence, and next action. Before creating a new slug, the agent should inspect these files and existing workstreams, then reuse an existing workstream unless the new task has a distinct research question or validation boundary.

Idea scouting is optional. Use it when a user asks to generate candidate ideas, evaluate whether an existing idea is worth doing, or converge a vague area into candidate research questions. A candidate may be recommended for intake only when it has a falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty risk, feasibility budget, and user-goal fit. The agent must ask before creating a workstream.

New workstream creation is forced through `$deep-interview --autoresearch -> $ralplan -> $autoresearch`. The agent should not create a new slug, implement code, or launch experiments until `INDEX.md` records the deep-interview handoff, ralplan PRD/test spec, and autoresearch state/completion artifact paths.

Artifact templates live under `skills/ai-research-workflow/assets/templates/`. They are starting points for portfolio, workstream, run, result, reproducibility, paper, and optional feedback files. Replace `TODO` placeholders before treating any artifact as complete.

## Optional feedback memory and Q&A capture

Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default. Enable them only when a project wants durable learning notes, Q&A capture, or growth review in addition to normal research artifacts:

```text
$ai-research-workflow --feedback-memory ...
$ai-research-workflow --qa-capture ...
$ai-research-workflow --growth-review ...
$ai-research-workflow --no-feedback ...
```

Project defaults can be stored in `.omx/ai-research/CONFIG.md`:

```yaml
workflow_preset: conservative | guided | autonomous
idea_scouting: auto | off | on
completion_handoff: auto | off
worktree_closeout: off | report-before-merge
feedback_memory: off | lite | full
qa_capture: off | research | all
growth_review: off | milestone | always
```

Use `workflow_preset: guided` to reduce manual workflow naming: broad idea prompts enter scouting, "done/wrap up" prompts enter completion handoff, and worktree closeout produces a report-before-merge plan. Use `conservative` for explicit-only behavior or `autonomous` for more proactive artifact maintenance; per-feature overrides win over the preset.

When enabled, the skill may add root feedback files such as `QUESTIONS.md`, `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, and `SKILL_GROWTH.md`, plus workstream files such as `QUESTIONS.md`, `DESIGN.md`, `NOTES.md`, and `REVIEW.md`. `QUESTIONS.md` records user questions and answer summaries when `--qa-capture` or `qa_capture` is enabled. These files store distilled issues, knowledge, architecture/design decisions, verification gaps, Q&A, and capability reflections; raw logs and run outputs stay under `runs/`.

The skill intentionally does **not** ship universal experiment runner scripts. Different research projects use different training stacks, config systems, clusters, notebooks, plotting tools, and logging conventions. Instead, it defines where project-local scripts should live and how they should be named and documented.

Run directories are raw evidence. After each terminal run, distill stable conclusions back into `RUNS.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, and then into project-root docs, reports, code, configs, or tests when the result is reusable.

When the user says the current experiment is done, the agent should treat that as an experiment completion handoff: inspect `runs/` and `scripts/`, update `RUNS.md` and `SCRIPT_REGISTRY.md`, persist valuable or user-requested content into `RESULTS.md`, `REPRODUCIBILITY.md`, or project-root docs, then report the paths written. If the workstream used a task worktree, the agent must also produce a report-before-merge closeout plan covering validation, semantic commits, merge/push target, worktree removal, branch deletion, and `.omx/worktrees/REGISTRY.md`; it waits for user confirmation before merging or deleting anything.

## Maintenance-only bundled scripts

The skill may include bundled scripts under `skills/ai-research-workflow/scripts/`, but those scripts are maintenance-only tools for validating and evolving this framework. They are not for running user experiments, collecting user metrics, plotting user results, or publishing user research docs.

User research scripts belong in the target project workspace:

```text
.omx/ai-research/<slug>/scripts/
.omx/ai-research/<slug>/SCRIPT_REGISTRY.md
```

## Task worktrees

When this skill is used to do substantive AI research work in a target project repository, open an isolated git worktree before editing:

```text
.omx/worktrees/<scope>/
.omx/worktrees/REGISTRY.md
```

Record each worktree's path, branch, purpose, owned files/areas, and status in `REGISTRY.md`. If `.omx/worktrees/` is not writable, use a writable fallback such as `~/omx-worktrees/<repo-name>/<scope>` and record the absolute path.

Before opening a worktree, inspect local git status. If the main worktree has modifications, split them by intent into semantic Lore-format commits first, then create the task worktree from the latest commit. After validation and any required report-before-merge confirmation, push the task branch or merged main branch to the remote.

Conflict policy:

- split work by non-overlapping file/area ownership
- use one worktree per logical task or lane
- avoid concurrent edits to shared files unless one worktree is the integrator
- rebase each worktree on `main` before final validation
- merge worktrees back serially, validating after each merge
- enable `git rerere` when repeated conflict patterns are expected
- rewrite or squash worker auto-checkpoint commits into Lore-format commits before merge-back

Maintenance helpers:

```bash
python3 skills/ai-research-workflow/scripts/check_worktree_registry.py .
```

See `skills/ai-research-workflow/references/worktree-development.md`.

This applies to target-project code, docs, experiment setup, refactors, and result packaging. Skip only for read-only analysis or tiny safe edits.

## Git tracking policy

This repository tracks the skill framework itself:

- track `README.md`, `README.zh-CN.md`, `skills/ai-research-workflow/**`, and the maintenance scripts that validate this framework
- keep `.omx/` ignored because it records local runtime state, logs, and temporary worktrees
- in downstream research projects, selectively track only stable research documents and experiment contracts

Good candidates for downstream git history:

- root `RESEARCH.md`
- root `INDEX.md`
- `RESEARCH.md`
- `LITERATURE.md`
- `EXPERIMENT.md`
- `RUNS.md`
- `RESULTS.md`
- `REPRODUCIBILITY.md`
- `PAPER_DRAFT.md`
- `SCRIPT_REGISTRY.md`

Usually keep local:

- `.omx/**/runs/`
- `.omx/**/logs/`
- `.omx/state/`
- `.omx/worktrees/`

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
- multi-seed experiments may run one seed per subagent/team lane, with each lane assigned an explicit idle GPU/device or scheduler slot
- method implementation and baseline reproduction happen in the target repository root, not inside `.omx/ai-research/`

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
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/check_worktree_registry.py .
python3 skills/ai-research-workflow/scripts/validate_research_workspace.py <project-root> --require-workstream
```

## License

MIT
