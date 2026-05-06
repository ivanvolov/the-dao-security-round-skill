#!/usr/bin/env python3
"""Search helpers for the Giveth Ethereum Security round skill.

All data lives in ../data/projects.json. This CLI reads it on demand and returns
a compact JSON or table for Claude to reason over.

Examples:
    search.py projects -q "audit fuzzing" --limit 10
    search.py projects -q "blob" --vouched
    search.py projects --category infrastructure
    search.py categories
    search.py show <slug>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROJECTS_FILE = DATA_DIR / "projects.json"

PROJECT_URL_BASE = "https://qf.giveth.io/project"


def load_projects() -> list[dict]:
    with PROJECTS_FILE.open() as f:
        return json.load(f)


def project_haystack(p: dict) -> str:
    parts = [
        p.get("title", ""),
        p.get("descriptionText", ""),
        p.get("descriptionSummary", ""),
    ]
    return " \n ".join(parts).lower()


def match_query(project: dict, terms: list[str]) -> bool:
    if not terms:
        return True
    hay = project_haystack(project)
    return all(t.lower() in hay for t in terms)


def category_strings(p: dict) -> list[str]:
    out: list[str] = []
    for c in p.get("categories") or []:
        for key in ("name", "value"):
            v = c.get(key)
            if v:
                out.append(str(v))
        main = c.get("mainCategory") or {}
        title = main.get("title")
        if title:
            out.append(str(title))
    return out


def match_category(project: dict, needle: str | None) -> bool:
    if not needle:
        return True
    needle_l = needle.lower()
    return any(needle_l in s.lower() for s in category_strings(project))


def project_summary(p: dict) -> dict:
    admin = p.get("adminUser") or {}
    stats = admin.get("publicStats") or {}
    cats = [c.get("value") or c.get("name") for c in (p.get("categories") or [])]
    cats = [c for c in cats if c]
    slug = p.get("slug") or ""
    return {
        "id": p.get("id"),
        "slug": slug,
        "title": p.get("title"),
        "url": f"{PROJECT_URL_BASE}/{slug}" if slug else None,
        "categories": cats,
        "vouched": p.get("vouched"),
        "totalDonated": stats.get("totalReceived"),
        "descriptionSummary": p.get("descriptionSummary"),
    }


def cmd_projects(args: argparse.Namespace) -> int:
    projects = load_projects()
    terms = list(args.query or [])

    results: list[dict] = []
    for p in projects:
        if args.vouched and not p.get("vouched"):
            continue
        if not match_category(p, args.category):
            continue
        if not match_query(p, terms):
            continue
        results.append(p if args.full else project_summary(p))

    results = results[: args.limit] if args.limit else results
    json.dump({"count": len(results), "results": results}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_categories(_: argparse.Namespace) -> int:
    projects = load_projects()
    rows: dict[str, dict] = {}
    for p in projects:
        seen_in_project: set[str] = set()
        for c in p.get("categories") or []:
            name = c.get("value") or c.get("name") or "Unknown"
            if name in seen_in_project:
                continue
            seen_in_project.add(name)
            main = (c.get("mainCategory") or {}).get("title")
            row = rows.setdefault(name, {"category": name, "mainCategory": main, "project_count": 0, "projects": []})
            row["project_count"] += 1
            row["projects"].append({"slug": p.get("slug"), "title": p.get("title")})
    output = sorted(rows.values(), key=lambda r: r["project_count"], reverse=True)
    json.dump({"count": len(output), "results": output}, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    projects = load_projects()
    needle = args.ref.lower()
    for p in projects:
        if (p.get("slug") or "").lower() == needle or str(p.get("id")) == needle:
            json.dump(p, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
            return 0
    print(f"no project with slug/id '{args.ref}'", file=sys.stderr)
    return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="search.py", description="Giveth Ethereum Security round data search.")
    sub = p.add_subparsers(dest="cmd", required=True)

    pr = sub.add_parser("projects", help="Filter project submissions.")
    pr.add_argument("-q", "--query", nargs="*", help="Keywords to AND-match across title/descriptionText/descriptionSummary.")
    pr.add_argument("--category", help="Substring match on category name/value/mainCategory.")
    pr.add_argument("--vouched", action="store_true", help="Only vouched projects.")
    pr.add_argument("--limit", type=int, default=20, help="Max results (default 20; 0 = no limit).")
    pr.add_argument("--full", action="store_true", help="Return full records instead of summaries.")
    pr.set_defaults(func=cmd_projects)

    cs = sub.add_parser("categories", help="List categories and the projects in each.")
    cs.set_defaults(func=cmd_categories)

    sh = sub.add_parser("show", help="Show one full project by slug or id.")
    sh.add_argument("ref", help="Project slug or id.")
    sh.set_defaults(func=cmd_show)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
