# Context Restore Protocol

## Purpose
Make the work crash-restartable. A new session can resume deterministically.

## Startup checklist (single-agent, strict order)
1) Read `core/START_HERE.md`
2) Read `core/STATUS_SNAPSHOT.md`
3) Read `core/GOALS.md`
4) Read `core/OPEN_ITEMS.md`
5) Read `core/INVARIANTS.md` + `core/NEVER_AGAIN.md`
6) Read `core/DECISIONS.md`
7) Read `core/FOLDER_MAP.md`
8) Skim `core/SESSION_DIARY.md` (milestones only)

## Update policy (single-agent)
After each meaningful milestone:
- Update `STATUS_SNAPSHOT.md`
- Update `OPEN_ITEMS.md`
- Append irreversible decisions to `DECISIONS.md`
- Append a milestone entry to `SESSION_DIARY.md`

## Evidence rule
If you only have summaries/counters, treat them as triage. Ask for primary artifacts.
