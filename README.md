# AI Research Workflow Skill

[中文文档](README.zh-CN.md)

A Codex/OMX skill for AI/ML research work. It helps turn vague ideas, papers, baselines, and experiment plans into evidence-gated research artifacts instead of jumping straight from idea to code.

The core principle is simple:

- `RESEARCH.md` records the research question, hypothesis, scope, and claim boundaries.
- `EXPERIMENT.md` records datasets, baselines, metrics, runs, and failure policy.
- `RUNS.md`, `RESULTS.md`, `CLAIMS.md`, and `REPRODUCIBILITY.md` keep evidence separate from claims.

This skill is a workflow and artifact framework. It does not ship universal experiment runners; project-specific code, configs, training scripts, and evaluation scripts should live in the target research repository.

## Dependency

This skill is designed for Codex sessions using [oh-my-codex (OMX)](https://github.com/Yeachan-Heo/oh-my-codex).

```bash
npm install -g oh-my-codex
omx setup
omx doctor
```

## Install

```bash
git clone https://github.com/MciG-ggg/ai-research-workflow.git
mkdir -p ~/.codex/skills
cp -R ai-research-workflow/skills/ai-research-workflow ~/.codex/skills/
```

Use the updater after pulling repo changes:

```bash
cd ai-research-workflow
./skills/ai-research-workflow/scripts/update_installed_skill.sh
```

For local development without pulling:

```bash
./skills/ai-research-workflow/scripts/update_installed_skill.sh --no-pull
```

## Typical workflow

```text
1. Start from an idea, paper, baseline, or experiment question.
2. Optionally scout ideas or papers:
   - IDEA_SCOUTING.md for candidate research ideas
   - PAPERS.md for SOTA/baseline paper lists
3. Before opening a new workstream, run:
   $deep-interview --autoresearch -> $ralplan -> $autoresearch
4. Create or reuse .omx/ai-research/<slug>/ for one concrete direction.
5. Choose the workstream type:
   - paper-reproduction: reproduce one paper/baseline/claim; uses REPRODUCTION.md
   - experiment-campaign: run a hypothesis/ablation/benchmark/method-evaluation campaign
6. Implement project code in the target repo, not inside .omx/ai-research/.
7. Record runs, scripts, metrics, summaries, and failures.
8. Distill evidence into RESULTS.md, CLAIMS.md, and REPRODUCIBILITY.md.
9. When the workstream is done, prepare a closeout/report-before-merge plan before merge, push, or worktree cleanup.
```

## Common commands

Invoke the skill explicitly when you want deterministic routing:

```text
$ai-research-workflow scout            # candidate idea scouting
$ai-research-workflow papers           # find/maintain SOTA and baseline paper list
$ai-research-workflow reproduce-paper  # gate a one-paper reproduction workstream
$ai-research-workflow experiment       # gate an experiment-campaign workstream
$ai-research-workflow new-workstream   # create a new gated direction
$ai-research-workflow handoff          # close out finished runs/scripts/results
$ai-research-workflow summarize        # summarize portfolio/workstream state
$ai-research-workflow score            # heuristic artifact quality review
$ai-research-workflow closeout         # prepare report-before-merge plan
$ai-research-workflow negative-result  # preserve failed/null/inconclusive results
$ai-research-workflow draft            # generate a paper/report outline
```

Local CLI helpers are available through:

```bash
python3 skills/ai-research-workflow/scripts/ai_research.py help
python3 skills/ai-research-workflow/scripts/ai_research.py resolve <project-root> --prompt "这个实验做完了，整理落盘"
python3 skills/ai-research-workflow/scripts/ai_research.py summarize <project-root>
python3 skills/ai-research-workflow/scripts/ai_research.py score <project-root>
python3 skills/ai-research-workflow/scripts/ai_research.py schema <project-root>
```

## Artifact layout

```text
.omx/ai-research/
  IDEA_SCOUTING.md   # optional candidate idea scouting
  PAPERS.md          # optional SOTA/baseline paper registry
  RESEARCH.md        # overall research program summary
  INDEX.md           # workstream index

.omx/ai-research/<slug>/
  STATE.json
  RESEARCH.md
  LITERATURE.md
  REPRODUCTION.md    # required for paper-reproduction workstreams
  EXPERIMENT.md
  RUNS.md
  RESULTS.md
  CLAIMS.md
  REPRODUCIBILITY.md
  SCRIPT_REGISTRY.md
  CLOSEOUT.md
  scripts/
  runs/
```

## Notes

- New workstreams should not be created automatically without the gate evidence.
- Merge, push, worktree removal, and branch deletion require report-before-merge confirmation.
- `runs/` stores raw evidence; stable conclusions should be distilled into the markdown artifacts.
- Bundled scripts are framework guardrails only, not user experiment runners.

## Validate

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ai-research-workflow
python3 skills/ai-research-workflow/scripts/run_e2e_scenarios.py
python3 skills/ai-research-workflow/scripts/validate_framework_contract.py skills/ai-research-workflow
```
