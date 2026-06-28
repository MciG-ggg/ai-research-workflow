#!/usr/bin/env python3
"""Update a downstream ai-research workstream STATE.json file.

Script: update_workstream_state.py.

This is a deterministic framework guardrail for phase state only. It does not
run experiments, collect metrics, plot results, publish research docs, merge
branches, push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

VALID_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,80}$")
VALID_PHASES = [
    "idea-scouting",
    "intake",
    "literature",
    "experiment-design",
    "implementation",
    "running",
    "completion-handoff",
    "report-before-merge",
    "reproducibility-review",
    "paper-draft",
    "archived",
]


def validate_slug(slug: str) -> str:
    normalized = slug.strip().lower().replace(" ", "-")
    if not VALID_SLUG_RE.match(normalized):
        raise SystemExit(
            "invalid slug; use 2-81 chars of lowercase letters, digits, hyphen, or underscore, starting with alnum"
        )
    return normalized


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_state(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise SystemExit(f"missing STATE.json: {path}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid STATE.json: {path}: {exc}") from exc
    if not isinstance(state, dict):
        raise SystemExit(f"STATE.json must contain an object: {path}")
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description="Update .ai-research-workflow/<slug>/STATE.json.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("slug", help="Workstream slug.")
    parser.add_argument("--phase", choices=VALID_PHASES, help="New workflow phase.")
    parser.add_argument("--phase-status", help="New phase status, e.g. draft, in-progress, blocked, complete.")
    parser.add_argument("--next-action", help="Next action text.")
    parser.add_argument("--owner", help="Owner label.")
    parser.add_argument("--blocker", action="append", default=[], help="Replace blockers with this blocker. Repeatable.")
    parser.add_argument("--clear-blockers", action="store_true", help="Clear current_blockers.")
    parser.add_argument("--active-artifact", action="append", default=[], help="Replace active_artifacts with these entries. Repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Print updated JSON without writing.")
    args = parser.parse_args()
    args.slug = validate_slug(args.slug)

    state_path = args.project_root.resolve() / ".ai-research-workflow" / args.slug / "STATE.json"
    state = load_state(state_path)
    before_phase = state.get("phase")

    if args.phase:
        state["phase"] = args.phase
    if args.phase_status:
        state["phase_status"] = args.phase_status
    if args.next_action:
        state["next_action"] = args.next_action
    if args.owner:
        state["owner"] = args.owner
    if args.clear_blockers:
        state["current_blockers"] = []
    if args.blocker:
        state["current_blockers"] = args.blocker
    if args.active_artifact:
        state["active_artifacts"] = args.active_artifact
    state.setdefault("schema_version", 1)
    state["workstream_slug"] = args.slug
    state["last_updated"] = utc_now()

    output = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    if args.dry_run:
        print(output, end="")
    else:
        state_path.write_text(output, encoding="utf-8")
        print(f"Updated {state_path}: phase {before_phase!r} -> {state.get('phase')!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
