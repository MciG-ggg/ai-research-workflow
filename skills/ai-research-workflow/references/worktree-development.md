# Worktree-based Framework Development

Use this reference when updating the `ai-research-workflow` skill itself. It is not part of a user's AI research experiment workflow.

## Goal

Different framework changes should happen in isolated git worktrees so unrelated edits do not collide. The leader owns task decomposition, conflict avoidance, serial merge-back, and cleanup.

## Worktree location and registry

Default location:

```text
<repo>/.omx/worktrees/
```

If `.omx/worktrees/` cannot be created, use a writable fallback such as `~/omx-worktrees/<repo-name>/` and still record the absolute path in `<repo>/.omx/worktrees/REGISTRY.md` when possible.

Maintain a local, gitignored registry:

```text
.omx/worktrees/REGISTRY.md
```

Minimum registry fields:

```markdown
| Worktree | Branch | Scope | Files/areas | Status |
| --- | --- | --- | --- | --- |
| `.omx/worktrees/worktree-dev-policy` | `omx/worktree-dev-policy` | Add worktree workflow guidance | `SKILL.md`, `references/worktree-development.md` | in-progress |
```

Update `Status` through `in-progress -> merged -> removed` or `blocked`.

## Conflict-minimizing task design

Before starting parallel framework changes:

1. Split by aspect and file ownership. Prefer one branch per reference file, script, README section, or validation lane.
2. Assign non-overlapping write scopes. Avoid two worktrees editing `SKILL.md` or the same reference file at the same time unless one is explicitly the integrator.
3. Put shared append points behind stable markers or separate reference files instead of editing the same paragraph.
4. Rebase each worktree on the current main branch before final validation and merge-back.
5. Merge branches back serially, one worktree at a time. Validate after every merge.
6. Enable `git rerere` for repeated conflict patterns when safe:

```bash
git config rerere.enabled true
```

## Standard lifecycle

```bash
# from the main worktree
git status --short
git fetch origin
git switch main
git pull --ff-only
mkdir -p .omx/worktrees
git worktree add -b omx/<scope> .omx/worktrees/<scope> main
```

Inside the isolated worktree:

```bash
# edit only the assigned scope
git status --short
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
git commit
```

Merge back serially from the main worktree:

```bash
git switch main
git merge --no-ff omx/<scope>
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
rsync -a --delete skills/ai-research-workflow/ ~/.codex/skills/ai-research-workflow/
git push origin main
```

Cleanup after merge:

```bash
git worktree remove .omx/worktrees/<scope>
git branch -d omx/<scope>
```

Then mark the registry row `removed` or keep a short completed history entry.

## Conflict resolution rules

- Prefer prevention over merge heroics: narrower write scopes, serial merges, and reference-file splits.
- If a conflict occurs, resolve only the branch being merged into main; do not mix multiple branches in one conflict session.
- Preserve both valid changes when they are additive, then simplify once tests pass.
- Run validation after conflict resolution before continuing to the next branch.
- If a worker auto-checkpoint commit appears, rewrite or squash it into a Lore-format commit before merge-back.
