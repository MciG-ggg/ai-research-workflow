#!/usr/bin/env python3
"""Validate a downstream .ai-research-workflow workspace.

This script is framework guardrail tooling for checking artifact contracts. It
does not run experiments, collect metrics, plot results, publish research docs,
merge branches, push remotes, or delete worktrees.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PORTFOLIO_FILES = ["RESEARCH.md", "INDEX.md"]
IDEA_SCOUTING_FILES = ["IDEA_SCOUTING.md"]
PAPER_REGISTRY_FILES = ["PAPERS.md"]

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
LIFECYCLE_WORKSTREAM_FILES = ["STATE.json", "CLAIMS.md"]

FEEDBACK_ROOT_FILES = ["LEARNINGS.md", "ISSUES.md", "DECISIONS.md"]
QA_ROOT_FILES = ["QUESTIONS.md"]
GROWTH_ROOT_FILES = ["SKILL_GROWTH.md"]

VALID_FEEDBACK_MEMORY = {"off", "lite", "full"}
VALID_WORKFLOW_PRESET = {"conservative", "guided", "autonomous"}
VALID_IDEA_SCOUTING = {"auto", "off", "on"}
VALID_COMPLETION_HANDOFF = {"auto", "off"}
VALID_WORKTREE_CLOSEOUT = {"off", "report-before-merge"}
VALID_QA_CAPTURE = {"off", "research", "all"}
VALID_GROWTH_REVIEW = {"off", "milestone", "always"}
VALID_WORKSTREAM_TYPES = {"experiment-campaign", "paper-reproduction"}
VALID_PHASES = {"all", "idea-scouting", "paper-scouting", "paper-reproduction", "new-workstream", "completion-handoff"}
VALID_STATE_PHASES = {
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
}

PATH_TOKEN_RE = re.compile(r"`([^`]+)`|\(([^)]+)\)")


@dataclass
class Finding:
    level: str
    message: str


@dataclass
class Config:
    schema_version: str = "1"
    workflow_preset: str = "guided"
    idea_scouting: str = "auto"
    completion_handoff: str = "auto"
    worktree_closeout: str = "report-before-merge"
    feedback_memory: str = "off"
    qa_capture: str = "off"
    growth_review: str = "off"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def add_missing_file(findings: list[Finding], path: Path, label: str) -> None:
    if not path.is_file():
        findings.append(Finding("error", f"missing {label}: {path}"))


def parse_config(ai_root: Path, findings: list[Finding]) -> Config:
    config_path = ai_root / "CONFIG.md"
    config = Config()
    if not config_path.is_file():
        return config

    text = read_text(config_path)
    for line in text.splitlines():
        match = re.match(
            r"^\s*(schema_version|workflow_preset|idea_scouting|completion_handoff|worktree_closeout|feedback_memory|qa_capture|growth_review)\s*:\s*([A-Za-z0-9_-]+)\s*$",
            line,
        )
        if match:
            setattr(config, match.group(1), match.group(2).lower())

    validators = {
        "schema_version": ({"1"}, "1"),
        "workflow_preset": (VALID_WORKFLOW_PRESET, "conservative, guided, or autonomous"),
        "idea_scouting": (VALID_IDEA_SCOUTING, "auto, off, or on"),
        "completion_handoff": (VALID_COMPLETION_HANDOFF, "auto or off"),
        "worktree_closeout": (VALID_WORKTREE_CLOSEOUT, "off or report-before-merge"),
        "feedback_memory": (VALID_FEEDBACK_MEMORY, "off, lite, or full"),
        "qa_capture": (VALID_QA_CAPTURE, "off, research, or all"),
        "growth_review": (VALID_GROWTH_REVIEW, "off, milestone, or always"),
    }
    for field, (allowed, expected) in validators.items():
        value = getattr(config, field)
        if value not in allowed:
            findings.append(Finding("error", f"{config_path} has invalid {field}={value!r}; expected {expected}"))
    return config


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


def index_text_for_slug(index_text: str, slug: str) -> str:
    """Return INDEX.md lines that specifically describe a workstream slug."""

    table_pattern = re.compile(rf"^\|\s*{re.escape(slug)}\s*\|", re.IGNORECASE)
    bullet_pattern = re.compile(rf"^\s*[-*]\s*`?{re.escape(slug)}`?\s*[:—-]", re.IGNORECASE)
    path_pattern = re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(slug)}/", re.IGNORECASE)
    lines = []
    for line in index_text.splitlines():
        stripped = line.strip()
        if table_pattern.search(stripped) or bullet_pattern.search(stripped) or path_pattern.search(stripped):
            lines.append(line)
    return "\n".join(lines)


def unresolved_todo_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if "TODO" in line]


def add_todo_finding(findings: list[Finding], path: Path, *, error_on_todo: bool, phase: str) -> None:
    if not path.is_file():
        return
    todos = unresolved_todo_lines(read_text(path))
    if not todos:
        return
    level = "error" if error_on_todo else "warning"
    findings.append(Finding(level, f"{path} contains {len(todos)} TODO placeholder(s) during phase {phase}"))


def validate_portfolio(ai_root: Path, findings: list[Finding], *, error_on_todo: bool, phase: str) -> str:
    for name in PORTFOLIO_FILES:
        path = ai_root / name
        add_missing_file(findings, path, f"portfolio {name}")
        add_todo_finding(findings, path, error_on_todo=error_on_todo, phase=phase)
    index_path = ai_root / "INDEX.md"
    return read_text(index_path) if index_path.is_file() else ""


def validate_workstream(path: Path, index_text: str, findings: list[Finding], *, error_on_todo: bool, phase: str) -> None:
    slug = path.name
    for name in WORKSTREAM_FILES:
        artifact = path / name
        add_missing_file(findings, artifact, f"workstream {slug}/{name}")
        add_todo_finding(findings, artifact, error_on_todo=error_on_todo, phase=phase)

    for name in LIFECYCLE_WORKSTREAM_FILES:
        artifact = path / name
        if not artifact.is_file():
            level = "error" if phase in {"new-workstream", "completion-handoff"} else "warning"
            findings.append(
                Finding(
                    level,
                    f"missing lifecycle artifact {slug}/{name}: {artifact}; run init_workstream.py or migrate the workstream",
                )
            )
        else:
            add_todo_finding(findings, artifact, error_on_todo=error_on_todo, phase=phase)

    if index_text and not index_text_for_slug(index_text, slug):
        findings.append(Finding("error", f"portfolio INDEX.md does not mention workstream slug: {slug}"))

    research_path = path / "RESEARCH.md"
    if research_path.is_file():
        text = read_text(research_path)
        if not has_non_placeholder_evidence(text, ["deep", "ralplan", "autoresearch"]):
            level = "error" if phase == "new-workstream" else "warning"
            findings.append(
                Finding(
                    level,
                    f"{research_path} does not appear to link completed deep-interview, ralplan, and autoresearch gate evidence",
                )
            )

    validate_state_file(path, findings, phase=phase)
    validate_experiment_quality(path, findings, strict=phase in {"completion-handoff"})
    validate_claims_file(path, findings, strict=phase in {"completion-handoff"})

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


def validate_state_file(workstream: Path, findings: list[Finding], *, phase: str) -> None:
    state_path = workstream / "STATE.json"
    if not state_path.is_file():
        return
    try:
        state = json.loads(read_text(state_path))
    except json.JSONDecodeError as exc:
        findings.append(Finding("error", f"{state_path} is not valid JSON: {exc}"))
        return
    if str(state.get("schema_version")) != "1":
        findings.append(Finding("error", f"{state_path} has unsupported schema_version={state.get('schema_version')!r}; expected 1"))
    if state.get("workstream_slug") and state.get("workstream_slug") != workstream.name:
        findings.append(
            Finding(
                "error",
                f"{state_path} workstream_slug={state.get('workstream_slug')!r} does not match directory {workstream.name!r}",
            )
        )
    state_phase = state.get("phase")
    if state_phase not in VALID_STATE_PHASES:
        findings.append(Finding("error", f"{state_path} has invalid phase={state_phase!r}"))
    if phase != "all" and phase in VALID_STATE_PHASES and state_phase != phase:
        findings.append(Finding("warning", f"{state_path} phase={state_phase!r} differs from validator phase={phase!r}"))
    if not state.get("next_action"):
        findings.append(Finding("warning", f"{state_path} is missing next_action"))
    workstream_type = state.get("workstream_type")
    if workstream_type is None:
        level = "error" if phase in {"new-workstream", "paper-reproduction"} else "warning"
        findings.append(Finding(level, f"{state_path} is missing workstream_type"))
    elif workstream_type not in VALID_WORKSTREAM_TYPES:
        findings.append(Finding("error", f"{state_path} has invalid workstream_type={workstream_type!r}"))
    if phase == "paper-reproduction" and workstream_type != "paper-reproduction":
        findings.append(Finding("error", f"{state_path} must use workstream_type='paper-reproduction' for paper-reproduction phase"))
    if workstream_type == "paper-reproduction" and not (workstream / "REPRODUCTION.md").is_file():
        findings.append(Finding("error", f"{state_path} declares paper-reproduction but REPRODUCTION.md is missing"))


def validate_experiment_quality(workstream: Path, findings: list[Finding], *, strict: bool) -> None:
    experiment_path = workstream / "EXPERIMENT.md"
    if not experiment_path.is_file():
        return
    text = read_text(experiment_path).lower()
    required = [
        "baseline fairness checklist",
        "same data split",
        "same evaluation metric",
        "hyperparameter",
        "negative / inconclusive result policy",
    ]
    level = "error" if strict else "warning"
    for term in required:
        if term not in text:
            findings.append(Finding(level, f"{experiment_path} missing experiment-quality field: {term}"))


def validate_claims_file(workstream: Path, findings: list[Finding], *, strict: bool) -> None:
    claims_path = workstream / "CLAIMS.md"
    if not claims_path.is_file():
        return
    text = read_text(claims_path).lower()
    required = [
        "claim ledger",
        "evidence paths",
        "allowed wording",
        "forbidden wording",
        "negative or inconclusive results",
        "retired or downgraded claims",
    ]
    level = "error" if strict else "warning"
    for term in required:
        if term not in text:
            findings.append(Finding(level, f"{claims_path} missing claim-ledger field: {term}"))


def validate_optional_modes(
    ai_root: Path,
    workstreams: list[Path],
    config: Config,
    findings: list[Finding],
    *,
    error_on_todo: bool,
    phase: str,
) -> None:
    if config.idea_scouting == "on":
        for name in IDEA_SCOUTING_FILES:
            path = ai_root / name
            add_missing_file(findings, path, f"idea-scouting root {name}")
            add_todo_finding(findings, path, error_on_todo=error_on_todo, phase=phase)

    if config.feedback_memory in {"lite", "full"}:
        for name in FEEDBACK_ROOT_FILES:
            path = ai_root / name
            add_missing_file(findings, path, f"feedback root {name}")
            add_todo_finding(findings, path, error_on_todo=error_on_todo, phase=phase)
        for workstream in workstreams:
            add_missing_file(findings, workstream / "NOTES.md", f"feedback workstream {workstream.name}/NOTES.md")
            if config.feedback_memory == "full":
                add_missing_file(findings, workstream / "DESIGN.md", f"full-feedback workstream {workstream.name}/DESIGN.md")

    if config.qa_capture in {"research", "all"}:
        for name in QA_ROOT_FILES:
            path = ai_root / name
            add_missing_file(findings, path, f"question-capture root {name}")
            add_todo_finding(findings, path, error_on_todo=error_on_todo, phase=phase)
        for workstream in workstreams:
            add_missing_file(
                findings,
                workstream / "QUESTIONS.md",
                f"question-capture workstream {workstream.name}/QUESTIONS.md",
            )

    if config.growth_review in {"milestone", "always"}:
        for name in GROWTH_ROOT_FILES:
            path = ai_root / name
            add_missing_file(findings, path, f"growth root {name}")
            add_todo_finding(findings, path, error_on_todo=error_on_todo, phase=phase)
        for workstream in workstreams:
            add_missing_file(findings, workstream / "REVIEW.md", f"growth workstream {workstream.name}/REVIEW.md")


def select_workstreams(workstreams: list[Path], slug: str | None, findings: list[Finding]) -> list[Path]:
    if slug is None:
        return workstreams
    selected = [path for path in workstreams if path.name == slug]
    if not selected:
        findings.append(Finding("error", f"requested workstream not found: {slug}"))
    return selected


def validate_idea_scouting_phase(ai_root: Path, findings: list[Finding], *, error_on_todo: bool) -> None:
    path = ai_root / "IDEA_SCOUTING.md"
    add_missing_file(findings, path, "idea-scouting root IDEA_SCOUTING.md")
    if not path.is_file():
        return
    text = read_text(path)
    required = [
        "Falsifiable hypothesis",
        "Evaluation metric",
        "Lightweight evidence",
        "Novelty",
        "Feasibility budget",
        "User-goal fit",
    ]
    for term in required:
        if term.lower() not in text.lower():
            findings.append(Finding("error", f"{path} missing idea promotion field: {term}"))
    add_todo_finding(findings, path, error_on_todo=error_on_todo, phase="idea-scouting")


def validate_paper_scouting_phase(ai_root: Path, findings: list[Finding], *, error_on_todo: bool) -> None:
    path = ai_root / "PAPERS.md"
    add_missing_file(findings, path, "paper-scouting root PAPERS.md")
    if not path.is_file():
        return
    text = read_text(path)
    required = [
        "SOTA",
        "baseline",
        "Code/data/checkpoints",
        "Key claim",
        "Benchmark / metric",
        "Reproduction priority",
        "Maintenance Log",
    ]
    for term in required:
        if term.lower() not in text.lower():
            findings.append(Finding("error", f"{path} missing paper-registry field: {term}"))
    add_todo_finding(findings, path, error_on_todo=error_on_todo, phase="paper-scouting")


def validate_paper_reproduction_phase(
    ai_root: Path,
    targets: list[Path],
    findings: list[Finding],
    *,
    error_on_todo: bool,
) -> None:
    validate_paper_scouting_phase(ai_root, findings, error_on_todo=error_on_todo)
    if not targets:
        findings.append(Finding("error", "paper-reproduction phase requires one selected workstream directory"))
        return
    for workstream in targets:
        path = workstream / "REPRODUCTION.md"
        add_missing_file(findings, path, f"paper-reproduction workstream {workstream.name}/REPRODUCTION.md")
        if not path.is_file():
            continue
        text = read_text(path)
        required = [
            "Target Paper",
            "Reproduction Objective",
            "Available Materials",
            "Minimal Reproduction Plan",
            "Run Evidence Links",
            "Deviations from Paper",
            "Reproduction-Derived Ideas",
            "Conclusions and Distillation",
        ]
        for term in required:
            if term.lower() not in text.lower():
                findings.append(Finding("error", f"{path} missing paper-reproduction field: {term}"))
        add_todo_finding(findings, path, error_on_todo=error_on_todo, phase="paper-reproduction")


def validate_new_workstream_phase(ai_root: Path, index_text: str, targets: list[Path], findings: list[Finding]) -> None:
    if not targets:
        findings.append(Finding("error", "new-workstream phase requires at least one workstream directory"))
        return
    if not index_text:
        findings.append(Finding("error", "new-workstream phase requires portfolio INDEX.md"))
        return
    for workstream in targets:
        slug = workstream.name
        slug_index_text = index_text_for_slug(index_text, slug)
        if not slug_index_text:
            findings.append(Finding("error", f"portfolio INDEX.md does not mention new workstream slug: {slug}"))
        if not has_non_placeholder_evidence(slug_index_text, ["deep", "ralplan", "autoresearch"]):
            findings.append(
                Finding(
                    "error",
                    f"portfolio INDEX.md does not record deep-interview, ralplan, and autoresearch gate evidence for {slug}",
                )
            )
        research_path = workstream / "RESEARCH.md"
        if research_path.is_file() and not has_non_placeholder_evidence(
            read_text(research_path), ["deep", "ralplan", "autoresearch"]
        ):
            findings.append(Finding("error", f"{research_path} does not record mandatory workflow gate evidence"))


def validate_completion_handoff_phase(targets: list[Path], config: Config, findings: list[Finding]) -> None:
    if not targets:
        findings.append(Finding("error", "completion-handoff phase requires at least one workstream directory"))
        return
    for workstream in targets:
        required_artifacts = ["STATE.json", "RUNS.md", "SCRIPT_REGISTRY.md", "RESULTS.md", "CLAIMS.md", "REPRODUCIBILITY.md"]
        for name in required_artifacts:
            add_missing_file(findings, workstream / name, f"completion handoff {workstream.name}/{name}")
        runs_path = workstream / "RUNS.md"
        if runs_path.is_file():
            runs_text = read_text(runs_path).lower()
            for term in ("log", "metrics", "summary", "distilled updates outside `runs/`"):
                if term not in runs_text:
                    findings.append(Finding("error", f"{runs_path} missing completion handoff evidence term: {term}"))
            if config.worktree_closeout == "report-before-merge":
                for term in ("worktree closeout plan", "user confirmation"):
                    if term not in runs_text:
                        findings.append(Finding("error", f"{runs_path} missing report-before-merge closeout field: {term}"))
        registry = workstream / "SCRIPT_REGISTRY.md"
        if registry.is_file() and "completion handoff" not in read_text(registry).lower():
            findings.append(Finding("warning", f"{registry} does not mention completion handoff script/command updates"))
        results_path = workstream / "RESULTS.md"
        if results_path.is_file():
            results_text = read_text(results_path).lower()
            for term in ("negative and inconclusive results", "evidence-to-claim mapping"):
                if term not in results_text:
                    findings.append(Finding("error", f"{results_path} missing result-quality field: {term}"))


def extract_candidate_paths(text: str) -> list[str]:
    paths: list[str] = []
    for match in PATH_TOKEN_RE.finditer(text):
        token = (match.group(1) or match.group(2) or "").strip()
        if not token or token.startswith(("http://", "https://", "#")):
            continue
        if token.lower() in {"todo", "pass", "fail", "blocked"}:
            continue
        if any(token.endswith(suffix) for suffix in (".md", ".json", ".jsonl", ".csv", ".txt", ".log", ".png", ".jpg")) or "/" in token:
            paths.append(token)
    return paths


def validate_linked_paths(project_root: Path, ai_root: Path, findings: list[Finding]) -> None:
    for artifact in ai_root.rglob("*.md"):
        text = read_text(artifact)
        for token in extract_candidate_paths(text):
            path = Path(token)
            if not path.is_absolute():
                path = (project_root / path).resolve()
            if not path.exists():
                findings.append(Finding("warning", f"linked artifact path does not exist: {token} (from {artifact})"))


def validate(
    project_root: Path,
    *,
    require_workstream: bool,
    phase: str,
    workstream_slug: str | None,
    error_on_todo: bool,
    check_paths: bool,
) -> list[Finding]:
    findings: list[Finding] = []
    ai_root = project_root / ".ai-research-workflow"
    if not ai_root.is_dir():
        return [Finding("error", f"missing ai-research root: {ai_root}")]

    config = parse_config(ai_root, findings)
    index_text = validate_portfolio(ai_root, findings, error_on_todo=error_on_todo, phase=phase)

    workstreams = find_workstreams(ai_root)
    targets = select_workstreams(workstreams, workstream_slug, findings)
    if require_workstream and not workstreams:
        findings.append(Finding("error", f"no workstream directories found under {ai_root}"))

    for workstream in workstreams:
        effective_phase = phase
        if workstream_slug and phase in {"new-workstream", "completion-handoff"} and workstream.name != workstream_slug:
            effective_phase = "all"
        validate_workstream(workstream, index_text, findings, error_on_todo=error_on_todo, phase=effective_phase)

    validate_optional_modes(
        ai_root,
        workstreams,
        config,
        findings,
        error_on_todo=error_on_todo,
        phase=phase,
    )

    if phase == "idea-scouting":
        validate_idea_scouting_phase(ai_root, findings, error_on_todo=error_on_todo)
    elif phase == "paper-scouting":
        validate_paper_scouting_phase(ai_root, findings, error_on_todo=error_on_todo)
    elif phase == "paper-reproduction":
        validate_paper_reproduction_phase(ai_root, targets, findings, error_on_todo=error_on_todo)
    elif phase == "new-workstream":
        validate_new_workstream_phase(ai_root, index_text, targets, findings)
    elif phase == "completion-handoff":
        validate_completion_handoff_phase(targets, config, findings)

    if check_paths:
        validate_linked_paths(project_root, ai_root, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a downstream .ai-research-workflow workspace.")
    parser.add_argument("project_root", type=Path, help="Target project root to validate.")
    parser.add_argument(
        "--require-workstream",
        action="store_true",
        help="Fail when portfolio files exist but no workstream directory is present.",
    )
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    parser.add_argument(
        "--phase",
        choices=sorted(VALID_PHASES),
        default="all",
        help="Run extra phase-aware checks for idea-scouting, paper-scouting, paper-reproduction, new-workstream, or completion-handoff.",
    )
    parser.add_argument("--workstream", help="Restrict phase-aware checks to one workstream slug.")
    parser.add_argument("--error-on-todo", action="store_true", help="Treat remaining TODO placeholders as errors.")
    parser.add_argument("--check-paths", action="store_true", help="Warn when linked local artifact paths do not exist.")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    findings = validate(
        project_root,
        require_workstream=args.require_workstream,
        phase=args.phase,
        workstream_slug=args.workstream,
        error_on_todo=args.error_on_todo,
        check_paths=args.check_paths,
    )
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
