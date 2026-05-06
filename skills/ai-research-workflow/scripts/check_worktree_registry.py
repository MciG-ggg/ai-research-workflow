#!/usr/bin/env python3
"""Check local worktree registry entries for framework maintenance.

This is maintenance-only tooling for this skill repository. It does not manage
user research experiment worktrees.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$")


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def parse_rows(registry: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in registry.read_text(encoding="utf-8").splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        cells = [cell.strip().strip("`") for cell in match.groups()]
        if cells[0].lower() == "worktree" or set(cells[0]) == {"-"}:
            continue
        rows.append(
            {
                "worktree": cells[0],
                "branch": cells[1],
                "scope": cells[2],
                "files": cells[3],
                "status": cells[4],
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Check .omx/worktrees/REGISTRY.md against git worktree state.")
    parser.add_argument("repo", nargs="?", default=".", type=Path, help="Repository root. Defaults to current directory.")
    args = parser.parse_args()
    repo = args.repo.resolve()
    registry = repo / ".omx" / "worktrees" / "REGISTRY.md"

    if not registry.is_file():
        print(f"No local worktree registry found; skipped: {registry}")
        return 0

    worktree_proc = run_git(repo, "worktree", "list", "--porcelain")
    if worktree_proc.returncode != 0:
        print(worktree_proc.stderr.strip(), file=sys.stderr)
        return worktree_proc.returncode

    listed_paths = set()
    for line in worktree_proc.stdout.splitlines():
        if line.startswith("worktree "):
            listed_paths.add(Path(line.removeprefix("worktree ")).resolve())

    errors: list[str] = []
    for row in parse_rows(registry):
        status = row["status"].lower()
        if status in {"removed", "merged", "blocked"}:
            continue
        path_text = row["worktree"]
        path = Path(path_text)
        if not path.is_absolute():
            path = (repo / path).resolve()
        if path not in listed_paths:
            errors.append(f"active registry row is not in git worktree list: {path_text} ({row['branch']})")
        if not row["scope"] or row["scope"] == "-":
            errors.append(f"registry row missing scope: {path_text}")
        if not row["files"] or row["files"] == "-":
            errors.append(f"registry row missing file/area ownership: {path_text}")

    if errors:
        print("Worktree registry check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Worktree registry valid: {registry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
