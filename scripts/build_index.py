#!/usr/bin/env python3
"""Consolidate the per-project JSONs scraped by RoundDetails into the skill's data/.

Reads:    theDao/RoundDetails/projects/*.json   (one file per project)
Writes:   data/projects.json                    (sorted list of records, no descriptionHtml)

Run after a fresh pull from RoundDetails/scripts/fetch_round_projects.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SKILL_DIR / "data"
SOURCE_DIR = SKILL_DIR.parent / "RoundDetails" / "projects"


def load_records() -> list[dict]:
    files = sorted(SOURCE_DIR.glob("*.json"))
    records: list[dict] = []
    for f in files:
        try:
            with f.open() as fh:
                rec = json.load(fh)
        except Exception as e:
            print(f"skip {f.name}: {e}", file=sys.stderr)
            continue
        rec.pop("descriptionHtml", None)
        records.append(rec)
    records.sort(key=lambda r: (r.get("roundPosition") or 1_000_000, r.get("id") or 0))
    return records


def main() -> int:
    if not SOURCE_DIR.is_dir():
        print(f"source dir not found: {SOURCE_DIR}", file=sys.stderr)
        return 1
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    records = load_records()
    projects_path = DATA_DIR / "projects.json"
    with projects_path.open("w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote {projects_path} ({len(records)} projects)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
