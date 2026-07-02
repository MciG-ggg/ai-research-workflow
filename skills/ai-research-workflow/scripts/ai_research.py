#!/usr/bin/env python3
"""Unified CLI facade for ai-research-workflow guardrail scripts.

Script: ai_research.py.

This facade dispatches to maintenance-only framework helpers. It does not run
experiments, collect metrics, plot results, publish research docs, merge
branches, push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

SCRIPT_COMMANDS = {
    "init": "init_research_workspace.py",
    "init-workspace": "init_research_workspace.py",
    "new-workstream": "init_workstream.py",
    "workstream": "init_workstream.py",
    "resolve": "resolve_workflow.py",
    "summarize": "summarize_research_state.py",
    "summary": "summarize_research_state.py",
    "score": "score_research_artifacts.py",
    "review": "score_research_artifacts.py",
    "qa": "capture_question.py",
    "capture-question": "capture_question.py",
    "hook": "question_capture_hook.py",
    "handoff": "prepare_workstream_closeout.py",
    "closeout": "prepare_workstream_closeout.py",
    "worktree-closeout": "prepare_worktree_closeout.py",
    "negative-result": "preserve_negative_result.py",
    "draft": "generate_report_outline.py",
    "validate": "validate_research_workspace.py",
    "schema": "validate_research_schema.py",
    "evidence-graph": "build_evidence_graph.py",
    "graph": "build_evidence_graph.py",
    "migrate": "migrate_research_workspace.py",
    "version": "check_skill_update.py",
    "update-check": "check_skill_update.py",
    "e2e": "run_e2e_scenarios.py",
    "fixtures": "check_regression_fixtures.py",
    "recall": "recall.py",
    "run-purposes": "validate_run_purposes.py",
}

ROUTE_ONLY = {"scout", "papers", "reproduce-paper", "experiment", "route", "commands"}

EXAMPLES = """
If you want X, say Y:
  Start a portfolio:          ai_research.py init <project-root> --preset guided
  Route a vague idea:         ai_research.py resolve <project-root> --prompt "generate candidate ideas"
  Scout ideas:                ai_research.py scout <project-root> --prompt "broad AI research direction"
  Maintain paper registry:    ai_research.py papers <project-root> --prompt "find SOTA and baseline papers"
  Reproduce one paper:        ai_research.py reproduce-paper <project-root> --prompt "reproduce this paper to find ideas"
  Open experiment campaign:   ai_research.py experiment <project-root> --prompt "run an ablation experiment campaign"
  Create a gated workstream:  ai_research.py new-workstream <project-root> <slug> --title ... --question ... --deep-interview ... --ralplan-prd ... --ralplan-test-spec ... --autoresearch-result ...
  Capture a Q&A:              ai_research.py qa <project-root> --question ... --answer-summary ...
  Close a finished stream:    ai_research.py handoff <project-root> <slug> --write
  Preserve a failed result:   ai_research.py negative-result <project-root> <slug> --finding ... --evidence ... --interpretation ... --claim-update ...
  Check schemas:              ai_research.py schema <project-root>
  Build evidence graph:       ai_research.py graph <project-root> <slug> --json
  Recall experiments/decisions: ai_research.py recall <project-root> [--query TEXT] [--slug SLUG] [--json]
  Validate per-run purpose.md:  ai_research.py run-purposes <project-root> [--strict]
  Check installed version:    ai_research.py update-check
"""


def dispatch(script: str, args: list[str]) -> int:
    path = SCRIPT_DIR / script
    if not path.is_file():
        print(f"missing helper script: {path}", file=sys.stderr)
        return 1
    proc = subprocess.run([sys.executable, str(path), *args], check=False)
    return int(proc.returncode)


def print_help() -> None:
    commands = ", ".join(sorted(set(SCRIPT_COMMANDS) | ROUTE_ONLY))
    print("ai_research.py — unified facade for ai-research-workflow guardrails")
    print()
    print("Usage: ai_research.py <command> [args passed to helper]")
    print()
    print(f"Commands: {commands}")
    print(EXAMPLES.strip())


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("command", nargs="?")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parsed = parser.parse_args()

    command = (parsed.command or "help").lower().replace("_", "-")
    if command in {"help", "--help", "-h"}:
        print_help()
        return 0
    if command in ROUTE_ONLY:
        route_args = list(parsed.args)
        if command == "scout" and "--command" not in route_args:
            route_args.extend(["--command", "scout"])
        if command == "papers" and "--command" not in route_args:
            route_args.extend(["--command", "papers"])
        if command == "reproduce-paper" and "--command" not in route_args:
            route_args.extend(["--command", "reproduce-paper"])
        if command == "experiment" and "--command" not in route_args:
            route_args.extend(["--command", "experiment"])
        return dispatch("resolve_workflow.py", route_args)
    script = SCRIPT_COMMANDS.get(command)
    if script is None:
        print(f"unknown ai_research.py command: {command}\n", file=sys.stderr)
        print_help()
        return 2
    return dispatch(script, list(parsed.args))


if __name__ == "__main__":
    raise SystemExit(main())
