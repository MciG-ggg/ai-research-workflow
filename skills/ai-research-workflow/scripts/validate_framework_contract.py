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
    "assets/templates/CLAIMS.md",
    "assets/templates/CONFIG.md",
    "assets/templates/DECISIONS.md",
    "assets/templates/DESIGN.md",
    "assets/templates/EXPERIMENT.md",
    "assets/templates/IDEA_SCOUTING.md",
    "assets/templates/ISSUES.md",
    "assets/templates/LEARNINGS.md",
    "assets/templates/LITERATURE.md",
    "assets/templates/NOTES.md",
    "assets/templates/PAPER_DRAFT.md",
    "assets/templates/QUESTIONS.md",
    "assets/templates/REPRODUCIBILITY.md",
    "assets/templates/RESULTS.md",
    "assets/templates/REVIEW.md",
    "assets/templates/RUNS.md",
    "assets/templates/SCRIPT_REGISTRY.md",
    "assets/templates/SKILL_GROWTH.md",
    "assets/templates/STATE.json",
    "assets/templates/portfolio-INDEX.md",
    "assets/templates/portfolio-RESEARCH.md",
    "assets/templates/workstream-RESEARCH.md",
    "assets/fixtures/research_workspace_cases.json",
    "references/artifact-contracts.md",
    "references/experiment-runtime-standards.md",
    "references/idea-scouting.md",
    "references/project-local-script-registry.md",
    "references/question-capture.md",
    "references/research-quality-gates.md",
    "references/workflow-orchestration.md",
    "references/worktree-development.md",
    "scripts/check_worktree_registry.py",
    "scripts/check_regression_fixtures.py",
    "scripts/init_research_workspace.py",
    "scripts/init_workstream.py",
    "scripts/prepare_worktree_closeout.py",
    "scripts/resolve_workflow.py",
    "scripts/update_installed_skill.sh",
    "scripts/update_workstream_state.py",
    "scripts/validate_research_workspace.py",
]

REQUIRED_PHRASES = {
    "SKILL.md": [
        "framework skill",
        "not a project-specific experiment runner",
        "This skill is an OMX workflow",
        "$deep-interview --autoresearch",
        "$ralplan",
        "$autoresearch",
        "Research control plane vs project implementation",
        "Optional feedback and growth modes",
        "assets/templates/",
        "Templates define shape only",
        "validate_research_workspace.py",
        "resolve_workflow.py",
        "init_research_workspace.py",
        "init_workstream.py",
        "update_workstream_state.py",
        "prepare_worktree_closeout.py",
        "check_regression_fixtures.py",
        "--phase idea-scouting",
        "STATE.json",
        "CLAIMS.md",
        "schema_version: 1",
        "baseline fairness",
        "negative/inconclusive",
        "Idea Scouting",
        "`--idea-scouting`",
        "workflow_preset: conservative | guided | autonomous",
        "idea_scouting: auto | off | on",
        "completion_handoff: auto | off",
        "worktree_closeout: off | report-before-merge",
        "references/idea-scouting.md",
        "IDEA_SCOUTING.md",
        "promotion gate",
        "Question Capture",
        "`--qa-capture`",
        "qa_capture: off | research | all",
        "references/question-capture.md",
        "QUESTIONS.md",
        "Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default",
        "`--feedback-memory`",
        "`--growth-review`",
        "`--no-feedback`",
        ".omx/ai-research/CONFIG.md",
        "feedback_memory: off | lite | full",
        "growth_review: off | milestone | always",
        "`SKILL_GROWTH.md`",
        "Feedback memory records distilled knowledge",
        "Portfolio layer",
        ".omx/ai-research/RESEARCH.md",
        ".omx/ai-research/INDEX.md",
        "Before creating a new `<slug>`",
        "New workstream creation has a mandatory workflow gate",
        "$deep-interview --autoresearch",
        "$ralplan",
        "$autoresearch",
        ".omx/plans/prd-<slug>.md",
        ".omx/plans/test-spec-<slug>.md",
        "completion_artifact_path",
        "research portfolio control plane",
        "Actual research work belongs in the target project root",
        "Distill completed runs",
        "Experiment completion handoff",
        "current experiment is done",
        "report-before-merge closeout plan",
        "persist user-requested outputs",
        "maintenance-only",
        "project-local scripts",
        "Task worktree rule",
        "target repository",
        "one worktree per logical task or lane",
        "target project repository",
        "inspect the local git status before opening any new worktree",
        "splitting them into semantic commits",
        "create the task worktree from the latest commit",
        "push the completed branch or merged main branch to the remote",
        "not about installing or maintaining this skill repository",
        "read-only analysis",
        ".omx/worktrees/REGISTRY.md",
        "The skill repository tracks the framework itself",
        "keep `.omx/` ignored",
        "multi-seed experiments",
        "idle GPU/device",
        ".omx/ai-research/<slug>/SCRIPT_REGISTRY.md",
        ".omx/ai-research/<slug>/scripts/",
    ],
    "README.md": [
        "README.zh-CN.md",
        "oh-my-codex",
        "does **not** ship universal experiment runner scripts",
        "maintenance-only",
        "not for running user experiments",
        "Task worktrees",
        "target AI research project",
        "open an isolated git worktree before editing",
        "inspect local git status",
        "semantic Lore-format commits",
        "create the task worktree from the latest commit",
        "one worktree per logical task or lane",
        ".omx/worktrees/REGISTRY.md",
        "Git tracking policy",
        "This repository tracks the skill framework itself",
        "README.zh-CN.md",
        "keep `.omx/` ignored",
        "stable research documents and experiment contracts",
        "Update this skill",
        "scripts/update_installed_skill.sh",
        "init_research_workspace.py",
        "init_workstream.py",
        "update_workstream_state.py",
        "resolve_workflow.py",
        "prepare_worktree_closeout.py",
        "check_regression_fixtures.py",
        "--phase completion-handoff",
        "--dry-run",
        "--keep-backups",
        "git pull --ff-only",
        "--symlink",
        "rsync -a --delete",
        "one seed per subagent/team lane",
        "This skill is a workflow, not just a logging template",
        "method implementation",
        "baseline reproduction",
        "Run directories are raw evidence",
        "portfolio control plane",
        "Before creating a new slug",
        "$deep-interview --autoresearch -> $ralplan -> $autoresearch",
        "ralplan PRD/test spec",
        "autoresearch state/completion artifact",
        "root `INDEX.md`",
        "IDEA_SCOUTING.md",
        "falsifiable hypothesis",
        "novelty risk",
        "experiment completion handoff",
        "report-before-merge",
        "persist valuable or user-requested content",
        "project-root docs",
        "Optional feedback memory",
        "assets/templates/",
        "validate_research_workspace.py",
        "Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default",
        "$ai-research-workflow --feedback-memory",
        "$ai-research-workflow --qa-capture",
        "$ai-research-workflow --growth-review",
        "$ai-research-workflow --no-feedback",
        ".omx/ai-research/CONFIG.md",
        "feedback_memory: off | lite | full",
        "qa_capture: off | research | all",
        "growth_review: off | milestone | always",
        "`LEARNINGS.md`",
        "`QUESTIONS.md`",
        "raw logs and run outputs stay under `runs/`",
        "STATE.json",
        "CLAIMS.md",
        "baseline fairness checklist",
        "negative/inconclusive result policy",
    ],
    "references/artifact-contracts.md": [
        "SCRIPT_REGISTRY.md",
        "Project-local commands/scripts",
        "not the presence of a bundled publisher",
        "Portfolio artifacts",
        "workstream registry",
        "New-workstream decision log",
        "New workstream mandatory workflow gate",
        "mandatory workflow gate evidence",
        ".omx/plans/prd-<slug>.md",
        "experiment completion handoff trigger",
        "valuable or user-requested content",
        "seed-to-device/resource allocation",
        "Control plane vs project-root outputs",
        "## Contents",
        "Idea scouting artifact",
        "assets/templates/IDEA_SCOUTING.md",
        "Idea promotion gate",
        "Use the Markdown templates in `assets/templates/`",
        "scripts/init_research_workspace.py",
        "scripts/init_workstream.py",
        "scripts/update_workstream_state.py",
        "assets/fixtures/research_workspace_cases.json",
        "scripts/check_regression_fixtures.py",
        "`STATE.json` minimum fields",
        "`CLAIMS.md` minimum sections",
        "Baseline fairness checklist",
        "Negative / inconclusive result policy",
        "Run distillation contract",
        "report-before-merge closeout plan",
        "Project-root files are the implementation plane",
        "Optional feedback memory artifacts",
        "Optional question capture artifacts",
        "Research Feedback Memory, Question Capture, and Researcher Growth Review are opt-in",
        "disabled by default",
        "Precedence is: `--no-feedback`, explicit enable flags, `.omx/ai-research/CONFIG.md`, then default off.",
        "`LEARNINGS.md` minimum sections",
        "`QUESTIONS.md` minimum sections",
        "Workstream `DESIGN.md` minimum sections when `feedback_memory` is `full`",
    ],
    "references/experiment-runtime-standards.md": [
        "contracts, not universal scripts",
        "## Contents",
        "project-local wrappers",
        "SCRIPT_REGISTRY.md",
        "Multi-seed and accelerator lane rules",
        "CUDA_VISIBLE_DEVICES",
        "seed-to-device allocation",
        "Terminal run distillation rules",
        "current experiment is done",
        "report a merge/cleanup plan",
        "user-requested content",
        "Update portfolio `.omx/ai-research/RESEARCH.md`",
        "Promote reusable method, baseline, config, or test changes to project-root files",
        "If Research Feedback Memory is enabled",
        "worktree closeout plan",
        "CLAIMS.md",
        "negative and inconclusive results",
        "optional Research Feedback Memory, Question Capture, or Researcher Growth Review artifact paths",
    ],
    "references/idea-scouting.md": [
        "Idea Scouting",
        "optional and is not the default path",
        "`--idea-scouting`",
        "idea_scouting: auto",
        "assets/templates/IDEA_SCOUTING.md",
        "falsifiable hypothesis",
        "evaluation metric",
        "lightweight evidence",
        "novelty-risk note",
        "feasibility budget",
        "user-goal fit",
        "must ask before",
    ],
    "references/project-local-script-registry.md": [
        "framework-first",
        "Create scripts only when the current project needs them",
        "Completion handoff updates",
        "Do not leave useful script knowledge only in chat",
        "maintenance scripts",
        "thin orchestration wrappers",
        "method code, baseline code, configs, tests",
    ],
    "references/research-quality-gates.md": [
        "SCRIPT_REGISTRY.md",
        "## Contents",
        "project-local wrapper scripts",
        "phase-aware validator",
        "Claim ledger gate",
        "baseline fairness checklist",
        "Negative/inconclusive result policy",
        "`STATE.json` records the current phase",
        "idle GPU/device",
        "seed-to-device/resource assignments",
        "Idea scouting gate",
        "Workflow gate",
        "New workstream gate",
        "Fail closed",
        "do not create the new slug",
        "Portfolio `.omx/ai-research/RESEARCH.md`",
        "Portfolio `.omx/ai-research/INDEX.md`",
        "Existing workstreams were checked",
        "Implementation gate",
        "Experiment completion handoff gate",
        "report-before-merge closeout plan",
        "valuable or user-requested content",
        "Distilled updates outside `runs/`",
        "Optional feedback memory gate",
        "Optional question capture gate",
        "Optional growth review gate",
        "When Research Feedback Memory is disabled by default or by `--no-feedback`, skip this gate",
        "When Question Capture is disabled by default or by `--no-feedback`, skip this gate",
    ],
    "references/workflow-orchestration.md": [
        "Default OMX sequence",
        "## Contents",
        "Deterministic routing helpers",
        "resolve_workflow.py",
        "init_research_workspace.py",
        "init_workstream.py",
        "update_workstream_state.py",
        "--phase new-workstream",
        "Optional idea scouting",
        "IDEA_SCOUTING.md",
        "Optional feedback mode resolution",
        "Question Capture is disabled by default",
        "feedback_memory: off | lite | full",
        "workflow_preset: conservative | guided | autonomous",
        "idea_scouting: auto | off | on",
        "completion_handoff: auto | off",
        "worktree_closeout: off | report-before-merge",
        "qa_capture: off | research | all",
        "growth_review: off | milestone | always",
        "Feedback writes happen at natural workflow boundaries",
        "question-capture.md",
        "Portfolio and workstream control plane",
        "portfolio RESEARCH.md / INDEX.md check",
        "Before creating a new slug",
        "New workstream mandatory workflow gate",
        "The gate blocks creating `.omx/ai-research/<slug>/`",
        "Control plane vs project implementation plane",
        "Run distillation rule",
        "experiment completion handoff signal",
        "report-before-merge closeout plan",
        "report the paths written",
        "Baseline and method work",
        "$deep-interview --autoresearch",
        "$ralplan",
        "$autoresearch",
    ],
    "references/worktree-development.md": [
        "Worktree-based Task Execution",
        "## Contents",
        "substantive AI research work in a target project repository",
        "target project repository before editing",
        ".omx/worktrees/REGISTRY.md",
        "non-overlapping write scopes",
        "git rerere",
        "Lore-format commit",
        "Preflight local git state",
        "Completion handoff closeout",
        "prepare_worktree_closeout.py",
        "report-before-merge",
        "split them into semantic commits",
        "git push -u origin omx/<scope>",
    ],
    "scripts/update_installed_skill.sh": [
        "update_installed_skill.sh",
        "--no-pull",
        "--symlink",
        "--dry-run",
        "--keep-backups",
        "source commit",
        "git pull --ff-only",
        "rsync -a --delete",
        "validate_framework_contract.py",
        "quick_validate.py",
    ],
    "scripts/resolve_workflow.py": [
        "resolve_workflow.py",
        "workflow_preset",
        "idea_scouting",
        "completion_handoff",
        "worktree_closeout",
        "report_before_merge_closeout",
        "ask_required",
        "schema_version",
    ],
    "scripts/init_research_workspace.py": [
        "init_research_workspace.py",
        "portfolio workspace",
        "workflow_preset",
        "schema_version: 1",
        "IDEA_SCOUTING.md",
        "does not create a new workstream",
        "--dry-run",
    ],
    "scripts/init_workstream.py": [
        "init_workstream.py",
        "gate evidence",
        "does not run",
        "deep_interview_autoresearch",
        "ralplan_prd",
        "autoresearch_result",
        "Workstream initialized",
    ],
    "scripts/update_workstream_state.py": [
        "update_workstream_state.py",
        "STATE.json",
        "VALID_PHASES",
        "--phase",
        "--next-action",
        "--dry-run",
    ],
    "scripts/prepare_worktree_closeout.py": [
        "prepare_worktree_closeout.py",
        "report-before-merge",
        "does not merge",
        "commands_pending_user_confirmation",
        "worktree closeout plan",
    ],
    "scripts/check_regression_fixtures.py": [
        "check_regression_fixtures.py",
        "research_workspace_cases.json",
        "validate_research_workspace.py",
        "Regression fixtures passed",
    ],
    "assets/fixtures/research_workspace_cases.json": [
        "valid-guided-portfolio",
        "invalid-preset",
        "valid-idea-scouting-phase",
        "invalid-new-workstream-gate",
        "valid-completion-handoff-phase",
        "legacy-workstream-warns-not-fails",
        "targeted-completion-allows-legacy-sibling",
        "new-workstream-index-evidence-is-slug-specific",
        "invalid-state-slug-mismatch",
    ],
    "assets/templates/STATE.json": [
        "schema_version",
        "workstream_slug",
        "phase",
        "gate_evidence",
        "confirmation_required_before",
    ],
    "assets/templates/CLAIMS.md": [
        "Claims Ledger",
        "Evidence Requirements",
        "Negative or Inconclusive Results",
        "Retired or Downgraded Claims",
        "Allowed wording",
        "Forbidden wording",
    ],
    "references/question-capture.md": [
        "Question Capture",
        "disabled by default",
        "`--qa-capture`",
        "qa_capture: off | research | all",
        "What Counts As A Question",
        "Do not capture",
        ".omx/ai-research/QUESTIONS.md",
        ".omx/ai-research/<slug>/QUESTIONS.md",
        "assets/templates/QUESTIONS.md",
        "Answer the user first",
        "Hook Boundary",
        "UserPromptSubmit",
    ],
}

ALLOWED_SKILL_SCRIPT_PATTERNS = [
    re.compile(r"^validate_[a-z0-9_]+\.py$"),
    re.compile(r"^check_[a-z0-9_]+\.py$"),
    re.compile(r"^resolve_[a-z0-9_]+\.py$"),
    re.compile(r"^init_[a-z0-9_]+\.py$"),
    re.compile(r"^prepare_[a-z0-9_]+\.py$"),
    re.compile(r"^update_[a-z0-9_]+\.py$"),
    re.compile(r"^update_[a-z0-9_]+\.sh$"),
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
