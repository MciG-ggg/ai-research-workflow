# Idea Scouting

Use this reference when the user does not yet have a clear research question, explicitly asks for idea generation, asks whether an idea is worth doing, or asks to turn a broad area into candidate research directions.

## Activation

Idea Scouting is optional and is not the default path for already-clear research questions.

Run it when:

- the user asks to generate research ideas from a broad area;
- the user asks whether an existing idea is worth pursuing;
- the user has a vague direction but no falsifiable research question;
- the current invocation includes `--idea-scouting`;
- `.omx/ai-research/CONFIG.md` sets `idea_scouting: on`, or sets `idea_scouting: auto` under a `guided` or `autonomous` workflow preset and the prompt is broad/vague.

Skip it when a concrete research question, hypothesis, metric, and baseline already exist; continue directly to research intake and the new-workstream gate.

## Non-goals

Idea Scouting must not:

- choose the final research topic without user confirmation;
- guarantee absolute novelty;
- replace full `LITERATURE.md` literature review;
- implement code or launch experiments;
- create a new `.omx/ai-research/<slug>/` workstream without user confirmation.

## Agent Decision Boundaries

The agent may autonomously:

- choose search queries and scouting sources;
- generate candidate ideas;
- rank and filter candidates;
- write `.omx/ai-research/IDEA_SCOUTING.md`;
- mark weak candidates as `parked` or `rejected`.

The agent must ask before:

- promoting an idea into a new workstream;
- creating `.omx/ai-research/<slug>/`;
- starting `$deep-interview --autoresearch` for a promoted candidate when multiple candidates remain plausible.

## Artifact

Write the portfolio-level scouting ledger to:

```text
.omx/ai-research/IDEA_SCOUTING.md
```

Use `assets/templates/IDEA_SCOUTING.md` when creating it.

Keep scouting concise. It is a lightweight evidence pass, not a full literature review. Full source-backed related work still belongs in `LITERATURE.md` after the idea is promoted.

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
3. Seed `$deep-interview --autoresearch` with the promoted candidate, evidence links, novelty-risk note, feasibility budget, and user-goal fit.
4. Record the chosen candidate and reason in portfolio `INDEX.md`.
