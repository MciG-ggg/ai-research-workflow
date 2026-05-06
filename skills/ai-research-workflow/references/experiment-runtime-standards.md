# Experiment Runtime Standards

These standards are mandatory by default whenever an AI agent designs, implements, runs, or audits experiments. Do not treat logs, structured metrics, progress reporting, or visualizations as optional niceties. They are the evidence layer for reproducible research. Skip only when no experiment is executed or the user explicitly opts out; record the reason when skipped.

## Run directory contract

Every experiment run must be launched in detached tmux by default and write to one run directory:

```text
.omx/ai-research/<slug>/runs/<UTC_TIMESTAMP>-<run-name>/
  run_manifest.json
  run.sh
  tmux_status.json              # present for tmux-launched runs
  logs/
    combined.log
  data/
    metrics.jsonl
    metrics.csv                 # optional but recommended for tabular metrics
    predictions.jsonl           # optional task outputs
    summary.json                # final machine-readable summary
  figures/
    *.png|*.svg|*.pdf           # generated plots
    figures_manifest.json       # what each figure shows and source data path
```

`run_manifest.json` must include absolute paths for `run_dir`, `log_file`, `metrics_jsonl`, `summary_json`, and `figures_dir` so a human can open outputs without guessing.


## Tmux orchestration rules

- Use `scripts/launch_experiment_tmux.py` by default for actual experiment execution.
- The runner/subagent returns immediately with `tmux_session`, `tmux_status`, `run_dir`, `log_file`, `metrics_jsonl`, `summary_json`, and `figures_dir`.
- The leader monitors periodically with `tmux capture-pane`, `tmux_status.json`, `data/summary.json`, and `logs/combined.log`.
- Completion is determined by durable files, not by optimistic status messages.
- Long-running panes may remain open briefly after completion for inspection; logs and summaries remain the source of truth.
- For parallel lanes, use distinct run directories and session names; aggregate only after all required runs are terminal.

Default launch pattern:

```bash
python3 <skill_dir>/scripts/launch_experiment_tmux.py <slug> --name <run-name> --command "python train.py ..."
```

## Logging rules

- Capture full stdout/stderr to `logs/combined.log` with `tee` or an equivalent logger.
- Final responses must include the absolute `combined.log` path.
- Do not rely on terminal scrollback as the only record.
- Keep logs human-readable, but write metrics to structured files instead of scraping logs.
- If the command fails, keep the log and mark the run status as failed; do not delete partial evidence.

Recommended shell pattern:

```bash
set -o pipefail
bash run.sh 2>&1 | tee -a /absolute/path/to/logs/combined.log
```

Use the bundled `launch_experiment_tmux.py` script for default detached execution. Use `prepare_experiment_run.py` only for short synchronous smoke runs, tmux-unavailable environments, or project-native runners that satisfy this same contract.

## Progress bar rules

- Long-running experiments must expose progress.
- In interactive terminals, a progress bar may render to stderr.
- In non-interactive runs, log periodic progress records instead of relying on carriage-return UI updates.
- Progress updates should include enough data to diagnose stalls: step, total steps when known, epoch, split, current metric, elapsed time, and ETA when available.
- Do not let progress bars corrupt JSONL/CSV outputs.

Python pattern without adding dependencies:

```python
import json, sys, time

def progress(step, total=None, **fields):
    payload = {"event": "progress", "step": step, "total": total, "time": time.time(), **fields}
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr, flush=True)
```

If `tqdm` is already a project dependency, use it for terminal UX, but still write structured metrics/progress records.

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
- exit status
- next action if the run failed or remained inconclusive
