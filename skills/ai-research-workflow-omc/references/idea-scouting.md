# Idea Scouting

Use this reference when the user does not yet have a clear research question, explicitly asks for idea generation, asks whether an idea is worth doing, or asks to turn a broad area into candidate research directions.

## Activation

Idea Scouting is optional and is not the default path for already-clear research questions.

Run it when:

- the user asks to generate research ideas from a broad area;
- the user asks whether an existing idea is worth pursuing;
- the user has a vague direction but no falsifiable research question;
- the user asks the agent to find SOTA or baseline papers and maintain a paper list;
- the user explicitly asks to reproduce a paper or baseline as an idea-discovery path;
- the current invocation includes `--idea-scouting`;
- `.omc/ai-research/CONFIG.md` sets `idea_scouting: on`, or sets `idea_scouting: auto` under a `guided` or `autonomous` workflow preset and the prompt is broad/vague.

Skip it when a concrete research question, hypothesis, metric, and baseline already exist; continue directly to research intake and the new-workstream gate.

## Non-goals

Idea Scouting must not:

- choose the final research topic without user confirmation;
- guarantee absolute novelty;
- replace full `LITERATURE.md` literature review;
- implement code or launch experiments;
- download papers, data, code, checkpoints, or run paper reproduction automatically;
- create a new `.omc/ai-research/<slug>/` workstream without user confirmation.

## Agent Decision Boundaries

The agent may autonomously:

- choose search queries and scouting sources;
- find SOTA and baseline candidate papers from allowed sources;
- maintain `.omc/ai-research/PAPERS.md`;
- generate candidate ideas;
- rank and filter candidates;
- write `.omc/ai-research/IDEA_SCOUTING.md`;
- mark weak candidates as `parked` or `rejected`.

The agent must ask before:

- promoting an idea into a new workstream;
- selecting one paper for reproduction when multiple plausible papers remain;
- creating `.omc/ai-research/<slug>/`;
- starting `/oh-my-claudecode:deep-interview --autoresearch` for a promoted candidate when multiple candidates remain plausible.

## Artifact

Write the portfolio-level scouting ledger to:

```text
.omc/ai-research/IDEA_SCOUTING.md
```

Use `assets/templates/IDEA_SCOUTING.md` when creating it.

When the user asks to find SOTA or baseline papers, also write or update:

```text
.omc/ai-research/PAPERS.md
```

Use `assets/templates/PAPERS.md` when creating it.

Keep scouting concise. It is a lightweight evidence pass, not a full literature review. Full source-backed related work still belongs in `LITERATURE.md` after the idea is promoted.

## SOTA and Baseline Paper Registry

Use `PAPERS.md` as the portfolio-level paper list when the user asks the agent to find, rank, or maintain SOTA and baseline articles.

Minimum fields:

- research area, search date, queries, and sources;
- paper role: SOTA, baseline, survey, dataset, benchmark, or method paper;
- title, venue/date, link, and citation handle when available;
- key claim, benchmark/metric, and why it matters;
- code, data, checkpoint, config, or seed availability;
- reproduction priority and current status;
- maintenance log explaining additions, removals, or priority changes.

The paper registry is a living index. It does not replace workstream `LITERATURE.md`: once a paper becomes central to a workstream, its detailed related-work analysis belongs in that workstream.

## Paper-Reproduction Scouting

Use this path only when the user explicitly says they want to reproduce a paper, reproduce a baseline, or find ideas by reproducing a paper.

Paper-reproduction scouting should identify:

- target paper and exact claim to inspect;
- reproduction type: exact, approximate, baseline-only, or mechanism validation;
- expected metric, benchmark, and tolerance;
- official/third-party code, data, checkpoints, configs, and environment availability;
- compute/time budget and likely blockers;
- what failure, partial reproduction, or inconclusive reproduction would mean;
- candidate ideas revealed by reproduction gaps, unfair comparisons, missing ablations, brittle assumptions, or unsupported claims.

When one paper is selected for actual reproduction, ask before opening a workstream. On confirmation, enter the normal new-workstream gate:

```text
/oh-my-claudecode:deep-interview --autoresearch
  -> /oh-my-claudecode:ralplan
  -> /oh-my-claudecode:autoresearch
```

The resulting workstream should include `REPRODUCTION.md` from `assets/templates/REPRODUCTION.md` and link back to the paper row in `PAPERS.md`.

## Promotion Gate

An idea may be recommended for formal research intake only when all fields are explicit:

- falsifiable hypothesis;
- evaluation metric, baseline, or benchmark;
- lightweight evidence from papers, benchmarks, datasets, products, failures, or project constraints;
- novelty-risk note with known adjacent work or duplication risk;
- feasibility budget covering data, compute, time, and engineering complexity;
- user-goal fit.

If any field is missing, keep the idea in `draft` or `parked` state and state the missing evidence instead of opening a workstream.

## Handoff

When one candidate passes the promotion gate:

1. Ask the user to confirm promotion.
2. On confirmation, enter the new-workstream mandatory workflow gate.
3. Seed `/oh-my-claudecode:deep-interview --autoresearch` with the promoted candidate, evidence links, novelty-risk note, feasibility budget, and user-goal fit.
4. Record the chosen candidate and reason in portfolio `INDEX.md`.

For a paper-reproduction candidate, also update `PAPERS.md` with the selected paper, target claim, reproduction priority, and planned workstream slug; then seed the workstream `REPRODUCTION.md` with the target paper and minimal reproduction objective.
