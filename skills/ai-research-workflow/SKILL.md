---
name: ai-research-workflow
description: "AI research workflow orchestration for turning vague AI/ML research ideas into validated project work and research artifacts: deep interview, literature review, falsifiable hypothesis spec, ralplan planning, method implementation, baseline reproduction, experiment design, experiment runs, result distillation, reproducibility review, optional research feedback memory, optional researcher growth review, and paper drafting. Use when Codex is asked to develop, implement, evaluate, reproduce, or write up an AI/ML research idea, benchmark, method, baseline, ablation, paper plan, experiment pipeline, or research report with clear hypotheses, baselines, metrics, validation, and claim boundaries."
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

Maintain two research control-plane layers under `.omx/ai-research/`:

- Portfolio layer: `.omx/ai-research/RESEARCH.md` and `.omx/ai-research/INDEX.md` capture the user's overall research program, current synthesis, active workstreams, and how small directions relate to the larger goal.
- Workstream layer: `.omx/ai-research/<slug>/` captures a specific subquestion, method lane, baseline, ablation, experiment family, or paper/report slice.

Before creating a new `<slug>`, inspect the portfolio `RESEARCH.md`, `INDEX.md`, and existing workstream directories. Reuse or update an existing workstream when the task is a continuation of the same subquestion. Create a new workstream only when the task has a distinct research question, validation target, or artifact boundary, and record that relationship in the portfolio index.

New workstream creation has a mandatory workflow gate. If the task requires a new `<slug>`, do not create the workstream directory, implement code, or run experiments until this sequence has completed and its artifact paths are recorded in `INDEX.md`:

```text
$deep-interview --autoresearch
  -> $ralplan
  -> $autoresearch
```

Required gate evidence:
- `$deep-interview --autoresearch`: a validator-ready mission/intake artifact, preferably under `.omx/specs/autoresearch-<slug>/`, and a workstream `RESEARCH.md` draft linked to the portfolio
- `$ralplan`: consensus planning output plus `.omx/plans/prd-<slug>.md` and `.omx/plans/test-spec-<slug>.md`
- `$autoresearch`: persisted autoresearch state with a `completion_artifact_path`, plus `.omx/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`

If any gate evidence is missing, stop at the gate, create or complete the missing workflow artifact, and report the blocker. Do not bypass this gate because the new direction seems obvious.

Minimum portfolio layout:

```text
.omx/ai-research/
  RESEARCH.md
  INDEX.md
```

Create or reuse a workstream workspace under `.omx/ai-research/<slug>/`.

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

Optional feedback layout, created only when enabled by flag or config:

```text
.omx/ai-research/
  CONFIG.md
  LEARNINGS.md
  ISSUES.md
  DECISIONS.md
  SKILL_GROWTH.md
.omx/ai-research/<slug>/
  DESIGN.md
  NOTES.md
  REVIEW.md
```

Read `references/workflow-orchestration.md` before starting or resuming the full research workflow. Read `references/artifact-contracts.md` when authoring or auditing artifact contents. Read `references/project-local-script-registry.md` before creating or relying on project-local scripts. Read `references/experiment-runtime-standards.md` before designing, implementing, running, or auditing experiments. Read `references/research-quality-gates.md` before approving a handoff, result, or paper claim. Read `references/worktree-development.md` when making substantive target-repo changes. Run maintenance-only scripts only when updating or validating this skill, not while executing a user's research workflow.

## Optional feedback and growth modes

Research Feedback Memory and Researcher Growth Review are disabled by default. Do not create or update feedback artifacts unless the current invocation or project config enables them.

Invocation flags:
- `--feedback-memory`: enable Research Feedback Memory for this invocation. Record distilled issues, learnings, decisions, architecture or method tradeoffs, and reusable process notes.
- `--growth-review`: enable Researcher Growth Review for this invocation. Record capability-focused reflection across problem definition, experiment design, verification, systems engineering, expression, and risk awareness.
- `--no-feedback`: force both optional modes off for this invocation, even when project config enables them.

Optional project config lives at `.omx/ai-research/CONFIG.md`:

```yaml
feedback_memory: off | lite | full
growth_review: off | milestone | always
```

Resolution precedence:
1. `--no-feedback` disables both optional modes for the current invocation.
2. Explicit `--feedback-memory` or `--growth-review` enables that mode for the current invocation.
3. `.omx/ai-research/CONFIG.md` supplies project defaults.
4. Missing config means both modes stay off.

When `feedback_memory` is `lite`, write concise cross-run notes to `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, and workstream `NOTES.md` only when they preserve reusable knowledge. When `feedback_memory` is `full`, also maintain workstream `DESIGN.md` for method, architecture, pipeline, and evaluation design rationale.

When `growth_review` is `milestone`, update `SKILL_GROWTH.md` and workstream `REVIEW.md` only at major milestones such as workstream intake, experiment completion handoff, reproducibility review, or paper/report drafting. When `growth_review` is `always`, include a short growth review whenever a workflow phase closes. Do not ask extra reflection questions unless growth review is enabled and the answer would materially change the review; ask at most one.

Feedback memory records distilled knowledge, not raw logs. Keep raw run outputs under `runs/` and link or summarize them.

## Research control plane vs project implementation

`.omx/ai-research/` is the research portfolio control plane. It holds the overall `RESEARCH.md` and `INDEX.md` so the user can see the larger research program rather than a pile of unrelated small directions.

`.omx/ai-research/<slug>/` is the workstream control plane: specs, decisions, run indexes, evidence summaries, and reproducibility notes for one concrete direction.

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

## Experiment completion handoff

When the user says the current experiment is done, finished, ready to wrap up, or otherwise asks to close out the current run, switch into experiment completion handoff before answering. Do not treat the user's message as a request for a chat-only summary.

Completion handoff requires:
- inspect the current `.omx/ai-research/<slug>/runs/` directories, run manifests, logs, metrics, summaries, and figures that exist locally
- inspect `.omx/ai-research/<slug>/scripts/` and update `SCRIPT_REGISTRY.md` for scripts or native commands that were used, changed, validated, deprecated, or requested by the user
- update `RUNS.md` with terminal statuses, command records, log paths, metrics paths, summary paths, figure paths, failures, and distilled updates made outside `runs/`
- update `RESULTS.md` when the completed experiment changes tables, comparisons, interpretations, hypothesis verdicts, or user-requested takeaways
- update `REPRODUCIBILITY.md` with rerun commands, environment notes, missing artifacts, nondeterminism, blockers, or cleanup decisions
- persist user-requested outputs, notable findings, reusable commands, decisions, and next-step TODOs into the appropriate research artifact or project-root docs instead of leaving them only in the final response

Only skip artifact updates when the relevant files or run outputs cannot be found. If skipped, record the missing paths and the next exact recovery command in the final response.

## Workflow

### 0. OMX workflow entry

Start by reading or creating `.omx/ai-research/RESEARCH.md` and `.omx/ai-research/INDEX.md`. Decide whether the current request continues an existing workstream or requires a new `<slug>`, and update the portfolio index before deep work starts.

Resolve optional feedback modes from invocation flags and `.omx/ai-research/CONFIG.md` before authoring artifacts. If enabled, initialize only the optional feedback files that are needed by the current phase; if disabled, leave them absent.

For an existing workstream, use `$deep-interview --autoresearch` unless the user already provides clear hypotheses, success criteria, non-goals, forbidden claims, and evaluator/validation criteria. Use `$ralplan` before implementation-heavy work. Use `$autoresearch` for the durable validator-gated loop over literature, implementation, experiments, and claims.

For a new workstream, `$deep-interview --autoresearch`, `$ralplan`, and `$autoresearch` are mandatory in that order. The new-workstream gate is complete only after the gate evidence is linked from portfolio `INDEX.md`.

### 1. Research intake

Produce or update portfolio `RESEARCH.md` before implementation so the overall research program remains visible. Then produce or update the workstream `RESEARCH.md` for the current `<slug>`. Include:
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

If Research Feedback Memory is enabled, record non-obvious design decisions, rejected alternatives, architecture constraints, evaluation risks, and evidence expectations in `DECISIONS.md` or workstream `DESIGN.md` according to the resolved mode.

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

If the user explicitly says the current experiment is done, treat that as a terminal-run distillation trigger. First organize runs and scripts, then persist valuable or user-requested content into `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, and project-root docs when appropriate. Also update the portfolio `RESEARCH.md` and `INDEX.md` when the completed run changes the overall synthesis, workstream status, or next priority. The final response should summarize what was written and cite the file paths.

If Research Feedback Memory is enabled during distillation, update `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, and workstream `NOTES.md`/`DESIGN.md` with durable lessons, blockers, failed assumptions, architecture/method decisions, and reusable commands. If Researcher Growth Review is enabled, update `SKILL_GROWTH.md` and workstream `REVIEW.md` with capability-focused reflection tied to concrete evidence.

### 9. Analyze results

Produce `RESULTS.md`. Separate evidence from interpretation. Include raw result locations, complete experiment log path, metrics and summary data paths, visualization paths/captions, summary tables, uncertainty/variance, ablation interpretation, negative findings, threats to validity, and hypothesis verdicts.

### 10. Reproducibility review

Produce `REPRODUCIBILITY.md` using the quality gates reference. Check whether a fresh agent could reproduce the result from artifacts alone. Missing seeds, data versions, commands, complete log paths, metrics files, visualization outputs for numeric/comparative results, or result paths are blockers.

When optional feedback modes are enabled, include reproducibility lessons, verification gaps, and future capability practice items in the feedback artifacts without weakening the required reproducibility gate.

### 11. Paper draft or report

Produce `PAPER_DRAFT.md` only after results and reproducibility review exist. Every scientific claim must point to a result, citation, or explicit assumption. Downgrade unsupported claims to hypotheses or future work. After settled conclusions exist, publish the current artifacts to `docs/ai-research/<slug>/` so they can be browsed with MkDocs.

## Completion rules

Stop only when one of these is true:
- The requested artifact set exists and passes the relevant quality gates.
- A project validator, test command, or `$autoresearch` completion artifact passes.
- A real blocker prevents progress; report the missing data, compute, credentials, or decision.

Final responses must list changed/created research artifacts, project-root files changed for method/baseline/config/test/docs work, validation evidence, project-local scripts created/updated, tmux session/status paths for launched experiments, complete log file absolute paths for every experiment run, metrics/summary/figure paths, distilled run updates outside `runs/`, docs/MkDocs paths when conclusions were published, unsupported claims removed or downgraded, and remaining risks.
