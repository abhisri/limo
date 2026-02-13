
# Folder Map

Last updated: YYYY-MM-DD HH:MM TZ
Freshness target: 30 days

## Purpose
Answer: “Where is stuff stored?” and “Which artifacts are authoritative?”

## How to use
- Keep it simple.
- Prefer paths + 1-line descriptions.
- Record “source of truth” locations.

## Suggested layout (edit to match your repo)
- `core/` — the domain-agnostic spine (this pack)
- `packs/` — domain overlays (optional)
- `addons/` — advanced extensions (optional)
- `analysis/` — generated analysis outputs (tables, reports, plots)
- `data/` — raw inputs (pdfs, logs, dumps)
- `artifacts/` — exported deliverables (bundles, reports)
- `scripts/` — helper scripts

## Sources of truth
- Goals: `core/GOALS.md`
- Current state: `core/STATUS_SNAPSHOT.md`
- Work queue: `core/OPEN_ITEMS.md`
- Decisions: `core/DECISIONS.md`
- Guardrails: `core/INVARIANTS.md` + `core/NEVER_AGAIN.md`
- Learnings: `core/LEARNINGS.md`
