#!/usr/bin/env python3
"""Report ai-research-workflow source/installed/remote update status.

Script: check_skill_update.py.

This is read-only framework maintenance tooling by default. It does not modify
files, run experiments, collect metrics, plot results, publish docs, merge
branches, push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[1]


def read_version(skill_dir: Path) -> str | None:
    path = skill_dir / "assets" / "VERSION"
    return path.read_text(encoding="utf-8").strip() if path.is_file() else None


def git_output(args: list[str], cwd: Path) -> str | None:
    try:
        proc = subprocess.run(["git", *args], cwd=str(cwd), text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False)
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def installed_mode(path: Path) -> str:
    if path.is_symlink():
        return f"symlink -> {path.resolve()}"
    if path.is_dir():
        return "copied directory"
    return "absent"


def remote_head(remote_url: str | None, cwd: Path) -> str | None:
    target = remote_url or "origin"
    output = git_output(["ls-remote", target, "HEAD"], cwd)
    if not output:
        return None
    return output.split()[0][:12]


def status(installed_dir: Path, *, check_remote: bool, remote_url: str | None) -> dict[str, Any]:
    source_commit = git_output(["rev-parse", "--short", "HEAD"], REPO_ROOT)
    source_dirty = bool(git_output(["status", "--porcelain"], REPO_ROOT))
    result = {
        "source_skill": str(SKILL_DIR),
        "source_repo": str(REPO_ROOT),
        "source_version": read_version(SKILL_DIR),
        "source_commit": source_commit,
        "source_dirty": source_dirty,
        "installed_dir": str(installed_dir),
        "installed_mode": installed_mode(installed_dir),
        "installed_version": read_version(installed_dir) if installed_dir.exists() else None,
        "installed_matches_source_version": False,
        "remote_checked": check_remote,
        "remote_head": None,
        "update_command": "./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh",
    }
    result["installed_matches_source_version"] = bool(result["source_version"] and result["source_version"] == result["installed_version"])
    if check_remote:
        result["remote_head"] = remote_head(remote_url, REPO_ROOT)
    return result


def markdown(result: dict[str, Any]) -> str:
    return f"""# ai-research-workflow Update Status

- Source skill: `{result['source_skill']}`
- Source version: `{result['source_version'] or 'unknown'}`
- Source commit: `{result['source_commit'] or 'unknown'}`
- Source dirty: `{result['source_dirty']}`
- Installed skill: `{result['installed_dir']}`
- Installed mode: `{result['installed_mode']}`
- Installed version: `{result['installed_version'] or 'unknown'}`
- Installed matches source version: `{result['installed_matches_source_version']}`
- Remote checked: `{result['remote_checked']}`
- Remote HEAD: `{result['remote_head'] or 'not checked'}`

To update the installed copy, run `{result['update_command']}` from the repository root. Use `--no-pull` for local validation, `--dry-run` to preview, or `--symlink` for development.
"""


def main() -> int:
    default_dest = Path.home() / ".claude" / "skills" / "ai-research-workflow"
    parser = argparse.ArgumentParser(description="Check source/installed/remote ai-research-workflow version status.")
    parser.add_argument("--installed-dir", type=Path, default=default_dest, help="Installed skill directory. Defaults to ~/.claude/skills/ai-research-workflow-omc.")
    parser.add_argument("--check-remote", action="store_true", help="Also run git ls-remote. Default is local-only/read-only.")
    parser.add_argument("--remote-url", help="Remote URL/name for --check-remote. Defaults to origin.")
    parser.add_argument("--fail-outdated", action="store_true", help="Exit 2 if installed VERSION differs from source VERSION.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    args = parser.parse_args()

    result = status(args.installed_dir.expanduser(), check_remote=args.check_remote, remote_url=args.remote_url)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(markdown(result), end="")
    if args.fail_outdated and not result["installed_matches_source_version"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
