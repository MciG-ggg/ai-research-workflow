---
name: ai-research-workflow
description: "AI research workflow orchestration for turning vague AI/ML research ideas into validated project work and research artifacts: optional idea scouting/generation, deep interview, literature review, falsifiable hypothesis spec, ralplan planning, method implementation, baseline reproduction, experiment design, experiment runs, result distillation, reproducibility review, optional research feedback memory, optional question capture, optional researcher growth review, and paper drafting. Use when Codex is asked to generate, scout, develop, implement, evaluate, reproduce, answer questions about, or write up an AI/ML research idea, benchmark, method, baseline, ablation, paper plan, experiment pipeline, or research report with clear hypotheses, baselines, metrics, validation, and claim boundaries."
---

# AI Research Workflow

## Purpose

Turn an AI/ML research idea into artifact-gated research work. This is a framework skill, not a project-specific experiment runner. Keep scientific intent, implementation work, run evidence, and claims separated so evidence controls conclusions.

Bundled scripts in this skill are maintenance and framework-guardrail helpers only. Do not use them as user experiment runners, metrics collectors, plotting scripts, or research-doc publishers. Generate or adapt project-local scripts only when the current project needs them.

This skill is an OMX workflow. By default it orchestrates:

```text
optional idea scouting when no clear research question exists
  -> $deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
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

## Reference map

- Read `references/workflow-orchestration.md` before starting or resuming the full workflow.
- Read `references/artifact-contracts.md` when authoring or auditing artifacts; prefer templates in `assets/templates/` when creating new artifacts.
- Read `references/research-quality-gates.md` before approving handoff, result, reproducibility, feedback, or paper claims.
- Read `references/idea-scouting.md` when the user asks for research idea generation, idea triage, or broad-direction scouting.
- Read `references/question-capture.md` when the user asks a research/workflow question and Q&A capture is enabled.
- Read `references/experiment-runtime-standards.md` before designing, implementing, running, or auditing experiments.
- Read `references/project-local-script-registry.md` before creating or relying on project-local scripts.
- Read `references/worktree-development.md` before substantive target-repo edits.

Maintenance validation:

```bash
python3 scripts/validate_framework_contract.py .
python3 scripts/validate_research_workspace.py <project-root>
python3 scripts/check_regression_fixtures.py
```

Framework guardrail helpers:

```bash
python3 scripts/resolve_workflow.py <project-root> --prompt "<user prompt>"
python3 scripts/init_research_workspace.py <project-root> --preset guided
python3 scripts/validate_research_workspace.py <project-root> --phase idea-scouting
python3 scripts/prepare_worktree_closeout.py <task-worktree> --base main
```

## Artifact setup

Maintain two research control-plane layers under `.omx/ai-research/`:

- Portfolio layer: `.omx/ai-research/RESEARCH.md` and `.omx/ai-research/INDEX.md` capture the user's overall research program, current synthesis, active workstreams, and how small directions relate to the larger goal.
- Workstream layer: `.omx/ai-research/<slug>/` captures a specific subquestion, method lane, baseline, ablation, experiment family, or paper/report slice.

Minimum portfolio layout:

```text
.omx/ai-research/
  IDEA_SCOUTING.md # optional when idea_scouting is enabled or the question is not yet clear
  RESEARCH.md
  INDEX.md
  QUESTIONS.md      # optional when qa_capture is enabled
```

Minimum workstream layout:

```text
.omx/ai-research/<slug>/
  STATE.json
  RESEARCH.md
  LITERATURE.md
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  CLAIMS.md
  REPRODUCIBILITY.md
  PAPER_DRAFT.md
  SCRIPT_REGISTRY.md
  QUESTIONS.md      # optional when qa_capture is enabled
  scripts/
  runs/
```

Use `assets/templates/portfolio-RESEARCH.md`, `portfolio-INDEX.md`, `STATE.json`, `workstream-RESEARCH.md`, `CLAIMS.md`, and the artifact-specific templates as the starting point when creating these files. Templates define shape only; replace TODO placeholders with project evidence before treating an artifact as complete.

## Workflow presets and overrides

Project config can reduce how often the user must name the workflow explicitly. Use `.omx/ai-research/CONFIG.md` from `assets/templates/CONFIG.md`:

```yaml
schema_version: 1
workflow_preset: conservative | guided | autonomous
idea_scouting: auto | off | on
completion_handoff: auto | off
worktree_closeout: off | report-before-merge
```

Preset meaning:
- `conservative`: run only explicitly requested phases.
- `guided`: infer common phases from user language; this is the recommended default.
- `autonomous`: proactively maintain relevant artifacts and next-step plans while still asking before final-topic selection, workstream creation, merge, push, worktree removal, or branch deletion.

Overrides win over the preset. `idea_scouting: auto` lets broad/vague idea prompts enter scouting; `completion_handoff: auto` treats "done", "wrap up", or "整理落盘" as completion handoff; `worktree_closeout: report-before-merge` prepares but does not execute merge/delete cleanup.

## Optional idea scouting

Idea Scouting is optional and is not the default path for already-clear research questions. Use it when the user asks for idea generation, asks whether an idea is worth doing, gives only a broad area, or explicitly passes `--idea-scouting`.

Write `.omx/ai-research/IDEA_SCOUTING.md` from `assets/templates/IDEA_SCOUTING.md`. The agent may choose search sources, generate candidate ideas, rank/filter candidates, and write the scouting artifact. It must not choose the final topic, guarantee absolute novelty, replace full `LITERATURE.md`, implement code, run experiments, or create a new workstream without user confirmation.

An idea may be recommended for formal research intake only when the promotion gate has all six fields: falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty risk, feasibility budget, and user-goal fit. If the user confirms promotion, enter the new-workstream gate.

## New workstream gate

Before creating a new `<slug>`, inspect the portfolio `RESEARCH.md`, `INDEX.md`, and existing workstream directories. Reuse or update an existing workstream when the task continues the same subquestion. Create a new workstream only when the task has a distinct research question, validation target, or artifact boundary, and record that relationship in the portfolio index.

New workstream creation has a mandatory workflow gate. If the task requires a new `<slug>`, do not create the workstream directory, implement code, run experiments, or publish docs until this sequence has completed and its artifact paths are recorded in `INDEX.md`:

```text
$deep-interview --autoresearch
  -> $ralplan
  -> $autoresearch
```

Required gate evidence:
- `$deep-interview --autoresearch`: validator-ready mission/intake artifact, preferably under `.omx/specs/autoresearch-<slug>/`, and a workstream `RESEARCH.md` draft linked to the portfolio
- `$ralplan`: consensus planning output plus `.omx/plans/prd-<slug>.md` and `.omx/plans/test-spec-<slug>.md`
- `$autoresearch`: persisted autoresearch state with a `completion_artifact_path`, plus `.omx/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`

If any gate evidence is missing, stop at the gate, create or complete the missing workflow artifact, and report the blocker. Do not bypass this gate because the new direction seems obvious.

## Optional feedback and growth modes

Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default. Do not create or update feedback artifacts unless the current invocation or project config enables them.

Invocation flags:
- `--feedback-memory`: enable Research Feedback Memory for this invocation.
- `--qa-capture`: enable Q&A capture for this invocation.
- `--growth-review`: enable Researcher Growth Review for this invocation.
- `--no-feedback`: force feedback memory, Q&A capture, and growth review off for this invocation.

Optional project config lives at `.omx/ai-research/CONFIG.md`:

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

Resolution precedence: `--no-feedback`, explicit enable flags, `.omx/ai-research/CONFIG.md`, then default off. Use `assets/templates/CONFIG.md`, `QUESTIONS.md`, `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, `SKILL_GROWTH.md`, `DESIGN.md`, `NOTES.md`, and `REVIEW.md` only when the resolved mode enables them.

Feedback memory records distilled knowledge, not raw logs. Keep raw run outputs under `runs/` and link or summarize them.

When Q&A capture is enabled and the user asks a research, design, architecture, experiment, interpretation, or workflow question rather than issuing a command, answer first, then append the question and answer summary to `.omx/ai-research/QUESTIONS.md` or `.omx/ai-research/<slug>/QUESTIONS.md`. Route durable concepts, decisions, issues, design notes, or growth lessons to the appropriate feedback artifacts.

## Research control plane vs project implementation

`.omx/ai-research/` is the research portfolio control plane. `.omx/ai-research/<slug>/` is a workstream control plane.

Actual research work belongs in the target project root using existing project conventions. Implement the user's method, reproduce baselines, add configs, tests, dataset adapters, training/evaluation entrypoints, and reports in project-root locations such as `src/`, `models/`, `baselines/`, `configs/`, `experiments/`, `scripts/`, `tests/`, `docs/`, or established equivalents. Do not put method code, baseline code, or production experiment code under `.omx/ai-research/`; only thin orchestration wrappers and metadata belong there.

## Task worktree rule

When this skill is used to make substantive AI research changes in a target project repository, inspect the local git status before opening any new worktree. If the main worktree has local modifications, preserve them first by splitting them into semantic commits with Lore-format commit messages; do not mix unrelated changes into one checkpoint. After the main worktree is clean, fetch/pull the primary branch, create the task worktree from the latest commit, and push the completed branch or merged main branch to the remote after validation and any required report-before-merge confirmation.

Prefer `<repo>/.omx/worktrees/<scope>/`; if that path is not writable, use a writable fallback and record the absolute path. Maintain `.omx/worktrees/REGISTRY.md` in the target repository with each worktree's path, branch, scope, owned files/areas, and status. Use one worktree per logical task or lane, merge worktrees back serially after validation, then clean them up.

Skip the worktree only for read-only analysis, quick lookups, or tiny safe edits. This task worktree rule is about executing research work inside the target project, not about installing or maintaining this skill repository.

## Git tracking rule

The skill repository tracks the framework itself:
- commit `README.md`, `README.zh-CN.md`, `skills/ai-research-workflow/**`, and the maintenance-only scripts that validate this framework
- keep `.omx/` ignored because it is local runtime state, logs, and temporary worktree data
- in downstream research projects, selectively version stable research documents and experiment contracts rather than raw run outputs

## Experiment defaults

When this skill runs, designs, implements, or audits experiments, structured runtime evidence is mandatory by default. Do not wait for the user to ask for logs, metrics, progress, or visualizations.

For every actual experiment run, ensure the project has existing native commands or project-local scripts recorded in `.omx/ai-research/<slug>/SCRIPT_REGISTRY.md`. Put wrappers under `.omx/ai-research/<slug>/scripts/`. Commands/scripts must produce a distinct run directory with command record, complete log, structured metrics, summary, and figures when visualizations are appropriate.

Each workstream keeps `STATE.json` as its phase state and `CLAIMS.md` as its evidence-to-claim ledger. Update `STATE.json` at workflow phase transitions. Update `CLAIMS.md` whenever results support, contradict, downgrade, or retire a claim.

Run long experiments in detached tmux by default when tmux is available. For multiple independent variants, baselines, ablations, datasets, or multi-seed experiments, use `$team` or native subagents when parallelism is safe. Assign each seed lane an explicit idle GPU/device or scheduler slot and record the seed-to-device mapping in `RUNS.md`.

When settled results or conclusions are finalized, publish them under project-root `docs/ai-research/<slug>/` and configure MkDocs when safe.

## Experiment completion handoff

When the user says the current experiment is done, finished, ready to wrap up, or otherwise asks to close out the current run, switch into Experiment completion handoff before answering. Do not treat the message as chat-only.

Completion handoff requires:
- inspect `.omx/ai-research/<slug>/runs/` manifests, logs, metrics, summaries, and figures
- inspect `.omx/ai-research/<slug>/scripts/` and update `SCRIPT_REGISTRY.md`
- update `RUNS.md`, `RESULTS.md`, and `REPRODUCIBILITY.md` when evidence changes status, conclusions, rerun requirements, or failures
- update `CLAIMS.md` and preserve negative or inconclusive results instead of deleting them
- persist user-requested outputs, notable findings, reusable commands, decisions, and next-step TODOs into stable artifacts or project-root docs
- update portfolio `RESEARCH.md` and `INDEX.md` when the overall synthesis, workstream status, or next priority changes
- if the workstream used a task worktree, prepare a report-before-merge closeout plan covering validation, semantic Lore-format commit status, merge/rebase target, push target, worktree removal, branch deletion, and `.omx/worktrees/REGISTRY.md` update; do not merge, push, delete the worktree, or delete the branch until the user confirms

Only skip artifact updates when relevant files or run outputs cannot be found. If skipped, record the missing paths and the next exact recovery command in the final response.

## Workflow phases

0. OMX workflow entry: read or create `.omx/ai-research/RESEARCH.md` and `.omx/ai-research/INDEX.md`; run optional idea scouting when there is no clear research question; decide whether to reuse a workstream or enter the new-workstream gate; resolve optional feedback and Q&A capture modes.
1. Research intake: produce portfolio and workstream `RESEARCH.md` with research question, falsifiable hypothesis, success/falsification criteria, non-goals, claim boundaries, and decision boundaries.
2. Literature review: produce `LITERATURE.md` with source-backed evidence from primary sources when facts are current or niche.
3. Research question spec: tighten hypotheses until each is testable.
4. Experiment design: produce `EXPERIMENT.md` before writing or changing experiment code, including baseline fairness and negative/inconclusive result policy.
5. Project-root implementation and baseline reproduction: implement method, baseline, configs, tests, and entrypoints in the target repository root after `$ralplan`.
6. Project-local orchestration scripts: reuse native project runners first; add thin wrappers only when needed and record them in `SCRIPT_REGISTRY.md`.
7. Run experiments: produce `RUNS.md`, never fabricate results, and record complete log, metrics, summary, figures, command, environment, commit, seeds, and failures.
8. Distill completed runs: update `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, project-root docs, and optional feedback/Q&A artifacts when enabled.
9. Analyze results: produce `RESULTS.md` and `CLAIMS.md`; separate evidence from interpretation, preserve negative/inconclusive findings, and keep claims within evidence.
10. Reproducibility review: produce `REPRODUCIBILITY.md`; missing seeds, data versions, commands, complete log paths, metrics, figures, or result paths are blockers.
11. Paper draft or report: produce `PAPER_DRAFT.md` only after results and reproducibility review exist.

## Completion rules

Stop only when the requested artifact set passes the relevant quality gates, a project validator/test command or `$autoresearch` completion artifact passes, or a real blocker prevents progress.

Final responses must list changed/created research artifacts, project-root method/baseline/config/test/docs files, validation evidence, project-local scripts, tmux/status/log/metrics/summary/figure paths, distilled run updates outside `runs/`, docs/MkDocs paths, unsupported claims removed or downgraded, optional feedback/Q&A artifacts when enabled, and remaining risks.
