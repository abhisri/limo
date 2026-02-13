# LIMO — LLM Interaction Memory OS

**Your AI agent forgets everything when the session ends. LIMO fixes that.**

---

## The Problem

You're three hours into a complex project with Claude, ChatGPT, Codex, or Cursor. You've made dozens of decisions. You've hit dead ends and found workarounds. You've built up real momentum.

Then the session crashes. Or the context window fills up. Or the sandbox resets. Or you just need to switch tools.

**Everything is gone.** You start the next session with "where were we?" and spend 30 minutes re-explaining context that the AI will only half-remember. Decisions get re-litigated. Mistakes get repeated. The same dead ends get explored again.

This isn't a model problem — it's a **memory problem**. LLMs have no durable working memory across sessions. Every restart is a cold start.

## The Solution

LIMO gives your AI agent a small set of Markdown files that act as persistent working memory:

| File | What it does |
| :--- | :--- |
| `STATUS_SNAPSHOT.md` | "Here's where we are right now" |
| `GOALS.md` | "Here's where we're heading" |
| `OPEN_ITEMS.md` | "Here's what's next" |
| `DECISIONS.md` | "Here's what we already decided (and why)" |
| `INVARIANTS.md` | "Here are the rules that must always hold" |
| `NEVER_AGAIN.md` | "Here are the mistakes we already made" |
| `LEARNINGS.md` | "Here's what we figured out" |
| `SESSION_DIARY.md` | "Here's what happened, in order" |

Drop these files into your project folder. Tell your AI agent to read them first. When the session ends, the files stay. When a new session starts, the agent reads the files and picks up exactly where you left off.

**No framework. No database. No vendor lock-in. Just Markdown files that any LLM can read.**

## Who This Is For

- **Anyone using AI agents for work that spans multiple sessions** — coding, research, analysis, writing, operations, finance, legal, data science
- **People who switch between tools** (Claude today, Codex tomorrow, Cursor next week) and need continuity
- **Teams running multi-agent workflows** where one agent shouldn't overwrite another's decisions

## How It Works

### 1. Copy the core files into your project

```bash
cp -r core/ your-project/limo/
```

### 2. Tell your AI agent about them

Paste the bootstrap prompt (see [INSTRUCTIONS.md](INSTRUCTIONS.md)) into your first message, or place the files where your agent auto-reads them (e.g., a project folder in Claude Code, or Codex's workspace).

### 3. Work normally — the agent maintains the files

After each meaningful step, the agent updates the workspace files. When a session ends and a new one starts, the agent reads the files and resumes.

That's it. No setup beyond copying files.

## What's in the Repo

```
core/           → The memory spine (8 Markdown templates + restore protocol)
packs/          → Domain-specific overlays (coding, finance, research, operations)
addons/         → Optional patterns (multi-agent coordination, git ops, automation)
scripts/        → Helpers (create workspace, staleness report, hashing)
examples/       → Sanitized example workspaces
INSTRUCTIONS.md → How to use LIMO with Claude, Codex, ChatGPT, and others
```

### Core (always use)

The `core/` directory is the only thing you need. Everything else is optional.

### Packs (optional, pick your domain)

Domain packs add specialized templates and checklists:

- **`packs/coding/`** — test matrix, architecture decisions, debug log
- **`packs/finance/`** — reconciliation tracker, variance log, close checklist
- **`packs/research/`** — hypothesis tracker, source registry, evidence chain
- **`packs/operations/`** — runbook, incident log, escalation rules

### Addons (optional, for power users)

- **`addons/multi_agent/`** — Coordinator/Worker pattern (one agent owns truth, the other proposes changes)
- **`addons/git_ops/`** — Git-aware workspace management
- **`addons/automation/`** — Staleness checks, manifest generation

## Solo Mode vs. Multi-Agent Mode

**Solo (default):** One agent reads and writes the workspace files directly. This is what most people need.

**Multi-agent (optional):** Two roles — a **Coordinator** that owns the source of truth, and a **Worker** that does deep dives and submits proposals. The Coordinator promotes proposals into the shared files. Useful for complex projects or when you want to prevent one agent from accidentally overwriting another's work. See `addons/multi_agent/`.

## Why Markdown?

- **Tool-agnostic** — works with any LLM, any editor, any platform
- **Diffable** — Git-friendly, easy to track changes over time
- **Auditable** — decisions and rationale don't vanish when a session ends
- **Portable** — no database, no API, no dependencies
- **Human-readable** — you can always open the files and see exactly what the AI "knows"

## What LIMO Is Not

- Not an agent framework (it works *inside* any framework)
- Not a vector DB or RAG system (it's simpler and more transparent)
- Not a replacement for good artifacts (code, data, docs still live where they normally do)

LIMO is a **discipline layer** — a small structure that makes AI work durable across sessions, tools, and context limits.

## Getting Started

See **[INSTRUCTIONS.md](INSTRUCTIONS.md)** for step-by-step setup with your specific AI tool.

## License

MIT — see [LICENSE](LICENSE).
