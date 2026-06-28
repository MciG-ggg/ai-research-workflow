# Workflow Orchestration

This skill is a workflow, not only an experiment logging template. It coordinates OMC modes and project work from vague idea to implemented method, reproduced baseline, evidence-backed results, and writeup.

## Contents

- [Default OMC sequence](#default-omx-sequence)
- [Deterministic routing helpers](#deterministic-routing-helpers)
- [Subcommand routing surface](#subcommand-routing-surface)
- [Optional idea scouting](#optional-idea-scouting)
- [Optional feedback mode resolution](#optional-feedback-mode-resolution)
- [Portfolio and workstream control plane](#portfolio-and-workstream-control-plane)
- [New workstream mandatory workflow gate](#new-workstream-mandatory-workflow-gate)
- [Control plane vs project implementation plane](#control-plane-vs-project-implementation-plane)
- [Run distillation rule](#run-distillation-rule)
- [Baseline and method work](#baseline-and-method-work)

## Default OMC sequence

Use this default sequence unless existing artifacts prove that a phase is already complete:

```text
optional idea scouting when no clear research question exists
  -> optional SOTA/baseline paper registry when requested
  -> optional paper-reproduction scouting when explicitly requested
  -> /oh-my-claudecode:deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
  -> literature / research artifact drafting
  -> /oh-my-claudecode:ralplan for implementation and validation plan
  -> task worktree execution in the target repo
  -> /oh-my-claudecode:autoresearch for validator-gated research loop
  -> run experiments / reproduce baselines / evaluate method
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Phase rules:

- Use Idea Scouting before formal intake when the user asks to generate ideas, evaluate whether an idea is worth doing, or only provides a broad area without a falsifiable research question.
- Use Paper Registry Scouting when the user asks to find SOTA/baseline papers or maintain a paper list; write `.ai-research-workflow/PAPERS.md`.
- Use Paper-Reproduction Scouting when the user explicitly wants to reproduce a paper to find ideas; prepare the paper and workstream artifacts without running experiments or creating a slug before confirmation.
- Use `/oh-my-claudecode:deep-interview --autoresearch` when the research mission, hypothesis, evaluator, non-goals, claim boundaries, or launch criteria are unclear.
- Use `/oh-my-claudecode:ralplan` before implementation-heavy work to produce a plan, tradeoffs, file ownership, and validation shape.
- Use `/oh-my-claudecode:autoresearch` when the work needs a persistent professor/critic or validator-gated loop over literature, implementation, experiments, and claims.
- Use `/oh-my-claudecode:team` or native subagents for independent lanes such as multiple seeds, baselines, ablations, literature blocks, or verification lanes.
- Use `/oh-my-claudecode:ralph`/`/oh-my-claudecode:autopilot` only after research and experiment specs exist and the remaining work is mainly implementation plus verification.

If the user provides mature artifacts, resume at the earliest failing gate instead of repeating completed phases.

## Deterministic routing helpers

Use framework guardrail scripts when the workflow decision should be reproducible instead of purely prose-driven:

```bash
python3 scripts/resolve_workflow.py <project-root> --prompt "<user prompt>"
python3 scripts/init_research_workspace.py <project-root> --preset guided
python3 scripts/init_workstream.py <project-root> <slug> --title "..." --question "..." --deep-interview <path> --ralplan-prd <path> --ralplan-test-spec <path> --autoresearch-result <path>
python3 scripts/update_workstream_state.py <project-root> <slug> --phase running --next-action "monitor run"
python3 scripts/summarize_research_state.py <project-root>
python3 scripts/score_research_artifacts.py <project-root>
python3 scripts/capture_question.py <project-root> --question "..." --answer-summary "..."
python3 scripts/prepare_workstream_closeout.py <project-root> <slug> --write
python3 scripts/preserve_negative_result.py <project-root> <slug> --finding "..." --evidence <path> --interpretation "..." --claim-update "..."
python3 scripts/generate_report_outline.py <project-root> <slug> --kind paper-outline --write
python3 scripts/validate_research_workspace.py <project-root> --phase idea-scouting
python3 scripts/validate_research_workspace.py <project-root> --phase paper-scouting
python3 scripts/validate_research_workspace.py <project-root> --phase paper-reproduction --workstream <slug>
python3 scripts/validate_research_workspace.py <project-root> --phase new-workstream --workstream <slug>
python3 scripts/validate_research_workspace.py <project-root> --phase completion-handoff --workstream <slug>
```

`resolve_workflow.py` emits JSON decisions for idea scouting, completion handoff, new-workstream gating, report-before-merge closeout, question capture, negative-result preservation, and ask-required boundaries. Its structured routing output includes `phase`, `workflow_action`, `requires_user_confirmation`, `next_artifacts`, and `guardrail_scripts`. `init_research_workspace.py` initializes the portfolio control plane only. `init_workstream.py` scaffolds a workstream only after user confirmation and explicit deep-interview, ralplan, and autoresearch gate evidence. `update_workstream_state.py` updates `STATE.json` without touching research code or running experiments.

`summarize_research_state.py` and `score_research_artifacts.py` are read-only review helpers. `capture_question.py`, `prepare_workstream_closeout.py`, `preserve_negative_result.py`, and `generate_report_outline.py` write only research control-plane artifacts.

## Subcommand routing surface

The skill supports these explicit lanes. Use them when the user wants less manual workflow steering:

| Subcommand | Phase | Primary artifacts |
| --- | --- | --- |
| `scout` | idea-scouting | `IDEA_SCOUTING.md` |
| `papers` | paper-scouting | `PAPERS.md` |
| `reproduce-paper` | paper-reproduction gate | `PAPERS.md`, `<slug>/REPRODUCTION.md` |
| `experiment` | new-workstream gate | `<slug>/EXPERIMENT.md`, `<slug>/RUNS.md`, `<slug>/RESULTS.md` |
| `new-workstream` | new-workstream gate | `INDEX.md`, `<slug>/STATE.json`, `<slug>/RESEARCH.md` |
| `handoff` | completion-handoff | `RUNS.md`, `SCRIPT_REGISTRY.md`, `RESULTS.md`, `CLAIMS.md`, `REPRODUCIBILITY.md` |
| `qa` | question-capture | `QUESTIONS.md` |
| `summarize` | portfolio-summary | portfolio/workstream status summary |
| `score` / `review` | research-review | artifact quality score and claim-risk review |
| `closeout` | report-before-merge | `CLOSEOUT.md`, worktree closeout plan |
| `negative-result` | result-analysis | negative/inconclusive result preservation in `RESULTS.md` and `CLAIMS.md` |
| `draft` | paper-draft | paper outline, workshop report, internal report, blog summary, or rebuttal notes |

Subcommands do not bypass confirmation boundaries. Workstream creation, final topic promotion, merge, push, worktree removal, branch deletion, and stronger claims after negative/inconclusive evidence still require explicit user confirmation.

## Optional idea scouting

Idea Scouting is optional. It is not a mandatory first stage when the user already has a concrete research question, hypothesis, metric, and baseline.

Activation:

1. Run when the user asks for research idea generation, idea triage, broad-direction scouting, or whether an idea is worth pursuing.
2. Run when the current invocation includes `--idea-scouting`.
3. Run when `.ai-research-workflow/CONFIG.md` sets `idea_scouting: on`.
4. Run when `workflow_preset` is `guided` or `autonomous`, `idea_scouting: auto`, and the prompt is broad/vague.
5. Skip when a formal workstream can already pass the intake gate.

Write `.ai-research-workflow/IDEA_SCOUTING.md` using `assets/templates/IDEA_SCOUTING.md`. The scouting pass may search sources, generate candidates, rank/filter them, and mark weak ideas as parked or rejected.

When the user asks to find SOTA/baseline papers, write `.ai-research-workflow/PAPERS.md` using `assets/templates/PAPERS.md`. This paper registry is portfolio-level and should be maintained across scouting passes. It tracks paper role, key claim, benchmark/metric, code/data/checkpoint availability, reproduction priority, status, and maintenance history.

When the user asks to reproduce a paper to find ideas, use paper-reproduction scouting. Update `PAPERS.md`, add paper-derived candidate ideas to `IDEA_SCOUTING.md`, and ask before selecting one paper for a workstream. On confirmation, enter the new-workstream mandatory gate and create a workstream with `REPRODUCTION.md` from `assets/templates/REPRODUCTION.md`. Paper-reproduction scouting never downloads data, runs experiments, or creates worktrees by itself.

Promotion gate: recommend a candidate for formal intake only when it has a falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty-risk note, feasibility budget, and user-goal fit. Ask the user before creating `.ai-research-workflow/<slug>/`; on confirmation, enter the new-workstream mandatory workflow gate.

## Optional feedback mode resolution

Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default. At workflow entry, resolve these modes from the user invocation and project config before creating optional files.
Question Capture is disabled by default and follows the same resolution step.

1. `--no-feedback` forces feedback memory, Q&A capture, and growth review off for the current invocation.
2. `--feedback-memory`, `--qa-capture`, or `--growth-review` enables that mode for the current invocation.
3. `.ai-research-workflow/CONFIG.md` can set `workflow_preset: conservative | guided | autonomous`, `idea_scouting: auto | off | on`, `completion_handoff: auto | off`, `worktree_closeout: off | report-before-merge`, `feedback_memory: off | lite | full`, `qa_capture: off | research | all`, and `growth_review: off | milestone | always`.
4. Missing config uses the `guided` workflow preset for routing, while feedback memory, Q&A capture, and growth review remain off.

Preset rules:

- `conservative`: run only explicitly requested phases.
- `guided`: infer common phases from user language while preserving confirmation boundaries.
- `autonomous`: proactively maintain relevant artifacts and next-step plans, but still ask before final-topic selection, workstream creation, merge, push, worktree removal, or branch deletion.
- Overrides win over the preset.

When Research Feedback Memory is enabled, write distilled issues, learnings, decisions, design notes, architecture tradeoffs, reusable commands, and failed assumptions to the optional feedback artifacts defined in `artifact-contracts.md`. When Question Capture is enabled, answer question-like prompts first and then write the Q&A ledger entry described in `question-capture.md`. When Researcher Growth Review is enabled, write capability-focused reflections to `SKILL_GROWTH.md` and workstream `REVIEW.md`.

Feedback writes happen at natural workflow boundaries: intake, experiment design, implementation handoff, experiment completion handoff, reproducibility review, and paper/report drafting. Do not interrupt default workflows with reflection questions unless growth review is enabled and one concise answer would materially improve the review.

## Portfolio and workstream control plane

Every project gets a root portfolio layer under `.ai-research-workflow/`:

- `.ai-research-workflow/RESEARCH.md`: the overall research program, central question, north-star hypotheses, claim boundaries, current synthesis, and next priorities.
- `.ai-research-workflow/INDEX.md`: the workstream registry mapping each `<slug>` to its subquestion, status, artifact links, latest evidence, and next action.
- `.ai-research-workflow/PAPERS.md`: optional SOTA/baseline paper registry when paper scouting or paper reproduction is requested.

Each `.ai-research-workflow/<slug>/` directory is a workstream, not the whole research program. It should link back to the portfolio `RESEARCH.md` and appear in `INDEX.md`.

Each active workstream also keeps `STATE.json` as the current phase state and `CLAIMS.md` as the claim ledger. Update `STATE.json` when the workflow moves between intake, literature, experiment-design, running, completion-handoff, report-before-merge, reproducibility-review, paper-draft, or archived phases. Update `CLAIMS.md` whenever evidence changes allowed wording, forbidden wording, or the status of a claim.

Before creating a new slug:

1. Read or create the portfolio `RESEARCH.md` and `INDEX.md`.
2. List existing `.ai-research-workflow/<slug>/` directories.
3. Reuse an existing workstream when the request is a continuation, replication, ablation, or follow-up within the same research question.
4. Create a new slug only for a distinct subquestion, method family, baseline family, dataset/benchmark lane, or paper/report slice.
5. Record the new slug, relationship to the overall objective, owned artifacts, and next action in `INDEX.md`.

## New workstream mandatory workflow gate

Creating a new workstream is a gated transition, not a directory operation. When the request requires a new slug, the following sequence is mandatory and ordered:

```text
/oh-my-claudecode:deep-interview --autoresearch
  -> /oh-my-claudecode:ralplan
  -> /oh-my-claudecode:autoresearch
```

The gate blocks creating `.ai-research-workflow/<slug>/`, implementation, experiment launch, or docs publishing until the portfolio `INDEX.md` records these evidence paths:

1. Deep interview autoresearch handoff: validator-ready mission/intake artifact, preferably `.omc/specs/autoresearch-<slug>/mission.md`, plus the workstream `RESEARCH.md` draft or exact planned path.
2. Ralplan consensus: final plan plus `.omc/plans/prd-<slug>.md` and `.omc/plans/test-spec-<slug>.md`.
3. Autoresearch state: persisted `/oh-my-claudecode:autoresearch` state with `completion_artifact_path`, plus `.omc/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`.

If any required evidence is missing, stop at the gate and complete the missing workflow. Do not bypass the gate because the user says the direction is small, obvious, or urgent. The only safe bypass is to reuse an existing workstream whose `INDEX.md` row already links equivalent gate evidence.

### Workstream type selection

Choose a `workstream_type` before scaffolding:

- `paper-reproduction`: the workstream is anchored to one selected paper, baseline, or claim. Scaffold `REPRODUCTION.md` and link the workstream from `PAPERS.md`.
- `experiment-campaign`: the workstream is anchored to a hypothesis, ablation set, benchmark/evaluation campaign, or method variant. `EXPERIMENT.md` is the primary design artifact.

“Running experiments” is a phase inside both types, not a sufficient type by itself. Use the type to preserve why the workstream exists and what must be distilled back to the portfolio.

## Control plane vs project implementation plane

`.ai-research-workflow/` is the portfolio control plane. `.ai-research-workflow/<slug>/` is a workstream control plane. Together they store specs, decisions, run indexes, evidence summaries, reproducibility notes, and the global synthesis.

Actual research work belongs in the target project root using that project's conventions. Examples:

- method implementation: `src/`, `models/`, `methods/`, `algorithms/`, or the existing package layout
- baseline or paper reproduction: `baselines/`, `configs/`, `scripts/`, `experiments/`, or existing benchmark layout
- training/evaluation entrypoints: project-native CLIs, notebooks, Make targets, Hydra configs, CI jobs, or shell scripts
- tests and verification: `tests/`, `evals/`, CI config, smoke tests, benchmark checks
- user-facing reports/docs: `docs/`, `reports/`, `mkdocs.yml`, README sections, benchmark cards

Do not implement the user's method, model, baseline, dataset adapter, or production experiment code inside `.ai-research-workflow/`. Only thin orchestration wrappers, run metadata, and research notes belong there.

## Run distillation rule

A completed run directory is raw evidence. After each terminal run, distill reusable knowledge out of `runs/<run-id>/`:

1. Update `.ai-research-workflow/<slug>/RUNS.md` with command, seed/device/resource, status, log path, metrics path, summary path, and failure notes.
2. Update `.ai-research-workflow/<slug>/SCRIPT_REGISTRY.md` with scripts or native commands that were used, changed, validated, deprecated, or requested by the user.
3. Update `.ai-research-workflow/<slug>/RESULTS.md` with tables, figures, hypothesis verdicts, and interpretation when the run changes the scientific picture.
4. Update `.ai-research-workflow/<slug>/REPRODUCIBILITY.md` with new blockers, environment notes, nondeterminism, or rerun instructions.
5. Promote stable conclusions to project-root `docs/`, `reports/`, benchmark cards, config docs, or README sections when useful.
6. Promote reusable implementation changes to project-root code/config/tests, not to `.ai-research-workflow/`.
7. When Research Feedback Memory is enabled, update `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, and workstream `NOTES.md`/`DESIGN.md` with distilled lessons, blockers, decisions, reusable commands, and design rationale.
8. When Researcher Growth Review is enabled, update `SKILL_GROWTH.md` and workstream `REVIEW.md` with concrete capability lessons tied to evidence.

Do not copy raw logs, large outputs, checkpoints, private data, or temporary run files into project-root docs. Link to them or summarize them.

If the user says the current experiment is done, use this as an experiment completion handoff signal: inspect runs and scripts, persist valuable or user-requested content into stable artifacts, then report the paths written.

If the workstream used a task worktree, completion handoff also includes a report-before-merge closeout plan: validation still needed, semantic commit status, base branch, merge/rebase command, push target, worktree removal, branch deletion, and `.omc/worktrees/REGISTRY.md` update. Do not merge, push, remove the worktree, or delete the branch until the user confirms the plan.

When distillation changes the global picture, update `.ai-research-workflow/RESEARCH.md` and `.ai-research-workflow/INDEX.md` in the same pass so the portfolio layer remains the user's overall map of the work.

For a paper-reproduction workstream, completion handoff also updates `.ai-research-workflow/PAPERS.md` with reproduction status, evidence links, blockers, and revised priority. If the reproduction generated new candidate ideas, update `.ai-research-workflow/IDEA_SCOUTING.md` or the relevant workstream artifacts with those ideas before closing the stream.

Negative or inconclusive runs are first-class evidence. Preserve them in `RESULTS.md` and `CLAIMS.md` before changing the story, and downgrade or retire unsupported claims instead of deleting failed evidence.

At handoff, run a research review pass: summarize portfolio state, score artifact quality, and generate report outlines only after evidence-to-claim mapping is stable.

## Baseline and method work

Baseline reproduction and new method implementation are first-class workflow tasks:

- Reproduce baselines before claiming improvement unless the research question explicitly excludes them.
- Reproduce a selected paper only inside a confirmed workstream with `REPRODUCTION.md`, `EXPERIMENT.md`, `RUNS.md`, `RESULTS.md`, `CLAIMS.md`, and `REPRODUCIBILITY.md` linked.
- Keep baseline commands/configs reproducible and trace them from `EXPERIMENT.md` and `RUNS.md`.
- Implement methods in the project root with tests or smoke checks before expensive runs.
- Record claim boundaries when a baseline cannot be reproduced due to missing data, compute, license, or environment.

## Productized guardrail surfaces

Use these helpers when a workflow needs more than natural-language routing:

- `scripts/ai_research.py`: unified CLI facade over common guardrails. It is useful when the user wants subcommand-style behavior but the shell entry point is easier than remembering individual script names.
- `scripts/question_capture_hook.py`: hook integration helper. `--stage submit` classifies and stores pending question state; `--stage answer` appends a final Q&A entry only after an answer summary exists.
- `scripts/migrate_research_workspace.py`: legacy workspace migration tool. Default mode is dry-run; `--write` creates missing control-plane artifacts and `--force` is required before overwriting.
- `scripts/validate_research_schema.py`: schema validator for `CONFIG.md`, workstream `STATE.json`, claim rows, run rows, and portfolio index rows using `assets/schemas/`.
- `scripts/build_evidence_graph.py`: claim/evidence graph helper that links `CLAIMS.md` to evidence paths, runs, and project-local scripts.
- `scripts/check_skill_update.py`: version/update check surface using `assets/VERSION`, source git status, installed skill version, and optional remote status.
- `scripts/run_e2e_scenarios.py`: maintenance-only E2E scenario tests for routing, workstream init, Q&A capture, negative result preservation, closeout, schema validation, and graph generation.

`assets/hooks/question-capture.example.json` is only example hook wiring; it does not install hooks automatically. `assets/schemas/STATE.schema.json`, `CONFIG.schema.json`, `CLAIM.schema.json`, `RUN.schema.json`, and `INDEX_ROW.schema.json` define framework artifact shape, not a research result schema.

If you want X, say Y:

| Desired action | Recommended command or phrase |
| --- | --- |
| Generate candidate topics | `/oh-my-claudecode:ai-research-workflow scout` |
| Find SOTA/baseline papers | `/oh-my-claudecode:ai-research-workflow papers` |
| Reproduce one selected paper | `/oh-my-claudecode:ai-research-workflow reproduce-paper` |
| Open an experiment campaign | `/oh-my-claudecode:ai-research-workflow experiment` |
| Open a gated small direction | `/oh-my-claudecode:ai-research-workflow new-workstream` |
| Finish and distill an experiment | `/oh-my-claudecode:ai-research-workflow handoff` or “current experiment is done” |
| Capture a durable question | `/oh-my-claudecode:ai-research-workflow qa` after enabling `qa_capture` |
| Preserve a negative/null result | `/oh-my-claudecode:ai-research-workflow negative-result` |
| Check current portfolio status | `/oh-my-claudecode:ai-research-workflow summarize` |
| Review readiness and claims | `/oh-my-claudecode:ai-research-workflow score`, `validate_research_schema.py`, and `build_evidence_graph.py` |

These helpers remain control-plane guardrails. They do not run experiments, collect user metrics, plot results, publish docs, merge branches, push remotes, remove worktrees, or delete branches.
