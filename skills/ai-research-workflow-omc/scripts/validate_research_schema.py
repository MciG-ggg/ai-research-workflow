#!/usr/bin/env python3
"""Validate ai-research JSON schemas and artifact-table contracts.

Script: validate_research_schema.py.

This is a framework guardrail. It validates CONFIG, STATE, claim ledger, run
ledger, and portfolio index-row shape with stdlib checks. It does not run
experiments, collect metrics, plot results, publish docs, merge branches, push
remotes, remove worktrees, or delete branches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = SCRIPT_DIR.parent / "assets" / "schemas"
EXCLUDED_DIRS = {"runs", "logs", "state", "worktrees", "scripts", "docs"}


@dataclass
class Finding:
    level: str
    path: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def load_schema(name: str, schema_dir: Path) -> dict[str, Any]:
    return json.loads((schema_dir / f"{name}.schema.json").read_text(encoding="utf-8"))


def parse_config(path: Path) -> dict[str, Any]:
    config: dict[str, Any] = {}
    text = read_text(path)
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-z0-9_]+)\s*:\s*([A-Za-z0-9_-]+)\s*$", line)
        if match:
            key, value = match.group(1), match.group(2)
            config[key] = int(value) if key == "schema_version" and value.isdigit() else value.lower()
    return config


def type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return True


def validate_object(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type and not type_ok(value, expected_type):
        return [f"{path} expected {expected_type}, got {type(value).__name__}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path} expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path} expected one of {schema['enum']!r}, got {value!r}")
    if isinstance(value, str) and "pattern" in schema and not re.match(str(schema["pattern"]), value):
        errors.append(f"{path} does not match pattern {schema['pattern']!r}: {value!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}.{key} is required")
        properties = schema.get("properties", {})
        for key, child in properties.items():
            if key in value:
                errors.extend(validate_object(value[key], child, f"{path}.{key}"))
    if isinstance(value, list) and "items" in schema:
        for idx, item in enumerate(value):
            errors.extend(validate_object(item, schema["items"], f"{path}[{idx}]"))
    return errors


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


def normalize_key(header: str) -> str:
    lower = header.lower().strip()
    mapping = {
        "claim id": "claim_id",
        "claim": "claim",
        "status": "status",
        "evidence paths": "evidence_paths",
        "evidence path": "evidence_paths",
        "scope / population": "scope",
        "allowed wording": "allowed_wording",
        "forbidden wording": "forbidden_wording",
        "last checked": "last_checked",
        "run id": "run_id",
        "command": "command",
        "log": "log_path",
        "metrics": "metrics_path",
        "summary": "summary_path",
        "seed/device/resource": "seed",
        "slug": "slug",
        "subquestion": "subquestion",
        "relationship to overall objective": "relationship",
        "key artifact links": "artifact_links",
        "latest evidence": "latest_evidence",
        "gate evidence": "gate_evidence",
        "next action": "next_action",
    }
    return mapping.get(lower, lower.replace(" ", "_").replace("/", "_"))


def split_paths(value: str) -> list[str]:
    parts = re.split(r"[,;]\s*|<br\s*/?>", value)
    cleaned = [part.strip(" `") for part in parts if part.strip(" `")]
    return cleaned


def row_to_object(headers: list[str], row: list[str], kind: str, fallback_commit: str = "unknown") -> dict[str, Any]:
    raw = {normalize_key(h): row[i] if i < len(row) else "" for i, h in enumerate(headers)}
    if kind == "claim":
        return {
            "claim_id": raw.get("claim_id", ""),
            "claim": raw.get("claim", ""),
            "status": raw.get("status", "").split("/")[0].strip(),
            "evidence_paths": split_paths(raw.get("evidence_paths", "")),
            "scope": raw.get("scope", ""),
            "allowed_wording": raw.get("allowed_wording", ""),
            "forbidden_wording": raw.get("forbidden_wording", ""),
            "last_checked": raw.get("last_checked", ""),
        }
    if kind == "run":
        return {
            "run_id": raw.get("run_id", ""),
            "command": raw.get("command", ""),
            "status": raw.get("status", ""),
            "log_path": raw.get("log_path", ""),
            "metrics_path": raw.get("metrics_path", ""),
            "summary_path": raw.get("summary_path", ""),
            "commit": fallback_commit,
            "seed": raw.get("seed", ""),
            "device": raw.get("seed", ""),
        }
    return {
        "slug": raw.get("slug", ""),
        "status": raw.get("status", ""),
        "subquestion": raw.get("subquestion", ""),
        "relationship": raw.get("relationship", ""),
        "artifact_links": split_paths(raw.get("artifact_links", "")),
        "latest_evidence": raw.get("latest_evidence", ""),
        "gate_evidence": raw.get("gate_evidence", ""),
        "next_action": raw.get("next_action", ""),
    }


def is_placeholder(row: list[str]) -> bool:
    cells = [cell.strip().lower() for cell in row]
    joined = " ".join(cells).strip()
    if not joined or joined in {"todo", "tbd"}:
        return True
    if cells and cells[0] in {"todo", "tbd", ""}:
        return True
    placeholder_count = sum(1 for cell in cells if cell in {"todo", "tbd", ""})
    return bool(cells) and placeholder_count >= max(1, len(cells) - 1)


def find_workstreams(ai_root: Path) -> list[Path]:
    if not ai_root.is_dir():
        return []
    return sorted(path for path in ai_root.iterdir() if path.is_dir() and not path.name.startswith(".") and path.name not in EXCLUDED_DIRS)


def table_with_header(path: Path, required: set[str]) -> tuple[list[str], list[list[str]]] | None:
    for headers, rows in parse_tables(path):
        normalized = {normalize_key(h) for h in headers}
        if required.issubset(normalized):
            return headers, rows
    return None


def validate_project(project_root: Path, schema_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    ai_root = project_root / ".omc" / "ai-research"
    if not ai_root.is_dir():
        return [Finding("error", str(ai_root), "missing ai-research root")]

    schemas = {name: load_schema(name, schema_dir) for name in ("CONFIG", "STATE", "CLAIM", "RUN", "INDEX_ROW")}
    config_path = ai_root / "CONFIG.md"
    if config_path.is_file():
        config = parse_config(config_path)
        for error in validate_object(config, schemas["CONFIG"], "CONFIG"):
            findings.append(Finding("error", str(config_path), error))
    else:
        findings.append(Finding("warning", str(config_path), "missing CONFIG.md; defaults will be inferred"))

    index_path = ai_root / "INDEX.md"
    index_table = table_with_header(index_path, {"slug", "status", "subquestion", "gate_evidence", "next_action"}) if index_path.is_file() else None
    if index_table is None:
        findings.append(Finding("error", str(index_path), "missing portfolio index row table"))
    else:
        concrete = 0
        headers, rows = index_table
        for row in rows:
            if is_placeholder(row):
                continue
            concrete += 1
            obj = row_to_object(headers, row, "index")
            for error in validate_object(obj, schemas["INDEX_ROW"], "INDEX_ROW"):
                findings.append(Finding("error", str(index_path), error))
        if concrete == 0:
            findings.append(Finding("warning", str(index_path), "no concrete non-TODO index rows found"))

    for workstream in find_workstreams(ai_root):
        state_path = workstream / "STATE.json"
        if state_path.is_file():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                for error in validate_object(state, schemas["STATE"], "STATE"):
                    findings.append(Finding("error", str(state_path), error))
            except json.JSONDecodeError as exc:
                findings.append(Finding("error", str(state_path), f"invalid JSON: {exc}"))
        else:
            findings.append(Finding("error", str(state_path), "missing STATE.json"))

        claims_path = workstream / "CLAIMS.md"
        claim_table = table_with_header(claims_path, {"claim_id", "claim", "status", "evidence_paths"}) if claims_path.is_file() else None
        if claim_table is None:
            findings.append(Finding("error", str(claims_path), "missing claim ledger table"))
        else:
            concrete = 0
            headers, rows = claim_table
            for row in rows:
                if is_placeholder(row):
                    continue
                concrete += 1
                obj = row_to_object(headers, row, "claim")
                for error in validate_object(obj, schemas["CLAIM"], "CLAIM"):
                    findings.append(Finding("error", str(claims_path), error))
            if concrete == 0:
                findings.append(Finding("warning", str(claims_path), "no concrete non-TODO claim rows found"))

        runs_path = workstream / "RUNS.md"
        run_table = table_with_header(runs_path, {"run_id", "status", "command", "log_path", "metrics_path", "summary_path"}) if runs_path.is_file() else None
        commit_match = re.search(r"Git commit:\s*([^\n]+)", read_text(runs_path), re.IGNORECASE)
        commit = commit_match.group(1).strip() if commit_match else "unknown"
        if run_table is None:
            findings.append(Finding("error", str(runs_path), "missing run ledger table"))
        else:
            concrete = 0
            headers, rows = run_table
            for row in rows:
                if is_placeholder(row):
                    continue
                concrete += 1
                obj = row_to_object(headers, row, "run", fallback_commit=commit)
                for error in validate_object(obj, schemas["RUN"], "RUN"):
                    findings.append(Finding("error", str(runs_path), error))
            if concrete == 0:
                findings.append(Finding("warning", str(runs_path), "no concrete non-TODO run rows found"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate .omc/ai-research schemas and artifact table contracts.")
    parser.add_argument("project_root", nargs="?", default=".", type=Path, help="Target project root. Defaults to cwd.")
    parser.add_argument("--schema-dir", type=Path, default=SCHEMA_DIR, help="Schema directory. Defaults to skill assets/schemas.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    parser.add_argument("--json", action="store_true", help="Print JSON findings.")
    args = parser.parse_args()

    findings = validate_project(args.project_root.resolve(), args.schema_dir.resolve())
    if args.json:
        print(json.dumps([finding.__dict__ for finding in findings], ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for finding in findings:
            print(f"{finding.level}: {finding.path}: {finding.message}", file=sys.stderr)
    errors = [finding for finding in findings if finding.level == "error"]
    warnings = [finding for finding in findings if finding.level == "warning"]
    if errors or (args.strict and warnings):
        return 1
    print(f"Research schema valid: {args.project_root.resolve()}")
    if warnings and not args.json:
        print(f"Warnings: {len(warnings)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
