#!/usr/bin/env python3
"""Validate the ai-research-workflow skill framework contract.

This script is maintenance tooling for the skill itself. It must not be used as
an experiment runner, metrics collector, plotter, or docs publisher for a user's
research project.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

OLD_USER_RUNNER_SCRIPTS = {
    "init_research_artifacts.py",
    "launch_experiment_tmux.py",
    "prepare_experiment_run.py",
    "publish_research_docs.py",
}

REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/artifact-contracts.md",
    "references/experiment-runtime-standards.md",
    "references/project-local-script-registry.md",
    "references/research-quality-gates.md",
]

REQUIRED_PHRASES = {
    "SKILL.md": [
        "framework skill",
        "not a project-specific experiment runner",
        "maintenance-only",
        "project-local scripts",
        ".omx/ai-research/<slug>/SCRIPT_REGISTRY.md",
        ".omx/ai-research/<slug>/scripts/",
    ],
    "README.md": [
        "oh-my-codex",
        "does **not** ship universal experiment runner scripts",
        "maintenance-only",
        "not for running user experiments",
    ],
    "references/artifact-contracts.md": [
        "SCRIPT_REGISTRY.md",
        "Project-local commands/scripts",
        "not the presence of a bundled publisher",
    ],
    "references/experiment-runtime-standards.md": [
        "contracts, not universal scripts",
        "project-local wrappers",
        "SCRIPT_REGISTRY.md",
    ],
    "references/project-local-script-registry.md": [
        "framework-first",
        "Create scripts only when the current project needs them",
        "maintenance scripts",
    ],
    "references/research-quality-gates.md": [
        "SCRIPT_REGISTRY.md",
        "project-local wrapper scripts",
    ],
}

ALLOWED_SKILL_SCRIPT_PATTERNS = [
    re.compile(r"^validate_[a-z0-9_]+\.py$"),
    re.compile(r"^check_[a-z0-9_]+\.py$"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_frontmatter_field(text: str, field: str) -> bool:
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end == -1:
        return False
    frontmatter = text[4:end]
    return re.search(rf"^{re.escape(field)}\s*:\s*.+$", frontmatter, re.MULTILINE) is not None


def validate(skill_dir: Path) -> list[str]:
    errors: list[str] = []

    readme_path: Path | None = None
    for ancestor in (skill_dir, *skill_dir.parents):
        candidate = ancestor / "README.md"
        if candidate.is_file():
            readme_path = candidate
            break

    for relative in REQUIRED_FILES:
        if not (skill_dir / relative).is_file():
            errors.append(f"missing required file: {skill_dir / relative}")

    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        text = read_text(skill_md)
        for field in ("name", "description"):
            if not has_frontmatter_field(text, field):
                errors.append(f"SKILL.md missing YAML frontmatter field: {field}")

    for relative, phrases in REQUIRED_PHRASES.items():
        if relative == "README.md":
            path = readme_path
            if path is None:
                continue
        else:
            path = skill_dir / relative
        if path is None or not path.is_file():
            errors.append(f"missing phrase-check target: {path if path is not None else 'README.md not found'}")
            continue
        text = read_text(path)
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{path} missing required phrase: {phrase!r}")

    script_dir = skill_dir / "scripts"
    if script_dir.exists():
        for path in script_dir.iterdir():
            if path.is_dir():
                errors.append(f"skill scripts/ must contain maintenance files only, found directory: {path}")
                continue
            if path.name in OLD_USER_RUNNER_SCRIPTS:
                errors.append(f"old project experiment runner must not be bundled: {path.name}")
            if not any(pattern.match(path.name) for pattern in ALLOWED_SKILL_SCRIPT_PATTERNS):
                errors.append(
                    "skill scripts/ is maintenance-only; use validate_*.py or check_*.py names, "
                    f"found: {path.name}"
                )

    searchable_files = list(skill_dir.rglob("*.md"))
    if readme_path is not None:
        searchable_files.append(readme_path)
    for path in searchable_files:
        if not path.is_file():
            continue
        text = read_text(path)
        for old_name in OLD_USER_RUNNER_SCRIPTS:
            if old_name in text:
                errors.append(f"stale bundled runner reference in {path}: {old_name}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ai-research-workflow framework invariants.")
    parser.add_argument(
        "skill_dir",
        nargs="?",
        default=Path(__file__).resolve().parents[1],
        type=Path,
        help="Path to skills/ai-research-workflow. Defaults to this script's parent skill directory.",
    )
    args = parser.parse_args()

    skill_dir = args.skill_dir.resolve()
    errors = validate(skill_dir)
    if errors:
        print("Framework contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Framework contract valid: {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
