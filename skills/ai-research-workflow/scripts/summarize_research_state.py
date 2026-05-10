#!/usr/bin/env python3
"""Summarize a downstream .omx/ai-research portfolio.

Script: summarize_research_state.py.

This is a read-only framework guardrail. It inspects research control-plane
artifacts and prints a portfolio/workstream status summary. It does not run
experiments, collect metrics, plot results, publish docs, merge branches, push
remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

CONTROL_FILES = [
    "STATE.json",
    "RESEARCH.md",
    "LITERATURE.md",
    "REPRODUCTION.md",
    "EXPERIMENT.md",
    "RUNS.md",
    "RESULTS.md",
    "CLAIMS.md",
    "REPRODUCIBILITY.md",
    "PAPER_DRAFT.md",
    "SCRIPT_REGISTRY.md",
]
EXCLUDED_DIRS = {"runs", "logs", "state", "worktrees", "scripts", "docs"}
VALID_WORKSTREAM_TYPES = {"experiment-campaign", "paper-reproduction"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def first_heading(text: str, default: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip() or default
    return default


def count_todos(text: str) -> int:
    return sum(1 for line in text.splitlines() if "TODO" in line)


def extract_markdown_links(text: str) -> list[str]:
    links: list[str] = []
    for match in re.finditer(r"`([^`]+)`|\(([^)]+)\)", text):
        token = (match.group(1) or match.group(2) or "").strip()
        if token and not token.startswith(("http://", "https://", "#")):
            links.append(token)
    return links[:20]


def load_state(workstream: Path) -> tuple[dict[str, Any], str | None]:
    state_path = workstream / "STATE.json"
    if not state_path.is_file():
        return {}, "missing STATE.json"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {}, f"invalid STATE.json: {exc}"
    if not isinstance(state, dict):
        return {}, "STATE.json is not an object"
    return state, None


def detect_workstream_type(workstream: Path, state: dict[str, Any]) -> str:
    value = state.get("workstream_type") if isinstance(state, dict) else None
    if value in VALID_WORKSTREAM_TYPES:
        return value
    if (workstream / "REPRODUCTION.md").is_file():
        return "paper-reproduction"
    return "unknown"


def find_workstreams(ai_root: Path) -> list[Path]:
    if not ai_root.is_dir():
        return []
    return sorted(
        path
        for path in ai_root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name not in EXCLUDED_DIRS
    )


def summarize_workstream(workstream: Path) -> dict[str, Any]:
    state, state_error = load_state(workstream)
    title = first_heading(read_text(workstream / "RESEARCH.md"), workstream.name)
    workstream_type = detect_workstream_type(workstream, state)
    missing = [
        name
        for name in CONTROL_FILES
        if not (workstream / name).is_file() and (name != "REPRODUCTION.md" or workstream_type == "paper-reproduction")
    ]
    todo_counts = {name: count_todos(read_text(workstream / name)) for name in CONTROL_FILES if (workstream / name).is_file()}
    run_dirs = sorted(child.name for child in (workstream / "runs").iterdir() if child.is_dir()) if (workstream / "runs").is_dir() else []
    script_files = sorted(child.name for child in (workstream / "scripts").iterdir() if child.is_file()) if (workstream / "scripts").is_dir() else []
    blockers = state.get("current_blockers", []) if isinstance(state.get("current_blockers", []), list) else []
    next_action = state.get("next_action") or "missing next_action"
    return {
        "slug": workstream.name,
        "title": title,
        "workstream_type": workstream_type,
        "phase": state.get("phase") or "unknown",
        "phase_status": state.get("phase_status") or "unknown",
        "next_action": next_action,
        "blockers": blockers,
        "state_error": state_error,
        "missing_artifacts": missing,
        "todo_counts": todo_counts,
        "run_count": len(run_dirs),
        "run_dirs": run_dirs[:10],
        "script_count": len(script_files),
        "script_files": script_files[:10],
        "active_artifacts": state.get("active_artifacts", []),
    }


def summarize(project_root: Path) -> dict[str, Any]:
    ai_root = project_root / ".omx" / "ai-research"
    if not ai_root.is_dir():
        return {"project_root": str(project_root), "ai_root": str(ai_root), "exists": False, "error": "missing ai-research root"}
    portfolio_research = read_text(ai_root / "RESEARCH.md")
    portfolio_index = read_text(ai_root / "INDEX.md")
    portfolio_papers = read_text(ai_root / "PAPERS.md")
    workstreams = [summarize_workstream(path) for path in find_workstreams(ai_root)]
    blockers = [f"{item['slug']}: {blocker}" for item in workstreams for blocker in item["blockers"]]
    missing_lifecycle = [item["slug"] for item in workstreams if item["state_error"] or "CLAIMS.md" in item["missing_artifacts"]]
    suggested_next: list[str] = []
    if missing_lifecycle:
        suggested_next.append("migrate lifecycle artifacts for: " + ", ".join(missing_lifecycle))
    incomplete = [item["slug"] for item in workstreams if any(item["todo_counts"].values())]
    if incomplete:
        suggested_next.append("replace TODO placeholders for: " + ", ".join(incomplete[:5]))
    if blockers:
        suggested_next.append("resolve current_blockers before making stronger claims")
    if not workstreams:
        suggested_next.append("run init_workstream.py only after the mandatory new-workstream gate completes")
    return {
        "project_root": str(project_root),
        "ai_root": str(ai_root),
        "exists": True,
        "portfolio_title": first_heading(portfolio_research, "Research Portfolio"),
        "portfolio_todos": count_todos(portfolio_research) + count_todos(portfolio_index),
        "paper_registry_exists": bool(portfolio_papers),
        "paper_registry_todos": count_todos(portfolio_papers),
        "portfolio_links": extract_markdown_links(portfolio_research + "\n" + portfolio_index + "\n" + portfolio_papers),
        "workstream_count": len(workstreams),
        "workstreams": workstreams,
        "blockers": blockers,
        "suggested_next_actions": suggested_next or ["continue the earliest failing artifact gate"],
    }


def markdown(summary: dict[str, Any]) -> str:
    if not summary.get("exists"):
        return f"# Research State Summary\n\nError: {summary.get('error')} at `{summary.get('ai_root')}`\n"
    rows = []
    for item in summary["workstreams"]:
        missing = ", ".join(item["missing_artifacts"]) or "none"
        blockers = "; ".join(str(x) for x in item["blockers"]) or "none"
        rows.append(
            f"| {item['slug']} | {item['workstream_type']} | {item['phase']} | {item['phase_status']} | {item['run_count']} | {item['script_count']} | {missing} | {blockers} | {item['next_action']} |"
        )
    if not rows:
        rows = ["| none | n/a | n/a | n/a | 0 | 0 | n/a | n/a | create a gated workstream |"]
    return f"""# Research State Summary

- Project root: `{summary['project_root']}`
- AI research root: `{summary['ai_root']}`
- Portfolio: {summary['portfolio_title']}
- Portfolio TODO count: {summary['portfolio_todos']}
- Paper registry: {'present' if summary.get('paper_registry_exists') else 'missing'} ({summary.get('paper_registry_todos', 0)} TODOs)
- Workstreams: {summary['workstream_count']}

## Workstream Status

| Slug | Type | Phase | Status | Runs | Scripts | Missing artifacts | Blockers | Next action |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
{chr(10).join(rows)}

## Suggested Next Actions

{chr(10).join(f'- {action}' for action in summary['suggested_next_actions'])}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize .omx/ai-research portfolio and workstream state.")
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--output", type=Path, help="Optional file to write the summary.")
    args = parser.parse_args()

    summary = summarize(args.project_root.resolve())
    text = json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n" if args.json else markdown(summary)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote research state summary: {args.output}")
    else:
        print(text, end="")
    return 0 if summary.get("exists") else 1


if __name__ == "__main__":
    raise SystemExit(main())
