#!/usr/bin/env python3
"""Prepare a workstream completion handoff and closeout plan.

Script: prepare_workstream_closeout.py.

This is a framework guardrail. It inspects control-plane artifacts and may write
CLOSEOUT.md when requested. It does not run experiments, collect metrics, plot
results, publish docs, merge branches, push remotes, remove worktrees, or delete
branches.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED = ["STATE.json", "RUNS.md", "SCRIPT_REGISTRY.md", "RESULTS.md", "CLAIMS.md", "REPRODUCIBILITY.md"]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def todo_count(path: Path) -> int:
    return sum(1 for line in read(path).splitlines() if "TODO" in line)


def inspect_workstream(project_root: Path, slug: str, validation: list[str], worktree: str | None) -> dict[str, Any]:
    workstream = project_root / ".omx" / "ai-research" / slug
    if not workstream.is_dir():
        raise SystemExit(f"missing workstream: {workstream}")
    state: dict[str, Any] = {}
    state_error = None
    if (workstream / "STATE.json").is_file():
        try:
            loaded = json.loads((workstream / "STATE.json").read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                state = loaded
        except json.JSONDecodeError as exc:
            state_error = str(exc)
    missing = [name for name in REQUIRED if not (workstream / name).is_file()]
    validation_evidence = []
    for raw in validation:
        path = Path(raw)
        if not path.is_absolute():
            path = (project_root / path).resolve()
        validation_evidence.append({"path": str(path), "exists": path.exists()})
    runs_dir = workstream / "runs"
    scripts_dir = workstream / "scripts"
    run_dirs = sorted(child.name for child in runs_dir.iterdir() if child.is_dir()) if runs_dir.is_dir() else []
    scripts = sorted(child.name for child in scripts_dir.iterdir() if child.is_file()) if scripts_dir.is_dir() else []
    blockers = []
    if missing:
        blockers.append("missing completion artifacts: " + ", ".join(missing))
    if state_error:
        blockers.append("invalid STATE.json: " + state_error)
    if state.get("current_blockers"):
        blockers.extend(str(item) for item in state.get("current_blockers", []))
    if validation_evidence and not all(item["exists"] for item in validation_evidence):
        blockers.append("one or more validation evidence paths are missing")
    return {
        "generated_at": utc_now(),
        "project_root": str(project_root),
        "slug": slug,
        "workstream_path": str(workstream),
        "phase": state.get("phase", "unknown"),
        "phase_status": state.get("phase_status", "unknown"),
        "next_action": state.get("next_action", "missing next_action"),
        "missing_artifacts": missing,
        "todo_counts": {name: todo_count(workstream / name) for name in REQUIRED if (workstream / name).is_file()},
        "run_dirs": run_dirs,
        "scripts": scripts,
        "validation_evidence": validation_evidence,
        "worktree_path": worktree,
        "blockers": blockers,
        "pending_user_confirmation": ["merge", "push", "worktree removal", "branch deletion"] if worktree else [],
    }


def markdown(plan: dict[str, Any]) -> str:
    validation = plan["validation_evidence"] or []
    validation_lines = [f"- {item['path']}: {'exists' if item['exists'] else 'missing'}" for item in validation] or ["- no validation evidence supplied"]
    closeout_lines = [
        "- Update RUNS.md with final run ledger and distilled updates outside `runs/`.",
        "- Update SCRIPT_REGISTRY.md with reusable project-local commands/scripts.",
        "- Update RESULTS.md and CLAIMS.md, preserving negative or inconclusive results.",
        "- Update REPRODUCIBILITY.md with rerun command, environment, data, seed, and known gaps.",
        "- Update portfolio RESEARCH.md / INDEX.md with status, evidence, and next priority.",
    ]
    if plan["worktree_path"]:
        closeout_lines.append("- Run prepare_worktree_closeout.py for report-before-merge; do not merge/push/delete until user confirms.")
    blockers = plan["blockers"] or ["none detected by control-plane inspection"]
    return f"""# Workstream Closeout Plan

- Generated at: {plan['generated_at']}
- Workstream: `{plan['slug']}`
- Path: `{plan['workstream_path']}`
- Phase / status: `{plan['phase']}` / `{plan['phase_status']}`
- Next action: {plan['next_action']}
- Worktree path: `{plan['worktree_path'] or 'none supplied'}`

## Evidence Inventory

- Run directories: {', '.join(plan['run_dirs']) or 'none found'}
- Script files: {', '.join(plan['scripts']) or 'none found'}
- Missing completion artifacts: {', '.join(plan['missing_artifacts']) or 'none'}

## Validation Evidence

{chr(10).join(validation_lines)}

## Required Distillation Updates

{chr(10).join(closeout_lines)}

## Blockers

{chr(10).join(f'- {item}' for item in blockers)}

## Confirmation Boundary

Merge, push, worktree removal, and branch deletion require explicit user confirmation after this report-before-merge plan.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a workstream completion handoff closeout plan.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("slug", help="Workstream slug.")
    parser.add_argument("--validation", action="append", default=[], help="Validation evidence path. Repeatable.")
    parser.add_argument("--worktree", help="Task worktree path if this workstream used one.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--write", action="store_true", help="Write .omx/ai-research/<slug>/CLOSEOUT.md instead of stdout.")
    parser.add_argument("--output", type=Path, help="Explicit output path.")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    plan = inspect_workstream(project_root, args.slug, args.validation, args.worktree)
    text = json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n" if args.json else markdown(plan)
    output = args.output
    if args.write and output is None:
        output = project_root / ".omx" / "ai-research" / args.slug / "CLOSEOUT.md"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Wrote workstream closeout plan: {output}")
    else:
        print(text, end="")
    return 0 if not plan["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
