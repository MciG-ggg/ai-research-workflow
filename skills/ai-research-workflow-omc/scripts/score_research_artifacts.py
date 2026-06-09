#!/usr/bin/env python3
"""Score downstream ai-research control-plane artifact quality.

Script: score_research_artifacts.py.

This is a read-only framework guardrail. It scores artifact completeness and
claim-safety heuristics; it does not run experiments, collect metrics, plot
results, publish docs, merge branches, push remotes, remove worktrees, or delete
branches.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RUBRICS: dict[str, list[str]] = {
    "RESEARCH.md": ["research question", "hypothesis", "success criteria", "falsification", "out of scope", "claim boundaries"],
    "LITERATURE.md": ["source", "evidence", "gap", "related", "limitation"],
    "REPRODUCTION.md": ["target paper", "reproduction objective", "available materials", "minimal reproduction plan", "run evidence links", "conclusions and distillation"],
    "EXPERIMENT.md": ["baseline fairness checklist", "same data split", "same evaluation metric", "hyperparameter", "negative / inconclusive result policy"],
    "RUNS.md": ["run ledger", "command", "log", "metrics", "summary", "distilled updates outside `runs/`"],
    "RESULTS.md": ["evidence", "interpretation", "negative and inconclusive results", "evidence-to-claim mapping", "limitations"],
    "CLAIMS.md": ["claim ledger", "evidence paths", "allowed wording", "forbidden wording", "negative or inconclusive results", "retired or downgraded claims"],
    "REPRODUCIBILITY.md": ["command", "environment", "data", "seed", "commit", "known gaps"],
    "SCRIPT_REGISTRY.md": ["command", "purpose", "inputs", "outputs", "owner", "completion handoff"],
    "PAPER_DRAFT.md": ["abstract", "method", "experiment", "result", "limitation"],
}
EXCLUDED_DIRS = {"runs", "logs", "state", "worktrees", "scripts", "docs"}
VALID_WORKSTREAM_TYPES = {"experiment-campaign", "paper-reproduction"}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def load_workstream_type(workstream: Path) -> str:
    state_path = workstream / "STATE.json"
    if not state_path.is_file():
        return "paper-reproduction" if (workstream / "REPRODUCTION.md").is_file() else "unknown"
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "paper-reproduction" if (workstream / "REPRODUCTION.md").is_file() else "unknown"
    value = state.get("workstream_type") if isinstance(state, dict) else None
    if value in VALID_WORKSTREAM_TYPES:
        return value
    return "paper-reproduction" if (workstream / "REPRODUCTION.md").is_file() else "unknown"


def count_todos(text: str) -> int:
    return sum(1 for line in text.splitlines() if "TODO" in line)


def score_file(path: Path, terms: list[str]) -> dict[str, Any]:
    if not path.is_file():
        return {"path": str(path), "exists": False, "score": 0, "present_terms": [], "missing_terms": terms, "todo_count": 0}
    text = read_text(path)
    lower = text.lower()
    present = [term for term in terms if term.lower() in lower]
    missing = [term for term in terms if term.lower() not in lower]
    base = round(100 * len(present) / len(terms)) if terms else 100
    todo_penalty = min(35, count_todos(text) * 3)
    score = max(0, base - todo_penalty)
    return {
        "path": str(path),
        "exists": True,
        "score": score,
        "present_terms": present,
        "missing_terms": missing,
        "todo_count": count_todos(text),
    }


def find_workstreams(ai_root: Path) -> list[Path]:
    if not ai_root.is_dir():
        return []
    return sorted(path for path in ai_root.iterdir() if path.is_dir() and not path.name.startswith(".") and path.name not in EXCLUDED_DIRS)


def score_project(project_root: Path) -> dict[str, Any]:
    ai_root = project_root / ".omc" / "ai-research"
    if not ai_root.is_dir():
        return {"project_root": str(project_root), "ai_root": str(ai_root), "exists": False, "error": "missing ai-research root"}
    portfolio = {
        "RESEARCH.md": score_file(ai_root / "RESEARCH.md", ["central", "hypoth", "claim", "current synthesis", "next priorities"]),
        "INDEX.md": score_file(ai_root / "INDEX.md", ["slug", "status", "subquestion", "gate evidence", "next action"]),
    }
    if (ai_root / "PAPERS.md").is_file():
        portfolio["PAPERS.md"] = score_file(ai_root / "PAPERS.md", ["sota", "baseline", "key claim", "benchmark", "reproduction priority", "maintenance log"])
    workstreams: list[dict[str, Any]] = []
    for workstream in find_workstreams(ai_root):
        workstream_type = load_workstream_type(workstream)
        artifact_scores = {
            name: score_file(workstream / name, terms)
            for name, terms in RUBRICS.items()
            if name != "REPRODUCTION.md" or workstream_type == "paper-reproduction" or (workstream / name).is_file()
        }
        avg = round(sum(item["score"] for item in artifact_scores.values()) / len(artifact_scores)) if artifact_scores else 0
        lowest = sorted(((name, item["score"]) for name, item in artifact_scores.items()), key=lambda pair: pair[1])[:3]
        workstreams.append({"slug": workstream.name, "workstream_type": workstream_type, "score": avg, "lowest_artifacts": lowest, "artifacts": artifact_scores})
    all_scores = [item["score"] for item in portfolio.values()] + [item["score"] for item in workstreams]
    overall = round(sum(all_scores) / len(all_scores)) if all_scores else 0
    return {"project_root": str(project_root), "ai_root": str(ai_root), "exists": True, "overall_score": overall, "portfolio": portfolio, "workstreams": workstreams}


def markdown(result: dict[str, Any]) -> str:
    if not result.get("exists"):
        return f"# Research Artifact Quality Score\n\nError: {result.get('error')} at `{result.get('ai_root')}`\n"
    portfolio_rows = [f"| {name} | {item['score']} | {item['todo_count']} | {', '.join(item['missing_terms']) or 'none'} |" for name, item in result["portfolio"].items()]
    workstream_rows = []
    for item in result["workstreams"]:
        lowest = "; ".join(f"{name}={score}" for name, score in item["lowest_artifacts"])
        workstream_rows.append(f"| {item['slug']} | {item['workstream_type']} | {item['score']} | {lowest or 'none'} |")
    if not workstream_rows:
        workstream_rows = ["| none | n/a | 0 | create a gated workstream first |"]
    return f"""# Research Artifact Quality Score

- Project root: `{result['project_root']}`
- Overall score: {result['overall_score']}/100

## Portfolio

| Artifact | Score | TODO count | Missing rubric terms |
| --- | ---: | ---: | --- |
{chr(10).join(portfolio_rows)}

## Workstreams

| Slug | Type | Average score | Lowest artifacts |
| --- | --- | ---: | --- |
{chr(10).join(workstream_rows)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Score .omc/ai-research artifact quality heuristics.")
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--min-score", type=int, help="Return non-zero if overall score is below this threshold.")
    parser.add_argument("--output", type=Path, help="Optional file to write the score report.")
    args = parser.parse_args()

    result = score_project(args.project_root.resolve())
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n" if args.json else markdown(result)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote research artifact quality score: {args.output}")
    else:
        print(text, end="")
    if not result.get("exists"):
        return 1
    if args.min_score is not None and int(result.get("overall_score", 0)) < args.min_score:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
