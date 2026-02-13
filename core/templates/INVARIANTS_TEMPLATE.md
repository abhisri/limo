
# Invariants

Last updated: YYYY-MM-DD HH:MM TZ
Freshness target: 30 days (review occasionally)

## Purpose
Convert “judgment” into **auditable rules** so sessions stop repeating the same class of mistakes.

## Tagging convention
- **[SOLO]** applies when running a single agent (default).
- **[WORKER]** applies only to Worker sessions (propose-only).
- **[COORDINATOR]** applies only to Coordinator sessions (promotion authority).
- **[SHARED]** applies in all modes.

## Enforcement rule
If an invariant conflicts with a plan: **stop**, log the conflict, and resolve it before proceeding.

---

## INV-001 [SHARED] Read before acting
- Invariant: Read the startup checklist before substantive work.
- Auto-action: follow `core/CONTEXT_RESTORE_PROTOCOL.md`.

## INV-002 [SHARED] Baselines before claims
- Invariant: Don’t claim causality without a baseline / control.
- Auto-action: write a minimal A/B plan first.

## INV-003 [SHARED] One variable class per run
- Invariant: Change one variable class per run unless explicitly testing interaction.
- Auto-action: split experiments.

## INV-004 [SHARED] Weak signals are triage only
- Invariant: Counters/summaries are not root-cause proof.
- Auto-action: request or generate primary artifacts (images, logs, tables, repro cases).

## INV-005 [WORKER] Propose-only discipline (optional mode)
- Invariant: Worker must not edit shared truth files.
- Auto-action: write a proposal in Worker notes; Coordinator promotes.

(Add domain-specific invariants in domain packs under `packs/<domain>/INVARIANTS_ADDON.md`.)
