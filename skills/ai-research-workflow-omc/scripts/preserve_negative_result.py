#!/usr/bin/env python3
"""Preserve a negative or inconclusive research result in stable artifacts.

Script: preserve_negative_result.py.

This framework guardrail appends distilled negative/inconclusive evidence to
RESULTS.md and CLAIMS.md. It does not run experiments, collect metrics, plot
results, publish docs, merge branches, push remotes, remove worktrees, or delete
branches.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_file(path: Path, heading: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {heading}\n", encoding="utf-8")


def sanitize_cell(value: str) -> str:
    return value.replace("\n", " ").replace("|", "\\|")


def result_block(args: argparse.Namespace) -> str:
    return f"""
## Preserved Negative / Inconclusive Result — {utc_now()}

| Result | Evidence path | Failure category | Interpretation | Preserved claim update |
| --- | --- | --- | --- | --- |
| {sanitize_cell(args.finding)} | {sanitize_cell(args.evidence)} | {sanitize_cell(args.category)} | {sanitize_cell(args.interpretation)} | {sanitize_cell(args.claim_update)} |

- Likely cause: {args.cause}
- Scientific value: {args.scientific_value}
- Follow-up / stop condition: {args.follow_up}
"""


def claim_block(args: argparse.Namespace) -> str:
    return f"""
## Negative or Inconclusive Results Update — {utc_now()}

| Finding | Evidence path | Likely cause | Scientific value | Follow-up / stop condition |
| --- | --- | --- | --- | --- |
| {sanitize_cell(args.finding)} | {sanitize_cell(args.evidence)} | {sanitize_cell(args.cause)} | {sanitize_cell(args.scientific_value)} | {sanitize_cell(args.follow_up)} |

## Retired or Downgraded Claims Update — {utc_now()}

| Claim ID | Previous wording | New wording/status | Reason | Evidence |
| --- | --- | --- | --- | --- |
| {sanitize_cell(args.claim_id)} | {sanitize_cell(args.previous_claim)} | {sanitize_cell(args.claim_update)} | negative or inconclusive evidence preserved | {sanitize_cell(args.evidence)} |
"""


def append(path: Path, text: str, *, dry_run: bool) -> None:
    if dry_run:
        print(f"--- {path} ---")
        print(text, end="")
        return
    with path.open("a", encoding="utf-8") as fh:
        if path.stat().st_size and not path.read_text(encoding="utf-8").endswith("\n"):
            fh.write("\n")
        fh.write(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append negative/inconclusive result evidence to RESULTS.md and CLAIMS.md.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("slug", help="Workstream slug.")
    parser.add_argument("--finding", required=True, help="Negative or inconclusive finding.")
    parser.add_argument("--evidence", required=True, help="Evidence path for the finding.")
    parser.add_argument("--category", default="negative / inconclusive", help="Failure/result category.")
    parser.add_argument("--cause", default="unknown", help="Likely cause or failure attribution.")
    parser.add_argument("--interpretation", required=True, help="Bounded interpretation of the finding.")
    parser.add_argument("--scientific-value", default="preserves a boundary condition or failed assumption", help="Why this result is useful.")
    parser.add_argument("--claim-id", default="TBD", help="Claim ID affected by the result.")
    parser.add_argument("--previous-claim", default="TBD", help="Previous claim wording to retire/downgrade.")
    parser.add_argument("--claim-update", required=True, help="New allowed wording/status after the result.")
    parser.add_argument("--follow-up", default="stop or redesign before claiming improvement", help="Follow-up or stop condition.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned updates without writing.")
    args = parser.parse_args()

    workstream = args.project_root.resolve() / ".ai-research-workflow" / args.slug
    if not workstream.is_dir():
        raise SystemExit(f"missing workstream: {workstream}")
    results = workstream / "RESULTS.md"
    claims = workstream / "CLAIMS.md"
    if not args.dry_run:
        ensure_file(results, "Results")
        ensure_file(claims, "Claims Ledger")
    append(results, result_block(args), dry_run=args.dry_run)
    append(claims, claim_block(args), dry_run=args.dry_run)
    if not args.dry_run:
        print(f"Preserved negative/inconclusive result: {results}, {claims}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
