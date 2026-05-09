# AI Research Artifact Contracts

Use these contracts to keep scientific goals separate from execution details and to keep `.omx/ai-research` metadata separate from project-root implementation work.

## Contents

- [Control plane vs project-root outputs](#control-plane-vs-project-root-outputs)
- [Idea scouting artifact](#idea-scouting-artifact)
- [Optional feedback memory artifacts](#optional-feedback-memory-artifacts)
- [Optional question capture artifacts](#optional-question-capture-artifacts)
- [Portfolio artifacts](#portfolio-artifacts)
- [Required artifacts](#required-artifacts)
- [`STATE.json` minimum fields](#statejson-minimum-fields)
- [Workstream `RESEARCH.md` minimum sections](#workstream-researchmd-minimum-sections)
- [`LITERATURE.md` minimum sections](#literaturemd-minimum-sections)
- [`EXPERIMENT.md` minimum sections](#experimentmd-minimum-sections)
- [`SCRIPT_REGISTRY.md` minimum sections](#script_registrymd-minimum-sections)
- [`RUNS.md` minimum sections](#runsmd-minimum-sections)
- [`RESULTS.md` minimum sections](#resultsmd-minimum-sections)
- [`CLAIMS.md` minimum sections](#claimsmd-minimum-sections)
- [`CLOSEOUT.md` minimum sections](#closeoutmd-minimum-sections)
- [Research review and report outline artifacts](#research-review-and-report-outline-artifacts)
- [Published docs minimum sections](#published-docs-minimum-sections)
- [Run distillation contract](#run-distillation-contract)

## Control plane vs project-root outputs

`.omx/ai-research/` has a portfolio control plane and one or more workstream control planes.

Portfolio control plane:

```text
.omx/ai-research/
  IDEA_SCOUTING.md # optional before a clear research question exists
  RESEARCH.md
  INDEX.md
```

Optional feedback memory, question capture, and growth review artifacts, created only when enabled:

```text
.omx/ai-research/
  CONFIG.md
  QUESTIONS.md
  LEARNINGS.md
  ISSUES.md
  DECISIONS.md
  SKILL_GROWTH.md
.omx/ai-research/<slug>/
  DESIGN.md
  NOTES.md
  QUESTIONS.md
  REVIEW.md
```

`.omx/ai-research/RESEARCH.md` stores the overall research program: central question, north-star hypotheses, success criteria, claim boundaries, current synthesis, active subquestions, and next priorities.

`.omx/ai-research/INDEX.md` stores the workstream registry: each `<slug>`, status, relationship to the overall question, artifact links, latest evidence, and next action.

`.omx/ai-research/<slug>/` is the workstream control plane. It stores research intent, plans, run indexes, evidence summaries, and reproducibility notes for one concrete direction.

Each workstream has `STATE.json` for phase state and `CLAIMS.md` for the authoritative evidence-to-claim ledger.

Project-root files are the implementation plane. Method code, baseline reproduction code, configs, tests, dataset adapters, benchmark entrypoints, and durable docs belong in the target repository's normal locations, not under `.omx/ai-research/`.

Use the Markdown templates in `assets/templates/` when creating new artifacts. They are scaffolds, not evidence; replace TODO placeholders before treating an artifact as complete.

Use `scripts/init_research_workspace.py` to initialize the portfolio `CONFIG.md`, `RESEARCH.md`, and `INDEX.md` from templates. It creates the portfolio control plane only and must not create a new workstream or bypass the mandatory workflow gate. Use `scripts/init_workstream.py` only after user confirmation and explicit deep-interview, ralplan, and autoresearch gate evidence are available. Use `scripts/update_workstream_state.py` for deterministic `STATE.json` phase updates. Use `scripts/summarize_research_state.py`, `scripts/score_research_artifacts.py`, `scripts/capture_question.py`, `scripts/prepare_workstream_closeout.py`, `scripts/preserve_negative_result.py`, and `scripts/generate_report_outline.py` for review, Q&A capture, closeout, negative-result preservation, and report-outline control-plane updates. Regression fixture cases for these contracts live in `assets/fixtures/research_workspace_cases.json` and are checked by `scripts/check_regression_fixtures.py`.

## Idea scouting artifact

`IDEA_SCOUTING.md` is optional and belongs at the portfolio root. It is used only before a clear research question exists, when the user asks for idea generation, idea triage, broad-direction scouting, `.omx/ai-research/CONFIG.md` sets `idea_scouting: on`, or `idea_scouting: auto` applies under a guided/autonomous preset.

Use `assets/templates/IDEA_SCOUTING.md` when creating it.

`IDEA_SCOUTING.md` minimum sections:

- Scouting objective: user goal, broad area, and whether the pass is generating candidates, evaluating an existing idea, or converging a vague direction.
- Candidate idea table: candidate idea, falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty risk, feasibility budget, user-goal fit, and status.
- Promotion gate: all six required fields before an idea can be recommended for formal research intake.
- Parked or rejected ideas with evidence and revisit triggers.
- Recommended next step and a reminder to ask the user before creating a workstream.

Idea promotion gate: an idea may enter formal research intake only when it has a falsifiable hypothesis, evaluation metric or baseline, lightweight evidence, novelty-risk note, feasibility budget, and user-goal fit. Scouting does not guarantee absolute novelty and does not replace full `LITERATURE.md`.

## Optional feedback memory artifacts

Research Feedback Memory, Question Capture, and Researcher Growth Review are opt-in. They are disabled by default and must not create extra files unless enabled by invocation flags or `.omx/ai-research/CONFIG.md`.

Supported invocation flags:

- `--feedback-memory`: enable Research Feedback Memory for the current invocation.
- `--qa-capture`: enable Q&A capture for the current invocation.
- `--growth-review`: enable Researcher Growth Review for the current invocation.
- `--no-feedback`: force feedback memory, Q&A capture, and growth review off for the current invocation.

Optional `.omx/ai-research/CONFIG.md` fields:

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

Precedence is: `--no-feedback`, explicit enable flags, `.omx/ai-research/CONFIG.md`, then default off.

`LEARNINGS.md` minimum sections:

- Concepts, papers, methods, or domain knowledge learned
- Evidence links to workstream artifacts, runs, code, or citations
- Applicability notes and limits
- Open questions or follow-up reading

`ISSUES.md` minimum sections:

- Problem, blocker, bug, failed assumption, or environment issue
- Detection evidence and affected workstream/run
- Root cause if known
- Resolution, workaround, or next recovery command
- Prevention note when reusable

`DECISIONS.md` minimum sections:

- Decision
- Context and constraints
- Alternatives considered and rejected
- Evidence or rationale
- Scope risk and revisit trigger

`SKILL_GROWTH.md` minimum sections:

- Capability area: problem definition, research taste, experiment design, verification, systems engineering, expression/collaboration, or risk awareness
- Concrete episode and artifact links
- Lesson learned
- Next practice item

Workstream `DESIGN.md` minimum sections when `feedback_memory` is `full`:

- Method, architecture, data, evaluation, and pipeline design decisions
- Constraints and rejected alternatives
- Interfaces or project-root paths affected
- Validation expectations and known risks

Workstream `NOTES.md` minimum sections when Research Feedback Memory is enabled:

- Durable process notes that are useful beyond the current chat
- Reusable commands or checks
- Cross-links to `RUNS.md`, `RESULTS.md`, `SCRIPT_REGISTRY.md`, and project-root files

Workstream `REVIEW.md` minimum sections when Researcher Growth Review is enabled:

- Milestone reviewed
- Evidence quality and overclaim risk
- Problem-definition, experiment-design, verification, and systems-engineering lessons
- Next capability practice item

Keep feedback files concise and distilled. Raw logs, checkpoints, private data, and large run outputs stay in `runs/` or external artifact storage.

## Optional question capture artifacts

Question Capture is opt-in. It records user questions and answer summaries when the user asks a research, design, architecture, experiment, interpretation, or workflow question rather than issuing a command. See `references/question-capture.md`.

`QUESTIONS.md` can exist at the portfolio root or inside a workstream:

```text
.omx/ai-research/QUESTIONS.md
.omx/ai-research/<slug>/QUESTIONS.md
```

Use `assets/templates/QUESTIONS.md` when creating either file.

`QUESTIONS.md` minimum sections:

- Q&A ledger with date, scope, user question, answer summary, evidence/links, routed updates, and follow-up
- Links to artifacts, code paths, citations, commands, or an explicit `chat-only reasoning` marker
- Routed update notes when the answer also changed `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, `DESIGN.md`, `NOTES.md`, `SKILL_GROWTH.md`, or `REVIEW.md`

Do not persist secrets, credentials, private data, transient status checks, command-only prompts, or unanswered questions.

## Portfolio artifacts

Minimum `.omx/ai-research/RESEARCH.md` sections:

- Overall research objective
- Central research question
- North-star hypotheses
- Success and falsification criteria
- Claim boundaries and non-goals
- Current synthesis / best-known answer
- Active workstreams and how they relate to the central question
- Evidence map linking to workstream artifacts
- Open decisions and next priorities
- Last updated

Minimum `.omx/ai-research/INDEX.md` sections:

- Workstream table: slug, status, subquestion, relationship to overall objective, key artifact links, latest evidence, mandatory workflow gate evidence, next action
- New-workstream decision log: why a new slug was created instead of reusing an existing one
- Archived or superseded workstreams
- Cross-workstream dependencies and conflicts

Before creating a new workstream, inspect portfolio `RESEARCH.md`, portfolio `INDEX.md`, and existing `.omx/ai-research/<slug>/` directories. Reuse an existing workstream unless the new task has a distinct research question, validation target, or artifact boundary.

New workstream mandatory workflow gate:

- `$deep-interview --autoresearch` must produce or link a validator-ready mission/intake artifact before a new slug is opened.
- `$ralplan` must produce or link consensus planning output, `.omx/plans/prd-<slug>.md`, and `.omx/plans/test-spec-<slug>.md`.
- `$autoresearch` must persist state with a `completion_artifact_path` and link `.omx/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`.
- `INDEX.md` must record the exact evidence paths for all three gates before implementation or experiment execution starts.

## Required artifacts

| Artifact | Purpose | Created by phase |
| --- | --- | --- |
| `IDEA_SCOUTING.md` | Optional candidate idea generation, triage, lightweight evidence, promotion gate, and rejected-idea ledger | idea scouting |
| `STATE.json` | Workstream phase state, gate evidence pointers, blockers, next action, and confirmation boundaries | every workstream phase |
| `RESEARCH.md` | Scientific intent, hypothesis, contribution, success/falsification criteria, non-goals, claim boundaries | intake / question spec |
| `LITERATURE.md` | Source-backed related work, baselines, datasets, benchmark constraints, evidence gaps | literature review |
| `EXPERIMENT.md` | Runnable experimental protocol and validation plan | experiment design |
| `SCRIPT_REGISTRY.md` | Project-local commands/scripts, ownership, inputs, outputs, dependencies, rerun safety, and validation status | implementation / experiment execution |
| `RUNS.md` | Commands, environment, tmux session/status, data versions, seeds, seed-to-device/resource allocation, complete log paths, metrics paths, figure paths, result paths, failures | experiment execution |
| `RESULTS.md` | Tables, analysis, uncertainty, ablations, threats to validity | analysis |
| `CLAIMS.md` | Evidence-to-claim ledger, allowed/forbidden wording, negative/inconclusive findings, retired or downgraded claims | analysis / paper/report drafting |
| `REPRODUCIBILITY.md` | Reproducibility checklist and blockers | reproducibility review |
| `PAPER_DRAFT.md` | Claim-traceable paper/report draft | paper/report drafting |
| `CLOSEOUT.md` | Workstream completion handoff, validation evidence, artifact distillation checklist, report-before-merge confirmation boundary | completion handoff / report-before-merge |
| `PAPER_OUTLINE.md` / report outlines | Paper, workshop, internal, blog, or rebuttal scaffold with claim/evidence boundaries | paper/report drafting |

## `STATE.json` minimum fields

- `schema_version: 1`
- `workstream_slug`
- `phase`: one of `idea-scouting`, `intake`, `literature`, `experiment-design`, `implementation`, `running`, `completion-handoff`, `report-before-merge`, `reproducibility-review`, `paper-draft`, or `archived`
- `phase_status`
- `last_updated`
- `active_artifacts`
- `gate_evidence`: deep-interview autoresearch, ralplan PRD/test spec, and autoresearch result paths when available
- `current_blockers`
- `next_action`
- `confirmation_required_before`: final-topic promotion, new workstream creation, merge, push, worktree removal, and branch deletion when applicable

## Workstream `RESEARCH.md` minimum sections

- Title
- Research question
- Hypothesis
- Contribution type
- Motivation and expected novelty
- Success criteria
- Falsification criteria
- In scope
- Out of scope / non-goals
- Claim boundaries / forbidden claims
- Decision boundaries
- Open questions
- Link to portfolio `RESEARCH.md`
- Links to new-workstream gate evidence: deep-interview autoresearch handoff, ralplan PRD/test spec, autoresearch state/completion artifact
- Parent workstream or sibling workstreams when relevant

## `LITERATURE.md` minimum sections

- Search date
- Query strategy
- Inclusion / exclusion criteria
- Source table: title, venue/date, link, relevance, key evidence
- Related-work matrix
- Baseline candidates
- Dataset and benchmark notes
- Gaps and risks

## `EXPERIMENT.md` minimum sections

- Experiment objective
- Datasets and splits
- Baselines
- Baseline fairness checklist: same data split/preprocessing, same evaluation metric, comparable compute/tuning budget, hyperparameter search budget, implementation source/version, and known reproduction gaps
- Method variants
- Training or inference configuration
- Metrics
- Statistical testing plan
- Ablations
- Seeds
- Hardware and runtime budget
- Multi-seed parallelism and accelerator/resource allocation plan
- Logging and artifact paths
- Reproduction commands
- Failure policy
- Negative / inconclusive result policy distinguishing environment failure, implementation bug, underpowered result, and hypothesis failure
- Run directory contract
- Detached tmux launch and monitoring plan
- Complete log capture plan
- Metrics output schema
- Progress reporting plan
- Visualization output plan
- Project-root implementation and baseline reproduction paths

## `SCRIPT_REGISTRY.md` minimum sections

- Project-native commands that already satisfy the research contract
- Project-local wrapper scripts under `.omx/ai-research/<slug>/scripts/`
- Purpose, owner phase, inputs, outputs, dependencies, and environment variables for each command/script
- Safe-to-rerun/idempotency notes
- Validation status and last validated command/log path
- Replacement/deprecation notes when a script becomes stale
- Completion-handoff notes for scripts or native commands that were used, changed, validated, deprecated, or explicitly requested by the user during the finished experiment

## `RUNS.md` minimum sections

- Run directory absolute path
- Run manifest path
- Tmux session name and `tmux_status.json` path when used
- Complete log file absolute path
- Command and project-local wrapper script path when used
- Environment and git commit
- Data versions
- Seeds
- Seed-to-device/resource allocation table for parallel runs
- Metrics file paths
- Summary file path
- Figure output paths
- Distilled updates made outside `runs/`
- Project-root docs/config/code/test updates caused by this run
- User-requested outputs or decisions persisted during experiment completion handoff
- Worktree closeout plan with validation, merge-back, push, cleanup, and user-confirmation status when a task worktree was used
- Exit status and failures

## `RESULTS.md` minimum sections

- Result artifact paths
- Summary tables
- Hypothesis verdicts: supported, contradicted, inconclusive
- Negative and inconclusive results with evidence paths, failure category, interpretation, and claim updates
- Uncertainty / variance
- Ablations
- Error analysis
- Threats to validity
- Evidence-to-claim mapping
- Link to `CLAIMS.md` as authoritative claim ledger
- Visualization manifest path and figure captions
- Run distillation notes: what moved from raw run evidence into stable conclusions, docs, configs, or code

## `CLAIMS.md` minimum sections

- Claim ledger with claim ID, claim, status, evidence paths, scope/population, allowed wording, forbidden wording, and last checked
- Evidence requirements for supported, contradicted, inconclusive, draft, and retracted claims
- Negative or inconclusive results with evidence path, likely cause, scientific value, and follow-up or stop condition
- Retired or downgraded claims with previous wording, new wording/status, reason, and evidence

## `CLOSEOUT.md` minimum sections

`CLOSEOUT.md` is optional but recommended when a workstream reaches completion handoff or report-before-merge. `scripts/prepare_workstream_closeout.py` can write it.

- Generated timestamp, workstream slug, phase/status, and next action
- Run directories and script files inspected
- Missing completion artifacts and TODO counts
- Validation evidence paths and whether they exist
- Required distillation updates for `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `CLAIMS.md`, `REPRODUCIBILITY.md`, portfolio `RESEARCH.md`, and portfolio `INDEX.md`
- Worktree path when applicable
- Blockers
- Confirmation boundary: merge, push, worktree removal, and branch deletion require explicit user confirmation

## Research review and report outline artifacts

Research review has two deterministic helpers:

- `scripts/summarize_research_state.py`: read-only portfolio/workstream state summary with phases, blockers, missing artifacts, run/script inventory, and suggested next actions.
- `scripts/score_research_artifacts.py`: read-only artifact quality score. Scores are heuristic; low scores are blockers to stronger claims, not proof that high scores make claims true.

Report-outline artifacts generated by `scripts/generate_report_outline.py` must include:

- source artifact list
- evidence-to-claim rule
- negative/inconclusive result rule
- sections appropriate to paper outline, workshop report, internal report, blog summary, or rebuttal notes
- TODO placeholders until evidence paths are filled

Negative-result preservation via `scripts/preserve_negative_result.py` must update both `RESULTS.md` and `CLAIMS.md`; it must not erase failed or inconclusive evidence.

## Published docs minimum sections

When findings are settled, publish browser-readable copies under `docs/ai-research/<slug>/`:

- `index.md`: summary and links to all artifact pages
- `research.md`
- `literature.md`
- `experiment.md`
- `runs.md`
- `results.md`
- `reproducibility.md`
- `paper-draft.md` when available

Project root should contain `mkdocs.yml` when safe to create. If a project already has MkDocs configuration, preserve it and report any nav update needed. Publishing can be done with a project-local `publish_docs_<name>.sh` entry in `SCRIPT_REGISTRY.md`, but the contract is the `docs/` output, not the presence of a bundled publisher.

## Run distillation contract

Each terminal run directory remains raw evidence. After completion, extract durable information outside `runs/`:

- Update `RUNS.md` as the run index and status ledger.
- Update `SCRIPT_REGISTRY.md` with scripts or native commands that were used, changed, validated, deprecated, or requested by the user.
- Update `RESULTS.md` with tables, figures, interpretation, and hypothesis verdicts when evidence changes.
- Update `REPRODUCIBILITY.md` with rerun instructions, blockers, environment notes, or nondeterminism.
- Promote stable conclusions to project-root `docs/`, `reports/`, benchmark cards, README sections, or MkDocs pages.
- Promote reusable code/config/test changes to the project root, not to `.omx/ai-research/`.
- Keep raw logs, checkpoints, private data, and large temporary outputs in run/artifact storage; link or summarize them instead of copying them into project docs.

When the user says the current experiment is done, treat that message as an experiment completion handoff trigger. Inspect available run directories and project-local scripts, then persist valuable or user-requested content into the stable artifacts above before giving the final answer. If a requested artifact cannot be written because evidence is missing, record the missing path and exact recovery step.

If a completed run changes the larger research picture, update portfolio `RESEARCH.md` with the new synthesis and portfolio `INDEX.md` with the workstream status, latest evidence, and next priority.

If the workstream used a task worktree, the completion handoff must also write a report-before-merge closeout plan. Include current branch/worktree path, base branch, validation evidence still needed, semantic Lore-format commit status, merge/rebase command plan, push target, worktree removal command, branch deletion command, and `.omx/worktrees/REGISTRY.md` update. Do not execute merge, push, worktree removal, or branch deletion until the user confirms.

## Schema and evidence graph artifacts

Machine-checkable schemas live in `assets/schemas/`:

- `assets/schemas/CONFIG.schema.json`: allowed config keys and values.
- `assets/schemas/STATE.schema.json`: required workstream lifecycle state, gate evidence, blockers, next action, and confirmation boundaries.
- `assets/schemas/CLAIM.schema.json`: claim ledger row shape, including status, evidence paths, scope, allowed wording, and forbidden wording.
- `assets/schemas/RUN.schema.json`: run ledger row shape, including command, status, log path, metrics path, summary path, and commit.
- `assets/schemas/INDEX_ROW.schema.json`: portfolio index row shape linking slug, status, subquestion, artifact links, gate evidence, and next action.

Use `scripts/validate_research_schema.py <project-root>` as a guardrail-level schema validator. It performs stdlib validation for CONFIG, STATE, `CLAIMS.md`, `RUNS.md`, and root `INDEX.md` rows. Warnings mean the artifact is still scaffold-like; errors mean the control-plane contract is malformed.

Use `scripts/build_evidence_graph.py <project-root> <slug> --json` before paper/report drafting or merge-back when claim traceability matters. The graph is a review aid: claim nodes link to evidence nodes, run nodes link to logs/metrics/summaries, and script nodes link to produced outputs. The graph does not prove a claim; it exposes whether evidence is traceable.

Use `scripts/migrate_research_workspace.py <project-root>` for legacy workspaces. Default mode is dry-run. `--write` creates missing control-plane files only; `--force` is required to overwrite. Migration should mark unknown gate evidence as a blocker rather than pretending old work passed the new-workstream mandatory workflow gate.
