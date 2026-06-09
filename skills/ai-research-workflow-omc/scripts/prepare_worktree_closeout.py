#!/usr/bin/env python3
"""Prepare a report-before-merge worktree closeout plan.

Script: prepare_worktree_closeout.py.

This is a read-only framework guardrail. It inspects git state and prints a
plan; it does not merge, push, remove worktrees, delete branches, run
experiments, collect metrics, or publish docs.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_out(repo: Path, *args: str, default: str = "") -> str:
    proc = git(repo, *args)
    if proc.returncode != 0:
        return default
    return proc.stdout.strip()


def require_git_root(path: Path) -> Path:
    proc = git(path, "rev-parse", "--show-toplevel")
    if proc.returncode != 0:
        print(proc.stderr.strip() or f"not a git repository: {path}", file=sys.stderr)
        raise SystemExit(proc.returncode or 1)
    return Path(proc.stdout.strip()).resolve()


def parse_worktrees(repo: Path) -> list[dict[str, str]]:
    proc = git(repo, "worktree", "list", "--porcelain")
    if proc.returncode != 0:
        return []
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        if key == "worktree" and current:
            entries.append(current)
            current = {}
        current[key] = value
    if current:
        entries.append(current)
    return entries


def default_base(repo: Path) -> str:
    origin_head = git_out(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    if origin_head.startswith("origin/"):
        return origin_head.removeprefix("origin/")
    for candidate in ("main", "master"):
        if git(repo, "rev-parse", "--verify", candidate).returncode == 0:
            return candidate
        if git(repo, "rev-parse", "--verify", f"origin/{candidate}").returncode == 0:
            return candidate
    return "main"


def compare_ref(repo: Path, base: str) -> str:
    if git(repo, "rev-parse", "--verify", f"origin/{base}").returncode == 0:
        return f"origin/{base}"
    if git(repo, "rev-parse", "--verify", base).returncode == 0:
        return base
    return ""


def registry_row(main_worktree: Path, worktree: Path, branch: str) -> str | None:
    registry = main_worktree / ".omc" / "worktrees" / "REGISTRY.md"
    if not registry.is_file():
        return None
    target_abs = str(worktree.resolve())
    target_rel = str(worktree.relative_to(main_worktree)) if worktree.is_relative_to(main_worktree) else target_abs
    for line in registry.read_text(encoding="utf-8").splitlines():
        if "|" not in line or "---" in line:
            continue
        if branch and branch in line:
            return line
        if target_abs in line or target_rel in line or f"`{target_rel}`" in line:
            return line
    return None


def quote_cmd(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def build_plan(worktree_arg: Path, base_arg: str | None, validation_paths: list[str]) -> dict[str, Any]:
    worktree = require_git_root(worktree_arg.resolve())
    entries = parse_worktrees(worktree)
    main_worktree = Path(entries[0]["worktree"]).resolve() if entries else worktree
    branch = git_out(worktree, "branch", "--show-current", default="DETACHED")
    head = git_out(worktree, "rev-parse", "--short", "HEAD", default="unknown")
    base_branch = base_arg or default_base(worktree)
    base_ref = compare_ref(worktree, base_branch)
    status = git_out(worktree, "status", "--short")
    dirty = bool(status.strip())
    upstream = git_out(worktree, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    commits = git_out(worktree, "log", "--oneline", f"{base_ref}..HEAD") if base_ref else ""
    unpushed = git_out(worktree, "log", "--oneline", f"{upstream}..HEAD") if upstream else commits
    remotes = git_out(worktree, "remote", "-v")
    registry = main_worktree / ".omc" / "worktrees" / "REGISTRY.md"
    row = registry_row(main_worktree, worktree, branch)
    validation = []
    for raw in validation_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = (worktree / path).resolve()
        validation.append({"path": str(path), "exists": path.exists()})

    blockers: list[str] = []
    if dirty:
        blockers.append("worktree has uncommitted changes; commit or discard before merge-back")
    if branch in {"", "DETACHED"}:
        blockers.append("worktree is detached; create or identify a branch before closeout")
    if not base_ref:
        blockers.append(f"base branch/ref not found for comparison: {base_branch}")
    if registry.exists() and row is None:
        blockers.append(".omc/worktrees/REGISTRY.md exists but no matching row was found")
    if validation and not all(item["exists"] for item in validation):
        blockers.append("one or more supplied validation evidence paths do not exist")

    commands = {
        "fetch": quote_cmd(["git", "-C", str(main_worktree), "fetch", "origin"]),
        "switch_base": quote_cmd(["git", "-C", str(main_worktree), "switch", base_branch]),
        "merge": quote_cmd(["git", "-C", str(main_worktree), "merge", "--no-ff", branch]) if branch else "",
        "push_base": quote_cmd(["git", "-C", str(main_worktree), "push", "origin", base_branch]),
        "remove_worktree": quote_cmd(["git", "-C", str(main_worktree), "worktree", "remove", str(worktree)]),
        "delete_branch": quote_cmd(["git", "-C", str(main_worktree), "branch", "-d", branch]) if branch else "",
    }
    if branch and upstream:
        remote_name, _, remote_branch = upstream.partition("/")
        commands["push_task_branch"] = quote_cmd(["git", "-C", str(worktree), "push", remote_name, f"HEAD:{remote_branch}"])
    elif branch:
        commands["push_task_branch"] = quote_cmd(["git", "-C", str(worktree), "push", "-u", "origin", branch])

    return {
        "worktree_path": str(worktree),
        "main_worktree_path": str(main_worktree),
        "branch": branch,
        "head": head,
        "base_branch": base_branch,
        "base_ref": base_ref,
        "upstream": upstream or None,
        "dirty": dirty,
        "status_short": status.splitlines(),
        "commits_since_base": commits.splitlines() if commits else [],
        "unpushed_commits": unpushed.splitlines() if unpushed else [],
        "remotes": remotes.splitlines() if remotes else [],
        "registry_path": str(registry),
        "registry_row": row,
        "validation_evidence": validation,
        "blockers": blockers,
        "commands_pending_user_confirmation": commands,
    }


def markdown(plan: dict[str, Any]) -> str:
    blockers = plan["blockers"] or ["none detected by dry-run inspection"]
    commits = plan["commits_since_base"] or ["none detected"]
    unpushed = plan["unpushed_commits"] or ["none detected"]
    validation = plan["validation_evidence"] or []
    validation_lines = [f"- {item['path']}: {'exists' if item['exists'] else 'missing'}" for item in validation]
    if not validation_lines:
        validation_lines = ["- no validation evidence paths supplied; add test/log paths before final closeout"]
    commands = "\n".join(plan["commands_pending_user_confirmation"].values())
    return f"""# Worktree Closeout Plan

## Worktree State

- Worktree path: `{plan['worktree_path']}`
- Main worktree path: `{plan['main_worktree_path']}`
- Branch: `{plan['branch']}`
- Head: `{plan['head']}`
- Base branch / compare ref: `{plan['base_branch']}` / `{plan['base_ref'] or 'missing'}`
- Upstream: `{plan['upstream'] or 'none'}`
- Dirty: `{plan['dirty']}`
- Registry path: `{plan['registry_path']}`
- Registry row: {plan['registry_row'] or 'not found'}

## Semantic Commit Status

{chr(10).join(f'- {line}' for line in commits)}

## Unpushed Commits

{chr(10).join(f'- {line}' for line in unpushed)}

## Validation Evidence

{chr(10).join(validation_lines)}

## Blockers

{chr(10).join(f'- {line}' for line in blockers)}

## Commands Pending User Confirmation

Do not run these until the user confirms the report-before-merge plan.

```bash
{commands}
# After successful merge validation, update .omc/worktrees/REGISTRY.md to merged/removed.
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a read-only report-before-merge worktree closeout plan.")
    parser.add_argument("worktree", nargs="?", default=".", type=Path, help="Task worktree path. Defaults to cwd.")
    parser.add_argument("--base", help="Base branch for merge-back. Defaults to origin HEAD, main, or master.")
    parser.add_argument("--validation", action="append", default=[], help="Validation evidence path to include. Repeatable.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--output", type=Path, help="Optional file to write the plan to.")
    args = parser.parse_args()

    plan = build_plan(args.worktree, args.base, args.validation)
    text = json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) if args.json else markdown(plan)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote worktree closeout plan: {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
