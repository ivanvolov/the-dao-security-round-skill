# the-dao-security-round-skill

A Claude Code skill that answers questions about projects in the **Giveth Ethereum Security** quadratic-funding round. Local-only — no backend, no API keys at query time.

## The round

**Ethereum Security QF Round** on Giveth — round id `16`, slug `ethereum-security`. Co-organized by [The DAO Fund](https://x.com/thedaofund) (commemorating the 10-year mark since The DAO incident) and [Giveth](https://giveth.io). Matching pool started at 500 ETH and has grown past 514 ETH with sponsor top-ups from [Chainsecurity](https://x.com/chain_security), [Quantstamp](https://x.com/Quantstamp) ($50,000), and [ECH Institute](https://x.com/ECHInstitute). 134 projects listed at the time the index was built.

Round page: <https://qf.giveth.io/qf/ethereum-security>

## What this skill does

When you ask Claude Code a question scoped to this round — *"what blob-data projects are in the round?"*, *"who's working on audit tooling?"*, *"which infrastructure projects are vouched?"* — it shells out to a small Python CLI that filters the indexed projects and returns compact JSON, then answers from real data.

Three commands the skill calls:

```bash
python3 scripts/search.py projects -q "<keywords>" [--category X] [--vouched] [--limit N]
python3 scripts/search.py categories
python3 scripts/search.py show <slug>
```

`-q` AND-matches keywords across `title`, `descriptionText`, and `descriptionSummary`. `--category` is a case-insensitive substring against each project's category and parent category.

## Layout

```
the-dao-security-round-skill/
├── SKILL.md             skill manifest (instructions Claude reads)
├── README.md            this file
├── data/
│   └── projects.json    134 consolidated project records
└── scripts/
    ├── search.py        query CLI; the skill's only entry point
    └── build_index.py   rebuilds projects.json from RoundDetails/projects/*.json
```

## Refreshing the data

The upstream parser lives at `theDao/RoundDetails/scripts/fetch_round_projects.py` (queries `core.v6.giveth.io/graphql`). Two-step refresh:

```bash
# 1. pull the latest per-project JSONs from Giveth
python3 ../RoundDetails/scripts/fetch_round_projects.py

# 2. rebuild the consolidated index this skill reads
python3 scripts/build_index.py
```

`build_index.py` strips `descriptionHtml` (the plain-text and summary fields are what the keyword search uses), sorts by `roundPosition`, and writes `data/projects.json`.

## Installation

The skill folder is registered to Claude Code by symlinking it into `~/.claude/skills/`:

```bash
ln -s "$(pwd)" ~/.claude/skills/the-dao-security-round-skill
```

Restart Claude Code; the skill appears in the available-skills list.

## Pattern

Mirrors the `ethglobal-copilot` skill pattern: pure local files + a small Python CLI invoked over Bash. No HTTP at query time, no full-text index — 134 records and ~1 MB makes in-memory substring search instant.
