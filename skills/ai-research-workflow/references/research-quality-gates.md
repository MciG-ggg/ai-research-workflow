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
- Ablations test the core mechanism rather than cosmetic variants.
- Failure policy distinguishes environment failures from hypothesis failures.

## Result gate

Pass only if:
- No result is invented or inferred without an artifact path.
- Tables trace back to raw outputs.
- Variance or uncertainty is reported when multiple runs are expected.
- Negative and inconclusive results are preserved.
- Claims do not exceed evidence.

## Reproducibility gate

Pass only if:
- A fresh agent can find data, configs, commands, seeds, logs, and outputs.
- Environment requirements are explicit.
- Known non-determinism is disclosed.
- Missing compute, credentials, or data access is reported as a blocker.
