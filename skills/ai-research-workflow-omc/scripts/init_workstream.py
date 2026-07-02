#!/usr/bin/env python3
"""Initialize a gated downstream ai-research workstream.

Script: init_workstream.py.

Success message includes: Workstream initialized.

This is a deterministic framework guardrail. It scaffolds control-plane
artifacts only after explicit gate evidence is supplied. It does not run
experiments, collect metrics, plot results, publish research docs, merge
branches, push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "assets" / "templates"
WORKSTREAM_TEMPLATES = {
    "STATE.json": "STATE.json",
    "RESEARCH.md": "workstream-RESEARCH.md",
    "LITERATURE.md": "LITERATURE.md",
    "EXPERIMENT.md": "EXPERIMENT.md",
    "RUNS.md": "RUNS.md",
    "RESULTS.md": "RESULTS.md",
    "CLAIMS.md": "CLAIMS.md",
    "REPRODUCIBILITY.md": "REPRODUCIBILITY.md",
    "PAPER_DRAFT.md": "PAPER_DRAFT.md",
    "SCRIPT_REGISTRY.md": "SCRIPT_REGISTRY.md",
    # DECISIONS.md is always-on per workstream: 1-2 lines per decision,
    # scoped to this workstream's lifetime and decisions.
    "DECISIONS.md": "DECISIONS.md",
}
PAPER_REPRODUCTION_TEMPLATES = {
    "REPRODUCTION.md": "REPRODUCTION.md",
}
VALID_WORKSTREAM_TYPES = {"experiment-campaign", "paper-reproduction"}
VALID_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,80}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_slug(slug: str) -> str:
    normalized = slug.strip().lower().replace(" ", "-")
    if not VALID_SLUG_RE.match(normalized):
        raise SystemExit(
            "invalid slug; use 2-81 chars of lowercase letters, digits, hyphen, or underscore, starting with alnum"
        )
    return normalized


def markdown_cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def index_has_slug(index_text: str, slug: str) -> bool:
    slug_pattern = re.compile(rf"^\|\s*{re.escape(slug)}\s*\|", re.IGNORECASE)
    return any(slug_pattern.search(line.strip()) for line in index_text.splitlines())


def insert_workstream_index_row(index_text: str, row: str) -> str:
    lines = index_text.splitlines()
    for idx, line in enumerate(lines):
        if "| Slug | Status | Subquestion" not in line:
            continue
        insert_at = idx + 2 if idx + 1 < len(lines) else idx + 1
        while insert_at < len(lines) and lines[insert_at].strip():
            if lines[insert_at].strip().startswith("| TODO |"):
                lines[insert_at] = row
                return "\n".join(lines) + "\n"
            insert_at += 1
        lines.insert(insert_at, row)
        return "\n".join(lines) + "\n"
    text = index_text.rstrip()
    return f"{text}\n\n{row}\n" if text else f"{row}\n"


def copy_template(src_name: str, dest: Path, *, force: bool, dry_run: bool, actions: list[str]) -> None:
    src = TEMPLATE_DIR / src_name
    if dest.exists() and not force:
        actions.append(f"skip existing {dest}")
        return
    actions.append(f"write {dest} from {src_name}")
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def write_state(path: Path, args: argparse.Namespace, *, force: bool, dry_run: bool, actions: list[str]) -> None:
    if path.exists() and not force:
        actions.append(f"skip existing {path}")
        return
    state = {
        "schema_version": 1,
        "workstream_slug": args.slug,
        "workstream_type": args.workstream_type,
        "allowed_workstream_types": sorted(VALID_WORKSTREAM_TYPES),
        "phase": args.phase,
        "phase_status": "initialized",
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
        "owner": args.owner,
        "active_artifacts": [
            "RESEARCH.md",
            *(['REPRODUCTION.md'] if args.workstream_type == "paper-reproduction" else []),
            "EXPERIMENT.md",
            "RUNS.md",
            "RESULTS.md",
            "CLAIMS.md",
        ],
        "gate_evidence": {
            "deep_interview_autoresearch": args.deep_interview,
            "ralplan_prd": args.ralplan_prd,
            "ralplan_test_spec": args.ralplan_test_spec,
            "autoresearch_result": args.autoresearch_result,
        },
        "current_blockers": [],
        "next_action": args.next_action,
        "confirmation_required_before": [
            "promoting final topic",
            "creating new workstream",
            "merge",
            "push",
            "worktree removal",
            "branch deletion",
        ],
    }
    actions.append(f"write {path} with gate evidence and phase={args.phase}")
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def patch_research(path: Path, args: argparse.Namespace, *, dry_run: bool, actions: list[str]) -> None:
    actions.append(f"patch {path} with title/question/gate evidence")
    if dry_run or not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    replacements = {
        "# Workstream Research Spec": f"# {args.title}",
        "TODO\n\n## Research Question": f"{args.title}\n\n## Research Question",
        "TODO: experiment-campaign | paper-reproduction": args.workstream_type,
        "## Research Question\n\nTODO": f"## Research Question\n\n{args.question}",
        "- Deep-interview autoresearch handoff: TODO": f"- Deep-interview autoresearch handoff: {args.deep_interview}",
        "- Ralplan PRD/test spec: TODO": f"- Ralplan PRD/test spec: {args.ralplan_prd}; {args.ralplan_test_spec}",
        "- Autoresearch state/completion artifact: TODO": f"- Autoresearch state/completion artifact: {args.autoresearch_result}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def ensure_portfolio(ai_root: Path, *, dry_run: bool, actions: list[str]) -> None:
    if not dry_run:
        ai_root.mkdir(parents=True, exist_ok=True)
    for name, template in (("RESEARCH.md", "portfolio-RESEARCH.md"), ("INDEX.md", "portfolio-INDEX.md")):
        dest = ai_root / name
        if not dest.exists():
            copy_template(template, dest, force=False, dry_run=dry_run, actions=actions)


def append_index(ai_root: Path, args: argparse.Namespace, *, dry_run: bool, actions: list[str]) -> None:
    index = ai_root / "INDEX.md"
    evidence = (
        f"deep: {args.deep_interview}; ralplan: {args.ralplan_prd}, {args.ralplan_test_spec}; "
        f"autoresearch: {args.autoresearch_result}"
    )
    artifact_links = [f"{args.slug}/RESEARCH.md", f"{args.slug}/EXPERIMENT.md", f"{args.slug}/CLAIMS.md"]
    if args.workstream_type == "paper-reproduction":
        artifact_links.insert(1, f"{args.slug}/REPRODUCTION.md")
    row = (
        f"| {args.slug} | initialized | {markdown_cell(args.question)} | {args.workstream_type} workstream for current objective | "
        f"{', '.join(artifact_links)} | pending runs | "
        f"{markdown_cell(evidence)} | {markdown_cell(args.next_action)} |"
    )
    text = index.read_text(encoding="utf-8") if index.exists() else "# Research Workstream Index\n\n"
    if index_has_slug(text, args.slug) and not args.force_index_row:
        actions.append(f"skip INDEX append; slug already present: {args.slug}")
        return
    actions.append(f"append {args.slug} row to {index}")
    if dry_run:
        return
    index.write_text(insert_workstream_index_row(text, row), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a gated .ai-research-workflow/<slug> workstream.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("slug", help="Workstream slug, lowercase hyphen/underscore style.")
    parser.add_argument("--title", required=True, help="Workstream title.")
    parser.add_argument("--question", required=True, help="Research question or subquestion.")
    parser.add_argument("--deep-interview", required=True, help="Path or identifier for deep-interview autoresearch handoff evidence.")
    parser.add_argument("--ralplan-prd", required=True, help="Path or identifier for ralplan PRD evidence.")
    parser.add_argument("--ralplan-test-spec", required=True, help="Path or identifier for ralplan test spec evidence.")
    parser.add_argument("--autoresearch-result", required=True, help="Path or identifier for autoresearch result/completion evidence.")
    parser.add_argument("--phase", default="intake", choices=["intake", "literature", "experiment-design", "implementation"])
    parser.add_argument("--owner", default="agent", help="Owner label for STATE.json.")
    parser.add_argument("--next-action", default="complete intake artifacts", help="Next action for STATE.json and INDEX.md.")
    parser.add_argument(
        "--workstream-type",
        choices=sorted(VALID_WORKSTREAM_TYPES),
        default="experiment-campaign",
        help="Workstream intent type. Use paper-reproduction for one selected paper; experiment-campaign for hypothesis/ablation/benchmark experiments.",
    )
    parser.add_argument(
        "--paper-reproduction",
        action="store_true",
        help="Compatibility alias for --workstream-type paper-reproduction; also scaffolds REPRODUCTION.md.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing workstream files.")
    parser.add_argument("--force-index-row", action="store_true", help="Append INDEX row even if slug already appears.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    args = parser.parse_args()

    args.slug = validate_slug(args.slug)
    if args.paper_reproduction:
        args.workstream_type = "paper-reproduction"
    project_root = args.project_root.resolve()
    ai_root = project_root / ".ai-research-workflow"
    workstream = ai_root / args.slug
    actions: list[str] = []

    if workstream.exists() and any(workstream.iterdir()) and not args.force:
        raise SystemExit(f"workstream already exists and is non-empty; use --force to overwrite files: {workstream}")

    ensure_portfolio(ai_root, dry_run=args.dry_run, actions=actions)
    for dest_name, template_name in WORKSTREAM_TEMPLATES.items():
        dest = workstream / dest_name
        if dest_name == "STATE.json":
            write_state(dest, args, force=args.force, dry_run=args.dry_run, actions=actions)
        else:
            copy_template(template_name, dest, force=args.force, dry_run=args.dry_run, actions=actions)
    if args.workstream_type == "paper-reproduction":
        for dest_name, template_name in PAPER_REPRODUCTION_TEMPLATES.items():
            copy_template(template_name, workstream / dest_name, force=args.force, dry_run=args.dry_run, actions=actions)
    for dirname in ("runs", "scripts"):
        actions.append(f"ensure directory {workstream / dirname}")
        if not args.dry_run:
            (workstream / dirname).mkdir(parents=True, exist_ok=True)
    patch_research(workstream / "RESEARCH.md", args, dry_run=args.dry_run, actions=actions)
    append_index(ai_root, args, dry_run=args.dry_run, actions=actions)

    for action in actions:
        print(action)
    print(f"Workstream {'dry-run complete' if args.dry_run else 'initialized'}: {workstream}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
