# AI Research Artifact Contracts

Use these contracts to keep scientific goals separate from execution details.

## Required artifacts

| Artifact | Purpose | Created by phase |
| --- | --- | --- |
| `RESEARCH.md` | Scientific intent, hypothesis, contribution, success/falsification criteria, non-goals, claim boundaries | intake / question spec |
| `LITERATURE.md` | Source-backed related work, baselines, datasets, benchmark constraints, evidence gaps | literature review |
| `EXPERIMENT.md` | Runnable experimental protocol and validation plan | experiment design |
| `RUNS.md` | Commands, environment, tmux session/status, data versions, seeds, complete log paths, metrics paths, figure paths, result paths, failures | experiment execution |
| `RESULTS.md` | Tables, analysis, uncertainty, ablations, threats to validity | analysis |
| `REPRODUCIBILITY.md` | Reproducibility checklist and blockers | reproducibility review |
| `PAPER_DRAFT.md` | Claim-traceable paper/report draft | paper/report drafting |

## `RESEARCH.md` minimum sections

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
- Logging and artifact paths
- Reproduction commands
- Failure policy
- Run directory contract
- Detached tmux launch and monitoring plan
- Complete log capture plan
- Metrics output schema
- Progress reporting plan
- Visualization output plan

## `RUNS.md` minimum sections

- Run directory absolute path
- Run manifest path
- Tmux session name and `tmux_status.json` path when used
- Complete log file absolute path
- Command and wrapper script path
- Environment and git commit
- Data versions
- Seeds
- Metrics file paths
- Summary file path
- Figure output paths
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

Project root should contain `mkdocs.yml` when safe to create. If a project already has MkDocs configuration, preserve it and report any nav update needed.
