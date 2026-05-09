#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: update_installed_skill.sh [--no-pull] [--symlink] [--dest DIR]

Safely update the installed ai-research-workflow skill from this repository.

Default behavior:
  1. require a clean git worktree
  2. git pull --ff-only
  3. validate the source skill
  4. sync to ~/.codex/skills/ai-research-workflow via a staged rsync
  5. validate the installed copy

Options:
  --no-pull   Skip git pull; useful while validating local edits.
  --symlink   Replace the installed skill with a symlink to this repo's skill dir.
  --dest DIR  Install destination. Defaults to ${CODEX_HOME:-~/.codex}/skills/ai-research-workflow.
EOF
}

NO_PULL=0
SYMLINK=0
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd -- "${SKILL_DIR}/../.." && pwd)"
CODEX_HOME_DIR="${CODEX_HOME:-"${HOME}/.codex"}"
DEST="${CODEX_HOME_DIR}/skills/ai-research-workflow"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-pull)
      NO_PULL=1
      shift
      ;;
    --symlink)
      SYMLINK=1
      shift
      ;;
    --dest)
      DEST="${2:?--dest requires a directory}"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

quick_validate() {
  local target="$1"
  local quick="${CODEX_HOME_DIR}/skills/.system/skill-creator/scripts/quick_validate.py"
  if [[ -f "$quick" ]]; then
    python3 "$quick" "$target"
  else
    echo "warning: quick_validate.py not found at $quick; skipping" >&2
  fi
}

framework_validate() {
  local target="$1"
  python3 "$target/scripts/validate_framework_contract.py" "$target"
}

if [[ ! -d "$SKILL_DIR" || ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo "Could not locate source skill at $SKILL_DIR" >&2
  exit 1
fi

if [[ "$NO_PULL" -eq 0 && -d "$REPO_ROOT/.git" ]]; then
  cd "$REPO_ROOT"
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Refusing to update with local repository modifications. Commit/stash them or rerun with --no-pull." >&2
    exit 1
  fi
  git pull --ff-only
fi

echo "Validating source skill: $SKILL_DIR"
quick_validate "$SKILL_DIR"
framework_validate "$SKILL_DIR"

if [[ "$SYMLINK" -eq 1 ]]; then
  mkdir -p "$(dirname "$DEST")"
  if [[ -e "$DEST" || -L "$DEST" ]]; then
    backup="${DEST}.backup.$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$DEST" "$backup"
    echo "Backed up existing install to $backup"
  fi
  ln -s "$SKILL_DIR" "$DEST"
  echo "Installed symlink: $DEST -> $SKILL_DIR"
  quick_validate "$DEST"
  framework_validate "$DEST"
  echo "Skill symlink install valid."
  exit 0
fi

DEST_PARENT="$(dirname "$DEST")"
mkdir -p "$DEST_PARENT"
TMP_DIR="$(mktemp -d "${DEST_PARENT}/.ai-research-workflow.tmp.XXXXXX")"
BACKUP_DIR=""

cleanup() {
  if [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]]; then
    rm -rf "$TMP_DIR"
  fi
}
trap cleanup EXIT

rsync -a --delete "${SKILL_DIR}/" "${TMP_DIR}/"

echo "Validating staged install: $TMP_DIR"
quick_validate "$TMP_DIR"
framework_validate "$TMP_DIR"

if [[ -e "$DEST" || -L "$DEST" ]]; then
  BACKUP_DIR="${DEST}.backup.$(date -u +%Y%m%dT%H%M%SZ)"
  mv "$DEST" "$BACKUP_DIR"
fi

mv "$TMP_DIR" "$DEST"
TMP_DIR=""

if ! quick_validate "$DEST" || ! framework_validate "$DEST"; then
  echo "Installed validation failed; restoring backup if available." >&2
  rm -rf "$DEST"
  if [[ -n "$BACKUP_DIR" && -e "$BACKUP_DIR" ]]; then
    mv "$BACKUP_DIR" "$DEST"
  fi
  exit 1
fi

if [[ -n "$BACKUP_DIR" && -e "$BACKUP_DIR" ]]; then
  rm -rf "$BACKUP_DIR"
fi

echo "Skill updated successfully: $DEST"
