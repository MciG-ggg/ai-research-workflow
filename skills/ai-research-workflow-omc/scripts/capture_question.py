#!/usr/bin/env python3
"""Capture a user research/workflow question and answer summary.

Script: capture_question.py.

This is a framework guardrail for optional Question Capture. It appends a
concise Q&A ledger entry to QUESTIONS.md when qa_capture is enabled. It does
not run experiments, collect metrics, plot results, publish docs, merge
branches, push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE = SCRIPT_DIR.parent / "assets" / "templates" / "QUESTIONS.md"
SENSITIVE_RE = re.compile(r"(api[_-]?key|secret|password|token|credential|private[_-]?key)", re.IGNORECASE)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_questions_file(path: Path, *, dry_run: bool) -> None:
    if path.exists() or dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.read_text(encoding="utf-8") if TEMPLATE.is_file() else "# Questions\n", encoding="utf-8")


def entry(args: argparse.Namespace) -> str:
    evidence = args.evidence or "none supplied"
    routed = args.routed_update or "none"
    follow = args.follow_up or "none"
    return f"""
## {utc_now()} — {args.scope}

- Workstream: {args.workstream or 'portfolio'}
- User question: {args.question}
- Answer summary: {args.answer_summary}
- Evidence / links: {evidence}
- Routed updates: {routed}
- Follow-up: {follow}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a distilled Q&A entry to .omc/ai-research QUESTIONS.md.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("--question", required=True, help="User question to record.")
    parser.add_argument("--answer-summary", required=True, help="Concise answer summary; answer the user before capture.")
    parser.add_argument("--workstream", help="Optional workstream slug; writes to that workstream QUESTIONS.md.")
    parser.add_argument("--scope", default="research", choices=["research", "workflow", "architecture", "experiment", "interpretation", "all"], help="Question scope.")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence/link/path to record. Repeatable.")
    parser.add_argument("--routed-update", action="append", default=[], help="Artifact updated because of this answer. Repeatable.")
    parser.add_argument("--follow-up", help="Optional follow-up action.")
    parser.add_argument("--allow-sensitive", action="store_true", help="Allow capture when text appears to contain secrets. Prefer not to use.")
    parser.add_argument("--dry-run", action="store_true", help="Print entry without writing.")
    args = parser.parse_args()

    combined = "\n".join([args.question, args.answer_summary, "\n".join(args.evidence), "\n".join(args.routed_update), args.follow_up or ""])
    if SENSITIVE_RE.search(combined) and not args.allow_sensitive:
        raise SystemExit("refusing to capture possible secret/credential text; redact it or pass --allow-sensitive intentionally")

    ai_root = args.project_root.resolve() / ".omc" / "ai-research"
    target = ai_root / args.workstream / "QUESTIONS.md" if args.workstream else ai_root / "QUESTIONS.md"
    text = entry(args)
    if args.dry_run:
        print(text, end="")
        return 0
    ensure_questions_file(target, dry_run=False)
    with target.open("a", encoding="utf-8") as fh:
        if target.stat().st_size and not target.read_text(encoding="utf-8").endswith("\n"):
            fh.write("\n")
        fh.write(text)
    print(f"Captured question: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
