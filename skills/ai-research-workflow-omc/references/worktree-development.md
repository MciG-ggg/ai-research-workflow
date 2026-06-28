# Worktree-based Task Execution

Use this reference when the skill is asked to do substantive AI research work in a target project repository. The goal is to keep each research task isolated, reduce merge conflicts, and make merge-back reviewable.

## Contents

- [When to open a worktree](#when-to-open-a-worktree)
- [Worktree location and registry](#worktree-location-and-registry)
- [Conflict-minimizing task design](#conflict-minimizing-task-design)
- [Standard lifecycle](#standard-lifecycle)
- [Completion handoff closeout](#completion-handoff-closeout)
- [Conflict resolution rules](#conflict-resolution-rules)

## When to open a worktree

Open a task worktree in the target project repository before editing for:

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
<repo>/.omc/worktrees/<scope>/
```

If `.omc/worktrees/` cannot be created, use a writable fallback such as `~/omx-worktrees/<repo-name>/<scope>/` and still record the absolute path in `<repo>/.omc/worktrees/REGISTRY.md` when possible.

Maintain a local, gitignored registry in the target repo:

```text
.omc/worktrees/REGISTRY.md
```

Minimum registry fields:

```markdown
| Worktree | Branch | Scope | Files/areas | Status |
| --- | --- | --- | --- | --- |
| `.omc/worktrees/experiment-design` | `omc/experiment-design` | Draft experiment protocol | `EXPERIMENT.md`, `SCRIPT_REGISTRY.md` | in-progress |
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

### Preflight local git state

Before opening a new worktree, inspect the main worktree and protect any existing local work:

```bash
# from the main worktree of the target repo
git status --short
git diff --stat
git diff --cached --stat
```

If there are modifications, split them into semantic commits before creating the task worktree. Do not mix unrelated edits just because they are already present. Use `git diff`, `git diff --cached`, and path-level staging to group changes by intent, then commit each group with a Lore-format message:

```bash
git add <paths-for-one-semantic-change>
git commit
```

If a change is incomplete but must be preserved before worktree creation, make the commit message say that explicitly with `Confidence: low` or a `Not-tested:` trailer. Do not stash and forget local work unless the user explicitly asked for a temporary stash workflow.

After the main worktree is clean, update the primary branch and create the task worktree from the latest commit:

```bash
# from the main worktree of the target repo
git status --short
git fetch origin
git switch main
git pull --ff-only
mkdir -p .omc/worktrees
git worktree add -b omc/<scope> .omc/worktrees/<scope> HEAD
```

If `worktree_closeout: report-before-merge` is active, treat the push, merge, and cleanup commands below as the closeout plan until the user confirms them.

Inside the isolated worktree:

```bash
# edit only the assigned scope
git status --short
# run project-appropriate tests or skill validators
git commit
git push -u origin omc/<scope>
```

Merge back serially from the main worktree:

```bash
git switch main
git merge --no-ff omc/<scope>
# run validation after merge
git push origin main
```

Cleanup after merge:

```bash
git worktree remove .omc/worktrees/<scope>
git branch -d omc/<scope>
```

Then mark the registry row `removed` or keep a short completed history entry.

## Completion handoff closeout

When the user says a workstream or experiment is done, do not stop after run/script distillation if the work happened in a task worktree.

Default behavior is report-before-merge:

1. Inspect the task worktree status, branch, base branch, commits, and validation evidence.
2. Ensure useful run/script/result/reproducibility artifacts were already distilled.
3. Write a closeout plan in `RUNS.md`, `REPRODUCIBILITY.md`, project-root docs, or `.omc/worktrees/REGISTRY.md` as appropriate.
4. Report the exact merge-back, push, worktree removal, branch deletion, and registry-update plan.
5. Wait for user confirmation before running merge, push, `git worktree remove`, or branch deletion commands.

Use the read-only framework guardrail script when available:

```bash
python3 scripts/prepare_worktree_closeout.py <task-worktree> --base main --validation <path>
```

`prepare_worktree_closeout.py` prints a report-before-merge plan and blockers; it must not merge, push, remove a worktree, or delete a branch.

The closeout plan must include:

- worktree path and branch
- base branch / merge target
- semantic Lore-format commit status
- validation already run and validation still required
- merge or rebase command plan
- push target
- cleanup commands for worktree and branch
- `.omc/worktrees/REGISTRY.md` status update
- blockers such as conflicts, dirty worktree, missing validation, or unpushed commits

If the user explicitly confirms the closeout plan, merge back serially, validate after merge, push, remove the worktree, delete the branch when safe, and mark the registry row `removed`.

## Conflict resolution rules

- Prefer prevention over merge heroics: narrower write scopes, serial merges, and file/area ownership.
- If a conflict occurs, resolve only the branch being merged into main; do not mix multiple branches in one conflict session.
- Preserve both valid changes when they are additive, then simplify once tests pass.
- Run validation after conflict resolution before continuing to the next branch.
- If a worker auto-checkpoint commit appears, rewrite or squash it into a Lore-format commit before merge-back.

## Workstream closeout plan

Worktree closeout and workstream closeout are related but distinct:

- `scripts/prepare_workstream_closeout.py <project-root> <slug> --write` writes `.ai-research-workflow/<slug>/CLOSEOUT.md` with completion-handoff artifacts, validation evidence, run/script inventory, blockers, and confirmation boundaries.
- `scripts/prepare_worktree_closeout.py <task-worktree> --base <branch>` inspects git worktree state and prints merge/push/remove/delete commands that remain pending user confirmation.

Run the workstream closeout first to ensure research evidence is distilled. Then run the worktree closeout to plan git lifecycle cleanup. Neither script should execute merge, push, worktree removal, or branch deletion.
