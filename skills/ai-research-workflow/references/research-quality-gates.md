# AI Research Quality Gates

Use these gates before moving to the next phase or approving a final answer.

## Intake gate

Pass only if:
- The research question is specific enough to design an experiment.
- The hypothesis is falsifiable.
- Success and falsification criteria are explicit.
- Non-goals are explicit.
- Forbidden claims are explicit.

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
- Ablations test the core mechanism rather than cosmetic variants.
- Failure policy distinguishes environment failures from hypothesis failures.

## Result gate

Pass only if:
- No result is invented or inferred without an artifact path.
- Tables trace back to raw outputs.
- Any metrics collection, plotting, or publishing script used for the result is listed in `SCRIPT_REGISTRY.md` with validation status.
- Tmux session/status paths, complete log file paths, metrics paths, summary paths, and figure paths are recorded.
- Visualizations exist for numeric/comparative results or a reason is documented.
- Variance or uncertainty is reported when multiple runs are expected.
- Negative and inconclusive results are preserved.
- Claims do not exceed evidence.

## Reproducibility gate

Pass only if:
- A fresh agent can find data, configs, commands, project-local scripts or native command records, seeds, tmux/run status, complete logs, metrics, figures, and outputs.
- Environment requirements are explicit.
- Known non-determinism is disclosed.
- Missing compute, credentials, or data access is reported as a blocker.


## Documentation publishing gate

Pass only if settled conclusions and data are mirrored into project-root `docs/ai-research/<slug>/` or a documented reason explains why publication is deferred. `mkdocs.yml` should exist or an existing MkDocs config should be preserved with a reported nav update requirement.
