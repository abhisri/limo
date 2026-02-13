# LIMO — LLM Interaction Memory OS

LIMO is a lightweight, file-based “memory + workflow spine” for long-running LLM work.
It turns LLM sessions into a **restartable process** using plain Markdown files: goals, open items, decisions, invariants, learnings, and session diaries.

If a session ends, context rolls off, a VM resets, or you switch tools/models — you can reboot in minutes by re-reading the workspace files and continuing from a clear “source of truth”.

**Default: single-agent (solo).**  
**Optional: multi-agent (Coordinator/Worker)** for teams or dual-agent setups.

---

## What problem does this solve?

LLMs are powerful, but long projects fail for boring reasons:
- context drift (“what were we doing again?”)
- repeated mistakes (“we already tried this”)
- lost rationale (“why did we decide that?”)
- session fragility (tool crashes / context limits / switching agents)
- fuzzy next steps (no durable task queue)

LIMO fixes this with a small, consistent set of files that act like a durable “working memory”:
- **Goal** stays stable
- **Decisions** stay auditable
- **Invariants** prevent repeated errors
- **Open items** keep work bounded
- **Session diary** preserves narrative continuity
- **Learnings** capture reusable insights

---

## Who is LIMO for?

- **Solo builders** using one agent (Claude, ChatGPT, Codex, etc.)
- **People juggling multiple sessions/tools** and needing continuity
- **Teams / power users** who want a clean Coordinator/Worker workflow
- Any domain where work spans hours → weeks: coding, finance, legal, HR, BI, research, operations, data science

---

## Core idea (in one line)

**Move the “brain” from the chat window into a tiny set of auditable files.**

---

## How it works (conceptual)

### Solo mode (default)
One agent edits the workspace files directly:
- update STATUS_SNAPSHOT + OPEN_ITEMS as you go
- log decisions in DECISIONS
- add hard rules in INVARIANTS / NEVER_AGAIN
- append progress to SESSION_DIARY

### Multi-agent mode (optional)
Two roles:
- **Coordinator** owns shared truth + final narrative
- **Worker** does deep dives (code/data) and makes **proposals**
- Coordinator **promotes** Worker proposals into shared truth (so nothing chaotic edits the source-of-truth files)

---

## Why Markdown + folders?

Because it’s:
- tool-agnostic (works with any LLM/tool)
- diffable (Git-friendly)
- auditable (decisions + evidence don’t vanish)
- easy to sanitize and share

---

## Repo layout (high level)

- `core/` — domain-agnostic “spine” (single-agent default)
- `packs/` — optional domain overlays (coding/finance/research/ops…)
- `addons/` — optional advanced patterns (multi-agent, automation, git ops…)
- `scripts/` — minimal helpers (create workspace, stale report, hashing, run manifests)
- `examples/` — sanitized example workspaces
- `workspaces/` — your real workspaces (gitignored)

---

## What LIMO is not

- Not an “agent framework”
- Not a vector DB / RAG system
- Not a replacement for good artifacts (logs, debug images, datasets)

It’s a **discipline layer**: a small OS-like structure that makes LLM work durable.

---

## License

Licensed under the MIT License. See `LICENSE`.
