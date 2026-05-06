---
name: ai-research-workflow
description: "AI research workflow orchestration for turning vague AI/ML research ideas into validated research artifacts: intake, literature review, falsifiable hypothesis spec, experiment design, implementation, experiment runs, result analysis, reproducibility review, and paper drafting. Use when Codex is asked to develop, evaluate, reproduce, or write up an AI/ML research idea, benchmark, method, ablation, paper plan, experiment pipeline, or research report with clear hypotheses, baselines, metrics, validation, and claim boundaries."
---

# AI Research Workflow

## Purpose

Turn an AI/ML research idea into artifact-gated research work. Do not jump from a vague idea directly to experiment code. First separate scientific intent from execution details, then keep every claim tied to evidence.

This skill coordinates a workflow. It may hand off to OMX workflows when available:
- Use `$deep-interview --autoresearch` when the research mission, evaluator, non-goals, or launch criteria are unclear.
- Use `$autoresearch` when a clarified mission needs a persistent validator-gated research loop.
- Use `$ralplan`/`$ralph`/`$autopilot` only for implementation-heavy phases after research and experiment specs exist.

## Artifact setup

Create or reuse a research workspace under `.omx/ai-research/<slug>/`.

Prefer the bundled initializer for a new workspace:

```bash
python3 <skill_dir>/scripts/init_research_artifacts.py <slug> --root .omx/ai-research --title "<short title>"
```

Read `references/artifact-contracts.md` when authoring or auditing artifact contents. Read `references/experiment-runtime-standards.md` before designing, implementing, running, or auditing experiments. Read `references/research-quality-gates.md` before approving a handoff, result, or paper claim.


## Default experiment execution contract

When this skill runs, designs, implements, or audits experiments, structured runtime evidence is mandatory by default. Do not wait for the user to ask for logs, metrics, progress, or visualizations.

For every experiment run, use `scripts/launch_experiment_tmux.py` by default so the run is prepared, launched in a detached tmux session, and monitored from durable artifacts. Use `scripts/prepare_experiment_run.py` only when tmux is unavailable, the run is intentionally short/synchronous, or a project-native runner already provides the same contract. Equivalent runners must still produce: `run_manifest.json`, `run.sh` or equivalent command record, `logs/combined.log`, `data/metrics.jsonl`, `data/summary.json`, `figures/`, and `figures/figures_manifest.json`.

Only skip this contract when no experiment is actually executed, or when the user explicitly opts out. If skipped, record the reason in `RUNS.md` or the final response.

## Default experiment orchestration contract

Run experiments in detached tmux by default. The experiment runner agent must return the tmux session name, run directory, complete log path, metrics path, summary path, and figures path to the leader immediately after launch. The leader must poll the durable status/summary/log files until completion before claiming results.

For multiple independent variants, seeds, datasets, or ablations, use OMX `$team` or native subagents when parallel execution materially reduces wall-clock time and resource contention is acceptable. Each parallel lane must own a distinct run directory and must not overwrite another lane's metrics, logs, figures, or summaries. Aggregate only after all required lanes finish or fail with preserved logs.

## Default docs publishing contract

When results, settled data, or research conclusions are finalized, publish them under the project root `docs/` directory by default and configure MkDocs when safe. Use `scripts/publish_research_docs.py <slug>` to copy research artifacts into `docs/ai-research/<slug>/` and create `mkdocs.yml` if one does not already exist. If an existing MkDocs config is present, preserve it and report any manual nav update needed.

## Workflow

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

Record:
- query strategy and inclusion/exclusion criteria
- related-work matrix
- baseline candidates
- dataset/benchmark constraints
- gaps or unresolved risks
- citation links for claims

### 3. Research question spec

Tighten `RESEARCH.md` until each hypothesis is testable. Convert vague goals into measurable predictions, e.g. metric deltas, cost/latency bounds, robustness criteria, or qualitative rubric thresholds.

### 4. Experiment design

Produce `EXPERIMENT.md` before writing or changing experiment code. Include:
- datasets and splits
- baselines and fairness constraints
- model/method variants
- training/inference config
- metrics and statistical tests
- ablations
- seeds and reproducibility settings
- hardware/runtime budget
- logging and artifact paths
- exact reproduction commands
- failure-handling policy
- required run directory, complete log capture, metrics files, progress reporting, and visualization outputs

### 5. Implement experiment

Only implement after `RESEARCH.md` and `EXPERIMENT.md` are coherent. Keep code changes minimal and traceable to the experiment spec. Prefer existing project patterns. Add config files, deterministic seeds, structured metric writers, progress reporting, visualization generation, and result-output paths needed for reproducibility. Long-running experiment code must expose progress without corrupting structured outputs.

### 6. Run experiments

Produce `RUNS.md`. Record commands, environment, commit hash if available, data versions, seed values, result file paths, tmux session/status paths, complete log file absolute paths, metrics file absolute paths, figure paths, exit status, and failures. By default, run experiments through `scripts/launch_experiment_tmux.py` so each run creates `.omx/ai-research/<slug>/runs/<run-id>/` with `run.sh`, `tmux_status.json`, `logs/combined.log`, `data/metrics.jsonl`, `data/summary.json`, and `figures/`. The leader must periodically inspect `tmux_status.json`, `data/summary.json`, and/or `logs/combined.log` until completion. Never fabricate results. If experiments cannot run locally, state the blocker and leave exact runnable commands plus expected output locations.

### 7. Analyze results

Produce `RESULTS.md`. Separate evidence from interpretation:
- raw result locations
- complete experiment log path
- metrics and summary data paths
- visualization paths and captions
- summary tables
- uncertainty, variance, or confidence intervals when applicable
- ablation interpretation
- negative findings
- threats to validity
- which hypotheses passed, failed, or remain unresolved

### 8. Reproducibility review

Produce `REPRODUCIBILITY.md` using the quality gates reference. Check whether a fresh agent could reproduce the result from artifacts alone. Missing seeds, data versions, commands, complete log paths, metrics files, visualization outputs for numeric/comparative results, or result paths are blockers.

### 9. Paper draft or report

Produce `PAPER_DRAFT.md` only after results and reproducibility review exist. Every scientific claim must point to a result, citation, or explicit assumption. Downgrade unsupported claims to hypotheses or future work. After settled conclusions exist, publish the current artifacts to `docs/ai-research/<slug>/` via `scripts/publish_research_docs.py` so they can be browsed with MkDocs.

## Completion rules

Stop only when one of these is true:
- The requested artifact set exists and passes the relevant quality gates.
- A validator script or `$autoresearch` completion artifact passes.
- A real blocker prevents progress; report the missing data, compute, credentials, or decision.

Final responses must list changed/created artifacts, validation evidence, tmux session/status paths for launched experiments, complete log file absolute paths for every experiment run, metrics/summary/figure paths, docs/MkDocs paths when conclusions were published, unsupported claims removed or downgraded, and remaining risks.
