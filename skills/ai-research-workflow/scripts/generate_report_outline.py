#!/usr/bin/env python3
"""Generate a paper/report outline from ai-research artifacts.

Script: generate_report_outline.py.

This framework guardrail drafts outline scaffolds only. It does not publish
research docs, run experiments, collect metrics, plot results, merge branches,
push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

KINDS = {
    "paper-outline": "PAPER_OUTLINE.md",
    "workshop-report": "WORKSHOP_REPORT.md",
    "internal-report": "INTERNAL_REPORT.md",
    "blog-summary": "BLOG_SUMMARY.md",
    "rebuttal-notes": "REBUTTAL_NOTES.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def first_heading(text: str, default: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line.removeprefix("# ").strip() or default
    return default


def outline(kind: str, workstream: Path) -> str:
    title = first_heading(read(workstream / "RESEARCH.md"), workstream.name)
    common = f"""- Generated at: {utc_now()}
- Workstream: `{workstream.name}`
- Source artifacts: `RESEARCH.md`, `LITERATURE.md`, `EXPERIMENT.md`, `RUNS.md`, `RESULTS.md`, `CLAIMS.md`, `REPRODUCIBILITY.md`
- Claim rule: every strong statement must map to `CLAIMS.md` evidence paths.
- Negative/inconclusive rule: preserve null or failed results as boundary evidence.
"""
    if kind == "paper-outline":
        sections = ["Abstract", "Introduction", "Related Work", "Method", "Experimental Setup", "Results", "Limitations", "Reproducibility", "Claim Ledger"]
    elif kind == "workshop-report":
        sections = ["One-line Contribution", "Motivation", "Method Sketch", "Preliminary Evidence", "Negative Results", "Open Risks", "Next Experiments"]
    elif kind == "internal-report":
        sections = ["Executive Summary", "Decision Context", "Evidence Table", "Engineering Changes", "Known Gaps", "Recommended Next Action"]
    elif kind == "blog-summary":
        sections = ["Problem", "What We Tried", "What Worked", "What Did Not Work", "Takeaways", "Reproduction Notes"]
    else:
        sections = ["Reviewer Concern", "Evidence Response", "Ablation / Baseline Needed", "Claim Downgrade", "Text Revision", "Risk"]
    body = "\n".join(f"## {section}\n\nTODO: fill from stable artifacts and evidence paths.\n" for section in sections)
    return f"# {title} — {kind}\n\n{common}\n{body}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a paper/report outline scaffold from workstream artifacts.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("slug", help="Workstream slug.")
    parser.add_argument("--kind", choices=sorted(KINDS), default="paper-outline", help="Outline kind to generate.")
    parser.add_argument("--write", action="store_true", help="Write the default report outline file under the workstream.")
    parser.add_argument("--output", type=Path, help="Explicit output path.")
    parser.add_argument("--force", action="store_true", help="Overwrite output if it already exists.")
    args = parser.parse_args()

    workstream = args.project_root.resolve() / ".ai-research-workflow" / args.slug
    if not workstream.is_dir():
        raise SystemExit(f"missing workstream: {workstream}")
    text = outline(args.kind, workstream)
    output = args.output
    if args.write and output is None:
        output = workstream / KINDS[args.kind]
    if output:
        if output.exists() and not args.force:
            raise SystemExit(f"output exists; use --force to overwrite: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Wrote report outline: {output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
