#!/usr/bin/env python3
"""Hook helper for optional ai-research-workflow Question Capture.

Script: question_capture_hook.py.

This is a deterministic framework guardrail for wiring prompt/answer hooks. It
may write a pending question marker under .omx/state at submit time and append a
final distilled Q&A entry only after an answer summary exists and qa_capture is
enabled. It does not run experiments, collect metrics, plot results, publish
research docs, merge branches, push remotes, remove worktrees, or delete
branches.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from capture_question import SENSITIVE_RE, ensure_questions_file, entry as question_entry
from resolve_workflow import classify_prompt, parse_config

PENDING_NAME = "ai-research-question-capture-pending.json"
RESEARCH_SCOPES = {"research", "workflow", "architecture", "experiment", "interpretation"}
ENV_PROMPT_KEYS = ("OMX_USER_PROMPT", "CODEX_USER_PROMPT", "USER_PROMPT")
ENV_ANSWER_KEYS = ("OMX_ASSISTANT_ANSWER", "CODEX_ASSISTANT_ANSWER", "ASSISTANT_ANSWER_SUMMARY")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def pending_path(project_root: Path, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit if explicit.is_absolute() else (project_root / explicit).resolve()
    return project_root / ".omx" / "state" / PENDING_NAME


def read_value(*, direct: str | None, file: Path | None, env_keys: tuple[str, ...], stdin_fallback: bool) -> str:
    if direct is not None:
        return direct
    if file is not None:
        return file.read_text(encoding="utf-8")
    for key in env_keys:
        value = os.environ.get(key)
        if value:
            return value
    if stdin_fallback and not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def infer_scope(prompt: str, override: str | None) -> str:
    if override:
        return override
    lower = prompt.lower()
    if any(term in lower for term in ("architecture", "design", "架构", "设计")):
        return "architecture"
    if any(term in lower for term in ("experiment", "baseline", "metric", "run", "实验", "指标", "运行", "baseline")):
        return "experiment"
    if any(term in lower for term in ("claim", "result", "interpret", "negative", "结论", "结果", "解释", "负结果")):
        return "interpretation"
    if any(term in lower for term in ("workflow", "skill", "worktree", "hook", "流程", "工作流")):
        return "workflow"
    return "research"


def capture_enabled(qa_capture: str, scope: str) -> bool:
    if qa_capture == "all":
        return True
    if qa_capture == "research" and scope in RESEARCH_SCOPES:
        return True
    return False


def decision(project_root: Path, prompt: str, scope_override: str | None) -> dict[str, Any]:
    cfg, warnings, config_path = parse_config(project_root)
    signals = classify_prompt(prompt)
    scope = infer_scope(prompt, scope_override)
    enabled = capture_enabled(cfg.qa_capture, scope)
    sensitive = bool(SENSITIVE_RE.search(prompt))
    should_capture = bool(signals["question_like_prompt"] and enabled and not sensitive)
    reason = "capture candidate"
    if not signals["question_like_prompt"]:
        reason = "not question-like"
    elif cfg.qa_capture == "off":
        reason = "qa_capture is off"
    elif not enabled:
        reason = f"scope {scope!r} not enabled by qa_capture={cfg.qa_capture!r}"
    elif sensitive:
        reason = "possible secret/credential text"
    return {
        "created_at": utc_now(),
        "project_root": str(project_root),
        "config_path": config_path,
        "config": asdict(cfg),
        "config_warnings": warnings,
        "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16],
        "prompt": prompt,
        "scope": scope,
        "signals": signals,
        "should_capture": should_capture,
        "reason": reason,
    }


def write_pending(path: Path, payload: dict[str, Any], *, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_pending(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def append_capture(
    project_root: Path,
    *,
    question: str,
    answer_summary: str,
    scope: str,
    workstream: str | None,
    evidence: list[str],
    routed_update: list[str],
    follow_up: str | None,
    dry_run: bool,
) -> Path:
    if SENSITIVE_RE.search("\n".join([question, answer_summary, "\n".join(evidence), "\n".join(routed_update), follow_up or ""])):
        raise SystemExit("refusing to capture possible secret/credential text; redact it first")

    ai_root = project_root / ".omx" / "ai-research"
    target = ai_root / workstream / "QUESTIONS.md" if workstream else ai_root / "QUESTIONS.md"
    capture_args = argparse.Namespace(
        question=question,
        answer_summary=answer_summary,
        scope=scope,
        workstream=workstream,
        evidence=evidence,
        routed_update=routed_update,
        follow_up=follow_up,
    )
    text = question_entry(capture_args)
    if dry_run:
        print(text, end="")
        return target
    ensure_questions_file(target, dry_run=False)
    with target.open("a", encoding="utf-8") as fh:
        if target.stat().st_size and not target.read_text(encoding="utf-8").endswith("\n"):
            fh.write("\n")
        fh.write(text)
    return target


def print_result(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    status = "capture" if payload.get("should_capture") or payload.get("captured") else "skip"
    print(f"{status}: {payload.get('reason', payload.get('target', ''))}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify and capture Q&A through ai-research-workflow hook stages.")
    parser.add_argument("--stage", choices=["submit", "answer"], required=True, help="Hook stage: submit classifies/stores pending; answer appends final Q&A.")
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Target project root. Defaults to cwd.")
    parser.add_argument("--prompt", help="User prompt/question text.")
    parser.add_argument("--prompt-file", type=Path, help="File containing the user prompt/question.")
    parser.add_argument("--answer-summary", help="Distilled answer summary supplied by the post-answer hook.")
    parser.add_argument("--answer-file", type=Path, help="File containing the distilled answer summary.")
    parser.add_argument("--workstream", help="Optional workstream slug for .omx/ai-research/<slug>/QUESTIONS.md.")
    parser.add_argument("--scope", choices=["research", "workflow", "architecture", "experiment", "interpretation", "all"], help="Override inferred question scope.")
    parser.add_argument("--evidence", action="append", default=[], help="Evidence/link/path to record. Repeatable.")
    parser.add_argument("--routed-update", action="append", default=[], help="Artifact updated because of the answer. Repeatable.")
    parser.add_argument("--follow-up", help="Optional follow-up action.")
    parser.add_argument("--pending-path", type=Path, help="Override pending marker path. Defaults to .omx/state/ai-research-question-capture-pending.json.")
    parser.add_argument("--no-pending-write", action="store_true", help="Submit stage classifies only; do not write the pending marker.")
    parser.add_argument("--keep-pending", action="store_true", help="Answer stage keeps the pending marker after successful capture.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    parser.add_argument("--json", action="store_true", default=True, help="Print JSON result. Default: on for hook friendliness.")
    parser.add_argument("--plain", action="store_true", help="Print one-line plain output instead of JSON.")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    ppath = pending_path(project_root, args.pending_path)
    as_json = not args.plain

    if args.stage == "submit":
        prompt = read_value(direct=args.prompt, file=args.prompt_file, env_keys=ENV_PROMPT_KEYS, stdin_fallback=True).strip()
        if not prompt:
            result = {"stage": "submit", "should_capture": False, "reason": "missing prompt", "pending_path": str(ppath)}
            print_result(result, as_json=as_json)
            return 2
        result = decision(project_root, prompt, args.scope)
        result.update({"stage": "submit", "pending_path": str(ppath), "pending_written": False})
        if result["should_capture"] and not args.no_pending_write:
            write_pending(ppath, result, dry_run=args.dry_run)
            result["pending_written"] = not args.dry_run
        print_result(result, as_json=as_json)
        return 0

    answer_summary = read_value(direct=args.answer_summary, file=args.answer_file, env_keys=ENV_ANSWER_KEYS, stdin_fallback=False).strip()
    pending = read_pending(ppath)
    prompt = read_value(direct=args.prompt, file=args.prompt_file, env_keys=ENV_PROMPT_KEYS, stdin_fallback=False).strip()
    if pending and not prompt:
        prompt = str(pending.get("prompt", "")).strip()
    if not prompt:
        result = {"stage": "answer", "captured": False, "reason": "missing prompt and no pending question", "pending_path": str(ppath)}
        print_result(result, as_json=as_json)
        return 2
    if not answer_summary:
        result = {"stage": "answer", "captured": False, "reason": "missing answer summary", "pending_path": str(ppath)}
        print_result(result, as_json=as_json)
        return 2

    result = decision(project_root, prompt, args.scope or (str(pending.get("scope")) if pending and pending.get("scope") else None))
    result.update({"stage": "answer", "pending_path": str(ppath), "captured": False})
    if not result["should_capture"]:
        print_result(result, as_json=as_json)
        return 0
    target = append_capture(
        project_root,
        question=prompt,
        answer_summary=answer_summary,
        scope=str(result["scope"]),
        workstream=args.workstream,
        evidence=args.evidence,
        routed_update=args.routed_update,
        follow_up=args.follow_up,
        dry_run=args.dry_run,
    )
    if not args.keep_pending and ppath.exists() and not args.dry_run:
        ppath.unlink()
    result.update({"captured": not args.dry_run, "target": str(target), "reason": "captured" if not args.dry_run else "dry-run capture"})
    print_result(result, as_json=as_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
