# Project-local Script Registry

This skill is framework-first. Do not assume bundled Python scripts fit the user's project. Instead, record the scripts that the current project actually needs inside the research workspace.

Distinguish project scripts from skill maintenance scripts. Scripts shipped in this skill's own `scripts/` directory are for validating or maintaining the framework itself; do not register or invoke them as user research scripts.

## Location

For each research workspace, maintain project-local scripts and script metadata here:

```text
.ai-research-workflow/<slug>/
  SCRIPT_REGISTRY.md
  scripts/
    run_<name>.sh
    monitor_<name>.sh
    collect_metrics_<name>.<ext>
    plot_<name>.<ext>
    publish_docs_<name>.sh
```

Use `.sh` for shell orchestration and the project's native language for data processing or plotting (`.py`, `.R`, `.jl`, `.ipynb`, etc.). Prefer existing project runners when they already exist; record wrapper commands rather than replacing them.

These scripts are thin orchestration wrappers. Do not put the user's method implementation, baseline implementation, model code, dataset adapter, or production experiment logic here. Those belong in the project root using the repository's normal layout.

## Naming conventions

- `run_<experiment>.sh`: launch one experiment or one reproducible lane.
- `monitor_<experiment>.sh`: inspect tmux/session/log/summary progress.
- `collect_metrics_<experiment>.<ext>`: transform raw outputs into metrics files.
- `plot_<experiment>.<ext>`: generate figures from metrics/results.
- `publish_docs_<experiment>.sh`: copy settled artifacts into `docs/` and update or report MkDocs nav.

Use short, stable, lowercase names. Include variant/seed/dataset only when the script is specific to that lane.

## Registry entry template

Add one entry per script in `SCRIPT_REGISTRY.md`:

```markdown
## scripts/run_baseline.sh

- Purpose: Launch baseline evaluation in detached tmux.
- Owner phase: run-experiments
- Inputs: config path, dataset version, seed
- Outputs: run directory, combined.log, metrics.jsonl, summary.json, figures/
- Command: `bash .ai-research-workflow/<slug>/scripts/run_baseline.sh`
- Safe to rerun: yes/no; explain idempotency
- Dependencies: project tools, environment variables, credentials
- Status: draft|validated|deprecated
- Last validated: YYYY-MM-DD, command/log path
```

## Script creation rules

- Create scripts only when the current project needs them.
- Keep scripts thin: wrap existing project commands, logging, tmux launch, metrics extraction, plotting, or docs sync.
- Keep method code, baseline code, configs, tests, and durable documentation in project-root locations; record their paths in research artifacts instead of moving them under `.ai-research-workflow/`.
- Do not introduce new dependencies unless the project already uses them or the user explicitly approves.
- Every script must write outputs into the current research workspace or a project-defined artifact directory recorded in `RUNS.md`.
- Every script must be referenced from `SCRIPT_REGISTRY.md` before relying on it as part of the workflow.
- If a script is unsuitable for a project, document the equivalent native command instead of forcing the framework's preferred shape.

## Completion handoff updates

When the user says the current experiment is done, inspect `.ai-research-workflow/<slug>/scripts/` and the native commands recorded by the run. Update `SCRIPT_REGISTRY.md` before final response:

- add missing entries for scripts or native commands that produced the completed run
- mark scripts as `validated` when the completed run proves they worked, including the command/log path
- mark scripts as `deprecated` when the experiment replaced or invalidated them
- record user-requested reusable commands, monitors, metrics collectors, plotting scripts, or docs publishers
- record known cleanup TODOs only when they are actionable and tied to a path

Do not leave useful script knowledge only in chat. If the script directory or registry is missing, create the minimal registry entry needed to preserve what happened, or report the missing path and exact recovery command.
