#!/usr/bin/env python3
"""Initialize an AI research workflow artifact directory."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

FILES = {
    "RESEARCH.md": """# {title}\n\n## Research question\n\nTBD\n\n## Hypothesis\n\nTBD\n\n## Contribution type\n\nTBD\n\n## Motivation and expected novelty\n\nTBD\n\n## Success criteria\n\nTBD\n\n## Falsification criteria\n\nTBD\n\n## In scope\n\nTBD\n\n## Out of scope / non-goals\n\nTBD\n\n## Claim boundaries / forbidden claims\n\nTBD\n\n## Decision boundaries\n\nTBD\n\n## Open questions\n\nTBD\n""",
    "LITERATURE.md": """# Literature Review: {title}\n\n## Search date\n\nTBD\n\n## Query strategy\n\nTBD\n\n## Inclusion / exclusion criteria\n\nTBD\n\n## Source table\n\n| Source | Link | Relevance | Key evidence |\n| --- | --- | --- | --- |\n| TBD | TBD | TBD | TBD |\n\n## Related-work matrix\n\nTBD\n\n## Baseline candidates\n\nTBD\n\n## Dataset and benchmark notes\n\nTBD\n\n## Gaps and risks\n\nTBD\n""",
    "EXPERIMENT.md": """# Experiment Plan: {title}\n\n## Experiment objective\n\nTBD\n\n## Datasets and splits\n\nTBD\n\n## Baselines\n\nTBD\n\n## Method variants\n\nTBD\n\n## Training or inference configuration\n\nTBD\n\n## Metrics\n\nTBD\n\n## Statistical testing plan\n\nTBD\n\n## Ablations\n\nTBD\n\n## Seeds\n\nTBD\n\n## Hardware and runtime budget\n\nTBD\n\n## Logging and artifact paths\n\nTBD\n\n## Reproduction commands\n\n```bash\n# TBD\n```\n\n## Failure policy\n\nTBD\n""",
    "RUNS.md": """# Experiment Runs: {title}\n\n## Environment\n\nTBD\n\n## Commands\n\nTBD\n\n## Data versions\n\nTBD\n\n## Seeds\n\nTBD\n\n## Logs and output paths\n\nTBD\n\n## Failures / retries\n\nTBD\n""",
    "RESULTS.md": """# Results: {title}\n\n## Result artifact paths\n\nTBD\n\n## Summary tables\n\nTBD\n\n## Hypothesis verdicts\n\nTBD\n\n## Uncertainty / variance\n\nTBD\n\n## Ablations\n\nTBD\n\n## Error analysis\n\nTBD\n\n## Threats to validity\n\nTBD\n\n## Evidence-to-claim mapping\n\nTBD\n""",
    "REPRODUCIBILITY.md": """# Reproducibility Review: {title}\n\n## Fresh-agent reproduction check\n\nTBD\n\n## Data access\n\nTBD\n\n## Environment requirements\n\nTBD\n\n## Commands and seeds\n\nTBD\n\n## Known non-determinism\n\nTBD\n\n## Blockers\n\nTBD\n""",
    "PAPER_DRAFT.md": """# Paper Draft: {title}\n\n## Abstract\n\nTBD\n\n## Introduction\n\nTBD\n\n## Related work\n\nTBD\n\n## Method\n\nTBD\n\n## Experimental setup\n\nTBD\n\n## Results\n\nTBD\n\n## Limitations\n\nTBD\n\n## Conclusion\n\nTBD\n\n## Claim traceability table\n\n| Claim | Evidence source | Status |\n| --- | --- | --- |\n| TBD | TBD | TBD |\n""",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower()).strip("-")
    return slug or "ai-research"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create AI research workflow artifact files.")
    parser.add_argument("slug", help="Research workspace slug")
    parser.add_argument("--root", default=".omx/ai-research", help="Root directory for research workspaces")
    parser.add_argument("--title", default="AI Research Project", help="Human-readable research title")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    target = Path(args.root) / slugify(args.slug)
    target.mkdir(parents=True, exist_ok=True)

    created = []
    skipped = []
    for filename, template in FILES.items():
        path = target / filename
        if path.exists() and not args.force:
            skipped.append(str(path))
            continue
        path.write_text(template.format(title=args.title), encoding="utf-8")
        created.append(str(path))

    print(f"workspace={target}")
    if created:
        print("created:")
        for item in created:
            print(f"  {item}")
    if skipped:
        print("skipped_existing:")
        for item in skipped:
            print(f"  {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
