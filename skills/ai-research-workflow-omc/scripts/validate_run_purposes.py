#!/usr/bin/env python3
"""Validate that every run directory has a purpose.md.

Script: validate_run_purposes.py.

Framework guardrail. Walks every `.ai-research-workflow/<slug>/runs/`
subdirectory and checks for a `purpose.md` describing why the run was
launched. This is the "why was this run even started" hook that lets
the agent (or future-you) recover intent from a directory named like
`20260619_205204_001_experiment_design` instead of guessing.

This is a soft gate by default: missing or stub purpose.md is a
warning. Pass `--strict` to make it an error. The validator is
deliberately separate from `validate_research_workspace.py` because
the runs/ directories are produced by the project-local execution
loop, not the workstream scaffolding, and we want the guardrail to
run on every completion handoff rather than block workstream
creation.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


# Terms that, if missing from a purpose.md, indicate the file is still a
# stub. Same heuristic used by validate_research_workspace.
REQUIRED_PURPOSE_TERMS = (
    "hypothesis being tested",
    "what \"success\" looks like",
    "linkage",
)


@dataclass
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def unresolved_todo_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if "TODO" in line]


def is_stub_purpose(text: str) -> bool:
    lowered = text.lower()
    return any(term not in lowered for term in REQUIRED_PURPOSE_TERMS)


def find_workstream_runs(ai_root: Path) -> list[Path]:
    runs: list[Path] = []
    if not ai_root.is_dir():
        return runs
    for entry in ai_root.iterdir():
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        runs_dir = entry / "runs"
        if not runs_dir.is_dir():
            continue
        for child in runs_dir.iterdir():
            if child.is_dir():
                runs.append(child)
    return sorted(runs)


def validate_run(run_dir: Path, *, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    purpose = run_dir / "purpose.md"
    if not purpose.is_file():
        level = "error" if strict else "warning"
        findings.append(
            Finding(
                level,
                f"{run_dir} missing purpose.md; create one before the next handoff",
            )
        )
        return findings
    text = read_text(purpose)
    todos = unresolved_todo_lines(text)
    if todos:
        level = "error" if strict else "warning"
        findings.append(
            Finding(
                level,
                f"{purpose} contains {len(todos)} TODO placeholder(s); fill before treating run as intentional",
            )
        )
    if is_stub_purpose(text):
        level = "error" if strict else "warning"
        findings.append(
            Finding(
                level,
                f"{purpose} is missing required sections (hypothesis / success / linkage); use assets/templates/run-purpose.md",
            )
        )
    return findings


def validate(project_root: Path, *, strict: bool) -> list[Finding]:
    ai_root = project_root / ".ai-research-workflow"
    if not ai_root.is_dir():
        return [Finding("error", f"missing ai-research root: {ai_root}")]
    findings: list[Finding] = []
    runs = find_workstream_runs(ai_root)
    if not runs:
        findings.append(
            Finding("warning", f"no runs/ subdirectories under {ai_root}; nothing to validate")
        )
    for run_dir in runs:
        findings.extend(validate_run(run_dir, strict=strict))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that every run directory has a purpose.md describing why it exists."
    )
    parser.add_argument("project_root", type=Path, help="Target project root to validate.")
    parser.add_argument("--strict", action="store_true", help="Treat missing or stub purpose.md as errors.")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    findings = validate(project_root, strict=args.strict)
    errors = [f for f in findings if f.level == "error"]
    warnings = [f for f in findings if f.level == "warning"]
    for finding in findings:
        print(f"{finding.level}: {finding.message}", file=sys.stderr)
    if errors:
        print(f"Run-purpose validation failed: {project_root}", file=sys.stderr)
        return 1
    print(f"Run-purpose validation passed: {project_root} ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())