---
name: ai-research-workflow
description: "AI research workflow orchestration for turning vague AI/ML research ideas into validated project work and research artifacts: optional idea scouting/generation, deep interview, literature review, falsifiable hypothesis spec, ralplan planning, method implementation, baseline reproduction, experiment design, experiment runs, result distillation, reproducibility review, optional research feedback memory, optional question capture, optional researcher growth review, and paper drafting. Use when Codex is asked to generate, scout, develop, implement, evaluate, reproduce, answer questions about, or write up an AI/ML research idea, benchmark, method, baseline, ablation, paper plan, experiment pipeline, or research report with clear hypotheses, baselines, metrics, validation, and claim boundaries."
---

# AI Research Workflow

## Purpose

Turn an AI/ML research idea into artifact-gated research work. This is a framework skill, not a project-specific experiment runner. Keep scientific intent, implementation work, run evidence, and claims separated so evidence controls conclusions.

Bundled scripts in this skill are maintenance and framework-guardrail helpers only. Do not use them as user experiment runners, metrics collectors, plotting scripts, or research-doc publishers. Generate or adapt project-local scripts only when the current project needs them.

This skill is an OMX workflow. By default it orchestrates:

```text
optional idea scouting when no clear research question exists
  -> optional SOTA/baseline paper registry when paper scouting is requested
  -> optional paper-reproduction scouting when the user explicitly wants ideas from reproducing a paper
  -> $deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
  -> literature and research artifacts
  -> $ralplan for implementation and validation shape
  -> task worktree execution in the target repo
  -> $autoresearch for validator-gated research loop
  -> implementation / baseline reproduction / experiments
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Skip completed phases only when existing artifacts pass the relevant gate.

## Reference map

- Read `references/workflow-orchestration.md` before starting or resuming the full workflow.
- Read `references/artifact-contracts.md` when authoring or auditing artifacts; prefer templates in `assets/templates/` when creating new artifacts.
- Read `references/research-quality-gates.md` before approving handoff, result, reproducibility, feedback, or paper claims.
- Read `references/idea-scouting.md` when the user asks for research idea generation, idea triage, or broad-direction scouting.
- Read `references/question-capture.md` when the user asks a research/workflow question and Q&A capture is enabled.
- Read `references/experiment-runtime-standards.md` before designing, implementing, running, or auditing experiments.
- Use schema/version helpers when validating mature artifacts, migrating legacy workspaces, building a claim/evidence graph, or checking installed skill drift.
- Read `references/project-local-script-registry.md` before creating or relying on project-local scripts.
- Read `references/worktree-development.md` before substantive target-repo edits.

Maintenance validation:

```bash
python3 scripts/validate_framework_contract.py .
python3 scripts/validate_research_workspace.py <project-root>
python3 scripts/validate_research_schema.py <project-root>
python3 scripts/validate_run_purposes.py <project-root>
python3 scripts/check_regression_fixtures.py
python3 scripts/run_e2e_scenarios.py
```

Framework guardrail helpers:

```bash
python3 scripts/ai_research.py help
python3 scripts/resolve_workflow.py <project-root> --prompt "<user prompt>"
python3 scripts/init_research_workspace.py <project-root> --preset guided
python3 scripts/init_workstream.py <project-root> <slug> --title "..." --question "..." --deep-interview <path> --ralplan-prd <path> --ralplan-test-spec <path> --autoresearch-result <path>
python3 scripts/update_workstream_state.py <project-root> <slug> --phase experiment-design --next-action "..."
python3 scripts/summarize_research_state.py <project-root>
python3 scripts/score_research_artifacts.py <project-root>
python3 scripts/capture_question.py <project-root> --question "..." --answer-summary "..."
python3 scripts/question_capture_hook.py --stage submit --project-root <project-root> --prompt "..."
python3 scripts/question_capture_hook.py --stage answer --project-root <project-root> --answer-summary "..."
python3 scripts/prepare_workstream_closeout.py <project-root> <slug> --write
python3 scripts/preserve_negative_result.py <project-root> <slug> --finding "..." --evidence <path> --interpretation "..." --claim-update "..."
python3 scripts/generate_report_outline.py <project-root> <slug> --kind paper-outline --write
python3 scripts/validate_research_schema.py <project-root>
python3 scripts/build_evidence_graph.py <project-root> <slug> --json
python3 scripts/migrate_research_workspace.py <project-root> --write
python3 scripts/check_skill_update.py
python3 scripts/validate_research_workspace.py <project-root> --phase idea-scouting
python3 scripts/prepare_worktree_closeout.py <task-worktree> --base main
python3 scripts/validate_research_workspace.py <project-root> --phase paper-scouting
python3 scripts/validate_research_workspace.py <project-root> --phase paper-reproduction --workstream <slug>
```

## Command surface

Prefer explicit subcommands when the user's intent matches one of these lanes. `scripts/resolve_workflow.py` recognizes the same subcommands and returns structured `routing.phase`, `routing.workflow_action`, `routing.next_artifacts`, `routing.guardrail_scripts`, and `requires_user_confirmation` fields.

```text
$ai-research-workflow scout              # idea scouting / candidate ranking
$ai-research-workflow papers             # find and maintain SOTA/baseline paper registry
$ai-research-workflow reproduce-paper    # gate a workstream for reproducing one selected paper
$ai-research-workflow experiment         # gate an experiment-campaign workstream
$ai-research-workflow new-workstream     # mandatory deep-interview -> ralplan -> autoresearch gate
$ai-research-workflow handoff            # current experiment is done; distill runs/scripts/results
$ai-research-workflow qa                 # answer then capture Q&A when qa_capture is enabled
$ai-research-workflow summarize          # portfolio/workstream state summary
$ai-research-workflow score              # artifact quality score / research review
$ai-research-workflow closeout           # workstream + report-before-merge closeout plan
$ai-research-workflow negative-result    # preserve failed/null/inconclusive evidence and downgrade claims
$ai-research-workflow draft              # paper/report/blog/rebuttal outline from stable artifacts
$ai-research-workflow recall            # "之前那个 X 实验干嘛的来着?" - 召回 workstreams / runs / decisions
$ai-research-workflow run-purposes       # validate every runs/<id>/ has a purpose.md
```

Bundled CLI facade for deterministic local use:

```bash
python3 scripts/ai_research.py help
python3 scripts/ai_research.py resolve <project-root> --prompt "这个实验做完了，整理落盘"
python3 scripts/ai_research.py schema <project-root>
python3 scripts/ai_research.py graph <project-root> <slug> --json
python3 scripts/ai_research.py recall <project-root> [--query TEXT] [--slug SLUG] [--limit N] [--json]
python3 scripts/ai_research.py run-purposes <project-root> [--strict]
python3 scripts/ai_research.py update-check
```

If you want X, say Y:

- Generate/rank candidate ideas -> `$ai-research-workflow scout`.
- Find and maintain SOTA/baseline papers -> `$ai-research-workflow papers` or “帮我找 SOTA 和 baseline 论文”.
- Reproduce one paper to find ideas -> `$ai-research-workflow reproduce-paper` or “开 workstream 复现这篇论文”.
- Open an experiment campaign -> `$ai-research-workflow experiment` or “开一个实验 workstream”.
- Start a new small direction -> `$ai-research-workflow new-workstream` and provide/complete the deep-interview, ralplan, and autoresearch gate.
- Finish the current experiment -> `$ai-research-workflow handoff` or “current experiment is done; distill runs/scripts and prepare closeout”.
- Preserve a failed/null result -> `$ai-research-workflow negative-result`.
- Record a durable question/answer -> enable `--qa-capture` or `qa_capture: research`, answer first, then capture.
- Check artifact quality before drafting -> `$ai-research-workflow score` plus `validate_research_schema.py` and `build_evidence_graph.py`.

When no subcommand is present, use `resolve_workflow.py --prompt` plus the project config to infer the lane. Subcommands do not bypass safety gates: final topic promotion, workstream creation, merge, push, worktree removal, branch deletion, and stronger claims after negative results still require explicit user confirmation.

## Artifact setup

Maintain two research control-plane layers under `.ai-research-workflow/`:

- Portfolio layer: `.ai-research-workflow/RESEARCH.md` and `.ai-research-workflow/INDEX.md` capture the user's overall research program, current synthesis, active workstreams, and how small directions relate to the larger goal.
- Workstream layer: `.ai-research-workflow/<slug>/` captures a specific subquestion, method lane, baseline, ablation, experiment family, or paper/report slice.

Minimum portfolio layout:

```text
.ai-research-workflow/
  CONTEXT.md       # always-on: ubiquitous language + active questions (DDD-style vocabulary)
  DECISIONS.md     # always-on: 1-2-line log of "why we did X this way"
  RESEARCH.md
  INDEX.md
  IDEA_SCOUTING.md # optional when idea_scouting is enabled or the question is not yet clear
  PAPERS.md        # optional SOTA/baseline paper registry when paper scouting is requested
  QUESTIONS.md      # optional when qa_capture is enabled
```

Minimum workstream layout:

```text
.ai-research-workflow/<slug>/
  STATE.json
  RESEARCH.md
  LITERATURE.md
  REPRODUCTION.md  # optional/required for a paper-reproduction workstream
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  CLAIMS.md
  REPRODUCIBILITY.md
  PAPER_DRAFT.md
  SCRIPT_REGISTRY.md
  DECISIONS.md     # always-on: per-workstream decision log
  CLOSEOUT.md       # optional workstream completion/report-before-merge plan
  PAPER_OUTLINE.md  # optional generated report outline
  QUESTIONS.md      # optional when qa_capture is enabled
  scripts/
  runs/
    <run-id>/
      purpose.md   # required: why this run exists, written before launch
      transcript.jsonl
      artifacts/
```

## Always-on vocabulary, decisions, and run-purpose artifacts

These three lightweight files exist by default in every fresh workspace and
every new workstream. They are the cheapest insurance against the three
failure modes below and should be maintained continuously rather than only
when a feedback-memory mode is enabled.

- `.ai-research-workflow/CONTEXT.md` — Ubiquitous language. A short table of
  project-specific terms with one-line definitions and legacy names to avoid,
  plus a list of active research questions. Borrowed from Eric Evans'
  Domain-Driven Design: every term here is the single source of truth used in
  artifacts, conversations, commits, and code. **Failure mode prevented**:
  the agent reinvents or misremembers project vocabulary between sessions.
- `.ai-research-workflow/DECISIONS.md` and `.ai-research-workflow/<slug>/DECISIONS.md` —
  One row per decision: date, scope, the choice made, what was rejected, and
  why. Two lines per row is enough. **Failure mode prevented**:
  "why did we do it this way" archaeology at the start of every workstream.
- `.ai-research-workflow/<slug>/runs/<run-id>/purpose.md` — Written BEFORE
  the run starts. Captures the hypothesis being tested, what success looks
  like, expected runtime, and stop conditions. Filled out post-run with what
  we actually learned. **Failure mode prevented**: a timestamped run folder
  whose name no longer matches anything the agent remembers about its purpose.

The validator `scripts/validate_run_purposes.py` walks every workstream's
`runs/` directory and warns (or, with `--strict`, errors) when a run is
missing `purpose.md` or only has TODO placeholders. Run it on every
completion handoff.

The recall helper `scripts/recall.py` (or `ai_research.py recall`) walks
the workspace and prints a compact report answering "what was that experiment
for?" without archaeology. It accepts `--query TEXT` to filter runs whose
`purpose.md` contains TEXT, `--slug SLUG` to restrict to one workstream,
and `--json` for machine-readable output. Use it before resuming a paused
project, before answering the user "what did we do last week?", or before
starting a new workstream to confirm whether the question already has a
running home.

Use `assets/templates/portfolio-RESEARCH.md`, `portfolio-INDEX.md`, `PAPERS.md`, `STATE.json`, `workstream-RESEARCH.md`, `REPRODUCTION.md`, `CLAIMS.md`, and the artifact-specific templates as the starting point when creating these files. Templates define shape only; replace TODO placeholders with project evidence before treating an artifact as complete.

Every new workstream has a `workstream_type` in `STATE.json`:

- `paper-reproduction`: one selected paper, baseline, or claim is being reproduced; scaffold `REPRODUCTION.md`.
- `experiment-campaign`: a hypothesis, ablation, benchmark, method variant, or evaluation campaign is being tested; `EXPERIMENT.md` is the primary design artifact.

Use `scripts/init_workstream.py --workstream-type paper-reproduction` or the compatibility flag `--paper-reproduction` for the first type. Use `--workstream-type experiment-campaign` for ordinary experiment campaigns.

## Workflow presets and overrides

Project config can reduce how often the user must name the workflow explicitly. Use `.ai-research-workflow/CONFIG.md` from `assets/templates/CONFIG.md`:

```yaml
schema_version: 1
workflow_preset: conservative | guided | autonomous
idea_scouting: auto | off | on
completion_handoff: auto | off
worktree_closeout: off | report-before-merge
```

Preset meaning:
- `conservative`: run only explicitly requested phases.
- `guided`: infer common phases from user language; this is the recommended default.
- `autonomous`: proactively maintain relevant artifacts and next-step plans while still asking before final-topic selection, workstream creation, merge, push, worktree removal, or branch deletion.

Overrides win over the preset. `idea_scouting: auto` lets broad/vague idea prompts enter scouting; `completion_handoff: auto` treats "done", "wrap up", or "整理落盘" as completion handoff; `worktree_closeout: report-before-merge` prepares but does not execute merge/delete cleanup.

## Optional idea scouting

Idea Scouting is optional and is not the default path for already-clear research questions. Use it when the user asks for idea generation, asks whether an idea is worth doing, gives only a broad area, or explicitly passes `--idea-scouting`.

Write `.ai-research-workflow/IDEA_SCOUTING.md` from `assets/templates/IDEA_SCOUTING.md`. The agent may choose search sources, generate candidate ideas, rank/filter candidates, and write the scouting artifact. It must not choose the final topic, guarantee absolute novelty, replace full `LITERATURE.md`, implement code, run experiments, or create a new workstream without user confirmation.

When the user explicitly asks to find SOTA/baseline papers, maintain the portfolio paper registry at `.ai-research-workflow/PAPERS.md` using `assets/templates/PAPERS.md`. The registry tracks candidate SOTA papers, baseline papers, benchmark/dataset papers, code/data/checkpoint availability, key claims, reproduction priority, and maintenance history.

When the user explicitly asks to reproduce a paper to find ideas, treat this as paper-reproduction scouting: update `PAPERS.md`, add the paper-derived idea section in `IDEA_SCOUTING.md`, and if the user confirms one paper, enter the new-workstream gate for a paper-reproduction workstream. The actual reproduction plan and evidence belong in the workstream `REPRODUCTION.md`, `EXPERIMENT.md`, `RUNS.md`, `RESULTS.md`, `CLAIMS.md`, and `REPRODUCIBILITY.md`. Do not launch reproduction runs, download data, or create the workstream without the normal confirmation and gate evidence.

An idea may be recommended for formal research intake only when the promotion gate has all six fields: falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty risk, feasibility budget, and user-goal fit. If the user confirms promotion, enter the new-workstream gate.

## New workstream gate

Before creating a new `<slug>`, inspect the portfolio `RESEARCH.md`, `INDEX.md`, and existing workstream directories. Reuse or update an existing workstream when the task continues the same subquestion. Create a new workstream only when the task has a distinct research question, validation target, or artifact boundary, and record that relationship in the portfolio index.

New workstream creation has a mandatory workflow gate. If the task requires a new `<slug>`, do not create the workstream directory, implement code, run experiments, or publish docs until this sequence has completed and its artifact paths are recorded in `INDEX.md`:

```text
$deep-interview --autoresearch
  -> $ralplan
  -> $autoresearch
```

Required gate evidence:
- `$deep-interview --autoresearch`: validator-ready mission/intake artifact, preferably under `.omx/specs/autoresearch-<slug>/`, and a workstream `RESEARCH.md` draft linked to the portfolio
- `$ralplan`: consensus planning output plus `.omx/plans/prd-<slug>.md` and `.omx/plans/test-spec-<slug>.md`
- `$autoresearch`: persisted autoresearch state with a `completion_artifact_path`, plus `.omx/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`

If any gate evidence is missing, stop at the gate, create or complete the missing workflow artifact, and report the blocker. Do not bypass this gate because the new direction seems obvious.

After the user confirms workstream creation and all gate evidence exists, `scripts/init_workstream.py` may scaffold the control-plane files. It must not be used to bypass the confirmation or gate evidence requirements.

Choose the workstream type before scaffolding. If the selected unit of work is a paper/claim/baseline reproduction, use `paper-reproduction`. If the selected unit of work is a hypothesis-driven run set, ablation, benchmark, or method evaluation, use `experiment-campaign`. “Running experiments” is a phase that both types may enter; the type records the research intent.

## Optional feedback and growth modes

Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default. Do not create or update feedback artifacts unless the current invocation or project config enables them.

Invocation flags:
- `--feedback-memory`: enable Research Feedback Memory for this invocation.
- `--qa-capture`: enable Q&A capture for this invocation.
- `--growth-review`: enable Researcher Growth Review for this invocation.
- `--no-feedback`: force feedback memory, Q&A capture, and growth review off for this invocation.

Optional project config lives at `.ai-research-workflow/CONFIG.md`:

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

Resolution precedence: `--no-feedback`, explicit enable flags, `.ai-research-workflow/CONFIG.md`, then default off. Use `assets/templates/CONFIG.md`, `QUESTIONS.md`, `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, `SKILL_GROWTH.md`, `DESIGN.md`, `NOTES.md`, and `REVIEW.md` only when the resolved mode enables them.

Feedback memory records distilled knowledge, not raw logs. Keep raw run outputs under `runs/` and link or summarize them.

When Q&A capture is enabled and the user asks a research, design, architecture, experiment, interpretation, or workflow question rather than issuing a command, answer first, then append the question and answer summary to `.ai-research-workflow/QUESTIONS.md` or `.ai-research-workflow/<slug>/QUESTIONS.md`. Route durable concepts, decisions, issues, design notes, or growth lessons to the appropriate feedback artifacts.

Use `scripts/capture_question.py` for deterministic question capture after the answer has been given. It refuses likely secret/credential text unless explicitly overridden. `scripts/question_capture_hook.py` adds the two-stage hook surface: submit classifies and records pending state, answer appends only after an answer summary exists. `assets/hooks/question-capture.example.json` shows example wiring; hooks may call capture only when `qa_capture` resolves to `research` or `all`.

Use `assets/schemas/` with `scripts/validate_research_schema.py` when CONFIG, STATE, claim rows, run rows, or portfolio index rows need machine-checkable guardrails.

## Research control plane vs project implementation

`.ai-research-workflow/` is the research portfolio control plane. `.ai-research-workflow/<slug>/` is a workstream control plane.

Actual research work belongs in the target project root using existing project conventions. Implement the user's method, reproduce baselines, add configs, tests, dataset adapters, training/evaluation entrypoints, and reports in project-root locations such as `src/`, `models/`, `baselines/`, `configs/`, `experiments/`, `scripts/`, `tests/`, `docs/`, or established equivalents. Do not put method code, baseline code, or production experiment code under `.ai-research-workflow/`; only thin orchestration wrappers and metadata belong there.

For a paper-reproduction workstream, `.ai-research-workflow/<slug>/REPRODUCTION.md` is the control-plane ledger for the target paper, claim, reproduction type, available materials, deviations, run evidence links, reproduction-derived ideas, and final distillation. Project-root code/config/data adapters still live in the target repository's normal implementation plane.

## Task worktree rule

When this skill is used to make substantive AI research changes in a target project repository, inspect the local git status before opening any new worktree. If the main worktree has local modifications, preserve them first by splitting them into semantic commits with Lore-format commit messages; do not mix unrelated changes into one checkpoint. After the main worktree is clean, fetch/pull the primary branch, create the task worktree from the latest commit, and push the completed branch or merged main branch to the remote after validation and any required report-before-merge confirmation.

Prefer `<repo>/.omx/worktrees/<scope>/`; if that path is not writable, use a writable fallback and record the absolute path. Maintain `.omx/worktrees/REGISTRY.md` in the target repository with each worktree's path, branch, scope, owned files/areas, and status. Use one worktree per logical task or lane, merge worktrees back serially after validation, then clean them up.

Skip the worktree only for read-only analysis, quick lookups, or tiny safe edits. This task worktree rule is about executing research work inside the target project, not about installing or maintaining this skill repository.

## Git tracking rule

The skill repository tracks the framework itself:
- commit `README.md`, `README.zh-CN.md`, `skills/ai-research-workflow/**`, and the maintenance-only scripts that validate this framework
- keep `.omx/` ignored because it is local runtime state, logs, and temporary worktree data
- in downstream research projects, selectively version stable research documents and experiment contracts rather than raw run outputs

## Experiment defaults

When this skill runs, designs, implements, or audits experiments, structured runtime evidence is mandatory by default. Do not wait for the user to ask for logs, metrics, progress, or visualizations.

For every actual experiment run, ensure the project has existing native commands or project-local scripts recorded in `.ai-research-workflow/<slug>/SCRIPT_REGISTRY.md`. Put wrappers under `.ai-research-workflow/<slug>/scripts/`. Commands/scripts must produce a distinct run directory with command record, complete log, structured metrics, summary, and figures when visualizations are appropriate.

Each workstream keeps `STATE.json` as its phase state and `CLAIMS.md` as its evidence-to-claim ledger. Update `STATE.json` at workflow phase transitions. Update `CLAIMS.md` whenever results support, contradict, downgrade, or retire a claim.

Run long experiments in detached tmux by default when tmux is available. For multiple independent variants, baselines, ablations, datasets, or multi-seed experiments, use `$team` or native subagents when parallelism is safe. Assign each seed lane an explicit idle GPU/device or scheduler slot and record the seed-to-device mapping in `RUNS.md`.

When settled results or conclusions are finalized and project policy allows, mirror distilled browser-readable docs under project-root `docs/ai-research/<slug>/` and report any MkDocs update needed. This is a project-local documentation update, not a bundled publishing script.

## Experiment completion handoff

When the user says the current experiment is done, finished, ready to wrap up, or otherwise asks to close out the current run, switch into Experiment completion handoff before answering. Do not treat the message as chat-only.

Completion handoff requires:
- inspect `.ai-research-workflow/<slug>/runs/` manifests, logs, metrics, summaries, and figures
- inspect `.ai-research-workflow/<slug>/scripts/` and update `SCRIPT_REGISTRY.md`
- update `RUNS.md`, `RESULTS.md`, and `REPRODUCIBILITY.md` when evidence changes status, conclusions, rerun requirements, or failures
- update `CLAIMS.md` and preserve negative or inconclusive results instead of deleting them
- persist user-requested outputs, notable findings, reusable commands, decisions, and next-step TODOs into stable artifacts or project-root docs
- update portfolio `RESEARCH.md` and `INDEX.md` when the overall synthesis, workstream status, or next priority changes
- if the workstream used a task worktree, prepare a report-before-merge closeout plan covering validation, semantic Lore-format commit status, merge/rebase target, push target, worktree removal, branch deletion, and `.omx/worktrees/REGISTRY.md` update; do not merge, push, delete the worktree, or delete the branch until the user confirms

Use `scripts/prepare_workstream_closeout.py` to write `CLOSEOUT.md` for the workstream-level handoff. Use `scripts/prepare_worktree_closeout.py` for git worktree closeout. These scripts prepare plans only; they do not execute merge, push, worktree removal, or branch deletion.

If a run is negative, null, or inconclusive, preserve it before changing claims. `scripts/preserve_negative_result.py` appends the finding to `RESULTS.md` and the claim downgrade/retirement evidence to `CLAIMS.md`. Do not delete failed runs to make the story cleaner.

Only skip artifact updates when relevant files or run outputs cannot be found. If skipped, record the missing paths and the next exact recovery command in the final response.

## Portfolio summary and artifact review

Use `scripts/summarize_research_state.py` when resuming a project, choosing the next workstream, or answering "what is the current research state?". It summarizes portfolio status, phases, blockers, run/script inventory, missing artifacts, and suggested next actions.

Use `scripts/score_research_artifacts.py` during research review, completion handoff, reproducibility review, and before drafting. Scores are heuristic guardrails, not scientific truth; low scores mean the agent must inspect the corresponding artifacts before making stronger claims.

Use `scripts/generate_report_outline.py` only after stable evidence exists. It can scaffold paper outlines, workshop reports, internal reports, blog summaries, or rebuttal notes, but it must preserve claim boundaries and evidence paths from `CLAIMS.md`.

## Workflow phases

0. OMX workflow entry: read or create `.ai-research-workflow/RESEARCH.md` and `.ai-research-workflow/INDEX.md`; run optional idea scouting when there is no clear research question; decide whether to reuse a workstream or enter the new-workstream gate; resolve optional feedback and Q&A capture modes.
1. Research intake: produce portfolio and workstream `RESEARCH.md` with research question, falsifiable hypothesis, success/falsification criteria, non-goals, claim boundaries, and decision boundaries.
2. Literature review: produce `LITERATURE.md` with source-backed evidence from primary sources when facts are current or niche.
3. Research question spec: tighten hypotheses until each is testable.
4. Experiment design: produce `EXPERIMENT.md` before writing or changing experiment code, including baseline fairness and negative/inconclusive result policy.
5. Project-root implementation and baseline reproduction: implement method, baseline, configs, tests, and entrypoints in the target repository root after `$ralplan`.
6. Project-local orchestration scripts: reuse native project runners first; add thin wrappers only when needed and record them in `SCRIPT_REGISTRY.md`.
7. Run experiments: produce `RUNS.md`, never fabricate results, and record complete log, metrics, summary, figures, command, environment, commit, seeds, and failures.
8. Distill completed runs: update `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `REPRODUCIBILITY.md`, project-root docs, and optional feedback/Q&A artifacts when enabled.
9. Analyze results: produce `RESULTS.md` and `CLAIMS.md`; separate evidence from interpretation, preserve negative/inconclusive findings, and keep claims within evidence.
10. Reproducibility review: produce `REPRODUCIBILITY.md`; missing seeds, data versions, commands, complete log paths, metrics, figures, or result paths are blockers.
11. Paper draft or report: produce `PAPER_DRAFT.md` only after results and reproducibility review exist.
12. Research review: summarize portfolio state, score artifact quality, prepare closeout plans, and generate report outlines without relaxing evidence-to-claim boundaries.

## Completion rules

Stop only when the requested artifact set passes the relevant quality gates, a project validator/test command or `$autoresearch` completion artifact passes, or a real blocker prevents progress.

Final responses must list changed/created research artifacts, project-root method/baseline/config/test/docs files, validation evidence, project-local scripts, tmux/status/log/metrics/summary/figure paths, distilled run updates outside `runs/`, docs/MkDocs paths, unsupported claims removed or downgraded, optional feedback/Q&A artifacts when enabled, and remaining risks.
