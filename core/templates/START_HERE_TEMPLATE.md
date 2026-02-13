
# START HERE

This repo provides a **domain-agnostic workspace spine** for running work with an AI agent in a way that survives context loss, crashes, and handoffs.

## Default mode (recommended): Solo agent
Assume **one AI agent** is operating in this workspace and may edit these files.

## Optional mode: Worker / Coordinator
If you want multi-agent later:
- **Coordinator** = owns “shared truth” + final decisions.
- **Worker** = does deep reading and proposes patches; Coordinator promotes.

If you are not explicitly using two agents, ignore Worker/Coordinator language.

## What to do first (every session)
1. Read: `core/CONTEXT_RESTORE_PROTOCOL.md`
2. Then open (in this order):
   - `core/STATUS_SNAPSHOT.md`
   - `core/GOALS.md`
   - `core/OPEN_ITEMS.md`
   - `core/INVARIANTS.md` + `core/NEVER_AGAIN.md`
   - `core/DECISIONS.md`
   - `core/FOLDER_MAP.md`

## After each meaningful work block (milestones only)
Update:
- `STATUS_SNAPSHOT.md` (what’s true right now)
- `OPEN_ITEMS.md` (what’s next / blocked)
- `DECISIONS.md` (if a decision was made)
- `LEARNINGS.md` (if a reusable lesson emerged)

(Next file in this pack: `core/CONTEXT_RESTORE_PROTOCOL.md`)
