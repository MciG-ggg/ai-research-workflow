# AI Research Quality Gates

Use these gates before moving to the next phase or approving a final answer.

## Intake gate

Pass only if:
- The research question is specific enough to design an experiment.
- The hypothesis is falsifiable.
- Success and falsification criteria are explicit.
- Non-goals are explicit.
- Forbidden claims are explicit.

## Workflow gate

Pass only if:
- The workflow stages that are relevant to the task are explicit: deep interview, planning, implementation, baseline reproduction, experiments, distillation, reproducibility review, and reporting.
- The chosen OMX handoff path is appropriate for the current ambiguity and risk.
- Control-plane artifacts in `.omx/ai-research/<slug>/` are clearly separated from project-root code/config/test/docs work.

## Literature gate

Pass only if:
- Current claims are backed by primary sources or clearly marked as assumptions.
- Baselines are justified, not cherry-picked.
- Dataset and benchmark constraints are recorded.
- The gap/novelty claim is scoped to the searched evidence.

## Experiment gate

Pass only if:
- Baselines are comparable under fair settings.
- Metrics match the research question.
- Seeds, data splits, and commands are specified.
- Existing project commands or project-local wrapper scripts are recorded in `SCRIPT_REGISTRY.md` before they are treated as part of the workflow.
- Detached tmux execution/monitoring, complete log capture, metrics files, progress reporting, and visualization outputs are specified.
- Multi-seed parallel plans assign each seed lane an explicit idle GPU/device, scheduler slot, or serial fallback.
- Ablations test the core mechanism rather than cosmetic variants.
- Failure policy distinguishes environment failures from hypothesis failures.

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
- Claims do not exceed evidence.
- Distilled updates outside `runs/` are recorded when the run changed stable conclusions or reusable project artifacts.
- User-requested findings, reusable commands, cleanup decisions, and next-step TODOs from experiment completion handoff are persisted to `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, or project-root docs as appropriate.

## Reproducibility gate

Pass only if:
- A fresh agent can find data, configs, commands, project-local scripts or native command records, seeds, seed-to-device/resource assignments, tmux/run status, complete logs, metrics, figures, and outputs.
- Environment requirements are explicit.
- Known non-determinism is disclosed.
- Missing compute, credentials, or data access is reported as a blocker.


## Documentation publishing gate

Pass only if settled conclusions and data are mirrored into project-root `docs/ai-research/<slug>/` or a documented reason explains why publication is deferred. `mkdocs.yml` should exist or an existing MkDocs config should be preserved with a reported nav update requirement.

## Experiment completion handoff gate

Pass only if, when the user says the current experiment is done:
- available run directories, manifests, logs, metrics, summaries, and figures were inspected
- `RUNS.md` records terminal status, evidence paths, failures, and distilled updates outside `runs/`
- `SCRIPT_REGISTRY.md` records scripts or native commands used, changed, validated, deprecated, or requested by the user
- `RESULTS.md` and `REPRODUCIBILITY.md` were updated when the evidence changed conclusions or rerun requirements
- valuable or user-requested content was written to stable artifacts instead of remaining only in chat
- missing evidence or skipped writes are reported with exact paths and recovery commands
