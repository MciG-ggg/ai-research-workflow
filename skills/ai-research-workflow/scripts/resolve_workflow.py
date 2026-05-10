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
VALID_SUBCOMMANDS = {
    "scout": {
        "phase": "idea-scouting",
        "action": "generate_or_rank_candidate_research_ideas",
        "artifacts": [".omx/ai-research/IDEA_SCOUTING.md"],
        "scripts": ["resolve_workflow.py", "validate_research_workspace.py --phase idea-scouting"],
    },
    "papers": {
        "phase": "paper-scouting",
        "action": "find_and_maintain_sota_baseline_papers",
        "artifacts": [".omx/ai-research/PAPERS.md"],
        "scripts": ["resolve_workflow.py", "validate_research_workspace.py --phase paper-scouting"],
    },
    "reproduce-paper": {
        "phase": "paper-reproduction",
        "action": "gate_one_paper_reproduction_workstream",
        "artifacts": [
            ".omx/ai-research/PAPERS.md",
            ".omx/ai-research/<slug>/REPRODUCTION.md",
            ".omx/ai-research/<slug>/EXPERIMENT.md",
            ".omx/ai-research/<slug>/RUNS.md",
            ".omx/ai-research/<slug>/RESULTS.md",
        ],
        "scripts": [
            "resolve_workflow.py",
            "init_workstream.py --paper-reproduction",
            "validate_research_workspace.py --phase paper-reproduction --workstream <slug>",
        ],
    },
    "experiment": {
        "phase": "new-workstream",
        "action": "gate_experiment_campaign_workstream",
        "artifacts": [
            ".omx/ai-research/INDEX.md",
            ".omx/ai-research/<slug>/STATE.json",
            ".omx/ai-research/<slug>/EXPERIMENT.md",
            ".omx/ai-research/<slug>/RUNS.md",
            ".omx/ai-research/<slug>/RESULTS.md",
        ],
        "scripts": [
            "init_workstream.py --workstream-type experiment-campaign",
            "validate_research_workspace.py --phase new-workstream --workstream <slug>",
        ],
    },
    "new-workstream": {
        "phase": "new-workstream",
        "action": "gate_and_initialize_new_workstream",
        "artifacts": [".omx/ai-research/INDEX.md", ".omx/ai-research/<slug>/RESEARCH.md", ".omx/ai-research/<slug>/STATE.json"],
        "scripts": ["init_workstream.py", "validate_research_workspace.py --phase new-workstream --workstream <slug>"],
    },
    "handoff": {
        "phase": "completion-handoff",
        "action": "distill_completed_runs_and_scripts",
        "artifacts": [".omx/ai-research/<slug>/RUNS.md", ".omx/ai-research/<slug>/RESULTS.md", ".omx/ai-research/<slug>/CLAIMS.md"],
        "scripts": ["prepare_workstream_closeout.py", "validate_research_workspace.py --phase completion-handoff --workstream <slug>"],
    },
    "qa": {
        "phase": "question-capture",
        "action": "answer_then_capture_question_summary",
        "artifacts": [".omx/ai-research/QUESTIONS.md", ".omx/ai-research/<slug>/QUESTIONS.md"],
        "scripts": ["capture_question.py"],
    },
    "review": {
        "phase": "research-review",
        "action": "score_and_review_artifact_quality",
        "artifacts": [".omx/ai-research/<slug>/CLAIMS.md", ".omx/ai-research/<slug>/REPRODUCIBILITY.md"],
        "scripts": ["score_research_artifacts.py", "validate_research_workspace.py"],
    },
    "summarize": {
        "phase": "portfolio-summary",
        "action": "summarize_research_portfolio_state",
        "artifacts": [".omx/ai-research/RESEARCH.md", ".omx/ai-research/INDEX.md"],
        "scripts": ["summarize_research_state.py"],
    },
    "closeout": {
        "phase": "report-before-merge",
        "action": "prepare_workstream_and_worktree_closeout_plan",
        "artifacts": [".omx/ai-research/<slug>/CLOSEOUT.md", ".omx/worktrees/REGISTRY.md"],
        "scripts": ["prepare_workstream_closeout.py", "prepare_worktree_closeout.py"],
    },
    "draft": {
        "phase": "paper-draft",
        "action": "generate_report_or_paper_outline",
        "artifacts": [".omx/ai-research/<slug>/PAPER_DRAFT.md", ".omx/ai-research/<slug>/PAPER_OUTLINE.md"],
        "scripts": ["generate_report_outline.py"],
    },
    "score": {
        "phase": "research-review",
        "action": "score_research_artifacts",
        "artifacts": [".omx/ai-research/<slug>/*.md"],
        "scripts": ["score_research_artifacts.py"],
    },
    "negative-result": {
        "phase": "result-analysis",
        "action": "preserve_negative_or_inconclusive_result",
        "artifacts": [".omx/ai-research/<slug>/RESULTS.md", ".omx/ai-research/<slug>/CLAIMS.md"],
        "scripts": ["preserve_negative_result.py"],
    },
}


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


def detect_subcommand(prompt: str, override: str | None = None) -> str | None:
    if override:
        return override
    stripped = prompt.strip().lower()
    if not stripped:
        return None
    parts = stripped.split()
    first = parts[0].lstrip("$").replace("_", "-")
    if first == "ai-research-workflow" and len(parts) > 1:
        first = parts[1].lstrip("$").replace("_", "-")
    aliases = {
        "idea-scouting": "scout",
        "new": "new-workstream",
        "wrap-up": "handoff",
        "done": "handoff",
        "question": "qa",
        "summary": "summarize",
        "state": "summarize",
        "quality": "score",
        "paper": "draft",
        "report": "draft",
        "negative": "negative-result",
        "paper-scouting": "papers",
        "paper-registry": "papers",
        "sota": "papers",
        "baseline-papers": "papers",
        "repro": "reproduce-paper",
        "reproduction": "reproduce-paper",
        "paper-repro": "reproduce-paper",
        "experiment-campaign": "experiment",
        "run-experiment": "experiment",
    }
    first = aliases.get(first, first)
    return first if first in VALID_SUBCOMMANDS else None


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
    negative_terms = [
        "negative result",
        "inconclusive",
        "failed result",
        "null result",
        "no improvement",
        "负结果",
        "无显著",
        "失败结果",
        "没提升",
        "不显著",
    ]
    paper_scouting_terms = [
        "sota",
        "state of the art",
        "baseline paper",
        "baseline papers",
        "paper list",
        "paper registry",
        "papers to reproduce",
        "find papers",
        "找论文",
        "论文列表",
        "论文池",
        "文章列表",
        "sota论文",
        "baseline论文",
        "基线论文",
        "维护论文",
    ]
    paper_reproduction_terms = [
        "reproduce paper",
        "reproduce this paper",
        "paper reproduction",
        "replicate paper",
        "replicate this paper",
        "reproduce baseline",
        "reproduce the baseline",
        "ideas from reproducing",
        "from paper to idea",
        "复现论文",
        "复现这篇",
        "复现文章",
        "复现 baseline",
        "复现baseline",
        "从论文找 idea",
        "通过复现",
        "开 workstream 复现",
    ]
    experiment_campaign_terms = [
        "experiment campaign",
        "run experiment campaign",
        "open experiment workstream",
        "experiment workstream",
        "开实验 workstream",
        "开实验小方向",
        "开一个实验",
        "跑实验 workstream",
        "跑一组实验",
        "实验 campaign",
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
        "negative_result_signal": contains_any(lower, negative_terms),
        "paper_scouting_signal": contains_any(lower, paper_scouting_terms),
        "paper_reproduction_signal": contains_any(lower, paper_reproduction_terms),
        "experiment_campaign_signal": contains_any(lower, experiment_campaign_terms),
        "question_like_prompt": question_like,
    }


def resolve(
    prompt: str,
    cfg: Config,
    config_warnings: list[str],
    config_path: str | None,
    *,
    command_override: str | None = None,
) -> dict[str, object]:
    signals = classify_prompt(prompt)
    subcommand = detect_subcommand(prompt, command_override)
    command_spec = VALID_SUBCOMMANDS.get(subcommand or "")
    guided_or_autonomous = cfg.workflow_preset in {"guided", "autonomous"}

    idea_scouting = False
    if cfg.idea_scouting == "on":
        idea_scouting = True
    elif cfg.idea_scouting == "auto" and guided_or_autonomous and signals["broad_or_vague_prompt"]:
        idea_scouting = True

    if subcommand == "scout":
        idea_scouting = True
    paper_scouting = bool(signals["paper_scouting_signal"]) or subcommand == "papers"
    paper_reproduction = bool(signals["paper_reproduction_signal"]) or subcommand == "reproduce-paper"
    paper_scouting = paper_scouting or paper_reproduction
    if paper_scouting or paper_reproduction:
        idea_scouting = True

    completion_handoff = (cfg.completion_handoff == "auto" and signals["completion_handoff_signal"]) or subcommand == "handoff"
    report_before_merge = completion_handoff and cfg.worktree_closeout == "report-before-merge"
    new_workstream_gate = bool(signals["new_workstream_signal"]) or subcommand == "new-workstream"
    experiment_campaign = bool(signals["experiment_campaign_signal"]) or subcommand == "experiment"
    if experiment_campaign:
        new_workstream_gate = True
    negative_result = signals["negative_result_signal"] or subcommand == "negative-result"
    question_capture = signals["question_like_prompt"] or subcommand == "qa"
    if subcommand == "closeout":
        report_before_merge = cfg.worktree_closeout == "report-before-merge"

    ask_before: list[str] = []
    if idea_scouting:
        ask_before.append("promoting final topic from IDEA_SCOUTING.md")
        ask_before.append("creating .omx/ai-research/<slug>")
    if paper_reproduction:
        ask_before.append("selecting a paper for reproduction workstream")
    if new_workstream_gate:
        ask_before.append("creating a new workstream after deep-interview/ralplan/autoresearch gate")
    if report_before_merge:
        ask_before.extend(["merge", "push", "worktree removal", "branch deletion"])
    if negative_result:
        ask_before.append("strengthening or generalizing claims after a negative/inconclusive result")

    recommended_steps: list[str] = []
    if config_warnings:
        recommended_steps.append("fix invalid .omx/ai-research/CONFIG.md fields before relying on automatic routing")
    if command_spec:
        recommended_steps.append(f"execute subcommand {subcommand}: {command_spec['action']}")
    if paper_scouting:
        recommended_steps.append("write/update .omx/ai-research/PAPERS.md with SOTA/baseline paper candidates and reproduction priority")
    if paper_reproduction:
        recommended_steps.append("select one paper only after confirmation, then prepare a gated paper-reproduction workstream with REPRODUCTION.md")
    if experiment_campaign:
        recommended_steps.append("prepare a gated experiment-campaign workstream with EXPERIMENT.md as the primary design artifact")
    if idea_scouting:
        recommended_steps.append("write/update .omx/ai-research/IDEA_SCOUTING.md and apply the six-field promotion gate")
    if new_workstream_gate:
        recommended_steps.append("run $deep-interview --autoresearch -> $ralplan -> $autoresearch before creating the new workstream")
    if completion_handoff:
        recommended_steps.append("inspect runs/ and scripts/, then distill RUNS.md, SCRIPT_REGISTRY.md, RESULTS.md, and REPRODUCIBILITY.md")
    if report_before_merge:
        recommended_steps.append("prepare report-before-merge closeout plan; wait for confirmation before merge/push/delete")
    if negative_result:
        recommended_steps.append("preserve the negative/inconclusive result in RESULTS.md and CLAIMS.md before revising claims")
    if not recommended_steps:
        recommended_steps.append("continue normal research intake or resume the earliest failing artifact gate")

    if command_spec:
        workflow_phase = command_spec["phase"]
        workflow_action = command_spec["action"]
        next_artifacts = command_spec["artifacts"]
        guardrail_scripts = command_spec["scripts"]
    elif paper_reproduction:
        workflow_phase = "paper-reproduction"
        workflow_action = "gate_one_paper_reproduction_workstream"
        next_artifacts = [".omx/ai-research/PAPERS.md", ".omx/ai-research/<slug>/REPRODUCTION.md"]
        guardrail_scripts = [
            "init_workstream.py --paper-reproduction",
            "validate_research_workspace.py --phase paper-reproduction --workstream <slug>",
        ]
    elif paper_scouting:
        workflow_phase = "paper-scouting"
        workflow_action = "find_and_maintain_sota_baseline_papers"
        next_artifacts = [".omx/ai-research/PAPERS.md"]
        guardrail_scripts = ["validate_research_workspace.py --phase paper-scouting"]
    elif new_workstream_gate:
        workflow_phase = "new-workstream"
        workflow_action = "gate_experiment_campaign_workstream" if experiment_campaign else "complete_mandatory_workstream_gate"
        next_artifacts = [
            ".omx/ai-research/INDEX.md",
            ".omx/ai-research/<slug>/STATE.json",
            *([] if not experiment_campaign else [".omx/ai-research/<slug>/EXPERIMENT.md"]),
        ]
        guardrail_scripts = [
            "init_workstream.py --workstream-type experiment-campaign" if experiment_campaign else "init_workstream.py",
            "validate_research_workspace.py --phase new-workstream --workstream <slug>",
        ]
    elif completion_handoff:
        workflow_phase = "completion-handoff"
        workflow_action = "distill_completed_runs"
        next_artifacts = [".omx/ai-research/<slug>/RUNS.md", ".omx/ai-research/<slug>/RESULTS.md"]
        guardrail_scripts = ["prepare_workstream_closeout.py", "validate_research_workspace.py --phase completion-handoff --workstream <slug>"]
    elif idea_scouting:
        workflow_phase = "idea-scouting"
        workflow_action = "scout_candidate_research_ideas"
        next_artifacts = [".omx/ai-research/IDEA_SCOUTING.md"]
        guardrail_scripts = ["validate_research_workspace.py --phase idea-scouting"]
    elif question_capture and cfg.qa_capture != "off":
        workflow_phase = "question-capture"
        workflow_action = "answer_then_capture_question"
        next_artifacts = [".omx/ai-research/QUESTIONS.md"]
        guardrail_scripts = ["capture_question.py"]
    else:
        workflow_phase = "normal-research"
        workflow_action = "resume_earliest_failing_artifact_gate"
        next_artifacts = [".omx/ai-research/RESEARCH.md", ".omx/ai-research/INDEX.md"]
        guardrail_scripts = ["summarize_research_state.py", "score_research_artifacts.py"]

    return {
        "config_path": config_path,
        "config": asdict(cfg),
        "config_warnings": config_warnings,
        "subcommand": subcommand,
        "signals": signals,
        "decisions": {
            "idea_scouting": idea_scouting,
            "completion_handoff": completion_handoff,
            "new_workstream_gate": new_workstream_gate,
            "paper_scouting": paper_scouting,
            "paper_reproduction_scouting": paper_reproduction,
            "experiment_campaign": experiment_campaign,
            "report_before_merge_closeout": report_before_merge,
            "negative_result_preservation": negative_result,
            "question_capture_candidate": question_capture,
            "ask_required": bool(ask_before),
            "ask_before": sorted(set(ask_before)),
        },
        "routing": {
            "phase": workflow_phase,
            "workflow_action": workflow_action,
            "requires_user_confirmation": bool(ask_before),
            "next_artifacts": next_artifacts,
            "guardrail_scripts": guardrail_scripts,
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
    parser.add_argument("--command", choices=sorted(VALID_SUBCOMMANDS), help="Explicit subcommand routing override.")
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

    result = resolve(prompt, cfg, warnings, config_path, command_override=args.command)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
