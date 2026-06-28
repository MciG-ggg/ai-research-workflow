#!/usr/bin/env python3
"""Run end-to-end guardrail scenarios for ai-research-workflow.

Script: run_e2e_scenarios.py.

This is maintenance-only framework testing. It creates temporary control-plane
workspaces and exercises routing, scaffolding, capture, schema, graph, and
closeout helpers. It does not run user experiments, collect metrics, plot
results, publish docs, merge branches, push remotes, remove worktrees, or delete
branches.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str], *, expect: set[int] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    expect = {0} if expect is None else expect
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode not in expect:
        raise AssertionError(
            f"command failed (expected {sorted(expect)}, got {proc.returncode}): {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc


def py(script: str, *args: str | Path, expect: set[int] | None = None, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return run([sys.executable, str(SCRIPT_DIR / script), *[str(arg) for arg in args]], expect=expect, cwd=cwd)


def replace_first(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"expected text not found in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write_gate_files(project: Path) -> dict[str, Path]:
    gate = project / ".omx" / "plans"
    gate.mkdir(parents=True, exist_ok=True)
    files = {
        "deep": gate / "deep-interview-demo.md",
        "prd": gate / "prd-demo.md",
        "test": gate / "test-spec-demo.md",
        "auto": gate / "autoresearch-complete.json",
    }
    files["deep"].write_text("# Deep Interview\n\nQuestion clarified.\n", encoding="utf-8")
    files["prd"].write_text("# PRD\n\nImplement bounded baseline comparison.\n", encoding="utf-8")
    files["test"].write_text("# Test Spec\n\nValidate control-plane artifacts.\n", encoding="utf-8")
    files["auto"].write_text('{"status":"complete"}\n', encoding="utf-8")
    return files


def add_concrete_evidence(project: Path, slug: str) -> None:
    workstream = project / ".ai-research-workflow" / slug
    run_dir = workstream / "runs" / "run-001"
    run_dir.mkdir(parents=True, exist_ok=True)
    for name, content in {
        "log.txt": "completed\n",
        "metrics.json": '{"accuracy":0.5}\n',
        "summary.md": "# Summary\n\nNo improvement over baseline.\n",
    }.items():
        (run_dir / name).write_text(content, encoding="utf-8")
    (workstream / "scripts" / "run_demo.sh").write_text("#!/usr/bin/env bash\necho demo\n", encoding="utf-8")

    replace_first(
        workstream / "RUNS.md",
        "| TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |",
        "| run-001 | complete | `bash scripts/run_demo.sh` | seed=1/cpu | `.ai-research-workflow/demo-lane/runs/run-001` | `.ai-research-workflow/demo-lane/runs/run-001/log.txt` | `.ai-research-workflow/demo-lane/runs/run-001/metrics.json` | `.ai-research-workflow/demo-lane/runs/run-001/summary.md` | none | control-plane fixture |",
    )
    replace_first(workstream / "RUNS.md", "- Git commit: TODO", "- Git commit: fixture-commit")
    replace_first(
        workstream / "CLAIMS.md",
        "| TODO | TODO | draft / supported / contradicted / inconclusive / retracted | TODO | TODO | TODO | TODO | TODO |",
        "| C1 | Demo method improves the metric | inconclusive | `.ai-research-workflow/demo-lane/runs/run-001/summary.md` | fixture scope | say inconclusive in fixture | say proven | 2026-05-09 |",
    )
    replace_first(
        workstream / "SCRIPT_REGISTRY.md",
        "| TODO | TODO | TODO | TODO | TODO | TODO |",
        "| `bash .ai-research-workflow/demo-lane/scripts/run_demo.sh` | fixture command only | none | `.ai-research-workflow/demo-lane/runs/run-001/summary.md` | dry-run validated | 2026-05-09 |",
    )


def scenario_main_workspace(tmp: Path) -> None:
    project = tmp / "project"
    project.mkdir()
    py("init_research_workspace.py", project, "--preset", "guided", "--idea-scouting", "on", "--qa-capture", "research")
    py("resolve_workflow.py", project, "--prompt", "Generate AI research ideas for efficient evaluation", "--command", "scout")
    paper_route = py("resolve_workflow.py", project, "--prompt", "帮我找 SOTA 和 baseline 论文并维护文章列表")
    assert json.loads(paper_route.stdout)["decisions"]["paper_scouting"] is True
    repro_route = py("resolve_workflow.py", project, "--prompt", "通过复现这篇论文找 idea")
    repro_json = json.loads(repro_route.stdout)
    assert repro_json["routing"]["phase"] == "paper-reproduction"
    assert repro_json["decisions"]["paper_reproduction_scouting"] is True
    experiment_route = py("resolve_workflow.py", project, "--prompt", "开一个实验 workstream 跑一组 ablation")
    experiment_json = json.loads(experiment_route.stdout)
    assert experiment_json["decisions"]["experiment_campaign"] is True
    assert experiment_json["routing"]["phase"] == "new-workstream"
    gates = write_gate_files(project)
    py(
        "init_workstream.py",
        project,
        "paper-fixture",
        "--title",
        "Paper Fixture",
        "--question",
        "Can the selected paper claim be approximately reproduced?",
        "--deep-interview",
        gates["deep"],
        "--ralplan-prd",
        gates["prd"],
        "--ralplan-test-spec",
        gates["test"],
        "--autoresearch-result",
        gates["auto"],
        "--paper-reproduction",
        "--dry-run",
    )
    py(
        "init_workstream.py",
        project,
        "demo-lane",
        "--title",
        "Demo Lane",
        "--question",
        "Does the fixture method improve the metric?",
        "--deep-interview",
        gates["deep"],
        "--ralplan-prd",
        gates["prd"],
        "--ralplan-test-spec",
        gates["test"],
        "--autoresearch-result",
        gates["auto"],
        "--phase",
        "experiment-design",
        "--next-action",
        "record fixture run evidence",
    )
    add_concrete_evidence(project, "demo-lane")

    submit = py(
        "question_capture_hook.py",
        "--stage",
        "submit",
        "--project-root",
        project,
        "--prompt",
        "为什么这个负结果仍然有科研价值？",
    )
    assert json.loads(submit.stdout)["should_capture"] is True
    answer = py(
        "question_capture_hook.py",
        "--stage",
        "answer",
        "--project-root",
        project,
        "--workstream",
        "demo-lane",
        "--answer-summary",
        "It constrains the claim boundary and prevents overclaiming.",
        "--evidence",
        ".ai-research-workflow/demo-lane/runs/run-001/summary.md",
    )
    assert json.loads(answer.stdout)["captured"] is True

    py(
        "preserve_negative_result.py",
        project,
        "demo-lane",
        "--finding",
        "No improvement over baseline in fixture evidence",
        "--evidence",
        ".ai-research-workflow/demo-lane/runs/run-001/summary.md",
        "--interpretation",
        "Treat the method as inconclusive for this fixture scope.",
        "--claim-id",
        "C1",
        "--previous-claim",
        "Demo method improves the metric",
        "--claim-update",
        "Only an inconclusive fixture result is supported.",
    )
    py("prepare_workstream_closeout.py", project, "demo-lane", "--write")
    py("generate_report_outline.py", project, "demo-lane", "--kind", "paper-outline", "--write")
    py("summarize_research_state.py", project)
    py("score_research_artifacts.py", project, "--min-score", "1")
    py("validate_research_workspace.py", project, "--phase", "completion-handoff", "--workstream", "demo-lane", expect={0})
    py("validate_research_schema.py", project)
    graph = py("build_evidence_graph.py", project, "demo-lane", "--json")
    graph_json = json.loads(graph.stdout)
    assert graph_json["nodes"] and graph_json["edges"]

    py("ai_research.py", "resolve", project, "--prompt", "这个实验做完了，整理落盘")
    py("ai_research.py", "help")
    py("ai_research.py", "summarize", project)
    py("ai_research.py", "score", project)
    py("ai_research.py", "schema", project)
    py("check_skill_update.py", "--installed-dir", tmp / "missing-install")


def scenario_migration(tmp: Path) -> None:
    legacy = tmp / "legacy"
    lane = legacy / ".ai-research-workflow" / "old-lane"
    lane.mkdir(parents=True)
    (lane / "RESULTS.md").write_text("# Legacy Results\n", encoding="utf-8")
    py("migrate_research_workspace.py", legacy)
    py("migrate_research_workspace.py", legacy, "--write")
    assert (lane / "STATE.json").is_file()
    assert (legacy / ".ai-research-workflow" / "RESEARCH.md").is_file()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ai-research-workflow E2E guardrail scenarios.")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary scenario workspace for debugging.")
    args = parser.parse_args()

    if args.keep_temp:
        tmp = Path(tempfile.mkdtemp(prefix="ai-research-e2e-"))
        scenario_main_workspace(tmp)
        scenario_migration(tmp)
        print(f"E2E scenarios passed; temp kept: {tmp}")
        return 0

    with tempfile.TemporaryDirectory(prefix="ai-research-e2e-") as raw:
        tmp = Path(raw)
        scenario_main_workspace(tmp)
        scenario_migration(tmp)
    print("E2E scenarios passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
