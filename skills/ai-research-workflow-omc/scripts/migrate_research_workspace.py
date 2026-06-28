#!/usr/bin/env python3
"""Safely migrate legacy .ai-research-workflow workspaces to current guardrails.

Script: migrate_research_workspace.py.

This is maintenance-only framework tooling. It creates missing control-plane
artifacts and directories only when --write is supplied. It does not overwrite
by default and does not run experiments, collect metrics, plot results, publish
research docs, merge branches, push remotes, remove worktrees, or delete
branches.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "assets" / "templates"
WORKSTREAM_TEMPLATES = {
    "RESEARCH.md": "workstream-RESEARCH.md",
    "LITERATURE.md": "LITERATURE.md",
    "EXPERIMENT.md": "EXPERIMENT.md",
    "RUNS.md": "RUNS.md",
    "RESULTS.md": "RESULTS.md",
    "CLAIMS.md": "CLAIMS.md",
    "REPRODUCIBILITY.md": "REPRODUCIBILITY.md",
    "PAPER_DRAFT.md": "PAPER_DRAFT.md",
    "SCRIPT_REGISTRY.md": "SCRIPT_REGISTRY.md",
}
PORTFOLIO_TEMPLATES = {
    "CONFIG.md": "CONFIG.md",
    "RESEARCH.md": "portfolio-RESEARCH.md",
    "INDEX.md": "portfolio-INDEX.md",
}
EXCLUDED_DIRS = {"runs", "logs", "state", "worktrees", "scripts", "docs"}
VALID_WORKSTREAM_TYPES = {"experiment-campaign", "paper-reproduction"}
DEFAULT_WORKSTREAM_TYPE = "experiment-campaign"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def template_text(name: str) -> str:
    path = TEMPLATE_DIR / name
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def find_workstreams(ai_root: Path) -> list[Path]:
    if not ai_root.is_dir():
        return []
    return sorted(path for path in ai_root.iterdir() if path.is_dir() and not path.name.startswith(".") and path.name not in EXCLUDED_DIRS)


def record(actions: list[dict[str, Any]], action: str, path: Path, status: str, detail: str = "") -> None:
    actions.append({"action": action, "path": str(path), "status": status, "detail": detail})


def write_file(path: Path, text: str, actions: list[dict[str, Any]], *, write: bool, force: bool, detail: str) -> None:
    if path.exists() and not force:
        record(actions, "write_file", path, "skip-existing", detail)
        return
    record(actions, "write_file", path, "would-write" if not write else "written", detail)
    if not write:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_template(dest: Path, template_name: str, actions: list[dict[str, Any]], *, write: bool, force: bool) -> None:
    src = TEMPLATE_DIR / template_name
    if not src.is_file():
        record(actions, "copy_template", dest, "missing-template", template_name)
        return
    if dest.exists() and not force:
        record(actions, "copy_template", dest, "skip-existing", template_name)
        return
    record(actions, "copy_template", dest, "would-copy" if not write else "copied", template_name)
    if not write:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def ensure_dir(path: Path, actions: list[dict[str, Any]], *, write: bool) -> None:
    if path.is_dir():
        record(actions, "ensure_dir", path, "exists")
        return
    record(actions, "ensure_dir", path, "would-create" if not write else "created")
    if write:
        path.mkdir(parents=True, exist_ok=True)


def infer_workstream_type(workstream: Path) -> str:
    return "paper-reproduction" if (workstream / "REPRODUCTION.md").is_file() else DEFAULT_WORKSTREAM_TYPE


def state_json(slug: str, workstream_type: str = DEFAULT_WORKSTREAM_TYPE) -> str:
    state = {
        "schema_version": 1,
        "workstream_slug": slug,
        "workstream_type": workstream_type,
        "allowed_workstream_types": sorted(VALID_WORKSTREAM_TYPES),
        "phase": "intake",
        "phase_status": "legacy-migrated",
        "allowed_phases": [
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
        ],
        "last_updated": utc_now(),
        "owner": "legacy migration",
        "active_artifacts": ["RESEARCH.md", "EXPERIMENT.md", "RUNS.md", "RESULTS.md", "CLAIMS.md"],
        "gate_evidence": {
            "deep_interview_autoresearch": "legacy migration: unknown; complete before new claims",
            "ralplan_prd": "legacy migration: unknown; complete before implementation changes",
            "ralplan_test_spec": "legacy migration: unknown; complete before implementation changes",
            "autoresearch_result": "legacy migration: unknown; complete before experiment execution",
        },
        "current_blockers": ["legacy migration requires gate evidence review before stronger claims"],
        "next_action": "review migrated artifacts, fill TODOs, and attach gate evidence",
        "confirmation_required_before": [
            "creating new workstream",
            "promoting final topic",
            "merge",
            "push",
            "worktree removal",
            "branch deletion",
        ],
    }
    return json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def ensure_state(path: Path, workstream: Path, actions: list[dict[str, Any]], *, write: bool, force: bool) -> None:
    inferred_type = infer_workstream_type(workstream)
    if force or not path.exists():
        write_file(path, state_json(workstream.name, inferred_type), actions, write=write, force=force, detail="legacy state scaffold")
        return

    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        record(actions, "patch_state", path, "skip-invalid-json", str(exc))
        return
    if not isinstance(state, dict):
        record(actions, "patch_state", path, "skip-non-object", "STATE.json root is not an object")
        return

    changed = False
    if state.get("workstream_type") not in VALID_WORKSTREAM_TYPES:
        state["workstream_type"] = inferred_type
        changed = True
    if state.get("allowed_workstream_types") != sorted(VALID_WORKSTREAM_TYPES):
        state["allowed_workstream_types"] = sorted(VALID_WORKSTREAM_TYPES)
        changed = True
    if not changed:
        record(actions, "patch_state", path, "already-current", "workstream_type present")
        return

    record(actions, "patch_state", path, "would-patch" if not write else "patched", "add workstream_type metadata")
    if write:
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def migrate(project_root: Path, *, write: bool, force: bool, include_optional: bool) -> dict[str, Any]:
    ai_root = project_root / ".ai-research-workflow"
    actions: list[dict[str, Any]] = []
    ensure_dir(ai_root, actions, write=write)
    for dest_name, src_name in PORTFOLIO_TEMPLATES.items():
        copy_template(ai_root / dest_name, src_name, actions, write=write, force=force)

    workstreams = find_workstreams(ai_root)
    for workstream in workstreams:
        for dest_name, src_name in WORKSTREAM_TEMPLATES.items():
            copy_template(workstream / dest_name, src_name, actions, write=write, force=force)
        ensure_state(workstream / "STATE.json", workstream, actions, write=write, force=force)
        ensure_dir(workstream / "runs", actions, write=write)
        ensure_dir(workstream / "scripts", actions, write=write)
        if include_optional:
            for name in ("QUESTIONS.md", "NOTES.md", "DESIGN.md", "REVIEW.md", "CLOSEOUT.md", "PAPER_OUTLINE.md"):
                copy_template(workstream / name, name, actions, write=write, force=force)

    return {
        "project_root": str(project_root),
        "ai_root": str(ai_root),
        "mode": "write" if write else "dry-run",
        "force": force,
        "workstream_count": len(workstreams),
        "actions": actions,
    }


def markdown(result: dict[str, Any]) -> str:
    rows = [f"| {a['status']} | {a['action']} | `{a['path']}` | {a.get('detail') or ''} |" for a in result["actions"]]
    return f"""# AI Research Workspace Migration {'Plan' if result['mode'] == 'dry-run' else 'Report'}

- Project root: `{result['project_root']}`
- AI research root: `{result['ai_root']}`
- Mode: `{result['mode']}`
- Force overwrite: `{result['force']}`
- Workstreams detected: {result['workstream_count']}

| Status | Action | Path | Detail |
| --- | --- | --- | --- |
{chr(10).join(rows) if rows else '| none | none | n/a | no actions |'}

Default migration is dry-run. Rerun with `--write` to create only missing control-plane files; use `--force` only when intentionally replacing existing scaffolds.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate legacy .ai-research-workflow control-plane workspaces safely.")
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--write", action="store_true", help="Apply the migration. Default is dry-run.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing control-plane files. Default: never overwrite.")
    parser.add_argument("--include-optional", action="store_true", help="Also scaffold optional feedback/review/closeout files.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    args = parser.parse_args()

    result = migrate(args.project_root.resolve(), write=args.write, force=args.force, include_optional=args.include_optional)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
