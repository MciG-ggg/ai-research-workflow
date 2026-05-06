#!/usr/bin/env python3
"""Prepare and launch an AI research experiment in a detached tmux session."""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(value: str, default: str = "run") -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or default


def parse_key_values(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch a prepared AI research experiment in detached tmux.")
    parser.add_argument("slug", help="Research workspace slug under --root")
    parser.add_argument("--name", default="experiment", help="Short run name")
    parser.add_argument("--root", default=".omx/ai-research", help="Research workspace root")
    parser.add_argument("--command", required=True, help="Experiment command to run")
    parser.add_argument("--seed", action="append", default=[], help="Seed value; repeat for multiple seeds")
    parser.add_argument("--dataset", action="append", default=[], help="Dataset/version note; repeat as needed")
    parser.add_argument("--session-prefix", default="ar", help="tmux session name prefix")
    parser.add_argument("--hold-seconds", type=int, default=300, help="Seconds to keep tmux pane open after completion")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args()

    if not shutil.which("tmux"):
        raise SystemExit("tmux is required but was not found on PATH")

    script_dir = Path(__file__).resolve().parent
    prepare_script = script_dir / "prepare_experiment_run.py"
    prepare_cmd = [
        sys.executable,
        str(prepare_script),
        args.slug,
        "--root",
        args.root,
        "--name",
        args.name,
        "--command",
        args.command,
    ]
    for seed in args.seed:
        prepare_cmd.extend(["--seed", seed])
    for dataset in args.dataset:
        prepare_cmd.extend(["--dataset", dataset])

    prepared_output = subprocess.check_output(prepare_cmd, text=True)
    prepared = parse_key_values(prepared_output)
    run_dir = Path(prepared["run_dir"]).resolve()
    run_script = Path(prepared["run_script"]).resolve()
    status_path = run_dir / "tmux_status.json"
    entrypoint = run_dir / "tmux_entrypoint.sh"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    session_name = "-".join([
        slugify(args.session_prefix, "ar")[:12],
        slugify(args.slug, "research")[:24],
        slugify(args.name, "run")[:24],
        timestamp,
    ])

    initial_status = {
        "status": "launched",
        "launched_at": datetime.now(timezone.utc).isoformat(),
        "tmux_session": session_name,
        "run_script": str(run_script),
        "hold_seconds": args.hold_seconds,
        "paths": prepared,
        "monitor": {
            "tmux_attach": f"tmux attach -t {session_name}",
            "tmux_capture": f"tmux capture-pane -pt {session_name}:0.0 -S -200",
            "summary": prepared.get("summary_json"),
            "log": prepared.get("log_file"),
        },
    }
    write_json(status_path, initial_status)

    entrypoint.write_text(
        f"""#!/usr/bin/env bash
set +e
STATUS_FILE={shlex.quote(str(status_path))}
RUN_SCRIPT={shlex.quote(str(run_script))}
HOLD_SECONDS={int(args.hold_seconds)}
python3 - "$STATUS_FILE" <<'PY'
import json, sys, datetime
from pathlib import Path
path = Path(sys.argv[1])
data = json.loads(path.read_text())
data["status"] = "running"
data["started_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\\n")
PY
bash "$RUN_SCRIPT"
exit_code=$?
python3 - "$STATUS_FILE" "$exit_code" <<'PY'
import json, sys, datetime
from pathlib import Path
path = Path(sys.argv[1])
exit_code = int(sys.argv[2])
data = json.loads(path.read_text())
data["status"] = "completed" if exit_code == 0 else "failed"
data["exit_code"] = exit_code
data["completed_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\\n")
PY
echo "[tmux] experiment finished with exit_code=$exit_code"
echo "[tmux] status=$STATUS_FILE"
echo "[tmux] holding pane for $HOLD_SECONDS seconds for inspection"
sleep "$HOLD_SECONDS"
exit "$exit_code"
""",
        encoding="utf-8",
    )
    entrypoint.chmod(0o755)

    subprocess.check_call(["tmux", "new-session", "-d", "-s", session_name, "bash", str(entrypoint)])

    payload = {
        "tmux_session": session_name,
        "tmux_status": str(status_path),
        "tmux_entrypoint": str(entrypoint),
        **prepared,
        "monitor_commands": initial_status["monitor"],
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        for key, value in payload.items():
            if isinstance(value, dict):
                print(f"{key}={json.dumps(value, ensure_ascii=False)}")
            else:
                print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
