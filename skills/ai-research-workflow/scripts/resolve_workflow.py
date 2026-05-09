#!/usr/bin/env python3
"""Resolve ai-research-workflow routing decisions from prompt plus project config.

Script: resolve_workflow.py.

This is a deterministic framework guardrail. It does not run experiments,
collect metrics, plot results, publish research docs, merge branches, or delete
worktrees.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

VALID_WORKFLOW_PRESET = {"conservative", "guided", "autonomous"}
VALID_IDEA_SCOUTING = {"auto", "off", "on"}
VALID_COMPLETION_HANDOFF = {"auto", "off"}
VALID_WORKTREE_CLOSEOUT = {"off", "report-before-merge"}
VALID_FEEDBACK_MEMORY = {"off", "lite", "full"}
VALID_QA_CAPTURE = {"off", "research", "all"}
VALID_GROWTH_REVIEW = {"off", "milestone", "always"}


@dataclass
class Config:
    schema_version: str = "1"
    workflow_preset: str = "guided"
    idea_scouting: str = "auto"
    completion_handoff: str = "auto"
    worktree_closeout: str = "report-before-merge"
    feedback_memory: str = "off"
    qa_capture: str = "off"
    growth_review: str = "off"


def parse_config(project_root: Path) -> tuple[Config, list[str], str | None]:
    cfg = Config()
    warnings: list[str] = []
    config_path = project_root / ".omx" / "ai-research" / "CONFIG.md"
    if not config_path.is_file():
        return cfg, warnings, None

    text = config_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        match = re.match(
            r"^\s*(schema_version|workflow_preset|idea_scouting|completion_handoff|worktree_closeout|feedback_memory|qa_capture|growth_review)\s*:\s*([A-Za-z0-9_-]+)\s*$",
            line,
        )
        if not match:
            continue
        setattr(cfg, match.group(1), match.group(2).lower())

    validators = {
        "schema_version": {"1"},
        "workflow_preset": VALID_WORKFLOW_PRESET,
        "idea_scouting": VALID_IDEA_SCOUTING,
        "completion_handoff": VALID_COMPLETION_HANDOFF,
        "worktree_closeout": VALID_WORKTREE_CLOSEOUT,
        "feedback_memory": VALID_FEEDBACK_MEMORY,
        "qa_capture": VALID_QA_CAPTURE,
        "growth_review": VALID_GROWTH_REVIEW,
    }
    for field, allowed in validators.items():
        value = getattr(cfg, field)
        if value not in allowed:
            warnings.append(f"invalid {field}={value!r}; using decision output as invalid-config signal")
    return cfg, warnings, str(config_path)


def contains_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def classify_prompt(prompt: str) -> dict[str, bool]:
    stripped = prompt.strip()
    lower = stripped.lower()
    idea_terms = [
        "idea",
        "ideas",
        "brainstorm",
        "scout",
        "scouting",
        "candidate",
        "worth pursuing",
        "worth doing",
        "research direction",
        "topic",
        "选题",
        "想法",
        "方向",
        "候选",
        "值得做",
        "调研",
        "产生",
        "生成",
    ]
    vague_terms = ["broad", "vague", "open-ended", "不清楚", "模糊", "宽泛", "大方向", "没有明确"]
    concrete_terms = [
        "hypothesis",
        "falsifiable",
        "metric",
        "baseline",
        "benchmark",
        "dataset",
        "ablation",
        "experiment",
        "evaluation",
        "假设",
        "指标",
        "baseline",
        "数据集",
        "实验",
        "评估",
        "消融",
    ]
    completion_terms = [
        "done",
        "finished",
        "wrap up",
        "close out",
        "complete this experiment",
        "current experiment is done",
        "workstream is done",
        "做完了",
        "结束了",
        "收尾",
        "整理落盘",
        "整理数据",
    ]
    new_workstream_terms = [
        "new workstream",
        "new direction",
        "new slug",
        "create workstream",
        "promote candidate",
        "新的小方向",
        "新方向",
        "新建 workstream",
        "开一个小方向",
        "创建 workstream",
        "进入 intake",
    ]
    question_starters = (
        "how ",
        "why ",
        "what ",
        "should ",
        "can ",
        "could ",
        "is ",
        "are ",
        "怎么",
        "为什么",
        "如何",
        "是否",
        "能不能",
        "要不要",
        "什么",
    )

    explicit_idea = contains_any(lower, idea_terms)
    vague = contains_any(lower, vague_terms)
    concrete = contains_any(lower, concrete_terms)
    completion = contains_any(lower, completion_terms)
    new_workstream = contains_any(lower, new_workstream_terms)
    question_like = stripped.endswith(("?", "？")) or lower.startswith(question_starters)
    broad_or_vague = explicit_idea or vague or (question_like and not concrete and contains_any(lower, ["research", "科研", "方向"]))

    return {
        "explicit_idea_or_scouting_request": explicit_idea,
        "broad_or_vague_prompt": broad_or_vague,
        "concrete_research_terms_present": concrete,
        "completion_handoff_signal": completion,
        "new_workstream_signal": new_workstream,
        "question_like_prompt": question_like,
    }


def resolve(prompt: str, cfg: Config, config_warnings: list[str], config_path: str | None) -> dict[str, object]:
    signals = classify_prompt(prompt)
    guided_or_autonomous = cfg.workflow_preset in {"guided", "autonomous"}

    idea_scouting = False
    if cfg.idea_scouting == "on":
        idea_scouting = True
    elif cfg.idea_scouting == "auto" and guided_or_autonomous and signals["broad_or_vague_prompt"]:
        idea_scouting = True

    completion_handoff = cfg.completion_handoff == "auto" and signals["completion_handoff_signal"]
    report_before_merge = completion_handoff and cfg.worktree_closeout == "report-before-merge"
    new_workstream_gate = bool(signals["new_workstream_signal"])

    ask_before: list[str] = []
    if idea_scouting:
        ask_before.append("promoting final topic from IDEA_SCOUTING.md")
        ask_before.append("creating .omx/ai-research/<slug>")
    if new_workstream_gate:
        ask_before.append("creating a new workstream after deep-interview/ralplan/autoresearch gate")
    if report_before_merge:
        ask_before.extend(["merge", "push", "worktree removal", "branch deletion"])

    recommended_steps: list[str] = []
    if config_warnings:
        recommended_steps.append("fix invalid .omx/ai-research/CONFIG.md fields before relying on automatic routing")
    if idea_scouting:
        recommended_steps.append("write/update .omx/ai-research/IDEA_SCOUTING.md and apply the six-field promotion gate")
    if new_workstream_gate:
        recommended_steps.append("run $deep-interview --autoresearch -> $ralplan -> $autoresearch before creating the new workstream")
    if completion_handoff:
        recommended_steps.append("inspect runs/ and scripts/, then distill RUNS.md, SCRIPT_REGISTRY.md, RESULTS.md, and REPRODUCIBILITY.md")
    if report_before_merge:
        recommended_steps.append("prepare report-before-merge closeout plan; wait for confirmation before merge/push/delete")
    if not recommended_steps:
        recommended_steps.append("continue normal research intake or resume the earliest failing artifact gate")

    return {
        "config_path": config_path,
        "config": asdict(cfg),
        "config_warnings": config_warnings,
        "signals": signals,
        "decisions": {
            "idea_scouting": idea_scouting,
            "completion_handoff": completion_handoff,
            "new_workstream_gate": new_workstream_gate,
            "report_before_merge_closeout": report_before_merge,
            "question_capture_candidate": signals["question_like_prompt"],
            "ask_required": bool(ask_before),
            "ask_before": sorted(set(ask_before)),
        },
        "recommended_steps": recommended_steps,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve ai-research-workflow routing from prompt and CONFIG.md.")
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--prompt", help="User prompt to classify. Reads stdin when omitted.")
    parser.add_argument("--workflow-preset", choices=sorted(VALID_WORKFLOW_PRESET), help="Override workflow_preset.")
    parser.add_argument("--idea-scouting", choices=sorted(VALID_IDEA_SCOUTING), help="Override idea_scouting.")
    parser.add_argument("--completion-handoff", choices=sorted(VALID_COMPLETION_HANDOFF), help="Override completion_handoff.")
    parser.add_argument("--worktree-closeout", choices=sorted(VALID_WORKTREE_CLOSEOUT), help="Override worktree_closeout.")
    args = parser.parse_args()

    prompt = args.prompt if args.prompt is not None else sys.stdin.read()
    cfg, warnings, config_path = parse_config(args.project_root.resolve())
    if args.workflow_preset:
        cfg.workflow_preset = args.workflow_preset
    if args.idea_scouting:
        cfg.idea_scouting = args.idea_scouting
    if args.completion_handoff:
        cfg.completion_handoff = args.completion_handoff
    if args.worktree_closeout:
        cfg.worktree_closeout = args.worktree_closeout

    result = resolve(prompt, cfg, warnings, config_path)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
