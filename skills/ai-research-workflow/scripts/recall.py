#!/usr/bin/env python3
"""Recall experiments, workstreams, and decisions from a research workspace.

Script: recall.py.

Answer "what was that experiment for?" without archaeology. Walks the
`.ai-research-workflow/` portfolio and returns a compact, human-readable
index of what exists, what it was for, and where to look for more.

Outputs four sections in plain text:

1. Portfolio snapshot: project objective + active research questions.
2. Workstreams: every workstream with its subquestion, status, and the
   most recent claim state.
3. Recent runs: every run directory across workstreams, with the
   purpose.md headline (first non-heading, non-empty paragraph) so the
   reader can identify a run from its timestamped folder name alone.
4. Recent decisions: the last N entries from portfolio + per-workstream
   DECISIONS.md tables.

Filters:

- `--query TEXT` keeps only runs whose purpose.md contains TEXT (case
  insensitive). Useful for "what was the run about ablations?" or
  "show me everything related to seed 3".
- `--slug SLUG` restricts the run listing to one workstream.
- `--limit N` caps the run and decision lists (default 20).
- `--json` emits machine-readable JSON instead of the text report.

This is a framework guardrail: it only reads, never writes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class WorkstreamSnapshot:
    slug: str
    root: Path
    research_path: Path
    subquestion: str = ""
    status: str = ""
    latest_claim: str = ""
    runs: list["RunSnapshot"] = field(default_factory=list)


@dataclass
class RunSnapshot:
    workstream_slug: str
    run_dir: Path
    purpose_path: Path | None
    purpose_headline: str = ""
    has_purpose: bool = False


@dataclass
class DecisionSnapshot:
    source: str  # "portfolio" or workstream slug
    date: str
    decision: str
    context: str = ""
    rationale: str = ""


@dataclass
class RecallReport:
    portfolio_objective: str = ""
    active_questions: list[str] = field(default_factory=list)
    workstreams: list[WorkstreamSnapshot] = field(default_factory=list)
    runs: list[RunSnapshot] = field(default_factory=list)
    decisions: list[DecisionSnapshot] = field(default_factory=list)


# Heuristics for parsing structured markdown tables.

TABLE_ROW_RE = re.compile(r"^\|\s*(?P<a>[^|]*?)\s*\|\s*(?P<b>[^|]*?)\s*\|")
H1_RE = re.compile(r"^#\s+(?P<title>.+?)\s*$")
H2_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
BOLD_OBJECTIVE_RE = re.compile(
    r"##\s+(?:Overall\s+Research\s+Objective|Project\s+Snapshot)[^\n]*\n+(?P<body>[^#\n][^\n]*)",
    re.IGNORECASE,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def is_placeholder(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.upper() == "TODO":
        return True
    return False


def first_meaningful_paragraph(text: str) -> str:
    """Return the first non-heading, non-empty paragraph, trimmed."""
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            if lines:
                break
            continue
        if line.strip():
            lines.append(line.strip())
        if len(lines) >= 3:
            break
    return " ".join(lines)[:240]


def parse_research_subquestion(research_text: str) -> str:
    match = re.search(
        r"##\s+(?:Research\s+Question|Subquestion)[^\n]*\n+(?P<body>[^#\n][^\n]*)",
        research_text,
        re.IGNORECASE,
    )
    if match:
        return match.group("body").strip()[:240]
    return first_meaningful_paragraph(research_text)


def parse_state_status(workstream_root: Path) -> str:
    state = workstream_root / "STATE.json"
    if not state.is_file():
        return "(no STATE.json)"
    try:
        data = json.loads(read_text(state))
    except json.JSONDecodeError:
        return "(STATE.json invalid)"
    phase = data.get("phase", "")
    phase_status = data.get("phase_status", "")
    return f"{phase} / {phase_status}".strip(" /")


def parse_latest_claim(workstream_root: Path) -> str:
    claims_path = workstream_root / "CLAIMS.md"
    if not claims_path.is_file():
        return ""
    text = read_text(claims_path)
    # Take the first non-TODO, non-empty table cell with "claim" content.
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        first = cells[1] if len(cells) > 1 else cells[0]
        if first and first.upper() != "TODO" and not first.lower().startswith(("claim", "status", "id", "workstream")):
            return first[:160]
    return ""


def parse_portfolio_objective(context_text: str, research_text: str) -> str:
    for src in (context_text, research_text):
        if not src:
            continue
        match = BOLD_OBJECTIVE_RE.search(src)
        if match and not is_placeholder(match.group("body")):
            return match.group("body").strip()
    return "(unset)"


def parse_active_questions(context_text: str) -> list[str]:
    if not context_text:
        return []
    out: list[str] = []
    in_table = False
    for line in context_text.splitlines():
        if line.startswith("## Active Research Questions"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table:
            continue
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        if cells[0].lower() in {"id", "todo"}:
            continue
        question = cells[1]
        if question and question.upper() != "TODO":
            out.append(question)
    return out


def parse_decisions_table(text: str, source_label: str) -> list[DecisionSnapshot]:
    decisions: list[DecisionSnapshot] = []
    lines = text.splitlines()
    header_idx: int | None = None
    for idx, line in enumerate(lines):
        if line.startswith("| Date") and "Decision" in line:
            header_idx = idx
            break
    if header_idx is None:
        return decisions
    for line in lines[header_idx + 2 :]:
        if not line.startswith("|"):
            if decisions:
                break
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if any(cell.upper() == "TODO" for cell in cells[:3]):
            continue
        decisions.append(
            DecisionSnapshot(
                source=source_label,
                date=cells[0],
                decision=cells[2] if len(cells) > 2 else cells[0],
                context=cells[3] if len(cells) > 3 else "",
                rationale=cells[5] if len(cells) > 5 else "",
            )
        )
    return decisions


def collect_workstreams(ai_root: Path) -> list[WorkstreamSnapshot]:
    out: list[WorkstreamSnapshot] = []
    if not ai_root.is_dir():
        return out
    excluded = {"runs", "logs", "state", "worktrees", "scripts", "docs"}
    for entry in sorted(ai_root.iterdir(), key=lambda p: p.name.lower()):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in excluded:
            continue
        research_path = entry / "RESEARCH.md"
        subquestion = ""
        if research_path.is_file():
            subquestion = parse_research_subquestion(read_text(research_path))
        out.append(
            WorkstreamSnapshot(
                slug=entry.name,
                root=entry,
                research_path=research_path,
                subquestion=subquestion,
                status=parse_state_status(entry),
                latest_claim=parse_latest_claim(entry),
            )
        )
    return out


def collect_runs(ai_root: Path, *, slug: str | None, query: str | None) -> list[RunSnapshot]:
    out: list[RunSnapshot] = []
    if not ai_root.is_dir():
        return out
    workstreams = collect_workstreams(ai_root)
    for ws in workstreams:
        if slug and ws.slug != slug:
            continue
        runs_dir = ws.root / "runs"
        if not runs_dir.is_dir():
            continue
        for child in sorted(runs_dir.iterdir(), key=lambda p: p.name):
            if not child.is_dir():
                continue
            purpose = child / "purpose.md"
            headline = ""
            has_purpose = purpose.is_file()
            if has_purpose:
                text = read_text(purpose)
                headline = first_meaningful_paragraph(text)
                if query and query.lower() not in text.lower():
                    continue
            elif query:
                continue
            out.append(
                RunSnapshot(
                    workstream_slug=ws.slug,
                    run_dir=child,
                    purpose_path=purpose if has_purpose else None,
                    purpose_headline=headline,
                    has_purpose=has_purpose,
                )
            )
    return out


def collect_decisions(ai_root: Path, *, limit: int) -> list[DecisionSnapshot]:
    out: list[DecisionSnapshot] = []
    portfolio = ai_root / "DECISIONS.md"
    if portfolio.is_file():
        out.extend(parse_decisions_table(read_text(portfolio), "portfolio"))
    for ws in collect_workstreams(ai_root):
        per = ws.root / "DECISIONS.md"
        if per.is_file():
            out.extend(parse_decisions_table(read_text(per), ws.slug))
    # Newest decisions first; keep date strings as-is (sortable ISO when used).
    out.sort(key=lambda d: d.date, reverse=True)
    return out[:limit]


def build_report(
    project_root: Path,
    *,
    slug: str | None,
    query: str | None,
    limit: int,
) -> RecallReport:
    ai_root = project_root / ".ai-research-workflow"
    context_text = read_text(ai_root / "CONTEXT.md") if (ai_root / "CONTEXT.md").is_file() else ""
    research_text = (
        read_text(ai_root / "RESEARCH.md") if (ai_root / "RESEARCH.md").is_file() else ""
    )
    workstreams = collect_workstreams(ai_root)
    runs = collect_runs(ai_root, slug=slug, query=query)
    decisions = collect_decisions(ai_root, limit=limit)
    # Attach per-workstream runs (we already collected globally; assign by slug).
    by_slug: dict[str, list[RunSnapshot]] = {ws.slug: [] for ws in workstreams}
    for run in runs:
        if run.workstream_slug in by_slug:
            by_slug[run.workstream_slug].append(run)
    for ws in workstreams:
        ws.runs = by_slug.get(ws.slug, [])
    return RecallReport(
        portfolio_objective=parse_portfolio_objective(context_text, research_text),
        active_questions=parse_active_questions(context_text),
        workstreams=workstreams,
        runs=runs[:limit],
        decisions=decisions,
    )


def render_text(report: RecallReport) -> str:
    sections: list[str] = []
    sections.append("# Research Recall")
    sections.append("")
    sections.append("## Portfolio")
    sections.append(f"- Objective: {report.portfolio_objective}")
    if report.active_questions:
        sections.append("- Active questions:")
        for q in report.active_questions[:10]:
            sections.append(f"  - {q}")
    else:
        sections.append("- Active questions: (none recorded in CONTEXT.md)")
    sections.append("")
    sections.append(f"## Workstreams ({len(report.workstreams)})")
    if not report.workstreams:
        sections.append("- (none)")
    for ws in report.workstreams:
        sections.append(f"- {ws.slug}")
        sections.append(f"    status: {ws.status}")
        if ws.subquestion:
            sections.append(f"    subquestion: {ws.subquestion}")
        if ws.latest_claim:
            sections.append(f"    latest claim: {ws.latest_claim}")
    sections.append("")
    sections.append(f"## Recent Runs ({len(report.runs)})")
    if not report.runs:
        sections.append("- (no runs match)")
    for run in report.runs:
        marker = "✓" if run.has_purpose else "✗"
        sections.append(f"- {marker} {run.workstream_slug} :: {run.run_dir.name}")
        if run.purpose_headline:
            sections.append(f"    why: {run.purpose_headline}")
        else:
            sections.append("    why: (no purpose.md — run is anonymous)")
    sections.append("")
    sections.append(f"## Recent Decisions ({len(report.decisions)})")
    if not report.decisions:
        sections.append("- (none)")
    for d in report.decisions:
        sections.append(f"- [{d.source}] {d.date}: {d.decision}")
        if d.context:
            sections.append(f"    context: {d.context}")
        if d.rationale:
            sections.append(f"    rationale: {d.rationale}")
    return "\n".join(sections) + "\n"


def render_json(report: RecallReport) -> str:
    payload = {
        "portfolio_objective": report.portfolio_objective,
        "active_questions": report.active_questions,
        "workstreams": [
            {
                "slug": ws.slug,
                "status": ws.status,
                "subquestion": ws.subquestion,
                "latest_claim": ws.latest_claim,
                "run_count": len(ws.runs),
            }
            for ws in report.workstreams
        ],
        "runs": [
            {
                "workstream_slug": r.workstream_slug,
                "run_dir": str(r.run_dir),
                "has_purpose": r.has_purpose,
                "purpose_headline": r.purpose_headline,
            }
            for r in report.runs
        ],
        "decisions": [
            {
                "source": d.source,
                "date": d.date,
                "decision": d.decision,
                "context": d.context,
                "rationale": d.rationale,
            }
            for d in report.decisions
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recall experiments, workstreams, and decisions from .ai-research-workflow/."
    )
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--slug", help="Restrict run listing to one workstream slug.")
    parser.add_argument("--query", help="Filter runs whose purpose.md contains this text (case insensitive).")
    parser.add_argument("--limit", type=int, default=20, help="Cap runs and decisions in the report (default 20).")
    parser.add_argument("--json", dest="as_json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    if not (project_root / ".ai-research-workflow").is_dir():
        print(f"missing ai-research root: {project_root / '.ai-research-workflow'}", file=sys.stderr)
        return 2
    report = build_report(
        project_root,
        slug=args.slug,
        query=args.query,
        limit=max(1, args.limit),
    )
    if args.as_json:
        sys.stdout.write(render_json(report))
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())