# Workflow Orchestration

This skill is a workflow, not only an experiment logging template. It coordinates OMX modes and project work from vague idea to implemented method, reproduced baseline, evidence-backed results, and writeup.

## Default OMX sequence

Use this default sequence unless existing artifacts prove that a phase is already complete:

```text
$deep-interview --autoresearch
  -> literature / research artifact drafting
  -> $ralplan for implementation and validation plan
  -> task worktree execution in the target repo
  -> $autoresearch for validator-gated research loop
  -> run experiments / reproduce baselines / evaluate method
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Phase rules:

- Use `$deep-interview --autoresearch` when the research mission, hypothesis, evaluator, non-goals, claim boundaries, or launch criteria are unclear.
- Use `$ralplan` before implementation-heavy work to produce a plan, tradeoffs, file ownership, and validation shape.
- Use `$autoresearch` when the work needs a persistent professor/critic or validator-gated loop over literature, implementation, experiments, and claims.
- Use `$team` or native subagents for independent lanes such as multiple seeds, baselines, ablations, literature blocks, or verification lanes.
- Use `$ralph`/`$autopilot` only after research and experiment specs exist and the remaining work is mainly implementation plus verification.

If the user provides mature artifacts, resume at the earliest failing gate instead of repeating completed phases.

## Control plane vs project implementation plane

`.omx/ai-research/<slug>/` is the research control plane. It stores specs, decisions, run indexes, evidence summaries, and reproducibility notes.

Actual research work belongs in the target project root using that project's conventions. Examples:

- method implementation: `src/`, `models/`, `methods/`, `algorithms/`, or the existing package layout
- baseline reproduction: `baselines/`, `configs/`, `scripts/`, `experiments/`, or existing benchmark layout
- training/evaluation entrypoints: project-native CLIs, notebooks, Make targets, Hydra configs, CI jobs, or shell scripts
- tests and verification: `tests/`, `evals/`, CI config, smoke tests, benchmark checks
- user-facing reports/docs: `docs/`, `reports/`, `mkdocs.yml`, README sections, benchmark cards

Do not implement the user's method, model, baseline, dataset adapter, or production experiment code inside `.omx/ai-research/`. Only thin orchestration wrappers, run metadata, and research notes belong there.

## Run distillation rule

A completed run directory is raw evidence. After each terminal run, distill reusable knowledge out of `runs/<run-id>/`:

1. Update `.omx/ai-research/<slug>/RUNS.md` with command, seed/device/resource, status, log path, metrics path, summary path, and failure notes.
2. Update `.omx/ai-research/<slug>/SCRIPT_REGISTRY.md` with scripts or native commands that were used, changed, validated, deprecated, or requested by the user.
3. Update `.omx/ai-research/<slug>/RESULTS.md` with tables, figures, hypothesis verdicts, and interpretation when the run changes the scientific picture.
4. Update `.omx/ai-research/<slug>/REPRODUCIBILITY.md` with new blockers, environment notes, nondeterminism, or rerun instructions.
5. Promote stable conclusions to project-root `docs/`, `reports/`, benchmark cards, config docs, or README sections when useful.
6. Promote reusable implementation changes to project-root code/config/tests, not to `.omx/ai-research/`.

Do not copy raw logs, large outputs, checkpoints, private data, or temporary run files into project-root docs. Link to them or summarize them.

If the user says the current experiment is done, use this as an experiment completion handoff signal: inspect runs and scripts, persist valuable or user-requested content into stable artifacts, then report the paths written.

## Baseline and method work

Baseline reproduction and new method implementation are first-class workflow tasks:

- Reproduce baselines before claiming improvement unless the research question explicitly excludes them.
- Keep baseline commands/configs reproducible and trace them from `EXPERIMENT.md` and `RUNS.md`.
- Implement methods in the project root with tests or smoke checks before expensive runs.
- Record claim boundaries when a baseline cannot be reproduced due to missing data, compute, license, or environment.
