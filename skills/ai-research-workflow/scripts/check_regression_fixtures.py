#!/usr/bin/env python3
"""Run regression fixtures for validate_research_workspace.py.

Script: check_regression_fixtures.py.

This is maintenance-only framework testing. It does not run user experiments,
collect metrics, plot results, publish docs, merge branches, or delete
worktrees.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FIXTURE_PATH = SKILL_DIR / "assets" / "fixtures" / "research_workspace_cases.json"
VALIDATOR = SCRIPT_DIR / "validate_research_workspace.py"


def write_fixture(root: Path, case: dict[str, object]) -> None:
    for directory in case.get("dirs", []):
        (root / str(directory)).mkdir(parents=True, exist_ok=True)
    files = case.get("files", {})
    if not isinstance(files, dict):
        raise TypeError(f"fixture files must be an object for {case.get('name')}")
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(content), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ai-research-workflow regression fixtures.")
    parser.add_argument("--case", help="Run one fixture case by name.")
    args = parser.parse_args()

    cases = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    ran = 0
    with tempfile.TemporaryDirectory(prefix="ai-research-fixtures-") as tmp:
        tmp_root = Path(tmp)
        for case in cases:
            name = str(case["name"])
            if args.case and name != args.case:
                continue
            ran += 1
            project = tmp_root / name
            write_fixture(project, case)
            cmd = [sys.executable, str(VALIDATOR), str(project)] + [str(arg) for arg in case.get("args", [])]
            proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            expected = int(case["expect_exit"])
            if proc.returncode != expected:
                failures.append(
                    f"{name}: expected exit {expected}, got {proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
                )
            else:
                print(f"ok {name} -> exit {proc.returncode}")
    if args.case and ran == 0:
        print(f"No fixture case matched: {args.case}", file=sys.stderr)
        return 2
    if failures:
        print("Regression fixture failures:", file=sys.stderr)
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"Regression fixtures passed: {ran}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
