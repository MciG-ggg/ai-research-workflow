#!/usr/bin/env python3
"""Prepare a reproducible experiment run directory and bash wrapper."""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "run"


def git_value(args: list[str], cwd: Path) -> str | None:
    try:
        return subprocess.check_output(["git", *args], cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip() or None
    except Exception:
        return None


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an AI research experiment run directory.")
    parser.add_argument("slug", help="Research workspace slug under --root")
    parser.add_argument("--name", default="experiment", help="Short run name")
    parser.add_argument("--root", default=".omx/ai-research", help="Research workspace root")
    parser.add_argument("--command", required=True, help="Experiment command to run")
    parser.add_argument("--seed", action="append", default=[], help="Seed value; repeat for multiple seeds")
    parser.add_argument("--dataset", action="append", default=[], help="Dataset/version note; repeat as needed")
    args = parser.parse_args()

    cwd = Path.cwd().resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{timestamp}-{slugify(args.name)}"
    workspace = (cwd / args.root / slugify(args.slug)).resolve()
    run_dir = workspace / "runs" / run_id
    logs_dir = run_dir / "logs"
    data_dir = run_dir / "data"
    figures_dir = run_dir / "figures"
    for directory in (logs_dir, data_dir, figures_dir):
        directory.mkdir(parents=True, exist_ok=True)

    paths = {
        "run_dir": str(run_dir),
        "log_file": str(logs_dir / "combined.log"),
        "metrics_jsonl": str(data_dir / "metrics.jsonl"),
        "metrics_csv": str(data_dir / "metrics.csv"),
        "summary_json": str(data_dir / "summary.json"),
        "figures_dir": str(figures_dir),
        "figures_manifest": str(figures_dir / "figures_manifest.json"),
    }
    manifest = {
        "run_id": run_id,
        "status": "initialized",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cwd": str(cwd),
        "command": args.command,
        "git_commit": git_value(["rev-parse", "HEAD"], cwd),
        "git_branch": git_value(["branch", "--show-current"], cwd),
        "seeds": args.seed,
        "datasets": args.dataset,
        "paths": paths,
    }
    manifest_path = run_dir / "run_manifest.json"
    write_json(manifest_path, manifest)

    write_json(figures_dir / "figures_manifest.json", {"figures": []})
    (data_dir / "metrics.jsonl").touch()

    run_sh = run_dir / "run.sh"
    run_sh.write_text(
        f"""#!/usr/bin/env bash
set -uo pipefail
cd {shlex.quote(str(cwd))}
RUN_DIR={shlex.quote(str(run_dir))}
MANIFEST={shlex.quote(str(manifest_path))}
LOG_FILE={shlex.quote(paths['log_file'])}
METRICS_JSONL={shlex.quote(paths['metrics_jsonl'])}
SUMMARY_JSON={shlex.quote(paths['summary_json'])}
FIGURES_DIR={shlex.quote(paths['figures_dir'])}
export RUN_DIR LOG_FILE METRICS_JSONL SUMMARY_JSON FIGURES_DIR
mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$METRICS_JSONL")" "$FIGURES_DIR"
{{
  printf '%s\n' {shlex.quote(f"[run] id={run_id}")}
  printf '%s\n' "[run] cwd=$(pwd)"
  printf '%s\n' {shlex.quote(f"[run] command={args.command}")}
  printf '%s\n' "[run] log=$LOG_FILE"
  printf '%s\n' "[run] metrics=$METRICS_JSONL"
  printf '%s\n' "[run] summary=$SUMMARY_JSON"
  printf '%s\n' "[run] figures=$FIGURES_DIR"
}} | tee -a "$LOG_FILE"
start_ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
set +e
bash -lc {shlex.quote(args.command)} 2>&1 | tee -a "$LOG_FILE"
exit_code=${{PIPESTATUS[0]}}
set -e
end_ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 - "$MANIFEST" "$SUMMARY_JSON" "$exit_code" "$start_ts" "$end_ts" <<'PY'
import json, sys
from pathlib import Path
manifest_path, summary_path, exit_code, start_ts, end_ts = sys.argv[1:]
manifest = json.loads(Path(manifest_path).read_text())
manifest["status"] = "passed" if exit_code == "0" else "failed"
manifest["started_at"] = start_ts
manifest["ended_at"] = end_ts
manifest["exit_code"] = int(exit_code)
Path(manifest_path).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\\n")
summary = {{
    "status": manifest["status"],
    "run_id": manifest["run_id"],
    "exit_code": int(exit_code),
    "log_file": manifest["paths"]["log_file"],
    "metrics_jsonl": manifest["paths"]["metrics_jsonl"],
    "figures_dir": manifest["paths"]["figures_dir"],
    "hypothesis_verdict": "inconclusive" if exit_code != "0" else "pending-analysis",
}}
Path(summary_path).write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\\n")
PY
echo "[run] exit_code=$exit_code" | tee -a "$LOG_FILE"
echo "[run] manifest=$MANIFEST" | tee -a "$LOG_FILE"
echo "[run] summary=$SUMMARY_JSON" | tee -a "$LOG_FILE"
exit "$exit_code"
""",
        encoding="utf-8",
    )
    run_sh.chmod(0o755)

    print(f"run_dir={run_dir}")
    print(f"run_script={run_sh}")
    print(f"log_file={paths['log_file']}")
    print(f"metrics_jsonl={paths['metrics_jsonl']}")
    print(f"summary_json={paths['summary_json']}")
    print(f"figures_dir={paths['figures_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
