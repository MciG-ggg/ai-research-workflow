# Worktree-based Task Execution

Use this reference when the skill is asked to do substantive work in any repository. The goal is to keep each task isolated, reduce merge conflicts, and make merge-back reviewable. Updating this skill repository itself is only a special case of the same rule.

## When to open a worktree

Open a task worktree before editing for:

- code changes
- documentation changes
- experiment setup or project-local scripts
- refactors, cleanup, or multi-file fixes
- result packaging or docs publishing work
- any parallel lane that could overlap with another agent's edits

Skip only for read-only analysis, quick lookups, or tiny safe edits that do not benefit from branch isolation.

## Worktree location and registry

Default location inside the target repo:

```text
<repo>/.omx/worktrees/<scope>/
```

If `.omx/worktrees/` cannot be created, use a writable fallback such as `~/omx-worktrees/<repo-name>/<scope>/` and still record the absolute path in `<repo>/.omx/worktrees/REGISTRY.md` when possible.

Maintain a local, gitignored registry in the target repo:

```text
.omx/worktrees/REGISTRY.md
```

Minimum registry fields:

```markdown
| Worktree | Branch | Scope | Files/areas | Status |
| --- | --- | --- | --- | --- |
| `.omx/worktrees/experiment-design` | `omx/experiment-design` | Draft experiment protocol | `EXPERIMENT.md`, `SCRIPT_REGISTRY.md` | in-progress |
```

Update `Status` through `in-progress -> merged -> removed` or `blocked`.

## Conflict-minimizing task design

Before starting parallel work:

1. Split by aspect and file ownership. Prefer one branch per independent task, module, reference file, script, or validation lane.
2. Assign non-overlapping write scopes. Avoid two worktrees editing the same file or same lines unless one is explicitly the integrator.
3. Put shared append points behind stable markers or separate files instead of editing the same paragraph.
4. Rebase each worktree on the current main branch before final validation and merge-back.
5. Merge branches back serially, one worktree at a time. Validate after every merge.
6. Enable `git rerere` for repeated conflict patterns when safe:

```bash
git config rerere.enabled true
```

## Standard lifecycle

```bash
# from the main worktree of the target repo
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
# run project-appropriate tests or skill validators
git commit
```

Merge back serially from the main worktree:

```bash
git switch main
git merge --no-ff omx/<scope>
# run validation after merge
git push origin main
```

Cleanup after merge:

```bash
git worktree remove .omx/worktrees/<scope>
git branch -d omx/<scope>
```

Then mark the registry row `removed` or keep a short completed history entry.

## Conflict resolution rules

- Prefer prevention over merge heroics: narrower write scopes, serial merges, and file/area ownership.
- If a conflict occurs, resolve only the branch being merged into main; do not mix multiple branches in one conflict session.
- Preserve both valid changes when they are additive, then simplify once tests pass.
- Run validation after conflict resolution before continuing to the next branch.
- If a worker auto-checkpoint commit appears, rewrite or squash it into a Lore-format commit before merge-back.

## Skill-repo special case

When the target repository is `ai-research-workflow` itself, use the same task worktree lifecycle, then run the skill maintenance validators and resync the installed copy:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
rsync -a --delete skills/ai-research-workflow/ ~/.codex/skills/ai-research-workflow/
```
