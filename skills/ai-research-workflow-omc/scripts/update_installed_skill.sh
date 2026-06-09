#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: update_installed_skill.sh [--no-pull] [--symlink] [--dry-run] [--keep-backups N] [--dest DIR]

Safely update the installed ai-research-workflow skill from this repository.

Default behavior:
  1. print source/install status
  2. require a clean git worktree
  3. git pull --ff-only
  4. validate the source skill
  5. sync to ~/.claude/skills/ai-research-workflow-omc via a staged rsync
  6. validate the installed copy
  7. keep the newest backup directories and remove older backups

Options:
  --no-pull         Skip git pull; useful while validating local edits.
  --symlink         Replace the installed skill with a symlink to this repo's skill dir.
  --dry-run         Validate and print the planned install without changing DEST.
  --keep-backups N  Keep N newest ${DEST}.backup.* directories. Defaults to 3.
  --dest DIR        Install destination. Defaults to ${CLAUDE_HOME:-~/.claude}/skills/ai-research-workflow-omc.
EOF
}

NO_PULL=0
SYMLINK=0
DRY_RUN=0
KEEP_BACKUPS=3
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd -- "${SKILL_DIR}/../.." && pwd)"
CLAUDE_HOME_DIR="${CLAUDE_HOME:-"${HOME}/.claude"}"
DEST="${CLAUDE_HOME_DIR}/skills/ai-research-workflow-omc"

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
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --keep-backups)
      KEEP_BACKUPS="${2:?--keep-backups requires a number}"
      shift 2
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

case "$KEEP_BACKUPS" in
  ''|*[!0-9]*)
    echo "--keep-backups must be a non-negative integer" >&2
    exit 2
    ;;
esac


framework_validate() {
  local target="$1"
  python3 "$target/scripts/validate_framework_contract.py" "$target"
}

source_commit() {
  if [[ -d "$REPO_ROOT/.git" ]]; then
    git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || true
  fi
}

installed_status() {
  if [[ -L "$DEST" ]]; then
    local link_target
    link_target="$(readlink "$DEST")"
    echo "installed mode: symlink -> $link_target"
    if git -C "$DEST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      echo "installed commit: $(git -C "$DEST" rev-parse --short HEAD 2>/dev/null || true)"
    else
      echo "installed commit: unavailable"
    fi
  elif [[ -d "$DEST" ]]; then
    echo "installed mode: copied directory"
    if git -C "$DEST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
      echo "installed commit: $(git -C "$DEST" rev-parse --short HEAD 2>/dev/null || true)"
    else
      echo "installed commit: unavailable (copied skill has no git metadata)"
    fi
  else
    echo "installed mode: absent"
  fi
}

cleanup_old_backups() {
  local keep="$1"
  local backup
  local count=0
  # shellcheck disable=SC2012
  for backup in $(ls -dt "${DEST}.backup."* 2>/dev/null || true); do
    count=$((count + 1))
    if [[ "$count" -gt "$keep" ]]; then
      rm -rf "$backup"
      echo "Removed old backup: $backup"
    fi
  done
}

if [[ ! -d "$SKILL_DIR" || ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo "Could not locate source skill at $SKILL_DIR" >&2
  exit 1
fi

printf 'source skill: %s\n' "$SKILL_DIR"
printf 'source commit: %s\n' "$(source_commit)"
installed_status

if [[ "$NO_PULL" -eq 0 && -d "$REPO_ROOT/.git" ]]; then
  cd "$REPO_ROOT"
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Refusing to update with local repository modifications. Commit/stash them or rerun with --no-pull." >&2
    exit 1
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "Dry run: would run git pull --ff-only"
  else
    git pull --ff-only
  fi
fi

echo "Validating source skill: $SKILL_DIR"
framework_validate "$SKILL_DIR"

if [[ "$SYMLINK" -eq 1 ]]; then
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "Dry run: would replace $DEST with symlink to $SKILL_DIR"
    exit 0
  fi
  mkdir -p "$(dirname "$DEST")"
  if [[ -e "$DEST" || -L "$DEST" ]]; then
    backup="${DEST}.backup.$(date -u +%Y%m%dT%H%M%SZ)"
    mv "$DEST" "$backup"
    echo "Backed up existing install to $backup"
  fi
  ln -s "$SKILL_DIR" "$DEST"
  echo "Installed symlink: $DEST -> $SKILL_DIR"
  framework_validate "$DEST"
  cleanup_old_backups "$KEEP_BACKUPS"
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
framework_validate "$TMP_DIR"

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "Dry run: would replace $DEST with validated staged install $TMP_DIR"
  echo "Dry run: would keep $KEEP_BACKUPS newest backup(s) matching ${DEST}.backup.*"
  exit 0
fi

if [[ -e "$DEST" || -L "$DEST" ]]; then
  BACKUP_DIR="${DEST}.backup.$(date -u +%Y%m%dT%H%M%SZ)"
  mv "$DEST" "$BACKUP_DIR"
fi

mv "$TMP_DIR" "$DEST"
TMP_DIR=""

if ! framework_validate "$DEST"; then
  echo "Installed validation failed; restoring backup if available." >&2
  rm -rf "$DEST"
  if [[ -n "$BACKUP_DIR" && -e "$BACKUP_DIR" ]]; then
    mv "$BACKUP_DIR" "$DEST"
  fi
  exit 1
fi

cleanup_old_backups "$KEEP_BACKUPS"

echo "Skill updated successfully: $DEST"
