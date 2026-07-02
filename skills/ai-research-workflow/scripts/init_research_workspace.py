#!/usr/bin/env python3
"""Initialize a downstream .ai-research-workflow portfolio workspace.

Script: init_research_workspace.py.

This is a deterministic framework guardrail. It creates research-control-plane
scaffolds only. It does not create a new workstream, run experiments, collect
metrics, publish docs, merge branches, or delete worktrees.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

VALID_WORKFLOW_PRESET = {"conservative", "guided", "autonomous"}
VALID_IDEA_SCOUTING = {"auto", "off", "on"}
VALID_COMPLETION_HANDOFF = {"auto", "off"}
VALID_WORKTREE_CLOSEOUT = {"off", "report-before-merge"}
VALID_FEEDBACK_MEMORY = {"off", "lite", "full"}
VALID_QA_CAPTURE = {"off", "research", "all"}
VALID_GROWTH_REVIEW = {"off", "milestone", "always"}

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.parent / "assets" / "templates"


def copy_template(template_name: str, dest: Path, *, force: bool, dry_run: bool, actions: list[str]) -> None:
    src = TEMPLATE_DIR / template_name
    if dest.exists() and not force:
        actions.append(f"skip existing {dest}")
        return
    actions.append(f"write {dest} from {template_name}")
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def write_config(dest: Path, args: argparse.Namespace, *, force: bool, dry_run: bool, actions: list[str]) -> None:
    if dest.exists() and not force:
        actions.append(f"skip existing {dest}")
        return
    text = f"""# AI Research Workflow Config

```yaml
schema_version: 1
workflow_preset: {args.preset}
idea_scouting: {args.idea_scouting}
completion_handoff: {args.completion_handoff}
worktree_closeout: {args.worktree_closeout}
feedback_memory: {args.feedback_memory}
qa_capture: {args.qa_capture}
growth_review: {args.growth_review}
```

Allowed values and mode descriptions are documented in the skill template `assets/templates/CONFIG.md`.
"""
    actions.append(f"write {dest} from selected preset and overrides")
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize .ai-research-workflow portfolio files.")
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--preset", choices=sorted(VALID_WORKFLOW_PRESET), default="guided")
    parser.add_argument("--idea-scouting", choices=sorted(VALID_IDEA_SCOUTING), default="auto")
    parser.add_argument("--completion-handoff", choices=sorted(VALID_COMPLETION_HANDOFF), default="auto")
    parser.add_argument("--worktree-closeout", choices=sorted(VALID_WORKTREE_CLOSEOUT), default="report-before-merge")
    parser.add_argument("--feedback-memory", choices=sorted(VALID_FEEDBACK_MEMORY), default="off")
    parser.add_argument("--qa-capture", choices=sorted(VALID_QA_CAPTURE), default="off")
    parser.add_argument("--growth-review", choices=sorted(VALID_GROWTH_REVIEW), default="off")
    parser.add_argument("--force", action="store_true", help="Overwrite existing portfolio/config files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without creating files.")
    args = parser.parse_args()

    root = args.project_root.resolve()
    ai_root = root / ".ai-research-workflow"
    actions: list[str] = []
    if not args.dry_run:
        ai_root.mkdir(parents=True, exist_ok=True)
    else:
        actions.append(f"ensure directory {ai_root}")

    write_config(ai_root / "CONFIG.md", args, force=args.force, dry_run=args.dry_run, actions=actions)
    copy_template("portfolio-RESEARCH.md", ai_root / "RESEARCH.md", force=args.force, dry_run=args.dry_run, actions=actions)
    copy_template("portfolio-INDEX.md", ai_root / "INDEX.md", force=args.force, dry_run=args.dry_run, actions=actions)
    # CONTEXT.md is always-on: project-level ubiquitous language so the
    # agent does not reinvent terminology every session.
    copy_template("CONTEXT.md", ai_root / "CONTEXT.md", force=args.force, dry_run=args.dry_run, actions=actions)
    # DECISIONS.md is always-on at portfolio level: 1-2 lines per decision,
    # low overhead, prevents "why did we do it this way" archaeology later.
    copy_template("DECISIONS.md", ai_root / "DECISIONS.md", force=args.force, dry_run=args.dry_run, actions=actions)

    if args.idea_scouting == "on":
        copy_template("IDEA_SCOUTING.md", ai_root / "IDEA_SCOUTING.md", force=args.force, dry_run=args.dry_run, actions=actions)
    if args.feedback_memory in {"lite", "full"}:
        for name in ("LEARNINGS.md", "ISSUES.md"):
            copy_template(name, ai_root / name, force=args.force, dry_run=args.dry_run, actions=actions)
    if args.qa_capture in {"research", "all"}:
        copy_template("QUESTIONS.md", ai_root / "QUESTIONS.md", force=args.force, dry_run=args.dry_run, actions=actions)
    if args.growth_review in {"milestone", "always"}:
        copy_template("SKILL_GROWTH.md", ai_root / "SKILL_GROWTH.md", force=args.force, dry_run=args.dry_run, actions=actions)

    for action in actions:
        print(action)
    print(f"Research portfolio workspace {'dry-run complete' if args.dry_run else 'initialized'}: {ai_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
