# Experiment Runtime Standards

These standards are mandatory by default whenever an AI agent designs, implements, runs, or audits experiments. Do not treat logs, structured metrics, progress reporting, or visualizations as optional niceties. They are the evidence layer for reproducible research. Skip only when no experiment is executed or the user explicitly opts out; record the reason when skipped.

This document defines contracts, not universal scripts. Use project-native tooling first and create thin project-local wrappers only when needed. Record those wrappers in `SCRIPT_REGISTRY.md`.

## Run directory contract

Every experiment run must write to one distinct run directory:

```text
.omx/ai-research/<slug>/runs/<UTC_TIMESTAMP>-<run-name>/
  run_manifest.json
  run_command.sh               # or equivalent command record
  tmux_status.json             # when tmux is used
  logs/
    combined.log
  data/
    metrics.jsonl
    metrics.csv                # optional but recommended for tabular metrics
    predictions.jsonl          # optional task outputs
    summary.json               # final machine-readable summary
  figures/
    *.png|*.svg|*.pdf          # generated plots
    figures_manifest.json      # what each figure shows and source data path
```

`run_manifest.json` must include absolute paths for `run_dir`, `log_file`, `metrics_jsonl`, `summary_json`, and `figures_dir` so a human can open outputs without guessing.

## Terminal run distillation rules

The run directory is raw evidence, not the final research memory. After each run becomes terminal:

- Update `.omx/ai-research/<slug>/RUNS.md` with status, command, seed/device/resource, log path, metrics path, summary path, and failure notes.
- Update `.omx/ai-research/<slug>/RESULTS.md` when the run changes tables, figures, comparisons, hypothesis verdicts, or threats to validity.
- Update `.omx/ai-research/<slug>/REPRODUCIBILITY.md` when the run reveals environment requirements, nondeterminism, missing data, missing compute, or rerun steps.
- Promote stable conclusions to project-root `docs/`, `reports/`, benchmark cards, README sections, or MkDocs pages when useful.
- Promote reusable method, baseline, config, or test changes to project-root files; do not bury them in `.omx/ai-research/`.
- Keep raw logs, checkpoints, private data, and large temporary outputs in run storage; link or summarize them instead of copying them into project-root docs.

## Tmux orchestration rules

- Launch long experiments in detached tmux by default when tmux is available.
- Implement the launch as a project-local script or native command recorded in `SCRIPT_REGISTRY.md`; do not assume a pre-bundled runner exists.
- The runner/subagent returns immediately with `tmux_session`, `tmux_status`, `run_dir`, `log_file`, `metrics_jsonl`, `summary_json`, and `figures_dir`.
- The leader monitors periodically with `tmux capture-pane`, `tmux_status.json`, `data/summary.json`, and `logs/combined.log`.
- Completion is determined by durable files, not by optimistic status messages.
- For parallel lanes, use distinct run directories and session names; aggregate only after all required runs are terminal.

Generic tmux pattern to adapt into a project-local script:

```bash
tmux new-session -d -s "<session>" \
  "cd <project-root> && bash <run-command-record> 2>&1 | tee -a <absolute-log-path>"
```

## Multi-seed and accelerator lane rules

When an experiment requires multiple seeds and each seed is independent, split seeds across native subagents or OMX `$team` lanes when parallelism is safe.

Leader responsibilities:

- Inspect available GPUs/accelerators or scheduler slots before launch.
- Assign each seed lane an explicit idle device or scheduler resource.
- Record a seed-to-device allocation table in `RUNS.md` before or immediately after launch.
- Cap parallelism at available idle resources; queue or serialize extra seeds.
- Ensure each lane has a distinct run directory, tmux session name, log file, metrics file, summary file, and figure directory.

Worker/subagent lane responsibilities:

- Use only the assigned seed and device.
- Set the project-appropriate device control, for example `CUDA_VISIBLE_DEVICES=<id>`, a scheduler GPU request, or the framework's native device flag.
- Report `seed`, `device`, `run_dir`, `log_file`, `metrics_jsonl`, `summary_json`, `figures_dir`, and exit status to the leader.
- Never auto-select a GPU in a way that can race with another lane unless the cluster scheduler provides exclusive allocation.

Resource inspection should use project-native or platform-native tools when available, for example `nvidia-smi`, `rocm-smi`, `gpustat`, Slurm/PBS/Kubernetes queue status, or a project-specific launcher. Treat low utilization as a hint, not a lock; prefer scheduler-exclusive allocation on shared machines.

Recommended allocation table:

```markdown
| Seed | Lane | Device/resource | Run directory | Log path | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | subagent-1 | GPU 0 via CUDA_VISIBLE_DEVICES=0 | `/abs/runs/...-seed1` | `/abs/runs/.../logs/combined.log` | running |
```

## Logging rules

- Capture full stdout/stderr to `logs/combined.log` with `tee` or an equivalent project logger.
- Final responses must include the absolute `combined.log` path.
- Do not rely on terminal scrollback as the only record.
- Keep logs human-readable, but write metrics to structured files instead of scraping logs.
- If the command fails, keep the log and mark the run status as failed; do not delete partial evidence.

Recommended shell pattern to adapt:

```bash
set -o pipefail
<project-command> 2>&1 | tee -a /absolute/path/to/logs/combined.log
```

## Progress rules

- Long-running experiments must expose progress.
- In interactive terminals, a progress bar may render to stderr.
- In non-interactive runs, log periodic progress records instead of relying on carriage-return UI updates.
- Progress updates should include enough data to diagnose stalls: step, total steps when known, epoch, split, current metric, elapsed time, and ETA when available.
- Do not let progress bars corrupt JSONL/CSV outputs.

Use the project's native progress tools when available. If no project convention exists, add a small progress event writer in the project's language and record it in `SCRIPT_REGISTRY.md`.

## Data output rules

Every run should emit machine-readable data:

- `data/metrics.jsonl`: append one JSON object per evaluation step, epoch, dataset split, or ablation.
- `data/summary.json`: final status, best metrics, primary hypothesis verdict, input/output artifact paths.
- `data/metrics.csv`: recommended for easy plotting and spreadsheet review.

Minimum `metrics.jsonl` event fields:

```json
{"event":"metric","step":1,"split":"validation","metric":"accuracy","value":0.82,"seed":42}
```

Minimum `summary.json` fields:

```json
{
  "status": "passed|failed|inconclusive",
  "run_id": "20260506T010203Z-demo",
  "primary_metric": {"name": "accuracy", "value": 0.82},
  "hypothesis_verdict": "supported|contradicted|inconclusive",
  "log_file": "/absolute/path/to/combined.log",
  "metrics_jsonl": "/absolute/path/to/metrics.jsonl",
  "figures_dir": "/absolute/path/to/figures"
}
```

## Visualization rules

Every completed analysis should create at least one visualization when the result is numeric, comparative, temporal, or distributional.

Recommended figures:

- metric over time / steps
- baseline vs method comparison
- ablation bar chart
- error distribution or confusion matrix
- cost/latency/quality tradeoff curve

Each figure must have a source data path and caption in `figures/figures_manifest.json`:

```json
{
  "figures": [
    {
      "path": "/absolute/path/to/figures/accuracy_by_method.png",
      "source_data": "/absolute/path/to/data/metrics.csv",
      "caption": "Validation accuracy by method across seeds."
    }
  ]
}
```

If visualization is not appropriate, record why in `RESULTS.md`.

## Agent final-report requirement

After running an experiment, the agent must report:

- tmux session name and status file when tmux was used
- run directory absolute path
- complete log file absolute path
- metrics file absolute path
- summary file absolute path
- figures directory and key figure paths
- distilled updates made to `RUNS.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, or project-root docs/code/configs
- exit status
- next action if the run failed or remained inconclusive
