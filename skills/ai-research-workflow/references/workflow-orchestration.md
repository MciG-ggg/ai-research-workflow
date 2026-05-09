# Workflow Orchestration

This skill is a workflow, not only an experiment logging template. It coordinates OMX modes and project work from vague idea to implemented method, reproduced baseline, evidence-backed results, and writeup.

## Contents

- [Default OMX sequence](#default-omx-sequence)
- [Deterministic routing helpers](#deterministic-routing-helpers)
- [Optional idea scouting](#optional-idea-scouting)
- [Optional feedback mode resolution](#optional-feedback-mode-resolution)
- [Portfolio and workstream control plane](#portfolio-and-workstream-control-plane)
- [New workstream mandatory workflow gate](#new-workstream-mandatory-workflow-gate)
- [Control plane vs project implementation plane](#control-plane-vs-project-implementation-plane)
- [Run distillation rule](#run-distillation-rule)
- [Baseline and method work](#baseline-and-method-work)

## Default OMX sequence

Use this default sequence unless existing artifacts prove that a phase is already complete:

```text
optional idea scouting when no clear research question exists
  -> $deep-interview --autoresearch
  -> portfolio RESEARCH.md / INDEX.md check
  -> literature / research artifact drafting
  -> $ralplan for implementation and validation plan
  -> task worktree execution in the target repo
  -> $autoresearch for validator-gated research loop
  -> run experiments / reproduce baselines / evaluate method
  -> run distillation and project-root updates
  -> reproducibility review
  -> paper/report drafting
```

Phase rules:

- Use Idea Scouting before formal intake when the user asks to generate ideas, evaluate whether an idea is worth doing, or only provides a broad area without a falsifiable research question.
- Use `$deep-interview --autoresearch` when the research mission, hypothesis, evaluator, non-goals, claim boundaries, or launch criteria are unclear.
- Use `$ralplan` before implementation-heavy work to produce a plan, tradeoffs, file ownership, and validation shape.
- Use `$autoresearch` when the work needs a persistent professor/critic or validator-gated loop over literature, implementation, experiments, and claims.
- Use `$team` or native subagents for independent lanes such as multiple seeds, baselines, ablations, literature blocks, or verification lanes.
- Use `$ralph`/`$autopilot` only after research and experiment specs exist and the remaining work is mainly implementation plus verification.

If the user provides mature artifacts, resume at the earliest failing gate instead of repeating completed phases.

## Deterministic routing helpers

Use framework guardrail scripts when the workflow decision should be reproducible instead of purely prose-driven:

```bash
python3 scripts/resolve_workflow.py <project-root> --prompt "<user prompt>"
python3 scripts/init_research_workspace.py <project-root> --preset guided
python3 scripts/init_workstream.py <project-root> <slug> --title "..." --question "..." --deep-interview <path> --ralplan-prd <path> --ralplan-test-spec <path> --autoresearch-result <path>
python3 scripts/update_workstream_state.py <project-root> <slug> --phase running --next-action "monitor run"
python3 scripts/validate_research_workspace.py <project-root> --phase idea-scouting
python3 scripts/validate_research_workspace.py <project-root> --phase new-workstream --workstream <slug>
python3 scripts/validate_research_workspace.py <project-root> --phase completion-handoff --workstream <slug>
```

`resolve_workflow.py` emits JSON decisions for idea scouting, completion handoff, new-workstream gating, report-before-merge closeout, and ask-required boundaries. `init_research_workspace.py` initializes the portfolio control plane only. `init_workstream.py` scaffolds a workstream only after user confirmation and explicit deep-interview, ralplan, and autoresearch gate evidence. `update_workstream_state.py` updates `STATE.json` without touching research code or running experiments.

## Optional idea scouting

Idea Scouting is optional. It is not a mandatory first stage when the user already has a concrete research question, hypothesis, metric, and baseline.

Activation:

1. Run when the user asks for research idea generation, idea triage, broad-direction scouting, or whether an idea is worth pursuing.
2. Run when the current invocation includes `--idea-scouting`.
3. Run when `.omx/ai-research/CONFIG.md` sets `idea_scouting: on`.
4. Run when `workflow_preset` is `guided` or `autonomous`, `idea_scouting: auto`, and the prompt is broad/vague.
5. Skip when a formal workstream can already pass the intake gate.

Write `.omx/ai-research/IDEA_SCOUTING.md` using `assets/templates/IDEA_SCOUTING.md`. The scouting pass may search sources, generate candidates, rank/filter them, and mark weak ideas as parked or rejected.

Promotion gate: recommend a candidate for formal intake only when it has a falsifiable hypothesis, evaluation metric/baseline, lightweight evidence, novelty-risk note, feasibility budget, and user-goal fit. Ask the user before creating `.omx/ai-research/<slug>/`; on confirmation, enter the new-workstream mandatory workflow gate.

## Optional feedback mode resolution

Research Feedback Memory, Question Capture, and Researcher Growth Review are disabled by default. At workflow entry, resolve these modes from the user invocation and project config before creating optional files.
Question Capture is disabled by default and follows the same resolution step.

1. `--no-feedback` forces feedback memory, Q&A capture, and growth review off for the current invocation.
2. `--feedback-memory`, `--qa-capture`, or `--growth-review` enables that mode for the current invocation.
3. `.omx/ai-research/CONFIG.md` can set `workflow_preset: conservative | guided | autonomous`, `idea_scouting: auto | off | on`, `completion_handoff: auto | off`, `worktree_closeout: off | report-before-merge`, `feedback_memory: off | lite | full`, `qa_capture: off | research | all`, and `growth_review: off | milestone | always`.
4. Missing config uses the `guided` workflow preset for routing, while feedback memory, Q&A capture, and growth review remain off.

Preset rules:

- `conservative`: run only explicitly requested phases.
- `guided`: infer common phases from user language while preserving confirmation boundaries.
- `autonomous`: proactively maintain relevant artifacts and next-step plans, but still ask before final-topic selection, workstream creation, merge, push, worktree removal, or branch deletion.
- Overrides win over the preset.

When Research Feedback Memory is enabled, write distilled issues, learnings, decisions, design notes, architecture tradeoffs, reusable commands, and failed assumptions to the optional feedback artifacts defined in `artifact-contracts.md`. When Question Capture is enabled, answer question-like prompts first and then write the Q&A ledger entry described in `question-capture.md`. When Researcher Growth Review is enabled, write capability-focused reflections to `SKILL_GROWTH.md` and workstream `REVIEW.md`.

Feedback writes happen at natural workflow boundaries: intake, experiment design, implementation handoff, experiment completion handoff, reproducibility review, and paper/report drafting. Do not interrupt default workflows with reflection questions unless growth review is enabled and one concise answer would materially improve the review.

## Portfolio and workstream control plane

Every project gets a root portfolio layer under `.omx/ai-research/`:

- `.omx/ai-research/RESEARCH.md`: the overall research program, central question, north-star hypotheses, claim boundaries, current synthesis, and next priorities.
- `.omx/ai-research/INDEX.md`: the workstream registry mapping each `<slug>` to its subquestion, status, artifact links, latest evidence, and next action.

Each `.omx/ai-research/<slug>/` directory is a workstream, not the whole research program. It should link back to the portfolio `RESEARCH.md` and appear in `INDEX.md`.

Each active workstream also keeps `STATE.json` as the current phase state and `CLAIMS.md` as the claim ledger. Update `STATE.json` when the workflow moves between intake, literature, experiment-design, running, completion-handoff, report-before-merge, reproducibility-review, paper-draft, or archived phases. Update `CLAIMS.md` whenever evidence changes allowed wording, forbidden wording, or the status of a claim.

Before creating a new slug:

1. Read or create the portfolio `RESEARCH.md` and `INDEX.md`.
2. List existing `.omx/ai-research/<slug>/` directories.
3. Reuse an existing workstream when the request is a continuation, replication, ablation, or follow-up within the same research question.
4. Create a new slug only for a distinct subquestion, method family, baseline family, dataset/benchmark lane, or paper/report slice.
5. Record the new slug, relationship to the overall objective, owned artifacts, and next action in `INDEX.md`.

## New workstream mandatory workflow gate

Creating a new workstream is a gated transition, not a directory operation. When the request requires a new slug, the following sequence is mandatory and ordered:

```text
$deep-interview --autoresearch
  -> $ralplan
  -> $autoresearch
```

The gate blocks creating `.omx/ai-research/<slug>/`, implementation, experiment launch, or docs publishing until the portfolio `INDEX.md` records these evidence paths:

1. Deep interview autoresearch handoff: validator-ready mission/intake artifact, preferably `.omx/specs/autoresearch-<slug>/mission.md`, plus the workstream `RESEARCH.md` draft or exact planned path.
2. Ralplan consensus: final plan plus `.omx/plans/prd-<slug>.md` and `.omx/plans/test-spec-<slug>.md`.
3. Autoresearch state: persisted `$autoresearch` state with `completion_artifact_path`, plus `.omx/specs/autoresearch-<slug>/mission.md`, `sandbox.md`, and `result.json`.

If any required evidence is missing, stop at the gate and complete the missing workflow. Do not bypass the gate because the user says the direction is small, obvious, or urgent. The only safe bypass is to reuse an existing workstream whose `INDEX.md` row already links equivalent gate evidence.

## Control plane vs project implementation plane

`.omx/ai-research/` is the portfolio control plane. `.omx/ai-research/<slug>/` is a workstream control plane. Together they store specs, decisions, run indexes, evidence summaries, reproducibility notes, and the global synthesis.

Actual research work belongs in the target project root using that project's conventions. Examples:

- method implementation: `src/`, `models/`, `methods/`, `algorithms/`, or the existing package layout
- baseline reproduction: `baselines/`, `configs/`, `scripts/`, `experiments/`, or existing benchmark layout
- training/evaluation entrypoints: project-native CLIs, notebooks, Make targets, Hydra configs, CI jobs, or shell scripts
- tests and verification: `tests/`, `evals/`, CI config, smoke tests, benchmark checks
- user-facing reports/docs: `docs/`, `reports/`, `mkdocs.yml`, README sections, benchmark cards

Do not implement the user's method, model, baseline, dataset adapter, or production experiment code inside `.omx/ai-research/`. Only thin orchestration wrappers, run metadata, and research notes belong there.

## Run distillation rule

A completed run directory is raw evidence. After each terminal run, distill reusable knowledge out of `runs/<run-id>/`:

1. Update `.omx/ai-research/<slug>/RUNS.md` with command, seed/device/resource, status, log path, metrics path, summary path, and failure notes.
2. Update `.omx/ai-research/<slug>/SCRIPT_REGISTRY.md` with scripts or native commands that were used, changed, validated, deprecated, or requested by the user.
3. Update `.omx/ai-research/<slug>/RESULTS.md` with tables, figures, hypothesis verdicts, and interpretation when the run changes the scientific picture.
4. Update `.omx/ai-research/<slug>/REPRODUCIBILITY.md` with new blockers, environment notes, nondeterminism, or rerun instructions.
5. Promote stable conclusions to project-root `docs/`, `reports/`, benchmark cards, config docs, or README sections when useful.
6. Promote reusable implementation changes to project-root code/config/tests, not to `.omx/ai-research/`.
7. When Research Feedback Memory is enabled, update `LEARNINGS.md`, `ISSUES.md`, `DECISIONS.md`, and workstream `NOTES.md`/`DESIGN.md` with distilled lessons, blockers, decisions, reusable commands, and design rationale.
8. When Researcher Growth Review is enabled, update `SKILL_GROWTH.md` and workstream `REVIEW.md` with concrete capability lessons tied to evidence.

Do not copy raw logs, large outputs, checkpoints, private data, or temporary run files into project-root docs. Link to them or summarize them.

If the user says the current experiment is done, use this as an experiment completion handoff signal: inspect runs and scripts, persist valuable or user-requested content into stable artifacts, then report the paths written.

If the workstream used a task worktree, completion handoff also includes a report-before-merge closeout plan: validation still needed, semantic commit status, base branch, merge/rebase command, push target, worktree removal, branch deletion, and `.omx/worktrees/REGISTRY.md` update. Do not merge, push, remove the worktree, or delete the branch until the user confirms the plan.

When distillation changes the global picture, update `.omx/ai-research/RESEARCH.md` and `.omx/ai-research/INDEX.md` in the same pass so the portfolio layer remains the user's overall map of the work.

## Baseline and method work

Baseline reproduction and new method implementation are first-class workflow tasks:

- Reproduce baselines before claiming improvement unless the research question explicitly excludes them.
- Keep baseline commands/configs reproducible and trace them from `EXPERIMENT.md` and `RUNS.md`.
- Implement methods in the project root with tests or smoke checks before expensive runs.
- Record claim boundaries when a baseline cannot be reproduced due to missing data, compute, license, or environment.
