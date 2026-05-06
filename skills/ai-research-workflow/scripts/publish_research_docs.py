#!/usr/bin/env python3
"""Publish AI research artifacts into project docs/ and create MkDocs config."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ARTIFACT_PAGES = [
    ("RESEARCH.md", "research.md", "Research Spec"),
    ("LITERATURE.md", "literature.md", "Literature Review"),
    ("EXPERIMENT.md", "experiment.md", "Experiment Plan"),
    ("RUNS.md", "runs.md", "Runs"),
    ("RESULTS.md", "results.md", "Results"),
    ("REPRODUCIBILITY.md", "reproducibility.md", "Reproducibility"),
    ("PAPER_DRAFT.md", "paper-draft.md", "Paper Draft"),
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "ai-research"


def first_heading(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def write_page(target: Path, title: str, source: Path) -> None:
    if source.exists():
        body = source.read_text(encoding="utf-8")
        source_note = f"> Source artifact: `{source}`\n\n"
        target.write_text(f"# {title}\n\n{source_note}{body}\n", encoding="utf-8")
    else:
        target.write_text(f"# {title}\n\n> Missing source artifact: `{source}`\n", encoding="utf-8")


def ensure_mkdocs(project_root: Path, site_name: str, slug: str, title: str) -> str:
    mkdocs = project_root / "mkdocs.yml"
    if mkdocs.exists():
        return "existing-preserved"
    mkdocs.write_text(
        f"""site_name: {site_name}
docs_dir: docs
nav:
  - Home: index.md
  - AI Research:
      - Overview: ai-research/index.md
      - {title}:
          - Summary: ai-research/{slug}/index.md
          - Research Spec: ai-research/{slug}/research.md
          - Literature Review: ai-research/{slug}/literature.md
          - Experiment Plan: ai-research/{slug}/experiment.md
          - Runs: ai-research/{slug}/runs.md
          - Results: ai-research/{slug}/results.md
          - Reproducibility: ai-research/{slug}/reproducibility.md
          - Paper Draft: ai-research/{slug}/paper-draft.md
theme:
  name: readthedocs
""",
        encoding="utf-8",
    )
    return "created"


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish AI research artifacts to docs/ and configure MkDocs.")
    parser.add_argument("slug", help="Research workspace slug under --root")
    parser.add_argument("--root", default=".omx/ai-research", help="Research workspace root")
    parser.add_argument("--docs-root", default="docs", help="Project documentation directory")
    parser.add_argument("--site-name", default="AI Research Workflow", help="MkDocs site_name when creating mkdocs.yml")
    parser.add_argument("--title", default=None, help="Human-readable project title")
    args = parser.parse_args()

    project_root = Path.cwd().resolve()
    slug = slugify(args.slug)
    workspace = (project_root / args.root / slug).resolve()
    docs_root = (project_root / args.docs_root).resolve()
    research_docs = docs_root / "ai-research" / slug
    research_docs.mkdir(parents=True, exist_ok=True)
    (docs_root / "ai-research").mkdir(parents=True, exist_ok=True)

    research_md = workspace / "RESEARCH.md"
    title = args.title
    if title is None and research_md.exists():
        title = first_heading(research_md.read_text(encoding="utf-8"), slug)
    title = title or slug

    if not (docs_root / "index.md").exists():
        (docs_root / "index.md").write_text("# Project Documentation\n\n- [AI Research](ai-research/)\n", encoding="utf-8")

    ai_index = docs_root / "ai-research" / "index.md"
    existing = ai_index.read_text(encoding="utf-8") if ai_index.exists() else "# AI Research\n\n"
    link = f"- [{title}]({slug}/)"
    if link not in existing:
        existing = existing.rstrip() + "\n" + link + "\n"
    ai_index.write_text(existing, encoding="utf-8")

    summary_lines = [
        f"# {title}",
        "",
        f"> Source workspace: `{workspace}`",
        "",
        "## Artifacts",
        "",
    ]
    for source_name, page_name, label in ARTIFACT_PAGES:
        source = workspace / source_name
        page = research_docs / page_name
        write_page(page, label, source)
        summary_lines.append(f"- [{label}]({page_name})")
    summary_lines.extend([
        "",
        "## Run outputs",
        "",
        "Run directories, logs, metrics, summaries, and figures are recorded under the source workspace `runs/` directory and linked from `Runs` / `Results` when finalized.",
    ])
    (research_docs / "index.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    mkdocs_action = ensure_mkdocs(project_root, args.site_name, slug, title)
    print(f"docs_dir={research_docs}")
    print(f"mkdocs_yml={project_root / 'mkdocs.yml'}")
    print(f"mkdocs_action={mkdocs_action}")
    print("serve_command=python3 -m mkdocs serve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
