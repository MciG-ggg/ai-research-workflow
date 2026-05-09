#!/usr/bin/env python3
"""Validate a downstream .omx/ai-research workspace.

This script is maintenance tooling for checking artifact contracts. It does not
run experiments, collect metrics, plot results, or publish user research docs.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PORTFOLIO_FILES = ["RESEARCH.md", "INDEX.md"]

WORKSTREAM_FILES = [
    "RESEARCH.md",
    "LITERATURE.md",
    "EXPERIMENT.md",
    "RUNS.md",
    "RESULTS.md",
    "REPRODUCIBILITY.md",
    "PAPER_DRAFT.md",
    "SCRIPT_REGISTRY.md",
]

FEEDBACK_ROOT_FILES = ["LEARNINGS.md", "ISSUES.md", "DECISIONS.md"]
GROWTH_ROOT_FILES = ["SKILL_GROWTH.md"]

VALID_FEEDBACK_MEMORY = {"off", "lite", "full"}
VALID_GROWTH_REVIEW = {"off", "milestone", "always"}


@dataclass
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_missing_file(findings: list[Finding], path: Path, label: str) -> None:
    if not path.is_file():
        findings.append(Finding("error", f"missing {label}: {path}"))


def parse_config(ai_root: Path, findings: list[Finding]) -> tuple[str, str]:
    config_path = ai_root / "CONFIG.md"
    feedback_memory = "off"
    growth_review = "off"
    if not config_path.is_file():
        return feedback_memory, growth_review

    text = read_text(config_path)
    for line in text.splitlines():
        match = re.match(r"^\s*(feedback_memory|growth_review)\s*:\s*([A-Za-z_-]+)\s*$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).lower()
        if key == "feedback_memory":
            feedback_memory = value
        elif key == "growth_review":
            growth_review = value

    if feedback_memory not in VALID_FEEDBACK_MEMORY:
        findings.append(
            Finding(
                "error",
                f"{config_path} has invalid feedback_memory={feedback_memory!r}; expected off, lite, or full",
            )
        )
    if growth_review not in VALID_GROWTH_REVIEW:
        findings.append(
            Finding(
                "error",
                f"{config_path} has invalid growth_review={growth_review!r}; expected off, milestone, or always",
            )
        )
    return feedback_memory, growth_review


def find_workstreams(ai_root: Path) -> list[Path]:
    if not ai_root.is_dir():
        return []
    excluded = {"runs", "logs", "state", "worktrees", "scripts", "docs"}
    return sorted(
        path
        for path in ai_root.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name not in excluded
    )


def has_non_placeholder_evidence(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    for pattern in patterns:
        if pattern not in lower:
            return False
    evidence_lines = [
        line.strip().lower()
        for line in text.splitlines()
        if any(pattern in line.lower() for pattern in patterns)
    ]
    return bool(evidence_lines) and not all("todo" in line for line in evidence_lines)


def validate_portfolio(ai_root: Path, findings: list[Finding]) -> str:
    for name in PORTFOLIO_FILES:
        add_missing_file(findings, ai_root / name, f"portfolio {name}")

    index_path = ai_root / "INDEX.md"
    return read_text(index_path) if index_path.is_file() else ""


def validate_workstream(path: Path, index_text: str, findings: list[Finding]) -> None:
    slug = path.name
    for name in WORKSTREAM_FILES:
        add_missing_file(findings, path / name, f"workstream {slug}/{name}")

    if index_text and slug not in index_text:
        findings.append(Finding("error", f"portfolio INDEX.md does not mention workstream slug: {slug}"))

    research_path = path / "RESEARCH.md"
    if research_path.is_file():
        text = read_text(research_path)
        if not has_non_placeholder_evidence(text, ["deep", "ralplan", "autoresearch"]):
            findings.append(
                Finding(
                    "warning",
                    f"{research_path} does not appear to link completed deep-interview, ralplan, and autoresearch gate evidence",
                )
            )
        if "TODO" in text:
            findings.append(Finding("warning", f"{research_path} still contains TODO placeholders"))

    runs_dir = path / "runs"
    if not runs_dir.is_dir():
        findings.append(Finding("warning", f"missing workstream runs/ directory: {runs_dir}"))

    scripts_dir = path / "scripts"
    if not scripts_dir.is_dir():
        findings.append(Finding("warning", f"missing workstream scripts/ directory: {scripts_dir}"))

    run_dirs = [child for child in runs_dir.iterdir() if child.is_dir()] if runs_dir.is_dir() else []
    runs_path = path / "RUNS.md"
    if run_dirs and runs_path.is_file():
        runs_text = read_text(runs_path)
        for required in ("log", "metrics", "summary"):
            if required not in runs_text.lower():
                findings.append(
                    Finding("warning", f"{runs_path} may be missing {required} paths for completed run evidence")
                )


def validate_feedback_modes(
    ai_root: Path,
    workstreams: list[Path],
    feedback_memory: str,
    growth_review: str,
    findings: list[Finding],
) -> None:
    if feedback_memory in {"lite", "full"}:
        for name in FEEDBACK_ROOT_FILES:
            add_missing_file(findings, ai_root / name, f"feedback root {name}")
        for workstream in workstreams:
            add_missing_file(findings, workstream / "NOTES.md", f"feedback workstream {workstream.name}/NOTES.md")
            if feedback_memory == "full":
                add_missing_file(
                    findings,
                    workstream / "DESIGN.md",
                    f"full-feedback workstream {workstream.name}/DESIGN.md",
                )

    if growth_review in {"milestone", "always"}:
        for name in GROWTH_ROOT_FILES:
            add_missing_file(findings, ai_root / name, f"growth root {name}")
        for workstream in workstreams:
            add_missing_file(findings, workstream / "REVIEW.md", f"growth workstream {workstream.name}/REVIEW.md")


def validate(project_root: Path, require_workstream: bool) -> list[Finding]:
    findings: list[Finding] = []
    ai_root = project_root / ".omx" / "ai-research"
    if not ai_root.is_dir():
        return [Finding("error", f"missing ai-research root: {ai_root}")]

    feedback_memory, growth_review = parse_config(ai_root, findings)
    index_text = validate_portfolio(ai_root, findings)

    workstreams = find_workstreams(ai_root)
    if require_workstream and not workstreams:
        findings.append(Finding("error", f"no workstream directories found under {ai_root}"))

    for workstream in workstreams:
        validate_workstream(workstream, index_text, findings)

    validate_feedback_modes(ai_root, workstreams, feedback_memory, growth_review, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a downstream .omx/ai-research workspace.")
    parser.add_argument("project_root", type=Path, help="Target project root to validate.")
    parser.add_argument(
        "--require-workstream",
        action="store_true",
        help="Fail when portfolio files exist but no workstream directory is present.",
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    findings = validate(project_root, args.require_workstream)
    errors = [finding for finding in findings if finding.level == "error"]
    warnings = [finding for finding in findings if finding.level == "warning"]

    for finding in findings:
        print(f"{finding.level}: {finding.message}", file=sys.stderr)

    if errors or (args.strict and warnings):
        print(f"Research workspace invalid: {project_root}", file=sys.stderr)
        return 1

    print(f"Research workspace valid: {project_root}")
    if warnings:
        print(f"Warnings: {len(warnings)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
