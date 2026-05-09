# AI Research Artifact Contracts

Use these contracts to keep scientific goals separate from execution details and to keep `.omx/ai-research` metadata separate from project-root implementation work.

## Control plane vs project-root outputs

`.omx/ai-research/` has a portfolio control plane and one or more workstream control planes.

Portfolio control plane:

```text
.omx/ai-research/
  RESEARCH.md
  INDEX.md
```

Optional feedback memory and growth review artifacts, created only when enabled:

```text
.omx/ai-research/
  CONFIG.md
  LEARNINGS.md
  ISSUES.md
  DECISIONS.md
  SKILL_GROWTH.md
.omx/ai-research/<slug>/
  DESIGN.md
  NOTES.md
  REVIEW.md
```

`.omx/ai-research/RESEARCH.md` stores the overall research program: central question, north-star hypotheses, success criteria, claim boundaries, current synthesis, active subquestions, and next priorities.

`.omx/ai-research/INDEX.md` stores the workstream registry: each `<slug>`, status, relationship to the overall question, artifact links, latest evidence, and next action.

`.omx/ai-research/<slug>/` is the workstream control plane. It stores research intent, plans, run indexes, evidence summaries, and reproducibility notes for one concrete direction.

Project-root files are the implementation plane. Method code, baseline reproduction code, configs, tests, dataset adapters, benchmark entrypoints, and durable docs belong in the target repository's normal locations, not under `.omx/ai-research/`.

## Optional feedback memory artifacts

Research Feedback Memory and Researcher Growth Review are opt-in. They are disabled by default and must not create extra files unless enabled by invocation flags or `.omx/ai-research/CONFIG.md`.

Supported invocation flags:

- `--feedback-memory`: enable Research Feedback Memory for the current invocation.
- `--growth-review`: enable Researcher Growth Review for the current invocation.
- `--no-feedback`: force both optional modes off for the current invocation.

Optional `.omx/ai-research/CONFIG.md` fields:

```yaml
feedback_memory: off | lite | full
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
| `RESEARCH.md` | Scientific intent, hypothesis, contribution, success/falsification criteria, non-goals, claim boundaries | intake / question spec |
| `LITERATURE.md` | Source-backed related work, baselines, datasets, benchmark constraints, evidence gaps | literature review |
| `EXPERIMENT.md` | Runnable experimental protocol and validation plan | experiment design |
| `SCRIPT_REGISTRY.md` | Project-local commands/scripts, ownership, inputs, outputs, dependencies, rerun safety, and validation status | implementation / experiment execution |
| `RUNS.md` | Commands, environment, tmux session/status, data versions, seeds, seed-to-device/resource allocation, complete log paths, metrics paths, figure paths, result paths, failures | experiment execution |
| `RESULTS.md` | Tables, analysis, uncertainty, ablations, threats to validity | analysis |
| `REPRODUCIBILITY.md` | Reproducibility checklist and blockers | reproducibility review |
| `PAPER_DRAFT.md` | Claim-traceable paper/report draft | paper/report drafting |

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
- Exit status and failures

## `RESULTS.md` minimum sections

- Result artifact paths
- Summary tables
- Hypothesis verdicts: supported, contradicted, inconclusive
- Uncertainty / variance
- Ablations
- Error analysis
- Threats to validity
- Evidence-to-claim mapping
- Visualization manifest path and figure captions
- Run distillation notes: what moved from raw run evidence into stable conclusions, docs, configs, or code


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
