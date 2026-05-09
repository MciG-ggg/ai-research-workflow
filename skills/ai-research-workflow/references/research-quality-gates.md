# AI Research Quality Gates

Use these gates before moving to the next phase or approving a final answer.

For deterministic checks, run the phase-aware validator:

```bash
python3 scripts/validate_research_workspace.py <project-root> --phase idea-scouting --error-on-todo
python3 scripts/validate_research_workspace.py <project-root> --phase new-workstream --workstream <slug>
python3 scripts/validate_research_workspace.py <project-root> --phase completion-handoff --workstream <slug> --check-paths
```

## Contents

- [Intake gate](#intake-gate)
- [Idea scouting gate](#idea-scouting-gate)
- [Workflow gate](#workflow-gate)
- [New workstream gate](#new-workstream-gate)
- [Literature gate](#literature-gate)
- [Experiment gate](#experiment-gate)
- [Implementation gate](#implementation-gate)
- [Result gate](#result-gate)
- [Claim ledger gate](#claim-ledger-gate)
- [Reproducibility gate](#reproducibility-gate)
- [Optional feedback memory gate](#optional-feedback-memory-gate)
- [Optional question capture gate](#optional-question-capture-gate)
- [Optional growth review gate](#optional-growth-review-gate)
- [Documentation publishing gate](#documentation-publishing-gate)
- [Experiment completion handoff gate](#experiment-completion-handoff-gate)

## Intake gate

Pass only if:
- Portfolio `.omx/ai-research/RESEARCH.md` exists or is created with the overall research program before opening a new workstream.
- Portfolio `.omx/ai-research/INDEX.md` exists or is created with a workstream registry before opening a new workstream.
- Existing workstreams were checked before a new slug was created.
- The research question is specific enough to design an experiment.
- The hypothesis is falsifiable.
- Success and falsification criteria are explicit.
- Non-goals are explicit.
- Forbidden claims are explicit.

## Idea scouting gate

This gate is active only when the user asks for idea generation, idea triage, broad-direction scouting, `.omx/ai-research/CONFIG.md` sets `idea_scouting: on`, or `idea_scouting: auto` applies under a guided/autonomous preset. Skip it for already-clear research questions.

Pass only if:
- `.omx/ai-research/IDEA_SCOUTING.md` exists and records the scouting objective.
- Candidate ideas include falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty risk, feasibility budget, and user-goal fit.
- Weak ideas are parked or rejected with evidence and revisit triggers instead of silently discarded.
- The recommended candidate passes all six promotion gate fields before formal intake is suggested.
- The final topic is not chosen for the user; creating a new workstream still requires user confirmation.
- Scouting is not treated as full literature review and does not replace `LITERATURE.md`.

## Workflow gate

Pass only if:
- The workflow stages that are relevant to the task are explicit: optional idea scouting, deep interview, planning, implementation, baseline reproduction, experiments, distillation, reproducibility review, and reporting.
- The chosen OMX handoff path is appropriate for the current ambiguity and risk.
- Workstream `STATE.json` records the current phase, next action, blockers, and confirmation boundaries.
- Portfolio artifacts in `.omx/ai-research/` describe the overall research program, while workstream artifacts in `.omx/ai-research/<slug>/` describe one concrete direction.
- Control-plane artifacts are clearly separated from project-root code/config/test/docs work.

## New workstream gate

Pass only if, before a new `.omx/ai-research/<slug>/` workstream is created:
- Portfolio `RESEARCH.md` and `INDEX.md` were inspected.
- Existing workstreams were checked and reuse was rejected with a recorded reason.
- `$deep-interview --autoresearch` completed and produced a validator-ready mission/intake artifact.
- `$ralplan` completed and produced consensus planning output plus `.omx/plans/prd-<slug>.md` and `.omx/plans/test-spec-<slug>.md`.
- `$autoresearch` was initialized with persisted state, `completion_artifact_path`, and `.omx/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`.
- Portfolio `INDEX.md` records the exact evidence paths for all three gates.

Fail closed: if any item is missing, do not create the new slug, implement code, run experiments, or publish docs. Reuse an existing workstream instead when equivalent gate evidence is already linked there.

## Literature gate

Pass only if:
- Current claims are backed by primary sources or clearly marked as assumptions.
- Baselines are justified, not cherry-picked.
- Dataset and benchmark constraints are recorded.
- The gap/novelty claim is scoped to the searched evidence.

## Experiment gate

Pass only if:
- Baselines are comparable under fair settings.
- The baseline fairness checklist covers same data split/preprocessing, same metric, comparable compute/tuning budget, hyperparameter budget, implementation source/version, and reproduction gaps.
- Metrics match the research question.
- Seeds, data splits, and commands are specified.
- Existing project commands or project-local wrapper scripts are recorded in `SCRIPT_REGISTRY.md` before they are treated as part of the workflow.
- Detached tmux execution/monitoring, complete log capture, metrics files, progress reporting, and visualization outputs are specified.
- Multi-seed parallel plans assign each seed lane an explicit idle GPU/device, scheduler slot, or serial fallback.
- Ablations test the core mechanism rather than cosmetic variants.
- Failure policy distinguishes environment failures from hypothesis failures.
- Negative/inconclusive result policy preserves failed, null, and underpowered results with a stop/rerun/redesign decision.

## Implementation gate

Pass only if:
- The method, baseline, or evaluation implementation lives in the target repository's normal source/config/test layout, not under `.omx/ai-research/`.
- Project-root code/config/test changes are recorded alongside the research plan when they are part of the task.
- Baseline reproduction is either completed or explicitly blocked with reasons.

## Result gate

Pass only if:
- No result is invented or inferred without an artifact path.
- Tables trace back to raw outputs.
- Any metrics collection, plotting, or publishing script used for the result is listed in `SCRIPT_REGISTRY.md` with validation status.
- Tmux session/status paths, complete log file paths, metrics paths, summary paths, and figure paths are recorded.
- Per-seed result paths and seed-to-device/resource assignments are recorded when multi-seed runs were parallelized.
- Visualizations exist for numeric/comparative results or a reason is documented.
- Variance or uncertainty is reported when multiple runs are expected.
- Negative and inconclusive results are preserved.
- `CLAIMS.md` is updated when evidence supports, contradicts, downgrades, retires, or leaves a claim inconclusive.
- Claims do not exceed evidence.
- Distilled updates outside `runs/` are recorded when the run changed stable conclusions or reusable project artifacts.
- User-requested findings, reusable commands, cleanup decisions, and next-step TODOs from experiment completion handoff are persisted to `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, or project-root docs as appropriate.
- When a task worktree was used, the completion handoff includes a report-before-merge closeout plan covering validation, semantic commit status, merge/rebase target, push target, worktree removal, branch deletion, and `.omx/worktrees/REGISTRY.md` update.
- Portfolio `RESEARCH.md` and `INDEX.md` are updated when a result changes the overall synthesis, workstream status, or next priority.
- Optional Research Feedback Memory artifacts are updated when the mode is enabled; when disabled, their absence is not a failure.
- Optional Question Capture artifacts are updated when the mode is enabled and the user asked question-like prompts; when disabled, their absence is not a failure.

## Claim ledger gate

Pass only if:
- `CLAIMS.md` exists for each active workstream that has results or draft report claims.
- Every non-draft claim has evidence paths, scope/population, allowed wording, forbidden wording, and status.
- Contradicted, negative, and inconclusive findings are preserved with scientific value and follow-up or stop condition.
- Retired or downgraded claims record previous wording, new wording/status, reason, and evidence.
- Paper/report wording links back to `CLAIMS.md` and does not introduce untracked claims.

## Reproducibility gate

Pass only if:
- A fresh agent can find data, configs, commands, project-local scripts or native command records, seeds, seed-to-device/resource assignments, tmux/run status, complete logs, metrics, figures, and outputs.
- Environment requirements are explicit.
- Known non-determinism is disclosed.
- Missing compute, credentials, or data access is reported as a blocker.

## Optional feedback memory gate

This gate is active only when `--feedback-memory` is present or `.omx/ai-research/CONFIG.md` sets `feedback_memory: lite` or `feedback_memory: full`. When Research Feedback Memory is disabled by default or by `--no-feedback`, skip this gate.

Pass only if enabled feedback artifacts contain concise, reusable entries:
- `LEARNINGS.md` records concepts, papers, methods, domain knowledge, or verification lessons with evidence links.
- `ISSUES.md` records blockers, bugs, failed assumptions, recovery steps, or prevention notes.
- `DECISIONS.md` records method, architecture, experiment, or workflow decisions with alternatives and rationale.
- Workstream `NOTES.md` records useful process notes, reusable commands, or cross-links to stable artifacts.
- Workstream `DESIGN.md` records non-obvious method, architecture, pipeline, or evaluation design rationale when `feedback_memory: full`.

Fail only on enabled modes when valuable durable knowledge was discovered but left only in chat.

## Optional question capture gate

This gate is active only when `--qa-capture` is present or `.omx/ai-research/CONFIG.md` sets `qa_capture: research` or `qa_capture: all`. When Question Capture is disabled by default or by `--no-feedback`, skip this gate.

Pass only if enabled Q&A artifacts contain concise, durable entries:
- Root `QUESTIONS.md` records cross-workstream or portfolio-level user questions and answer summaries.
- Workstream `QUESTIONS.md` records workstream-specific questions and answer summaries.
- Each captured entry includes scope, question, answer summary, evidence/links, routed updates, and follow-up.
- Durable concepts, decisions, issues, design notes, or growth lessons are routed to the appropriate feedback artifacts when applicable.

Do not fail when no question-like prompt occurred. Fail only when a durable answered question occurred under enabled capture and was left only in chat.

## Optional growth review gate

This gate is active only when `--growth-review` is present or `.omx/ai-research/CONFIG.md` sets `growth_review: milestone` or `growth_review: always`. When Researcher Growth Review is disabled by default or by `--no-feedback`, skip this gate.

Pass only if enabled growth artifacts link capability lessons to concrete evidence:
- `SKILL_GROWTH.md` records lessons across problem definition, research taste, experiment design, verification, systems engineering, expression/collaboration, or risk awareness.
- Workstream `REVIEW.md` records milestone reflection, evidence quality, overclaim risk, and next capability practice items.

Growth review must not weaken scientific gates or invent self-improvement claims without artifact evidence.


## Documentation publishing gate

Pass only if settled conclusions and data are mirrored into project-root `docs/ai-research/<slug>/` or a documented reason explains why publication is deferred. `mkdocs.yml` should exist or an existing MkDocs config should be preserved with a reported nav update requirement.

## Experiment completion handoff gate

Pass only if, when the user says the current experiment is done:
- available run directories, manifests, logs, metrics, summaries, and figures were inspected
- `RUNS.md` records terminal status, evidence paths, failures, and distilled updates outside `runs/`
- `SCRIPT_REGISTRY.md` records scripts or native commands used, changed, validated, deprecated, or requested by the user
- `RESULTS.md` and `REPRODUCIBILITY.md` were updated when the evidence changed conclusions or rerun requirements
- valuable or user-requested content was written to stable artifacts instead of remaining only in chat
- if a task worktree was used, a report-before-merge closeout plan was written and the agent did not merge, push, remove the worktree, or delete the branch before user confirmation
- `STATE.json` was moved to `completion-handoff` or `report-before-merge` as appropriate
- `CLAIMS.md` records supported, contradicted, inconclusive, downgraded, or retired claims from the finished experiment
- missing evidence or skipped writes are reported with exact paths and recovery commands

## Research review gate

Before paper/report drafting or merge-back, run a research review pass:

1. `scripts/summarize_research_state.py <project-root>` to inspect portfolio state, workstream phases, blockers, missing artifacts, run/script inventory, and suggested next actions.
2. `scripts/score_research_artifacts.py <project-root>` to produce an artifact quality score. A high score is not proof of truth, but a low score is a blocker to stronger claims.
3. `scripts/prepare_workstream_closeout.py <project-root> <slug> --write` when a workstream is done.
4. `scripts/preserve_negative_result.py` whenever evidence is negative, null, failed, or inconclusive.
5. `scripts/generate_report_outline.py` only after evidence-to-claim mapping is stable.

Fail closed when the score highlights missing hypothesis, baseline fairness, run evidence, claim ledger, negative/inconclusive preservation, or reproducibility terms. The remedy is to improve the artifact or downgrade the claim, not to ignore the score.

## Schema, graph, and version gates

Use these additional checks when a workstream is mature enough for closeout, drafting, or merge-back:

1. Run `scripts/validate_research_schema.py <project-root>` to validate CONFIG, STATE, claim rows, run rows, and portfolio index rows against `assets/schemas/`.
2. Run `scripts/build_evidence_graph.py <project-root> <slug> --json` to expose claim -> evidence -> run/script traceability before strengthening claims or drafting.
3. Run `scripts/check_skill_update.py` when behavior looks stale; it reports `assets/VERSION`, source commit/dirty status, installed version, and optional remote status without changing files.
4. Run `scripts/run_e2e_scenarios.py` only while maintaining this skill framework, not inside a user experiment.

Fail closed if schema validation reports errors, if the evidence graph shows claims without evidence paths, or if the installed skill is stale and the observed behavior depends on a newer helper. The remedy is to fix artifacts or update the installed skill, not to relax scientific gates.
