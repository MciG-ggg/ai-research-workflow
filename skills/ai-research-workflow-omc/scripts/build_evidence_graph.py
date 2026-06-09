#!/usr/bin/env python3
"""Build a claim/evidence graph from ai-research workstream artifacts.

Script: build_evidence_graph.py.

This is a read-only framework guardrail. It parses CLAIMS.md, RESULTS.md,
RUNS.md, and SCRIPT_REGISTRY.md to expose claim -> evidence -> run/script links.
It does not run experiments, collect metrics, plot results, publish docs, merge
branches, push remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_tables(path: Path) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    lines = read_text(path).splitlines()
    idx = 0
    while idx < len(lines) - 1:
        if lines[idx].lstrip().startswith("|") and lines[idx + 1].lstrip().startswith("|") and "---" in lines[idx + 1]:
            headers = split_row(lines[idx])
            rows: list[list[str]] = []
            idx += 2
            while idx < len(lines) and lines[idx].lstrip().startswith("|"):
                rows.append(split_row(lines[idx]))
                idx += 1
            tables.append((headers, rows))
        else:
            idx += 1
    return tables


def norm(header: str) -> str:
    return header.lower().replace(" / ", "_").replace("/", "_").replace(" ", "_").replace("-", "_")


def rows_for(path: Path, required: set[str]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for headers, rows in parse_tables(path):
        normalized = [norm(h) for h in headers]
        if not required.issubset(set(normalized)):
            continue
        for row in rows:
            if all(cell.strip().lower() in {"", "todo", "tbd"} for cell in row):
                continue
            out.append({normalized[i]: row[i] if i < len(row) else "" for i in range(len(normalized))})
    return out


def split_paths(value: str) -> list[str]:
    tokens = []
    for part in re.split(r"[,;]\s*|<br\s*/?>|\s+and\s+", value):
        cleaned = part.strip().strip("`")
        if cleaned and cleaned.lower() not in {"todo", "tbd", "none"}:
            tokens.append(cleaned)
    return tokens


def add_node(nodes: dict[str, dict[str, Any]], node_id: str, node_type: str, **attrs: Any) -> None:
    if not node_id:
        return
    node = nodes.setdefault(node_id, {"id": node_id, "type": node_type})
    node.update({k: v for k, v in attrs.items() if v not in (None, "")})


def add_edge(edges: list[dict[str, str]], source: str, target: str, relation: str) -> None:
    if source and target:
        edge = {"source": source, "target": target, "relation": relation}
        if edge not in edges:
            edges.append(edge)


def build(project_root: Path, slug: str) -> dict[str, Any]:
    workstream = project_root / ".omc" / "ai-research" / slug
    if not workstream.is_dir():
        raise SystemExit(f"missing workstream: {workstream}")
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []

    add_node(nodes, f"workstream:{slug}", "workstream", path=str(workstream))

    claims = rows_for(workstream / "CLAIMS.md", {"claim_id", "claim", "status", "evidence_paths"})
    for row in claims:
        claim_id = row.get("claim_id") or row.get("claim") or "claim:unknown"
        if claim_id.lower() in {"todo", "tbd"}:
            continue
        cid = f"claim:{claim_id}"
        add_node(nodes, cid, "claim", text=row.get("claim"), status=row.get("status"), scope=row.get("scope_population"))
        add_edge(edges, f"workstream:{slug}", cid, "contains_claim")
        for evidence in split_paths(row.get("evidence_paths", "")):
            eid = f"evidence:{evidence}"
            add_node(nodes, eid, "evidence", path=evidence)
            add_edge(edges, cid, eid, "supported_by")

    results = rows_for(workstream / "RESULTS.md", {"result", "evidence_path"})
    for row in results:
        result_text = row.get("result") or row.get("claim") or row.get("method") or "result"
        rid = f"result:{result_text[:80]}"
        add_node(nodes, rid, "result", text=result_text, interpretation=row.get("interpretation"), status=row.get("status"))
        add_edge(edges, f"workstream:{slug}", rid, "contains_result")
        for evidence in split_paths(row.get("evidence_path", "") or row.get("source", "")):
            eid = f"evidence:{evidence}"
            add_node(nodes, eid, "evidence", path=evidence)
            add_edge(edges, rid, eid, "uses_evidence")

    runs = rows_for(workstream / "RUNS.md", {"run_id", "status", "command"})
    for row in runs:
        run_id = row.get("run_id", "")
        if run_id.lower() in {"todo", "tbd", ""}:
            continue
        rid = f"run:{run_id}"
        add_node(nodes, rid, "run", status=row.get("status"), command=row.get("command"), run_dir=row.get("run_dir"))
        add_edge(edges, f"workstream:{slug}", rid, "contains_run")
        for key, relation in (("log", "has_log"), ("metrics", "has_metrics"), ("summary", "has_summary"), ("figures", "has_figure")):
            for evidence in split_paths(row.get(key, "")):
                eid = f"evidence:{evidence}"
                add_node(nodes, eid, "evidence", path=evidence)
                add_edge(edges, rid, eid, relation)

    commands = rows_for(workstream / "SCRIPT_REGISTRY.md", {"command", "purpose"})
    scripts = rows_for(workstream / "SCRIPT_REGISTRY.md", {"script", "purpose"})
    for row in [*commands, *scripts]:
        name = row.get("script") or row.get("command") or ""
        if name.lower() in {"todo", "tbd", ""}:
            continue
        sid = f"script:{name}"
        add_node(nodes, sid, "script", purpose=row.get("purpose"), outputs=row.get("outputs"))
        add_edge(edges, f"workstream:{slug}", sid, "uses_script")
        for output in split_paths(row.get("outputs", "")):
            eid = f"evidence:{output}"
            add_node(nodes, eid, "evidence", path=output)
            add_edge(edges, sid, eid, "produces")

    evidence_ids = {node_id for node_id, node in nodes.items() if node.get("type") == "evidence"}
    for run_id, run_node in list(nodes.items()):
        if run_node.get("type") != "run":
            continue
        run_dir = str(run_node.get("run_dir", ""))
        if not run_dir:
            continue
        for evidence_id in evidence_ids:
            if run_dir and run_dir in evidence_id:
                add_edge(edges, run_id, evidence_id, "may_have_produced")

    return {"project_root": str(project_root), "workstream": slug, "nodes": sorted(nodes.values(), key=lambda x: x["id"]), "edges": edges}


def markdown(graph: dict[str, Any]) -> str:
    claims = [node for node in graph["nodes"] if node["type"] == "claim"]
    rows = []
    for claim in claims:
        evidence = [edge["target"].removeprefix("evidence:") for edge in graph["edges"] if edge["source"] == claim["id"]]
        rows.append(f"| `{claim['id'].removeprefix('claim:')}` | {claim.get('status', '')} | {claim.get('text', '')} | {', '.join(evidence) or 'none'} |")
    if not rows:
        rows = ["| none | n/a | no claim rows found | none |"]
    return f"""# Claim Evidence Graph

- Project root: `{graph['project_root']}`
- Workstream: `{graph['workstream']}`
- Nodes: {len(graph['nodes'])}
- Edges: {len(graph['edges'])}

| Claim | Status | Text | Evidence |
| --- | --- | --- | --- |
{chr(10).join(rows)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build claim/evidence/run/script graph from workstream artifacts.")
    parser.add_argument("project_root", type=Path, help="Target project root.")
    parser.add_argument("slug", help="Workstream slug.")
    parser.add_argument("--json", action="store_true", help="Print JSON graph instead of Markdown.")
    parser.add_argument("--output", type=Path, help="Optional output path.")
    args = parser.parse_args()

    graph = build(args.project_root.resolve(), args.slug)
    text = json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True) + "\n" if args.json else markdown(graph)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"Wrote evidence graph: {args.output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
