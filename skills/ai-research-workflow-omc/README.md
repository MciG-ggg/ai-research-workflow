# AI Research Workflow Skill (OMC)

[中文文档](README.zh-CN.md)

A Claude Code/oh-my-claudecode (OMC) skill for AI/ML research work. It helps turn vague ideas, papers, baselines, and experiment plans into evidence-gated research artifacts instead of jumping straight from idea to code.

The core principle is simple:

- `RESEARCH.md` records the research question, falsifiable hypothesis, scope, and claim boundaries.
- `EXPERIMENT.md` records datasets, baselines, metrics, runs, and failure policy.
- `RUNS.md`, `RESULTS.md`, `CLAIMS.md`, and `REPRODUCIBILITY.md` keep evidence separate from claims.

This skill is a workflow and artifact framework. It does **not** ship universal experiment runner scripts; project-specific code, configs, training scripts, and evaluation scripts should live in the target AI research project. The bundled scripts are maintenance-only helpers for the framework itself and are not for running user experiments.

This skill is the OMC-flavored sibling of the Codex/OMX `ai-research-workflow` skill. It shares the artifact contract and Python guardrail scripts but routes workflow gates through [oh-my-claudecode (OMC)](https://github.com/MciG-ggg/oh-my-claudecode) skills (`/oh-my-claudecode:deep-interview`, `/oh-my-claudecode:ralplan`, `/oh-my-claudecode:autoresearch`, `/oh-my-claudecode:ralph`, `/oh-my-claudecode:autopilot`, `/oh-my-claudecode:ultrawork`, `/oh-my-claudecode:team`) and keeps the portfolio/workstream control plane under `.omc/ai-research/`.

## Dependency

```bash
# Claude Code with oh-my-claudecode plugin enabled
# See: https://github.com/MciG-ggg/oh-my-claudecode
omc setup
omc doctor
```

## Install

```bash
git clone https://github.com/MciG-ggg/ai-research-workflow.git
mkdir -p ~/.claude/skills
cp -R ai-research-workflow/skills/ai-research-workflow-omc ~/.claude/skills/
```

Use the updater after pulling repo changes:

```bash
cd ai-research-workflow
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh
```

For local development without pulling:

```bash
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --no-pull
```

Updater flags: `--no-pull`, `--symlink`, `--dry-run`, `--keep-backups N`, `--dest DIR`. The updater does `git pull --ff-only`, validates the source via `validate_framework_contract.py`, then performs a staged `rsync -a --delete` of the skill into the install destination and validates the installed copy again.

## Typical workflow

This skill is a workflow, not just a logging template. By default it orchestrates:

```text
optional idea scouting when no clear research question exists
  -> optional SOTA/baseline paper registry when requested
  -> optional paper-reproduction scouting when explicitly requested
  -> /oh-my-claudecode:deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
  -> literature / research artifact drafting
  -> /oh-my-claudecode:ralplan for implementation and validation shape
  -> task worktree execution in the target repo
  -> /oh-my-claudecode:autoresearch for validator-gated research loop
  -> run experiments / reproduce baselines / evaluate method
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Method implementation and baseline reproduction (method implementation, baseline reproduction) live in the target AI research project, never under `.omc/ai-research/`.

```text
1. Start from an idea, paper, baseline, or experiment question.
2. Optionally scout ideas or papers:
   - IDEA_SCOUTING.md for candidate research ideas
   - PAPERS.md for SOTA/baseline paper lists
3. Before opening a new workstream, run:
   /oh-my-claudecode:deep-interview --autoresearch -> /oh-my-claudecode:ralplan -> /oh-my-claudecode:autoresearch
4. Create or reuse .omc/ai-research/<slug>/ for one concrete direction.
5. Choose the workstream type:
   - paper-reproduction: reproduce one paper/baseline/claim; uses REPRODUCTION.md
   - experiment-campaign: run a hypothesis/ablation/benchmark/method-evaluation campaign
6. Implement project code in the target AI research project, not inside .omc/ai-research/.
7. Record runs, scripts, metrics, summaries, and failures.
8. Distill evidence into RESULTS.md, CLAIMS.md, and REPRODUCIBILITY.md.
9. When the workstream is done, prepare a closeout/report-before-merge plan before merge, push, or worktree cleanup.
```

## Common commands

Invoke the skill explicitly when you want deterministic routing:

```text
/oh-my-claudecode:ai-research-workflow scout            # candidate idea scouting
/oh-my-claudecode:ai-research-workflow papers           # find/maintain SOTA and baseline paper list
/oh-my-claudecode:ai-research-workflow reproduce-paper  # gate a one-paper reproduction workstream
/oh-my-claudecode:ai-research-workflow experiment       # gate an experiment-campaign workstream
/oh-my-claudecode:ai-research-workflow new-workstream   # create a new gated direction
/oh-my-claudecode:ai-research-workflow handoff          # close out finished runs/scripts/results
/oh-my-claudecode:ai-research-workflow qa               # answer then capture Q&A when qa_capture is enabled
/oh-my-claudecode:ai-research-workflow summarize        # summarize portfolio/workstream state
/oh-my-claudecode:ai-research-workflow score            # heuristic artifact quality score
/oh-my-claudecode:ai-research-workflow closeout         # prepare report-before-merge plan
/oh-my-claudecode:ai-research-workflow negative-result  # preserve failed/null/inconclusive results
/oh-my-claudecode:ai-research-workflow draft            # generate a paper/report outline
```

If you want X, say Y:

- Generate/rank candidate ideas -> `/oh-my-claudecode:ai-research-workflow scout`.
- Find and maintain SOTA/baseline papers -> `/oh-my-claudecode:ai-research-workflow papers` or "帮我找 SOTA 和 baseline 论文".
- Reproduce one paper to find ideas -> `/oh-my-claudecode:ai-research-workflow reproduce-paper` or "开 workstream 复现这篇论文".
- Open an experiment campaign -> `/oh-my-claudecode:ai-research-workflow experiment` or "开一个实验 workstream".
- Start a new small direction -> `/oh-my-claudecode:ai-research-workflow new-workstream` and provide/complete the deep-interview, ralplan, and autoresearch gate.
- Finish the current experiment -> `/oh-my-claudecode:ai-research-workflow handoff` or "current experiment is done; distill runs/scripts and prepare closeout".
- Preserve a failed/null result -> `/oh-my-claudecode:ai-research-workflow negative-result`.
- Record a durable question/answer -> enable `--qa-capture` or `qa_capture: research`, answer first, then capture.
- Check artifact quality before drafting -> `/oh-my-claudecode:ai-research-workflow score` plus `validate_research_schema.py` and `build_evidence_graph.py`.

Local CLI helpers are available through:

```bash
python3 skills/ai-research-workflow-omc/scripts/ai_research.py help
python3 skills/ai-research-workflow-omc/scripts/ai_research.py resolve <project-root> --prompt "这个实验做完了，整理落盘"
python3 skills/ai-research-workflow-omc/scripts/ai_research.py summarize <project-root>
python3 skills/ai-research-workflow-omc/scripts/ai_research.py score <project-root>
python3 skills/ai-research-workflow-omc/scripts/ai_research.py schema <project-root>
```

## Artifact layout

The promotion gate for promoting a candidate into formal intake requires: falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty risk, feasibility budget, and user-goal fit.

```text
.omc/ai-research/
  IDEA_SCOUTING.md   # optional candidate idea scouting
  PAPERS.md          # optional SOTA/baseline paper registry
  RESEARCH.md        # overall research program summary
  INDEX.md           # workstream index
  CONFIG.md          # optional workflow preset / mode flags
  QUESTIONS.md       # optional when qa_capture is enabled

.omc/ai-research/<slug>/
  STATE.json
  RESEARCH.md
  LITERATURE.md
  REPRODUCTION.md    # required for paper-reproduction workstreams
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  CLAIMS.md
  REPRODUCIBILITY.md
  PAPER_DRAFT.md
  SCRIPT_REGISTRY.md
  CLOSEOUT.md
  PAPER_OUTLINE.md
  QUESTIONS.md       # optional when qa_capture is enabled
  scripts/
  runs/
```

## Optional feedback memory, question capture, and growth review

Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default. Do not create or update feedback artifacts unless the current invocation or project config enables them.

Invocation flags:

- `/oh-my-claudecode:ai-research-workflow --feedback-memory`: enable Research Feedback Memory for this invocation.
- `/oh-my-claudecode:ai-research-workflow --qa-capture`: enable Q&A capture for this invocation.
- `/oh-my-claudecode:ai-research-workflow --growth-review`: enable Researcher Growth Review for this invocation.
- `/oh-my-claudecode:ai-research-workflow --no-feedback`: force feedback memory, Q&A capture, and growth review off for this invocation.

Optional project config lives at `.omc/ai-research/CONFIG.md`:

```yaml
schema_version: 1
workflow_preset: conservative | guided | autonomous
idea_scouting: auto | off | on
completion_handoff: auto | off
worktree_closeout: off | report-before-merge
feedback_memory: off | lite | full
qa_capture: off | research | all
growth_review: off | milestone | always
```

Resolution precedence: `--no-feedback`, explicit enable flags, `.omc/ai-research/CONFIG.md`, then default off. Use `assets/templates/CONFIG.md`, `QUESTIONS.md`, `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, `SKILL_GROWTH.md`, `DESIGN.md`, `NOTES.md`, and `REVIEW.md` only when the resolved mode enables them.

Feedback memory records distilled knowledge, not raw logs. Keep raw logs and run outputs stay under `runs/` and link or summarize them.

When Q&A capture is enabled and the user asks a research/design question rather than issuing a command, answer first, then append the question and answer summary to `.omc/ai-research/QUESTIONS.md` or `.omc/ai-research/<slug>/QUESTIONS.md`.

## New workstream gate

Before creating a new `<slug>`, inspect the portfolio `RESEARCH.md`, root `INDEX.md`, and existing workstream directories. Reuse or update an existing workstream when the task continues the same subquestion. Before creating a new slug, the portfolio `RESEARCH.md` and root `INDEX.md` must already exist; if they don't, run the workspace initializer first.

New workstream creation has a mandatory workflow gate. The gate blocks creating `.omc/ai-research/<slug>/`, implementation, experiment launch, or docs publishing until this sequence has completed and its artifact paths are recorded in `INDEX.md`:

```text
/oh-my-claudecode:deep-interview --autoresearch
  -> /oh-my-claudecode:ralplan
  -> /oh-my-claudecode:autoresearch
```

Required gate evidence:

- `/oh-my-claudecode:deep-interview --autoresearch`: validator-ready mission/intake artifact, preferably under `.omc/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json` (autoresearch state/completion artifact) and a workstream `RESEARCH.md` draft linked to the portfolio.
- `/oh-my-claudecode:ralplan`: consensus planning output plus `.omc/plans/prd-<slug>.md` (ralplan PRD/test spec) and `.omc/plans/test-spec-<slug>.md`.
- `/oh-my-claudecode:autoresearch`: persisted autoresearch state with a `completion_artifact_path`, plus the autoresearch state/completion artifact under `.omc/specs/autoresearch-<slug>/`.

## Task worktrees

When this skill is used to make substantive AI research changes in a target AI research project, inspect local git status before opening any new worktree. If the main worktree has local modifications, preserve them first by splitting them into semantic Lore-format commits; do not mix unrelated changes into one checkpoint. After the main worktree is clean, fetch/pull the primary branch, open an isolated git worktree before editing, create the task worktree from the latest commit, and push the completed branch or merged main branch to the remote after validation and any required report-before-merge confirmation.

Prefer `<repo>/.omc/worktrees/<scope>/`; if that path is not writable, use a writable fallback and record the absolute path. Maintain `.omc/worktrees/REGISTRY.md` in the target AI research project with each worktree's path, branch, scope, owned files/areas, and status. Use one worktree per logical task or lane, merge worktrees back serially after validation, then clean them up.

Multi-seed experiments: assign one seed per subagent/team lane and an explicit idle GPU/device or scheduler slot, and record the seed-to-device mapping in `RUNS.md`.

Skip the worktree only for read-only analysis, quick lookups, or tiny safe edits. This task worktree rule is about executing research work inside the target project, not about installing or maintaining this skill repository.

## Run distillation and experiment completion handoff

Run directories are raw evidence. After each terminal run, distill reusable knowledge out of `runs/<run-id>/`:

1. Update `RUNS.md` with command, seed/device/resource, status, log path, metrics path, summary path, and failure notes.
2. Update `SCRIPT_REGISTRY.md` with scripts or native commands that were used, changed, validated, deprecated, or requested.
3. Update `RESULTS.md` and `REPRODUCIBILITY.md` when the run changes the scientific picture.
4. Update `CLAIMS.md` and preserve negative/inconclusive results.
5. Persist user-requested outputs, notable findings, reusable commands, decisions, and next-step TODOs into stable artifacts or project-root docs. As part of experiment completion handoff, persist valuable or user-requested content into stable artifacts instead of leaving it only in chat.
6. Update portfolio `RESEARCH.md` and root `INDEX.md` when the overall synthesis, workstream status, or next priority changes.
7. If a task worktree was used, prepare a report-before-merge closeout plan; do not merge, push, delete the worktree, or delete the branch until the user confirms.

The `baseline fairness checklist` in `EXPERIMENT.md` and the `negative/inconclusive result policy` are mandatory — every experiment design must distinguish environment failure, implementation bug, underpowered result, and hypothesis failure.

## Git tracking policy

This repository tracks the skill framework itself:

- commit `README.md`, `README.zh-CN.md`, `skills/ai-research-workflow-omc/**`, and the maintenance-only scripts that validate this framework
- keep `.omc/` ignored because it is local runtime state, logs, and temporary worktree data
- in downstream research projects, selectively version stable research documents and experiment contracts rather than raw run outputs

## Update this skill

```bash
cd ai-research-workflow
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh             # git pull + sync
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --no-pull   # local-only sync
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --symlink    # dev: symlink install
./skills/ai-research-workflow-omc/scripts/update_installed_skill.sh --dry-run    # preview only
```

The updater does `git pull --ff-only`, validates the source, performs a staged `rsync -a --delete`, then validates the installed copy.

## Framework guardrail helpers

```bash
# Deterministic workflow routing
python3 skills/ai-research-workflow-omc/scripts/resolve_workflow.py <project-root> --prompt "<user prompt>"

# Portfolio / workstream scaffolding
python3 skills/ai-research-workflow-omc/scripts/init_research_workspace.py <project-root> --preset guided
python3 skills/ai-research-workflow-omc/scripts/init_workstream.py <project-root> <slug> --title "..." --question "..." --deep-interview <path> --ralplan-prd <path> --ralplan-test-spec <path> --autoresearch-result <path>
python3 skills/ai-research-workflow-omc/scripts/update_workstream_state.py <project-root> <slug> --phase experiment-design --next-action "..."

# Read-only review
python3 skills/ai-research-workflow-omc/scripts/summarize_research_state.py <project-root>
python3 skills/ai-research-workflow-omc/scripts/score_research_artifacts.py <project-root>            # heuristic artifact quality score

# Q&A capture
python3 skills/ai-research-workflow-omc/scripts/capture_question.py <project-root> --question "..." --answer-summary "..."
python3 skills/ai-research-workflow-omc/scripts/question_capture_hook.py --stage submit --project-root <project-root> --prompt "..."
python3 skills/ai-research-workflow-omc/scripts/question_capture_hook.py --stage answer --project-root <project-root> --answer-summary "..."

# Closeout, negative result, report outline
python3 skills/ai-research-workflow-omc/scripts/prepare_workstream_closeout.py <project-root> <slug> --write
python3 skills/ai-research-workflow-omc/scripts/preserve_negative_result.py <project-root> <slug> --finding "..." --evidence <path> --interpretation "..." --claim-update "..."
python3 skills/ai-research-workflow-omc/scripts/generate_report_outline.py <project-root> <slug> --kind paper-outline --write

# Schema, evidence graph, migration
python3 skills/ai-research-workflow-omc/scripts/validate_research_schema.py <project-root>
python3 skills/ai-research-workflow-omc/scripts/build_evidence_graph.py <project-root> <slug> --json
python3 skills/ai-research-workflow-omc/scripts/migrate_research_workspace.py <project-root> --write

# Update / maintenance
python3 skills/ai-research-workflow-omc/scripts/check_skill_update.py
python3 skills/ai-research-workflow-omc/scripts/run_e2e_scenarios.py

# Worktree closeout
python3 skills/ai-research-workflow-omc/scripts/prepare_worktree_closeout.py <task-worktree> --base main

# Phase validators
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase idea-scouting
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase paper-scouting
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase paper-reproduction --workstream <slug>
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase new-workstream --workstream <slug>
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root> --phase completion-handoff --workstream <slug> --check-paths

# Maintenance: contract + fixtures
python3 skills/ai-research-workflow-omc/scripts/check_regression_fixtures.py
python3 skills/ai-research-workflow-omc/scripts/validate_framework_contract.py skills/ai-research-workflow-omc
```

## Notes

- New workstreams should not be created automatically without the gate evidence.
- Merge, push, worktree removal, and branch deletion require report-before-merge confirmation.
- `runs/` stores raw evidence; stable conclusions should be distilled into the markdown artifacts.
- Bundled scripts are framework guardrails only, not user experiment runners.
- The framework's portfolio control plane lives at `.omc/ai-research/`, and `INDEX.md` (root `INDEX.md`) is the workstream registry.
- `assets/templates/`, `assets/schemas/`, `assets/VERSION`, and `assets/hooks/question-capture.example.json` ship with the skill as starting scaffolds.

## Validate

```bash
python3 skills/ai-research-workflow-omc/scripts/validate_framework_contract.py skills/ai-research-workflow-omc
python3 skills/ai-research-workflow-omc/scripts/run_e2e_scenarios.py
python3 skills/ai-research-workflow-omc/scripts/validate_research_workspace.py <project-root>
```

## See also

- [Codex/OMX sibling skill](../ai-research-workflow/) — same artifact contract, different workflow routing surface.
- [oh-my-claudecode (OMC)](https://github.com/MciG-ggg/oh-my-claudecode) — the OMC framework that provides `/oh-my-claudecode:deep-interview`, `/oh-my-claudecode:ralplan`, `/oh-my-claudecode:autoresearch`, `/oh-my-claudecode:ralph`, `/oh-my-claudecode:autopilot`, `/oh-my-claudecode:ultrawork`, `/oh-my-claudecode:team`.
- `references/workflow-orchestration.md` — full OMC workflow sequence and routing helpers.
- `references/artifact-contracts.md` — control-plane artifact shapes.
- `references/research-quality-gates.md` — phase gates and confirmation boundaries.
