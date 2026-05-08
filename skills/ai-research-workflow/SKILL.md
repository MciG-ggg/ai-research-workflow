---
name: ai-research-workflow
description: "AI research workflow orchestration for turning vague AI/ML research ideas into validated project work and research artifacts: deep interview, literature review, falsifiable hypothesis spec, ralplan planning, method implementation, baseline reproduction, experiment design, experiment runs, result distillation, reproducibility review, and paper drafting. Use when Codex is asked to develop, implement, evaluate, reproduce, or write up an AI/ML research idea, benchmark, method, baseline, ablation, paper plan, experiment pipeline, or research report with clear hypotheses, baselines, metrics, validation, and claim boundaries."
---

# AI Research Workflow

## Purpose

Turn an AI/ML research idea into artifact-gated research work. Do not jump from a vague idea directly to experiment code. First separate scientific intent from execution details, then keep every claim tied to evidence.

This is a framework skill, not a project-specific experiment runner. It defines artifacts, quality gates, orchestration expectations, and script-recording conventions. Generate or adapt project-local scripts inside the research workspace only when the current project needs them.

Bundled scripts under this skill's own `scripts/` directory are maintenance-only tools for validating or evolving the skill framework itself. Do not use them as user experiment runners, metrics collectors, plotting scripts, or research-doc publishers.

This skill is an OMX workflow. By default it orchestrates:

```text
$deep-interview --autoresearch
  -> literature and research artifacts
  -> $ralplan for implementation and validation shape
  -> task worktree execution in the target repo
  -> $autoresearch for validator-gated research loop
  -> implementation / baseline reproduction / experiments
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Skip completed phases only when existing artifacts pass the relevant gate.

## Artifact setup

Create or reuse a research workspace under `.omx/ai-research/<slug>/`.

Minimum framework layout:

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

Read `references/workflow-orchestration.md` before starting or resuming the full research workflow. Read `references/artifact-contracts.md` when authoring or auditing artifact contents. Read `references/project-local-script-registry.md` before creating or relying on project-local scripts. Read `references/experiment-runtime-standards.md` before designing, implementing, running, or auditing experiments. Read `references/research-quality-gates.md` before approving a handoff, result, or paper claim. Read `references/worktree-development.md` when making substantive target-repo changes. Run maintenance-only scripts only when updating or validating this skill, not while executing a user's research workflow.

## Research control plane vs project implementation

`.omx/ai-research/<slug>/` is the research control plane: specs, decisions, run indexes, evidence summaries, and reproducibility notes.

Actual research work belongs in the target project root using existing project conventions. Implement the user's method, reproduce baselines, add configs, tests, datasets adapters, training/evaluation entrypoints, and reports in project-root locations such as `src/`, `models/`, `baselines/`, `configs/`, `experiments/`, `scripts/`, `tests/`, `docs/`, or the repository's established equivalents. Do not put method code, baseline code, or production experiment code under `.omx/ai-research/`; only thin orchestration wrappers and metadata belong there.

## Task worktree rule

When this skill is used to make substantive AI research changes in a target project repository, inspect the local git status before opening any new worktree. If the main worktree has local modifications, preserve them first by splitting them into semantic commits with Lore-format commit messages; do not mix unrelated changes into one checkpoint. After the main worktree is clean, fetch/pull the primary branch, create the task worktree from the latest commit, and push the completed branch or merged main branch to the remote after validation. Prefer `<repo>/.omx/worktrees/<scope>/`; if that path is not writable, use a writable fallback and record the absolute path. Maintain `.omx/worktrees/REGISTRY.md` in the target repo with each worktree's path, branch, scope, owned files/areas, and status. Use one worktree per logical task or lane, merge worktrees back serially after validation, then clean them up. Keep write scopes narrow so parallel worktrees avoid editing the same files or lines.

Skip the worktree only for read-only analysis, quick lookups, or tiny safe edits. This task worktree rule is about executing research work inside the target project, not about installing or maintaining this skill repository.

## Git tracking rule

The skill repository tracks the framework itself:
- commit `README.md`, `skills/ai-research-workflow/**`, and the maintenance-only scripts that validate this framework
- keep `.omx/` ignored because it is local runtime state, logs, and temporary worktree data
- in downstream research projects, selectively version stable research documents and experiment contracts rather than raw run outputs

## Default experiment evidence contract

When this skill runs, designs, implements, or audits experiments, structured runtime evidence is mandatory by default. Do not wait for the user to ask for logs, metrics, progress, or visualizations.

For every actual experiment run, ensure the project has either existing native commands or project-local scripts recorded in `.omx/ai-research/<slug>/SCRIPT_REGISTRY.md`. Those commands/scripts must produce a distinct run directory with command record, complete log, structured metrics, summary, and figures when visualizations are appropriate.

Only skip this contract when no experiment is actually executed, or when the user explicitly opts out. If skipped, record the reason in `RUNS.md` or the final response.

## Default experiment orchestration contract

Run long experiments in detached tmux by default when tmux is available. The runner lane returns the tmux session name, run directory, complete log path, metrics path, summary path, and figures path to the leader immediately after launch. The leader polls durable status/summary/log files until completion before claiming results.

For multiple independent variants, seeds, datasets, or ablations, use OMX `$team` or native subagents when parallel execution materially reduces wall-clock time and resource contention is acceptable. Each parallel lane must own a distinct run directory and must not overwrite another lane's metrics, logs, figures, or summaries. Aggregate only after all required lanes finish or fail with preserved logs.

For multi-seed experiments, treat each seed as an independent execution lane when the experiment design allows it. The leader must inspect available accelerators first, assign each seed lane an explicit idle GPU/device or scheduler slot, and record the seed-to-device mapping in `RUNS.md` and the run manifest. Use native subagents or `$team` lanes to launch seeds in parallel only when enough idle cards are available; otherwise run seeds serially or queue them. Prevent resource races by setting project-appropriate device controls such as `CUDA_VISIBLE_DEVICES`, scheduler GPU requests, or the framework's native device flag per lane.

## Default docs publishing contract

When results, settled data, or research conclusions are finalized, publish them under the project root `docs/` directory by default and configure MkDocs when safe. Prefer project-local docs/publishing scripts recorded in `SCRIPT_REGISTRY.md`; otherwise create the minimal `docs/ai-research/<slug>/` pages and `mkdocs.yml` by following `artifact-contracts.md`. If an existing MkDocs config is present, preserve it and report any manual nav update needed.

## Workflow

### 0. OMX workflow entry

Start with `$deep-interview --autoresearch` unless the user already provides clear hypotheses, success criteria, non-goals, forbidden claims, and evaluator/validation criteria. Use `$ralplan` before implementation-heavy work. Use `$autoresearch` for the durable validator-gated loop over literature, implementation, experiments, and claims.

### 1. Research intake

Produce `RESEARCH.md` before implementation. Include:
- research question
- falsifiable hypothesis
- expected contribution type: method, system, dataset, benchmark, analysis, or negative result
- success criteria and falsification criteria
- non-goals
- claim boundaries: what must not be claimed without evidence
- decision boundaries: what Codex may decide without asking

Ask one high-leverage clarification question if any of hypothesis, success criteria, non-goals, or forbidden claims are missing. For high-rigor intake, hand off to `$deep-interview --autoresearch`.

### 2. Literature review

Produce `LITERATURE.md` with source-backed evidence. For current or niche research facts, search instead of relying on memory. Prefer primary sources: papers, official project docs, benchmarks, dataset cards, and release notes.

Record query strategy, inclusion/exclusion criteria, related-work matrix, baseline candidates, dataset/benchmark constraints, gaps/risks, and citation links for claims.

### 3. Research question spec

Tighten `RESEARCH.md` until each hypothesis is testable. Convert vague goals into measurable predictions, e.g. metric deltas, cost/latency bounds, robustness criteria, or qualitative rubric thresholds.

### 4. Experiment design

Produce `EXPERIMENT.md` before writing or changing experiment code. Include datasets, splits, baselines, fairness constraints, method variants, configs, metrics, statistical tests, ablations, seeds, runtime budget, logging/artifact paths, reproduction commands, failure policy, run directory contract, progress reporting, and visualization plan.

### 5. Project-root implementation and baseline reproduction

After `$ralplan` and before expensive runs, implement or adapt the actual research method, baseline reproduction, configs, tests, and project-native experiment entrypoints in the target repository root. Use the task worktree rule for these edits.

Baseline reproduction is first-class work: preserve exact commands/configs, record blockers, and do not claim improvement over a baseline that was not fairly reproduced or explicitly scoped out.

### 6. Project-local orchestration scripts

Before running experiments, inspect the project for existing runners, notebooks, Make targets, Hydra configs, shell scripts, or CI jobs. Reuse them when possible.

If wrappers are needed, create them under `.omx/ai-research/<slug>/scripts/` and document them in `SCRIPT_REGISTRY.md`. Keep wrappers thin and project-specific: tmux launch, log capture, metrics extraction, plotting, or docs publishing. Do not assume a bundled framework script will fit the project.

### 7. Run experiments

Produce `RUNS.md`. Record commands, environment, commit hash if available, data versions, seed values, tmux session/status paths when used, result paths, complete log file absolute paths, metrics file absolute paths, figure paths, exit status, and failures.

Default run behavior:
- Long runs: launch in detached tmux through a project-local script or existing native command.
- Short smoke runs: may run synchronously if they still capture complete logs and structured outputs.
- Parallel runs: use `$team` or native subagents only for independent lanes with distinct output directories.
- Multi-seed runs: assign one seed per lane when possible, choose idle GPUs/devices before launch, record `seed`, `device`, `subagent/team lane`, run directory, log path, metrics path, and exit status for every seed.

Never fabricate results. If experiments cannot run locally, state the blocker and leave exact runnable commands plus expected output locations.

### 8. Distill completed runs

After each run reaches a terminal state, distill reusable information out of `runs/<run-id>/`. Update `RUNS.md` with status, command, seed/device/resource, log, metrics, summary, and failure notes. Update `RESULTS.md` when the run changes evidence or interpretation. Update `REPRODUCIBILITY.md` with new blockers or rerun instructions. Promote stable conclusions or reusable implementation changes to project-root docs, reports, configs, tests, or code as appropriate. Do not copy raw logs, checkpoints, private data, or large temporary outputs into project-root docs.

### 9. Analyze results

Produce `RESULTS.md`. Separate evidence from interpretation. Include raw result locations, complete experiment log path, metrics and summary data paths, visualization paths/captions, summary tables, uncertainty/variance, ablation interpretation, negative findings, threats to validity, and hypothesis verdicts.

### 10. Reproducibility review

Produce `REPRODUCIBILITY.md` using the quality gates reference. Check whether a fresh agent could reproduce the result from artifacts alone. Missing seeds, data versions, commands, complete log paths, metrics files, visualization outputs for numeric/comparative results, or result paths are blockers.

### 11. Paper draft or report

Produce `PAPER_DRAFT.md` only after results and reproducibility review exist. Every scientific claim must point to a result, citation, or explicit assumption. Downgrade unsupported claims to hypotheses or future work. After settled conclusions exist, publish the current artifacts to `docs/ai-research/<slug>/` so they can be browsed with MkDocs.

## Completion rules

Stop only when one of these is true:
- The requested artifact set exists and passes the relevant quality gates.
- A project validator, test command, or `$autoresearch` completion artifact passes.
- A real blocker prevents progress; report the missing data, compute, credentials, or decision.

Final responses must list changed/created research artifacts, project-root files changed for method/baseline/config/test/docs work, validation evidence, project-local scripts created/updated, tmux session/status paths for launched experiments, complete log file absolute paths for every experiment run, metrics/summary/figure paths, distilled run updates outside `runs/`, docs/MkDocs paths when conclusions were published, unsupported claims removed or downgraded, and remaining risks.
