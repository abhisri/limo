
# Context Restore Protocol

## Purpose
Make work **restartable**. Any new session/agent should be able to:
- reconstruct the current state fast,
- avoid repeating mistakes,
- continue work with minimal drift.

## Modes
### Solo mode (default)
One agent edits core files directly.

### Worker/Coordinator mode (optional)
- Worker = propose-only (does NOT change shared truth)
- Coordinator = promotes proposals into shared truth

If you are not explicitly running two agents, treat everything as Solo.

---

## Startup checklist — SOLO (strict order)
1. Read `core/START_HERE.md`
2. Read `core/STATUS_SNAPSHOT.md`
3. Read `core/GOALS.md`
4. Read `core/OPEN_ITEMS.md`
5. Read `core/INVARIANTS.md` and `core/NEVER_AGAIN.md`
6. Read `core/DECISIONS.md`
7. Read `core/FOLDER_MAP.md`
8. Begin work on the top item in `OPEN_ITEMS.md`.

## Startup checklist — WORKER (strict order)
1. Read `core/START_HERE.md`
2. Read `core/STATUS_SNAPSHOT.md`
3. Read `core/GOALS.md`
4. Read `core/OPEN_ITEMS.md`
5. Read `core/INVARIANTS.md` and `core/NEVER_AGAIN.md`
6. Read `core/DECISIONS.md`
7. Read `core/FOLDER_MAP.md`
8. Do deep work and produce **Proposals** (format below).

## Startup checklist — COORDINATOR (strict order)
1. Read `core/START_HERE.md`
2. Read `core/STATUS_SNAPSHOT.md`
3. Read `core/GOALS.md`
4. Read `core/OPEN_ITEMS.md`
5. Read `core/INVARIANTS.md` and `core/NEVER_AGAIN.md`
6. Read `core/DECISIONS.md`
7. Read `core/FOLDER_MAP.md`
8. Decide next actions and **promote** Worker proposals into shared truth.

---

## Promotion rule (Worker → Coordinator)
Worker output is **not truth** until promoted.

### Proposal format (copy-paste)
**Proposed patch**
- File(s):
- Exact change:
- Rationale:

**Evidence**
- Artifact path(s):
- Relevant snippet(s) / logs / measurements:

**Risk**
- What could go wrong:
- Rollback plan:

**Next step**
- How to validate (A/B, check, test):

Coordinator actions:
- **Promote** (apply patch) OR **Reject** (reason + alternative).

---

## “Milestone-only” update rule
Do **not** log every interim thought. Only update diaries/snapshots when something meaningful happened:
- decision made,
- hypothesis falsified,
- new artifact produced,
- blocker found/removed,
- run completed.

---

## Freshness / staleness guard
If a file’s “Last updated” is older than your domain’s freshness window:
- Treat it as a **hypothesis** until revalidated.
- Prefer regenerating artifacts over trusting old summaries.
