# LIMO — LLM Interaction Memory OS

**Your AI agent forgets everything when the session ends. LIMO fixes that.**

---

## The Problem

You're three hours into a complex project with Claude, ChatGPT, Codex, or Cursor. You've made dozens of decisions. You've hit dead ends and found workarounds. You've built up real momentum.

Then the session crashes. Or the context window fills up. Or the sandbox resets. Or you just need to switch tools.

**Everything is gone.** You start the next session with "where were we?" and spend 30 minutes re-explaining context that the AI will only half-remember. Decisions get re-litigated. Mistakes get repeated. The same dead ends get explored again.

And if you switch tools? It’s worse.
Claude doesn't know what Codex did.
Codex doesn’t know why Cursor rejected that refactor.

This isn't a model problem — it's a **memory and state coordination problem**. LLMs have no durable working memory across sessions. Every restart or tool switch is a cold start.

## The Solution

LIMO gives your AI agent a small set of Markdown files that act as persistent working memory, organized around a 4-tier memory model that:

- Preserve decisions and rationale
- Enforce invariants
- Gate repeated mistakes
- Track evolving learnings
- Enable deterministic session restore
- Allow multiple AI tools to resume from the same architectural state

The result:

Not just persistent memory —
but shared reasoning continuity across agents and tools.

LIMO does not route tasks or execute agents — it provides the durable state layer that makes orchestration possible.

| Tier | What | Where |
|:-----|:-----|:------|
| Procedural | Model capabilities | Built into weights |
| Declarative | Facts + history | Boot prompt + session prompt + session diary |
| Behavioral | Learned patterns | Brain transfer + learnings + never again |
| Episodic | Specific recall | Raw transcripts (grep, don't load) |

The core files:

| File | What it does |
|:-----|:-------------|
| `AI_AGENTS_READ_THIS_FIRST.md` | Bootstrap: read order, three rules, episodic recall |
| `[DOMAIN]_SESSION_PROMPT.md` | The soul of the domain — everything a cold-start AI needs |
| `STATUS_SNAPSHOT.md` | "Here's where we are right now" |
| `GOALS.md` | "Here's where we're heading (and what we're NOT doing)" |
| `OPEN_ITEMS.md` | "Here's what's next" |
| `DECISIONS.md` | "Here's what we already decided (and why)" |
| `INVARIANTS.md` | "Here are the rules that must always hold" |
| `NEVER_AGAIN.md` | "Here are the mistakes we already made" |
| `LEARNINGS.md` | "Here's what we figured out" |
| `SESSION_DIARY.md` | "Here's what happened, in order" |
| `CONTEXT_RESTORE_PROTOCOL.md` | Deterministic startup checklist + write-back triggers |

Drop these files into your project folder. Tell your AI agent to read them first. When the session ends, the files stay. When a new session starts, the agent reads the files and picks up exactly where you left off.

**No framework. No database. No vendor lock-in. Just Markdown files that any LLM can read.**

## Who This Is For

- **Anyone using AI agents for work that spans multiple sessions** — coding, research, analysis, writing, operations, finance, legal, data science
- **People who switch between tools** (Claude today, Codex tomorrow, Cursor next week) and need continuity
- **Builders orchestrating multiple AI agents — where one model writes, another critiques, another optimizes, and all of them inherit the same decision history, invariants, and mistakes log
- **Anyone tired of re-explaining context** every time a session crashes or resets

## What's in the Repo

```
LIMO_FRAMEWORK.md     → The complete spec — architecture, memory model, file specs, rules
file_templates.md     → Copy-paste templates for every core file
SKILL.md              → Scaffolding workflow (how to set up a new domain)
advanced_patterns.md  → Optional patterns for complex domains (handover, cross-domain)
INSTRUCTIONS.md       → Tool-specific setup for Claude, Codex, ChatGPT, Cursor, etc.
```

**`LIMO_FRAMEWORK.md`** — The full specification. Explains the 4-tier memory model, every file's purpose and format, write-back triggers, freshness guards, domain forking, and compression protocols. Start here to understand LIMO.

**`file_templates.md`** — Ready-to-use templates for every core file. Replace `[DOMAIN]` with your domain name, `[USER]` with your name, and populate from your first conversation. This is what makes LIMO actionable.

**`SKILL.md`** — A step-by-step scaffolding workflow: interview the user, create the file tree, populate files with real content, verify nothing is empty. Written as a Claude skill but the phased approach (interview → scaffold → populate → verify) works with any AI agent.

**`advanced_patterns.md`** — Patterns from complex, high-stakes domains (Finance, Legal). Session handover templates, cross-domain boot prompts, extended brain transfer formats. Most domains won't need these.

## How It Works

### 1. Set up a new domain

Share `LIMO_FRAMEWORK.md` and `file_templates.md` with your AI agent and tell it: *"Set up LIMO for [my project]."*

The agent interviews you about the domain, creates the file tree, and populates every file with real content from the conversation.

### 2. Work normally — the agent maintains the files

`CONTEXT_RESTORE_PROTOCOL.md` tells the agent when to update which files. After each meaningful step (decision made, task completed, blocker hit), the agent updates the relevant files.

### 3. On new sessions, the agent reads and resumes

Tell the new session: *"Read AI_AGENTS_READ_THIS_FIRST.md and follow the restore protocol."* The agent reconstructs full context from the files and picks up where the last session left off.

## Design Principles

**Opinionated about memory, permissive about everything else.** LIMO prescribes the memory architecture (4 tiers, specific files, write-back triggers) but doesn't prescribe your domain. A photography workflow and a legal case use the same spine with different content.

**Files over chat.** If chat history and LIMO files disagree, the files win. That's the whole point.

**Write in real time, not at session end.** LEARNINGS.md and NEVER_AGAIN.md get updated the moment an insight or mistake happens. Waiting until session end means you forget or the session crashes first.

**Freshness guards.** Every file has a "Last updated" date and a freshness target. If a file is older than its target, the agent treats it as hypothesis, not truth.

**Earned complexity.** Core LIMO is ~11 files. Advanced patterns exist for domains that earn them through real usage. Don't add handover templates until you actually need handovers.

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

## Provenance

LIMO v2.1 was developed iteratively across real domains — Photography/Hobbies, LIFE management, Legal, Code Development and Finance — each adding patterns that proved their worth through actual multi-session work. The framework was then generalized by removing domain-specific patterns from the core and preserving them as optional advanced patterns.

## Getting Started

See **[INSTRUCTIONS.md](INSTRUCTIONS.md)** for tool-specific setup.

## License

MIT — see [LICENSE](LICENSE).
