# LIMO — LLM Interaction Memory OS

**Version:** 2.5 (Field adaptations — pull-based boot, trigger injection, line validity + supersession, reconcile/reflect, interruption hooks, ready/claim/stall, git write-ahead log, consistency lint)
**Author:** Abhishek Srivastava
**Last updated:** 2026-09-15
**Last verified against production:** 2026-09-15 (workspace `CLAUDE-PROJECTS/`, 14 domains; 9 memory repos initialised)
**Freshness target (this spec):** 180 days — past that, re-verify every `Source:` reference below against the workspace before trusting it.

> **Reading this outside the author's workspace:** paths cited in *Source:* lines (`shared/…`, `infra/…`, `Research-Experiment/…`) are
> evidence trails into the production workspace where each convention was first used. They are not files in this repository.
> Domain names are illustrative; the mechanisms are what matter.

> **v2.4 in one line:** the spec describes what actually runs; every convention cites the production file it was lifted from.
> **v2.5 in one line:** the eight mechanisms the field does better (survey of 29 systems, `(comparative survey, author workspace)`)
> are adopted without touching the governance taxonomy the field lacks. Changes are grouped by **conformance level**
> so a reader with only markdown and one agent can ignore what needs git, two agents, or an infrastructure stack.

---

## What LIMO Is

LIMO is a filesystem-based persistent memory architecture for AI sessions. It solves the fundamental problem of LLM context windows: every new conversation starts from zero. LIMO gives each domain its own structured memory that survives across sessions, prevents repeated mistakes, and enables behavioral adaptation over time.

The name maps to how it works: just as a limousine carries passengers across destinations without them having to re-explain where they're going, LIMO carries context across sessions without the AI having to re-learn who you are and what you've decided.

---

LIMO is model-agnostic by construction. Everything canonical is markdown on disk, so any agent
with file access (Claude Code, Claude Cowork, Codex CLI, Gemini CLI, Qwen CLI, any MCP client)
can run the full read/write loop, and a chat-only model (ChatGPT web) can participate by paste or
upload. The `Agent:` field on every checkpoint records who wrote what.

---

## Conformance Levels

*Added v2.4 (P6). Decided in the Feb–May 2026 build sessions as a 3-tier architecture; first written into the spec here.*

The spec is one file, but it describes three levels of adoption. Every section below carries a tag.
Adopt the lowest level that fits; nothing at a higher level is required by a lower one.

| Level | Tag | Needs | What it gives you |
|:------|:----|:------|:------------------|
| **LIMO Core** | `[Core]` | Markdown files + one agent with file access (or a chat model + paste) | Domains, core files, write-back loop, freshness, checkpoints, forking. This is what `github.com/abhisri/limo` ships. |
| **LIMO Git** | `[Git]` | A git repository holding `limo-populated/` (memory only, never code) | Every core-file write is a commit; `git log -p` is the audit trail; worktrees for concurrent agents; stale-lock recovery. Adopted v2.5 — this was always the intended middle tier. |
| **LIMO Agents** | `[Agents]` | Two or more agents (or seats) working the same domain | Ownership manifest, single writer of truth, propose-only workers, seat separation, SETTLED tables, Director Layer, inter-agent messaging |
| **LIMO Infra** | `[Infra]` | A backend (this workspace: Event API on Neo4j, mem0, Postgres, Qdrant — the automation stack) | Memory classes, hybrid boot, event-logged history, semantic recall, node trust boundaries |

`[Core]` sections are the specification proper. `[Git]`, `[Agents]` and `[Infra]` sections are additive: they
change *where* some things live, *who* may write them and *how the history is kept*, never the file formats.
LIMO is one hybrid: the basic system is markdown files; add git for history; add the EC2 stack (`infra/`) for
events, semantic recall and the bus. Each level is a superset of the one before.

The scaffolder (`SKILL.md`) asks which level a new domain targets and creates only the files that
level needs.

---

## 4-Tier Memory Model `[Core]`

LIMO mirrors how human memory works:

| Tier | Human analogy | LIMO equivalent | Persistence |
|:-----|:-------------|:----------------|:------------|
| **Procedural** | Muscle memory, how-to | Model weights (not file-stored) | Permanent (built into model) |
| **Declarative** | Facts, identity, what happened | BOOT_PROMPT + SESSION_PROMPT + SESSION_DIARY | Updated per session |
| **Behavioral** | Learned preferences, instincts | BRAIN_TRANSFER + LEARNINGS + NEVER_AGAIN | Updated in real time |
| **Episodic** | Specific memories on demand | Raw transcripts (grepped, not loaded whole) | Append-only archive |

**Key insight:** Tiers 2 and 3 are the active memory. Tier 4 is recall — expensive to load, used only when deep context is needed. Tier 1 is the model itself.


### Memory Classes `[Infra]`

*Added v2.4 (A2). Source: `shared/MEMORY_CLASSES.md` (adopted 2026-04-21), `shared/SESSION_BOOT_PROTOCOL.md`.*

The 4-tier model stays the mental model. At the Infra level, storage is split into six classes so
sessions stop collapsing "memory" into one idea. The mapping from core files to classes:

| Class | Purpose | Store | LIMO files that live here |
|:------|:--------|:------|:--------------------------|
| `canonical` | stable rules, doctrine, decisions, open items, profile truth | flat files | SESSION_PROMPT, INVARIANTS, DECISIONS, OPEN_ITEMS, LEARNINGS, NEVER_AGAIN, USER_PROFILE, BOOT_PROMPT, BRAIN_TRANSFER, OWNERS |
| `episodic` | timestamped things that happened | Event API / Neo4j | SESSION_DIARY (flat file becomes a stub), milestones, deployments, blockers |
| `working` | current task state, ownership, retries, leases | Postgres control plane | (no flat file — STATUS_SNAPSHOT stays flat as the human-readable summary) |
| `semantic` | meaning-based recall, summaries, insights | mem0 | GOALS content, cross-domain insights |
| `corpus` | quoted source text and real artifacts | Qdrant + MinIO | `{Domain}/Documents/` ingested copies |
| `local` | node-private scratch, cache, auth | node-local | never treated as shared truth |

**Transition state (verified 2026-09-15):** several domains still carry full SESSION_DIARY.md files
(Contracts 397 lines, Venture 256, Legal 203, 3d printing 96). Read them if present; log *new*
history to the Event API; stub the file per `shared/SESSION_DIARY_FORMAT.md` when the domain is
migrated. `limo_lint.py` flags diaries over the threshold.

---

## Architecture: System Bus `[Core]`

```
CLAUDE-PROJECTS/                          ← Root (all domains MUST share this root)
├── USER_PROFILE.md                       ← Shared identity (all sessions read + write)
├── CLAUDE_BOOT_PROMPT.md                 ← Shared: who is this AI, working style
├── CLAUDE_BRAIN_TRANSFER.md              ← Shared: communication patterns, corrections
├── _messages/                            ← Inter-agent message bus [Agents] (see Messaging section)
│   └── _processed/                       ← Handled messages (audit trail)
├── shared/                               ← [Infra] boot protocol, memory classes, write boundaries
│   ├── SESSION_BOOT_PROTOCOL.md          ← Supersedes per-domain CONTEXT_RESTORE_PROTOCOL (v2.4)
│   ├── MEMORY_CLASSES.md
│   └── DEAD_END_INDEX.md                 ← GENERATED by limo_lint.py deadends (v2.4)
├── tools/
│   ├── limo_lint.py                      ← lint / bootpack / triggers / ready / reflect / deadends / agentsmd / commit / git-init (v2.5)
│   └── hooks/                            ← Claude Code hook scripts: prompt → triggers, pre-compact → flush, session-end → bootpack + commit
│
├── Domain-A/                             ← e.g., Finance, LIFE, Legal
│   ├── AGENTS.md                         ← [Agents] optional: per-repo seat instructions (Tier 0 orientation doc)
│   ├── Documents/                        ← FACTS live here (possessions, contracts, lab reports, source docs)
│   └── limo-populated/                   ← [Git] memory-only repository root; `.limo-memory-repo` marker enables agent commits
│       ├── AGENTS.md                     ← GENERATED from BOOT_PACK Part A + OWNERS.md (v2.5) — any CLI agent boots here
│       └── core/                         ← GOVERNANCE lives here (summaries, rules, decisions)
│           ├── AI_AGENTS_READ_THIS_FIRST.md
│           ├── BOOT_PACK.md              ← GENERATED — Part A ≤ 60 lines + signpost index (v2.5, never hand-edited)
│           ├── TRIGGER_INDEX.md          ← GENERATED — keyword/glob → gate map (v2.5)
│           ├── _pending/                 ← proposals awaiting promotion: reflect_<date>.md, worker-proposed entries (v2.5)
│           ├── START_HERE.md
│           ├── OWNERS.md                 ← [Agents] who may write which file (v2.4)
│           ├── [DOMAIN]_SESSION_PROMPT.md
│           ├── STATUS_SNAPSHOT.md
│           ├── GOALS.md
│           ├── OPEN_ITEMS.md
│           ├── DECISIONS.md
│           ├── INVARIANTS.md
│           ├── LEARNINGS.md
│           ├── NEVER_AGAIN.md
│           ├── KEY_PEOPLE.md             ← If domain involves people/relationships
│           ├── ARCHITECTURE.md           ← If domain involves a codebase
│           ├── CONTEXT_RESTORE_PROTOCOL.md  ← ⚠️ LEGACY (pre-v2.4); keep if present, do not create
│           ├── MEMORY_COMPRESSION_PROTOCOL.md
│           ├── FOLDER_MAP.md
│           ├── SESSION_DIARY.md          ← Session milestones (stub at [Infra] level; compress when large)
│           ├── CHECKPOINTS.md            ← Structured progress: golden paths + dead ends
│           └── _archive/                 ← Old versions of core files
│
├── Domain-B/
│   └── limo-populated/core/...
│
└── Domain-C/
    └── limo-populated/core/...
```

**Prerequisite:** All LIMO domains must share a common root folder (e.g., `CLAUDE-PROJECTS/`). The shared bus (USER_PROFILE, BOOT_PROMPT, BRAIN_TRANSFER, `_messages/`) lives at this root. If domains are scattered across different folders or drives, the shared bus and inter-agent messaging won't work. When setting up LIMO, pick one root folder and put everything under it.

**Governance vs facts (added v2.4, A1).** `limo-populated/core/` is the *governance* layer. It is not
where facts about possessions, purchases, contracts, inventories or lab values live — those sit in
`{Domain}/Documents/`. **Every number in a core file is a summary, not a source.** Open the
document before quoting a figure, and state its date alongside it. Source: `shared/SESSION_BOOT_PROTOCOL.md`
Phase 2b, added after a 2026-08-09 session made six wrong factual claims with every correcting file mounted and unread.

**Domain boundary rules:**
- Each session WRITES only to its own domain folder
- Each session READS from sibling domains (cross-pollination)
- Shared files at root are read+write for all sessions
- `_messages/` at root is the inter-agent communication bus (see Messaging section)
- Cross-domain items are noted and redirected — or messaged directly to the target domain
- At the `[Agents]` level, `OWNERS.md` narrows this further per file (see Multi-Agent Operation)

---

## File Specifications `[Core]`

### Layer 1: Bootstrap (what the AI reads first)

#### AI_AGENTS_READ_THIS_FIRST.md
**Purpose:** Fastest possible orientation for a cold-start AI.
**Format:** Numbered list, no phases. Maximum 10 items pointing to files in read order.
**Includes:** Three Rules that govern all behavior in this domain.
**Freshness target:** 30 days


```markdown
# [Domain] — AI Agents Read This First

You're continuing work on [1-sentence domain description].

## Read these files in order:
1. `BOOT_PACK.md` — GENERATED digest: settled questions, status, open items, gates, Documents/ tree, lint (v2.4)
2. `CLAUDE_BOOT_PROMPT.md` — who the user is
3. `[DOMAIN]_SESSION_PROMPT.md` — domain context, current state
4. `CLAUDE_BRAIN_TRANSFER.md` — communication style, corrections log
5. `OWNERS.md` — which files you may write, which you may only propose to ([Agents] level)
6. `DECISIONS.md` — what's been decided (don't re-litigate)
7. `INVARIANTS.md` — rules that never break
8. Open STATUS_SNAPSHOT / GOALS / OPEN_ITEMS / CHECKPOINTS in full only when BOOT_PACK's signposts point you there

## Before acting on any request (v2.5)
Run `python3 tools/limo_lint.py triggers "<request>" <Domain>` and read every gate it returns in full.
First line of your first reply in this domain: `[LIMO: <Domain> booted from BOOT_PACK <date>]`.

## Three Rules
1. Write LEARNINGS.md and NEVER_AGAIN.md IN REAL TIME when corrections happen
2. Action over permission — do the work, don't ask if you should
3. Trust files over chat — if files and conversation conflict, files win

## Before asserting a fact
`ls -R ../Documents/` then grep before writing "you don't have", "you never mentioned", "X is missing".
Core files are summaries. Documents/ is the source.

## Episodic recall
For deep history, grep SESSION_DIARY.md / CHECKPOINTS.md (`checkpoint-tail:`) or query the Event API. Don't load whole files.
```

#### BOOT_PACK.md `[Core]` — GENERATED
*Added v2.4 (P2); redesigned v2.5 (M1) as pull-based. Sources: Letta MemFS `system/` vs `reference/` split with `description:` signposts; Claude Code auto-memory index budget (200 lines / 25 KB, error on overflow); Serena list-then-read; Anthropic context-engineering guidance (just-in-time retrieval by identifier).*
**Purpose:** Cold start in one read, then everything else on demand. The v2.4 pack pushed ~150 lines of content; the v2.5 pack pushes a **Part A of at most 60 lines** and a **Part B signpost index** so the agent chooses what to open.
**Generated by:** `tools/limo_lint.py bootpack {Domain}` — **never hand-edited.** Banner on first and last line.
**Part A (always loaded, hard cap 60 lines):** SETTLED tables (first 3) · Goal · Blockers · Next 3 · NEVER_AGAIN *titles* (first 10) · INVARIANTS *titles* (first 10) · one-line lint summary. Over budget → the pack is truncated, stamped **OVER BUDGET**, and `bootpack` exits 1 naming what to compress at source (Claude's overflow-error pattern). The budget is the mechanism: it forces SETTLED tables and STATUS to stay short.
**Part B (signposts, read on demand):** one line per core file — `path — description — last updated ⚠️stale?` — where *description* comes from a `description:` frontmatter line (lint flags files without one; falls back to the first prose line) · `Documents/` tree to depth 2 with file counts · last 3 `checkpoint-tail:` lines. Bodies are opened by the agent when a signpost is relevant, never pre-loaded.
**What moved out of the pack vs v2.4:** active OPEN_ITEMS rows (use `limo_lint.py ready`), NEVER_AGAIN bodies (use `triggers`), INVARIANTS bodies (open the file when a title is relevant).
**Rule:** summaries of summaries. It says *where* to look, not *what is true*. Open the source before quoting.
**Freshness:** regenerate at every boot and after any write-back; lint flags a pack older than STATUS_SNAPSHOT.

#### TRIGGER_INDEX.md `[Core]` — GENERATED
*Added v2.5 (M2). Sources: OpenHands `triggers:` / `paths:` frontmatter, Devin Knowledge trigger descriptions, Cursor description-gated rules, Windsurf trigger types.*
**Purpose:** A NEVER_AGAIN entry protects only if it is in front of the agent when the matching request arrives. At boot it is one title among forty. Triggers make the gate fire *deterministically* when a request contains a keyword or a path matching a glob — no semantic matching, so the behaviour is auditable.
**Convention:** any NEVER_AGAIN or INVARIANTS entry may carry a line `- Triggers: keyword, another phrase, *.docx, src/core/*` immediately under its heading (or a `{triggers: …}` tag). Keywords match case-insensitively as substrings of the request; globs match against request tokens containing `/` or `.`.
**Generated by:** `limo_lint.py all` (or `bootpack`) writes `core/TRIGGER_INDEX.md` — the keyword → gate table.
**Used by:** `limo_lint.py triggers "<request text>" <Domain>` prints every matching entry in full. The boot instruction makes this the first step before acting; where hooks exist (Claude Code `UserPromptSubmit`) it runs automatically — see `tools/hooks/`.
**Seeding rule:** add triggers to the gates that have actually been violated first (2026-09-15 seed in the author's workspace: twelve gates across four domains — possessions and inventory claims, lab values, unprompted legal analysis, cooking oils, external investor material, ownership figures). Every other gate still fires at boot by title.

#### START_HERE.md
**Purpose:** Richer orientation with architecture context, cross-domain reading rules, and the 4-tier memory model explanation.
**Freshness target:** 30 days

#### Boot protocol (replaces per-domain CONTEXT_RESTORE_PROTOCOL.md)
*Changed v2.4 (A1). Source: `shared/SESSION_BOOT_PROTOCOL.md` (ADOPTED 2026-03-01; Phase 2b added 2026-08-09).*

At `[Core]` level the boot sequence is the AI_AGENTS_READ_THIS_FIRST list above. At `[Infra]` level
it is the shared hybrid protocol, and per-domain CONTEXT_RESTORE_PROTOCOL.md files are **legacy**:
keep them if present, do not create new ones, and point AI_AGENTS_READ_THIS_FIRST at the shared file.

The rules that CONTEXT_RESTORE_PROTOCOL carried remain in force and now live here:
- **Phase 0: Orientation** — Check for existing orientation docs (AGENTS.md, CLAUDE.md, .github/agents/, .cursor/rules) before exploring
- **Phase 2b: Documents** — `ls -R {Domain}/Documents/`; grep before asserting (see Governance vs facts above)
- **File Authority Hierarchy** — When files conflict: INVARIANTS > NEVER_AGAIN > SETTLED tables > DECISIONS > STATUS_SNAPSHOT > DIARY/CHECKPOINTS > BOOT_PACK > Chat
- **Mutation Gating** — Do not write to persistent files without explicit instruction or trigger; casual acknowledgment ("LGTM", "sounds good") is not write permission
- **Freshness Guard** — If a file's "Last updated" is older than its freshness target, treat as hypothesis; run `limo_lint.py lint` rather than eyeballing
- **Stale File Handling** — Flag stale files to user, prefer regeneration over trusting stale content
- **Domain Boundaries** — Write to own folder only, read from siblings; at `[Agents]` level obey OWNERS.md
- **Episodic Memory** — How to access deep history (grep or Event API query, not load)
- **Large File Handling** — If any file is too large to load: read last 200 lines first, or grep for keywords. For CHECKPOINTS.md: grep `checkpoint-tail:` for index.
- **Temporal context** — establish the real date/time from a trusted source before any reply that states a date or computes a deadline; do not extrapolate from an earlier reading
- **Assume interruption (v2.5, M5)** — the two events that actually destroy state are context compaction and a killed session; neither waits for a session-end ritual. Before any long step, and whenever compaction is imminent, write STATUS_SNAPSHOT next-3 + blockers and one diary line, then regenerate BOOT_PACK. Where hooks exist they enforce this (`tools/hooks/`). *Sources: Anthropic memory-tool protocol, an automation runtime pre-compaction flush, Letta sleep-time consolidation on compaction.*
- **Boot banner (v2.5)** — first line of the first reply in a domain: `[LIMO: <Domain> booted from BOOT_PACK <date>]` so a human can see that memory loaded (Roo Code's load-status banner).

---

### Layer 2: Identity (shared across all domains)

#### USER_PROFILE.md (at CLAUDE-PROJECTS root)
**Purpose:** Cross-session narrative profile of the human. Any session updates this when something changes the story of who the person is.
**Update rule:** Any session can write. Only when something matters cross-domain.
**Format:** Narrative sections covering the person's full context — health, career, relationships, patterns, milestones.

#### CLAUDE_BOOT_PROMPT.md (at root or in core/)
**Purpose:** Who this AI is in relation to this human. Working style, personality, values alignment.
**Freshness target:** 90 days

#### CLAUDE_BRAIN_TRANSFER.md (at root or in core/)
**Purpose:** Communication patterns learned over time. Corrections log. Reasoning style preferences.
**Freshness target:** 60 days
**Format — 3 sections:**

1. **Corrections Log** — Specific corrections with "What happened" / "Lesson" format. These are the highest-value behavioral data.
2. **Communication Style** — Voice, information density, when to push back, what NOT to do.
3. **Reasoning Patterns** — How the user thinks. Domain-specific reasoning approaches.

Domains can add sections as needed (e.g., key relationships, personality markers), but these three are the universal core.

---

### Layer 3: Domain Context (domain-specific, the primary knowledge file)

#### [DOMAIN]_SESSION_PROMPT.md
**Purpose:** THE most important file. Everything the AI needs to know about this domain — current state, history, constraints, standing instructions.
**Format:** Numbered sections covering all relevant aspects of the domain.
**Size:** Can be large (200-400 lines). This is the file that makes the AI competent in this domain.
**Freshness target:** 14 days

**Examples of sections by domain type:**
- **Health/Life:** Medical status, household, nutrition, mobility, exercise, wellbeing, standing instructions
- **Legal:** Case status, parties, timeline, evidence summary, strategy, court schedule
- **Finance:** Accounts, cash flow, investments, obligations, projections
- **Hobby:** Skill level, equipment, goals, exercises, environments
- **Work/Career:** Role, projects, team, OKRs, blockers
- **Coding/Engineering:** Architecture overview, module map, build status, tech debt, codebase conventions, standing instructions

---
### Layer 4: Working Memory (what's happening NOW)

#### STATUS_SNAPSHOT.md
**Purpose:** Current state in 30 seconds of reading.
**Freshness target:** 7 days (during active work)

**Source tags (added v2.4, P3).** Any figure, date, quantity or lab value in STATUS_SNAPSHOT, SESSION_PROMPT,
GOALS or KEY_PEOPLE carries a source tag: `[src: Documents/Household/Furnishing_Roadmap.txt#2026-04-12]`
(path relative to the domain, `#` the date of the source document). A figure with no source is written
as approximate (`~$1,000, see tracker`) or moved to prose. `limo_lint.py` reports untraced numbers in
those four files. This does not guarantee the source is current; it guarantees the agent knows where to look.

**Format:**
```markdown
## Goal (1 line)
[Single sentence]

## Current phase
[What stage of work]

## What's done
- [Completed items]

## What's next (top 3)
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## Blockers
- [What's preventing progress]

## Latest artifacts
- [Recently created files with paths]

## Risks / gotchas
- [Things that could go wrong]
```

#### GOALS.md
**Purpose:** Where this domain is headed.
**Freshness target:** 14 days
**Format:**
```markdown
## North Star
[1-2 sentence ultimate objective]

## Objectives
- O1: [Objective]
- O2: [Objective]

## Milestones
- M1: [DONE] Description
- M2: [NEXT] Description
- M3: [PENDING] Description
- M4: [FUTURE] Description

## Non-Goals
- [What this domain is explicitly NOT trying to do — prevents scope creep]

## Constraints
- [Budget, time, health, dependencies on other domains]
```

#### OPEN_ITEMS.md
**Purpose:** Action items with ownership and deadlines.
**Freshness target:** 7 days
**Readiness, claims and stalls (v2.5, M6; `[Agents]`).** *Sources: Beads `bd ready` / `--claim` / stall detection, Basic Memory relations.* Three optional tags on a row make "what can I do right now" a computed answer and stop two agents taking one item:
- `{blocked_by: OI-X-012, OI-X-015}` — the row is not ready until those rows are closed
- `{claimed: codex 2026-09-15}` — one agent per row; lint flags a second claim
- `{started: 2026-09-01}` — lint flags **stall**: a claimed or started row with no diary or checkpoint mention after 7 days
`limo_lint.py ready <Domain> --agent <me>` lists rows with no open blockers that are unclaimed or mine; blocked and taken rows are listed separately. Rows may be list rows (`- OI-…`) or table rows (`| OI-… |`); a struck-through ID (`~~OI-…~~`) counts as closed. In domains worked by more than one agent use the date-stamped ID form to avoid collisions.
**Format:**
```markdown
## Active
- OI-[DOMAIN]-001 | Owner | Due date | Priority | Description | Context/success criteria

## Parking Lot
- OI-[DOMAIN]-P01 | Owner | DEFERRED | Description | Why deferred

## Cross-Domain (note only — action belongs to other sessions)
- [Item] → [Which session owns it]
```

**ID format options:**
- Sequential: `OI-L001` (simpler, good for smaller domains)
- Date-stamped: `OI-L-20260215-01` (better for high-volume domains, embeds when it was created)

#### DECISIONS.md
**Purpose:** What's been decided. Prevents re-litigating settled questions.
**Freshness target:** 90 days
**Format:**
```markdown
### D-[DOMAIN]-001 — [Decision title]
- Decision: [What was decided]
- Why: [Reasoning]
- Alternatives rejected: [What was considered and ruled out]
- Evidence: [What data/documents/analysis supports this — optional, but prevents re-litigation]
- Revisit triggers: [What would reopen this decision]
- Origin: [Which session/date this was decided]
```

---
### Memory Line Conventions (v2.5) `[Core]`

*Added v2.5 (M3, M4). Sources: Zep/Graphiti bi-temporal edges and invalidate-don't-delete; Supermemory `isLatest` update chains; Mastra three dates per line and reflector; Hindsight facts vs opinions with confidence; LangMem profile vs collection; mem0 ADD/UPDATE/DELETE/NOOP; A-MEM neighbour revision; Cursor approval-before-save.*

**Profile vs collection.** STATUS_SNAPSHOT, GOALS and KEY_PEOPLE are *profiles*: regenerate the section, never append a second version under the first. DECISIONS, LEARNINGS, NEVER_AGAIN, INVARIANTS and CHECKPOINTS are *collections*: append, with reconciliation.

**Line tags.** Any entry in a collection file may carry, on its heading line or first bullet, any of:
```
{valid: 2026-03-19..}            open range — live entry
{valid: 2026-03-19..2026-06-01}  closed range — superseded or expired; never deleted
{supersedes: D-VENTURE-003}         the entry this one replaces (target must exist somewhere in core)
{class: fact|opinion|preference|episode|rule}
{confidence: 0.7}                opinions only; reinforce or downgrade when evidence arrives
{triggers: keyword, *.glob}      NEVER_AGAIN / INVARIANTS only — see TRIGGER_INDEX
{observed_by: codex}             KEY_PEOPLE only — whose picture of the person this is
```
**Rules.** (1) Never delete a superseded entry: close its `valid` range and point the new one at it with `supersedes:`. (2) BOOT_PACK, DEAD_END_INDEX and `ready` show only open-range entries. (3) An `opinion` older than 90 days with no `confidence` is flagged; a `rule` or `fact` never decays by age. (4) Lint flags: two open-range entries with the same ID, a `supersedes:` target that does not exist, a class outside the set.

**Reconcile on write.** Before appending to a collection file: search the file for the same subject; then **ADD** (new subject), **UPDATE** (close the old entry's range, write the new one with `supersedes:`), or **NOOP** (already captured — say so in the diary line instead). Never a third phrasing of the same learning.

**Reflect pass (`limo_lint.py reflect <Domain>`).** A scheduled pass that proposes: near-duplicate merges (string similarity ≥ 0.6 across DECISIONS/LEARNINGS/NEVER_AGAIN/INVARIANTS), archival of closed-range entries, and moves of misplaced content (a `Decision:` field in LEARNINGS, a `Prevention gate:` in DECISIONS, a NEVER_AGAIN entry with no gate). It writes **only** to `core/_pending/reflect_<date>.md`. Nothing is applied until a human, or a session given the explicit instruction, edits the source and deletes the proposal file. The same `_pending/` inbox is where propose-only workers (OWNERS.md `propose`) put entries for promotion. Every system in the survey that auto-writes memory either gates it on approval or warns that an unreviewed memory is an invisible system prompt; LIMO gates it.

**Frontmatter.** Every core file carries at its top:
```
description: <one line — what this file is for, when to open it>
modified: YYYY-MM-DD          ← written by whoever writes the file; lint prefers it over "Last updated"
```
`description:` feeds the BOOT_PACK signposts; `modified:` makes freshness checkable without trusting a hand-typed header.

---

### Layer 5: Behavioral Adaptation (learned patterns)

These files are the AI's "muscle memory" for this domain. They're written IN REAL TIME during sessions, not at session end.

#### LEARNINGS.md
**Purpose:** Reusable insights. Things that were learned the hard way.
**Freshness target:** 60 days
**Format:**
```markdown
### L-[DOMAIN]-001 — [Title]
- Context: [What happened]
- Observation: [The insight]
- Why it matters: [What goes wrong if this is forgotten]
- How to reuse: [Practical application for future sessions]
```

**Sections:** Split into "Inherited" (universal, from other domains) and "[Domain]-specific".

"Why it matters" is separate from "Observation" because the insight and its stakes are different things. A successor session needs to know BOTH what was learned AND why forgetting it is costly.

#### NEVER_AGAIN.md
**Purpose:** Hard failure gates. Things that went wrong and must never recur.
**Freshness target:** 180 days
**Format:**
```markdown
### NA-[DOMAIN]-001 — [Title]
- Symptom: [What went wrong]
- Root cause: [Why it happened]
- Prevention gate: [The rule that prevents recurrence]
- Evidence signal: [How to detect you're about to make this mistake again]
- Fix: [What to do instead]
```

#### INVARIANTS.md
**Purpose:** Rules that never break. If a plan conflicts with an invariant, stop and resolve.
**Freshness target:** 30 days
**Format:**
```markdown
## Enforcement rule
If an invariant conflicts with a plan: **stop**, log the conflict, and resolve before proceeding.

## INV-[DOMAIN]-001 — [Rule name]
[Rule description. 1-2 sentences max.]

Default invariants (see file_templates.md for full list): read workspace files before acting,
action over permission, trust corrections immediately, files are source of truth,
milestone-only diary updates, write only to own domain, unreadable input → blocker writeback.
```

---

### Layer 6: People & Relationships (optional, for domains involving people)

#### KEY_PEOPLE.md
**Purpose:** Structured reference for all people relevant to this domain.
**Freshness target:** 30 days
**When to include:** Legal, family, business, any domain where tracking people/roles/relationships matters.
**Format:**
```markdown
## [Group Name] (e.g., "Legal Team", "Family", "Investors")

### [Person Name]
- Role: [Their function]
- Relationship: [To the user]
- Contact: [If relevant]
- Last status: [Most recent known state]
- Notes: [Anything critical]
```

---

### Layer 6b: Architecture (optional, for domains involving a codebase)

#### ARCHITECTURE.md
**Purpose:** System design overview with module-to-file mapping. Gives the AI a mental model of the codebase so it can navigate without exploring blindly.
**Freshness target:** 90 days
**When to include:** Any domain that involves building or maintaining a codebase — software projects, research prototypes, scripts collections.
**Format:**
```markdown
# Architecture — [Domain Name]
Last updated: [DATE]
Freshness target: 90 days

## The Big Picture
[2-3 sentences: what the system does, what the core thesis/approach is, what it is NOT.]

## System Architecture
[High-level diagram using ASCII art or description of layers/services/modules. Show data flow.]

## Core Modules
### [Module 1 Name]
[What it does. Key sub-components if any.]

## Module-to-File Mapping
| Module | File(s) | Status |
|:-------|:--------|:-------|
| [Module 1] | `src/path/to/file.ts` | ✅ Active |
| [Module 2] | `src/path/to/other.ts` | ✅ Active |
| [Module 3] | `legacy/old_file.ts` | ⚠️ Legacy — port to new arch |
| [Module 4] | — | 🔲 Not yet implemented |

## Key Concepts
- **[Concept 1]**: [1-sentence definition]

## Build & Test
- **Build command:** `[command]`
- **Test command:** `[command]`
- **Key config files:** `[tsconfig.json, package.json, etc.]`
```

**Relationship to SESSION_PROMPT:** ARCHITECTURE.md is the structural reference; SESSION_PROMPT is the behavioral reference. SESSION_PROMPT says "how we work here" — ARCHITECTURE.md says "what we built and where things live."

---
### Layer 7: Memory Management

#### SESSION_DIARY.md
**Purpose:** Crash-recovery journal. Milestone-only entries that let a new session reconstruct context fast.
**Freshness target:** 180 days (it's a log, not a living doc)
**Format:**
```markdown
## How to Use This File (for a fresh session)
1. Read START_HERE.md first
2. Read this diary. Current State section at bottom is ground truth.
3. Read OPEN_ITEMS.md and DECISIONS.md
4. You are now caught up.

## Pre-Domain History (if domain was forked from another)
[Key milestones from predecessor sessions]

## Session Log

### Session [ID] — [Date]
**[Timestamp] — [Milestone description]**
[1-3 sentence detail. Decision made, artifact produced, blocker found/removed.]
```

**Rules:**
- Milestone-only. Not stream-of-consciousness.
- All timestamps in UTC.
- Each entry should be meaningful enough that a cold-start session knows whether to care about it.
- When the diary grows large, use MEMORY_COMPRESSION_PROTOCOL to age entries. Don't split into multiple files.

**`[Infra]` transition (v2.4):** at the Infra level SESSION_DIARY.md is a stub and history goes to the Event API
(`event_log` via the `neo4j-events` MCP connector — a raw curl to the webhook returns empty 200s indistinguishable
from silent failure). See `shared/SESSION_DIARY_FORMAT.md` for the stub. Domains not yet migrated keep the full file.

#### CHECKPOINTS.md
**Purpose:** Structured history of meaningful progress — the solution paths taken and the dead ends hit. Unlike SESSION_DIARY (milestone-only narrative), checkpoints capture the *how* and *why* with enough structure that any agent on any platform can reconstruct the reasoning, not just the outcome.

**Relationship to SESSION_DIARY:** SESSION_DIARY is the *what happened* log — terse milestones for quick orientation. CHECKPOINTS.md is the *how it happened* record — structured entries that capture solution paths, failed approaches, and evidence. A new session reads SESSION_DIARY for orientation, then CHECKPOINTS.md for depth when needed.

**Freshness target:** 180 days (it's a log, not a living doc)

**Design-Intent Anchor (CP-[DOMAIN]-000):** When a domain has an existing blueprint, design document, or specification, the FIRST checkpoint must be a design-intent anchor. This records:
- The original design's stated goals and components
- Which components are specified but not yet implemented
- The baseline against which all future work is measured

This is the "four-wheel blueprint" that prevents autorickshaw drift — agents patching around missing components instead of implementing them. Every subsequent checkpoint can be checked against CP-000: "Is this solution implementing from the blueprint, or patching around something the blueprint already specified?"

If no formal design document exists, the anchor still captures the user's stated intent and the agreed-upon approach. Even informal intent is better than no baseline.

**When to write a checkpoint:**
- A meaningful problem was solved (capture the golden path)
- A meaningful attempt failed (capture what was ruled out and why)
- A significant decision was reached after investigation
- A session ends mid-investigation with useful partial findings
- A commit lands that represents a logical unit of progress
- Do NOT checkpoint trivial exchanges or routine status updates

**Entry format:**
```markdown
### CP-[DOMAIN]-[NNN] — [Topic/title]
**Date:** [YYYY-MM-DD HH:MM UTC]
**Agent:** [Which agent produced this: Claude Code / Claude Cowork / Monday (ChatGPT) / Codex / Gemini / Human]
**Session:** [Session ID or "manual" if written by hand]
**Outcome:** [SOLVED | DEAD-END | PARTIAL | PIVOT]
**Class:** [fabrication | scope-drift | tooling | data-quality | judgment | other]   ← added v2.4 (P5); required for DEAD-END


#### Golden Path (what worked)
[If outcome is SOLVED or PARTIAL: the actual steps that produced the result.
Not "we investigated X" — the specific sequence that worked.]

#### Dead-Ends / Abandoned Paths
[What was tried and rejected. For each dead end:]
- **Attempted:** [What was tried]
- **Failed because:** [Specific failure evidence — error messages, test results, logical contradiction]
- **Lesson:** [Why this path is closed — don't retry without new evidence]

#### State + Evidence
[What changed as a result of this checkpoint. Concrete artifacts:]
- Files created/modified: [paths]
- Test results: [pass/fail counts, specific failures]
- Commit: [hash + subject, if applicable]
- Measurements: [metrics, benchmarks, counts — anything quantitative]

#### Tips & Insights
[Non-obvious discoveries. Things a successor session couldn't figure out from reading code alone.]

#### Next Actions
[Concrete follow-up work. Not vague "continue investigating" — specific next steps with enough context to execute.]

#### Key Files
[Files that a successor session should read to pick up this thread.]
- `path/to/file.md` — [why it matters]

<!-- checkpoint-tail: [1-sentence summary of this checkpoint's outcome] -->
```

**The tail marker** (`<!-- checkpoint-tail: ... -->`) lets a recovery session scan the file quickly — grep for `checkpoint-tail` to get a one-line summary of every checkpoint without loading full entries.

**Outcome tags:**
- **SOLVED** — Problem fully resolved. Lead with Golden Path.
- **DEAD-END** — Investigation concluded with no solution. Lead with Dead-Ends (this is the main value).
- **PARTIAL** — Progress made but not complete. Include both Golden Path (what worked so far) and Next Actions.
- **PIVOT** — Direction changed based on findings. Explain what triggered the pivot and the new direction.

**Agent attribution:** Every checkpoint records which agent wrote it. This matters in multi-agent workflows — when Monday flags a dead end, a successor Claude Code session needs to know that judgment came from a different agent with different capabilities and biases. Attribution also enables pattern detection: if one agent consistently produces DEAD-END checkpoints on a particular class of problem, that's a signal to route differently.

**Dead-ends as first-class content:** A failed session's main value is the rejected approaches with specific failure evidence. If a session did not find a solution, the checkpoint should lead with what was ruled out and why — not just note that it failed. Dead ends with good evidence prevent successor sessions from re-walking the same path.

#### MEMORY_COMPRESSION_PROTOCOL.md
**Purpose:** Defines how session diary entries age and compress over time.
**When to include:** Any domain that accumulates significant history (>5 sessions).
**Format:**
```markdown
## Philosophy
Human memory compresses naturally. Raw experiences → key moments → lessons → identity.
LIMO should do the same.

## What survives indefinitely
- Decisions and their reasoning
- Key milestones with dates
- People introduced with roles
- Errors and their fixes

## What compresses (detail → summary)
- Multi-step work sequences → single milestone line
- Exploration that led to decisions → just the decision
- Debugging/troubleshooting → just the fix

## What gets pruned
- Superseded information (old values replaced by new)
- Redundant entries (same milestone noted multiple ways)
- Dead-end explorations ONLY AFTER extracting the failure evidence into LEARNINGS.md or NEVER_AGAIN.md (dead ends without extraction are never pruned — the negative evidence is too valuable)

## Compression procedure
1. Read SESSION_DIARY.md
2. For each entry older than [domain-specific threshold]:
   - Extract decisions → DECISIONS.md (if not already there)
   - Extract insights → LEARNINGS.md
   - Extract failures → NEVER_AGAIN.md
   - Compress the diary entry to milestone-only format
3. Archive the verbose version if needed
```

#### FOLDER_MAP.md
**Purpose:** Directory structure reference showing where everything lives.
**Freshness target:** 30 days
**Format:** Tree structure with file-level descriptions for critical files. Include file counts for large directories.

**Tip:** Organizing the folder map by memory tier (Declarative / Behavioral / Working / Protocol) rather than flat file listing makes it clearer which cognitive layer each file serves.


**Cross-domain dead-end index (added v2.4, P5).** `tools/limo_lint.py deadends` builds `shared/DEAD_END_INDEX.md`:
one row per `Outcome: DEAD-END` checkpoint and per NEVER_AGAIN entry across all domains — domain, agent,
date, class, tail summary, link — sorted by agent then class. This is the mechanism behind the promise
above that attribution "enables pattern detection": if one agent keeps producing dead-ends of one class,
route that class elsewhere (see Worker-class routing under Multi-Agent Operation). Read the index at boot
only when the current task's class has entries.

---

### Advanced Patterns (for mature domains)

These patterns aren't part of the core scaffolding. They emerged from long-running, complex domains and are available when a domain earns the complexity.

**Session Handover:** When a long-running domain session ends or migrates, it can generate a handover document capturing what a successor needs: in-progress state, unwritten context that can't be reconstructed from files alone, mistakes made, and what's next. The format should fit the domain — a simple domain might need a one-page summary, a complex domain might need structured sections with decision trees. The key principle: anything that took multiple sessions to figure out should be written down so the successor doesn't re-derive it.

**Cross-domain Boot Prompts:** If Domain A accumulates significant context relevant to Domain B, it can generate a boot prompt for a new Domain B session. This is rare — most domains operate independently. When it applies, package only what's relevant to the target domain, not everything the source knows.

For detailed templates of both patterns (including a 12-section handover format and an 8-section boot prompt), see `advanced_patterns.md`.


**Director Layer (added v2.4, A6).** *Source: Research-Experiment `limo-populated.AGENTS.md`.*
When an agent puts a decision to the human, page one is plain English: what this is, why now, what is
being decided, what happens on yes and on no, risks, unknowns, cost, next step — ending with a numbered
**"Your turn"** block of the exact actions requested. Dense relay text between seats is fine everywhere
else; *decisions are translated.*


### Inter-Agent Messaging `[Agents]` (for multi-domain ecosystems)

When multiple LIMO domains exist, agents accumulate insights relevant to sibling domains. Currently, cross-domain notes sit in OPEN_ITEMS and wait for the user to relay them. Inter-agent messaging removes the human as copy-paste relay — agents communicate directly through the filesystem.

#### The Problem

Without messaging, cross-domain knowledge transfer looks like this:
1. Research agent discovers oracle separation validates ASENT Embodiment 47
2. Research agent writes a note in OPEN_ITEMS: "Cross-Domain → ASENT session: oracle separation validates Embodiment 47"
3. User reads it, copy-pastes it into the ASENT session
4. ASENT agent processes it

With messaging:
1. Research agent drops a message in `_messages/`
2. ASENT agent boots, checks inbox, processes it, optionally replies
3. User approves important actions but doesn't relay data

#### Architecture

```
CLAUDE-PROJECTS/
├── _messages/                               ← Shared message bus (root level)
│   ├── 2026-02-20_from-Research_to-ASENT_oracle-separation.md
│   ├── 2026-02-20_from-ASENT_to-Research_embodiment47-cite.md
│   ├── 2026-02-21_from-LIMO_to-ALL_compression-update.md
│   └── _processed/                          ← Messages that have been read and acted on
│       └── 2026-02-19_from-LIFE_to-Finance_insurance-update.md
│
├── USER_PROFILE.md                          ← Shared identity (unchanged)
├── Domain-A/
│   └── limo-populated/core/...
└── Domain-B/
    └── limo-populated/core/...
```

The `_messages/` folder lives at the CLAUDE-PROJECTS root — same level as USER_PROFILE.md. It's a shared bus, not per-domain. This is intentional: messages are about cross-domain communication, so they belong to the ecosystem, not to any single domain.

#### Message Format

Each message is a standalone markdown file. The filename encodes routing; the body carries the payload.

**Filename convention:**
```
[DATE]_from-[SOURCE]_to-[TARGET]_[slug].md
```
- DATE: `YYYY-MM-DD`
- SOURCE: Domain name of the sender (e.g., `Research`, `ASENT`, `LIFE`, `Finance`)
- TARGET: Domain name of the recipient, or `ALL` for broadcast
- slug: kebab-case summary (e.g., `oracle-separation`, `insurance-update`)

**Message body:**
```markdown
# Message: [Short title]

| Field       | Value                          |
|:------------|:-------------------------------|
| From        | [Source domain]                |
| To          | [Target domain or ALL]         |
| Date        | [YYYY-MM-DD HH:MM UTC]         |
| Priority    | [routine / important / urgent] |
| In-Reply-To | [filename of original message, if this is a reply] |

## Context
[1-3 sentences: why this message exists, what triggered it]

## Payload
[The actual information, insight, request, or question. Be specific and actionable.]

## Suggested Action
[What the recipient agent should do with this. Optional but helpful.]

## References
- [Links to files, decisions, or evidence that support this message]
```

#### Priority Levels

| Priority | Meaning | Agent behavior |
|:---------|:--------|:---------------|
| **routine** | FYI — useful but not time-sensitive | Process when convenient, no urgency |
| **important** | Affects decisions or planning in the target domain | Process before starting new work |
| **urgent** | Blocks progress or has time-sensitive implications | Surface to user immediately, process first |

#### Agent Behavior: Inbox Processing

When a domain agent boots, after completing the standard LIMO startup sequence (read AI_AGENTS_READ_THIS_FIRST.md, etc.), it should:

1. **Check inbox:** Glob `_messages/` for files matching `*_to-[MY_DOMAIN]_*` and `*_to-ALL_*`
2. **Skip processed:** Ignore anything already in `_messages/_processed/`
3. **Sort by priority:** Urgent → important → routine
4. **Process each message:**
   - Read the payload
   - If actionable: take the suggested action (or determine a better one)
   - If it affects domain files: update the relevant files (DECISIONS, LEARNINGS, OPEN_ITEMS, etc.)
   - If it requires a response: create a reply message
5. **Move to processed:** After handling, move the message to `_messages/_processed/`
6. **Log in SESSION_DIARY:** Note that messages were processed: "Processed [N] inter-agent messages from [domains]"

#### When to Send Messages

Agents should send messages when they encounter information that:
- Validates or challenges a decision in another domain
- Produces evidence relevant to another domain's goals
- Discovers a dependency or conflict between domains
- Learns something that would be a LEARNING or NEVER_AGAIN in another domain
- Completes work that unblocks another domain

Agents should NOT send messages for:
- Routine status updates (that's what STATUS_SNAPSHOT is for — sibling domains can read it)
- Information already captured in USER_PROFILE.md (shared bus handles this)
- Trivial updates that don't change anything in the target domain

#### Broadcast Messages (to-ALL)

Some messages apply to all domains. Examples:
- LIMO framework updates (compression protocol changed, new convention adopted)
- User profile changes that affect multiple domains
- Cross-cutting learnings (e.g., "discovered that Claude's context window handles X better when Y")

Broadcast messages use `to-ALL` in the filename. Every domain agent processes them on next boot.

#### Relationship to Existing Cross-Domain Mechanisms

Inter-agent messaging **complements** existing mechanisms, it doesn't replace them:

| Mechanism | Purpose | Still used? |
|:----------|:--------|:------------|
| USER_PROFILE.md | Shared identity — who the user is | Yes — for identity, not for operational messages |
| OPEN_ITEMS cross-domain section | Noting that work belongs elsewhere | Yes — for task routing. But now the note can also trigger a message |
| Cross-domain boot prompts | Packaging context for a new domain | Yes — for domain creation. Messages are for ongoing communication |
| Sibling domain reading | Agent reads another domain's files | Yes — for background context. Messages are for directed communication |
| **_messages/** | **Directed, actionable, asynchronous communication** | **New** |

#### Safety and User Control

The user remains in control:
- Agents process messages autonomously for routine/important items
- For **urgent** messages or messages that would trigger irreversible actions, the agent surfaces the message to the user and asks for confirmation
- The user can always read `_messages/` directly to see what agents are telling each other
- The user can delete, edit, or add messages manually — it's just markdown files
- Messages are never deleted, only moved to `_processed/` — full audit trail

#### Future Extensions (not yet specified)

These are directions the messaging system could evolve, noted here for future reference:
- **Scheduled polling:** Agent boots on a cron schedule, checks inbox, processes messages, shuts down. No human prompt needed.
- **Message threading:** Replies chain via `In-Reply-To` field, enabling multi-turn agent conversations.
- **MCP bridge:** Messages could be relayed through MCP servers (e.g., mem0, n8n) for agents running in different environments.
- **Priority escalation:** A message that sits unprocessed for N days auto-escalates from routine → important.


---

## Multi-Agent Operation `[Agents]`

*Added v2.4 (A3, A4, A5, A7, P4). Sources: `Research-Experiment/limo-populated/AGENTS.md`;
the Feb 2026 Cowork/Codex ownership design (LIMO build sessions, chapters 02–05); project feedback
`settle_it_in_the_file`, `local_model_harness`; in production use in the Legal and Venture domains.*

Everything in `[Core]` assumes one agent per domain at a time. This section is what changes when two
or more agents — or two seats of the same agent — work the same files.

### Single writer of truth

One agent (in this workspace: the primary agent) **owns** the truth files: STATUS_SNAPSHOT, DECISIONS,
OPEN_ITEMS, SESSION_DIARY, SESSION_PROMPT. Every other agent is a **propose-only worker**: it logs
findings and suggested edits in its own file (`codex_session_diary.md`, `CODEX_TODO.md`) and the
owner promotes what survives review. **Worker output is not truth until promoted.** The reasoning
(the owner, Feb 2026): letting a second agent edit truth files directly is "too easy to drift."

### OWNERS.md — the write manifest

One small file per domain, read at boot, checked by lint. Replaces the hand-maintained
Audience/Owner header block in each file (keep the header if you like; OWNERS.md is authoritative).

```markdown
# Owners — [Domain]
Last updated: YYYY-MM-DD

| file / glob               | owner         | others  |
|:--------------------------|:--------------|:--------|
| STATUS_SNAPSHOT.md        | cowork        | propose |
| DECISIONS.md              | cowork        | propose |
| OPEN_ITEMS.md             | cowork        | propose |
| SESSION_DIARY.md          | primary+owner   | read    |
| [DOMAIN]_SESSION_PROMPT.md| primary+owner   | read    |
| LEARNINGS.md              | shared        | edit    |
| NEVER_AGAIN.md            | shared        | edit    |
| codex_session_diary.md    | codex         | read    |
| CODEX_TODO.md             | codex         | read    |
| ../Documents/**           | owner          | read    |
```

`others` is one of `edit` (anyone may write), `propose` (write to your own diary, owner promotes),
`read` (no writes). Sections inside a file may still be tagged `[SHARED]` / `[CODEX]` for finer grain.
`limo_lint.py` reports OWNERS.md missing, and (where git history exists) writes by a non-owner.

### Seat separation

- Whoever designs a protocol revision cannot review it; whoever implements cannot approve.
- Never name, appoint or invent your own reviewer.
- Disclose inherited context (memory, prior threads) in the record.
- **Reviewed bytes are pinned.** A packet under review is not edited; a correction is built as a separate
  preview and applied only after its checks pass and the record says so.

### Records discipline

- Trackers are updated **as work happens**, not at session end, so a crashed thread resumes from files alone.
- `Last updated` / controlling-checkpoint headers are **replaced** each cycle, never chained into prior-entry
  blocks. Chronology lives in the log, not in headers.
- Codebase domains: committed vs uncommitted state is always stated with the hash; verify which checkout
  you are in by path (`git rev-parse --show-toplevel`), never by content; large regenerable artifacts stay
  out of git — record their SHA-256 in the checkpoint instead.
- **The human drives git.** Agents never run `git commit`, `push`, `reset`, `checkout -- <path>`, `clean`,
  or `worktree remove`; they hand exact commands to the human. Staging is the human's too.

### SETTLED — DO NOT RE-LITIGATE tables

DECISIONS.md holds the *reasoning*. It does not stop a question being re-asked, because the agent
re-asking it is reading the domain file, not DECISIONS.md. So: **the same turn a debate resolves**, write
a `SETTLED — DO NOT RE-LITIGATE` table at the **top of the file where the question will come up again**,
and mark superseded text *where it sits* (`~~old~~ → SUPERSEDED YYYY-MM-DD, see SETTLED`). Stale text
left unmarked gets quoted back months later as if current.

```markdown
## SETTLED — DO NOT RE-LITIGATE
| Question | Settled | Date | Where reasoning lives |
|:---------|:--------|:-----|:----------------------|
| Authorized capital | figure and split as decided | 2026-03-19 | DECISIONS D-VENTURE-004 |
```

BOOT_PACK.md hoists every SETTLED table in the domain to its first section.

### Worker-class routing

- **Scripts own the loop; local or reserve-tier models fill fields.** A local model never self-reports
  what it did — the harness records it. (A 2026 cull run where local models "fabricated everything" is the
  evidence.)
- Mechanical work — board reruns, digests, checkpoint regeneration, pre-commit verification — goes to a
  subagent or a script, never the main thread of a quota-priced seat.
- Design, correction text and adjudication wait for the advanced model. If the picker shows a reserve
  model, do mechanical work only.
- **Batch.** Given a task list, work the whole list before reporting. Do not end a turn to ask
  "continue?" when the mandate already says to continue.
- Every resume begins with the lane README / checkpoint, never with chat memory; state what was verified
  and what was not.
- Use `shared/DEAD_END_INDEX.md` to decide routing: an agent with repeated DEAD-ENDs of one class does not
  get that class again without a reason written down.

### AGENTS.md — generated at `limo-populated/` (v2.5)

`limo_lint.py agentsmd` writes `{Domain}/limo-populated/AGENTS.md` from BOOT_PACK Part A plus OWNERS.md and the
fences above, so Codex, Copilot, Cursor, Gemini and Jules boot from the same text without knowing LIMO exists
(the AGENTS.md standard: nearest file wins, 60k+ repositories). It is generated — do not edit; change the source
files. A hand-written `AGENTS.md` at the *domain root* (the Research experiment pattern with seat-specific fences) still
takes precedence for agents working there; keep it to boot order, fences, records discipline, quota routing and
the Director Layer.

---

## Git as Write-Ahead Log `[Git]`

*Added v2.5 (M7). Sources: Letta MemFS (every memory edit is a commit; subagents in isolated worktrees merged by git), Beads hash IDs. Owner: "Git was an idea I always had. The issue was the stale locks."*

**What it is.** Each domain's `limo-populated/` is a git repository holding memory only — never code. Every
core-file write-back ends with a commit, made by the tool: `limo_lint.py commit <Domain> --agent <name> --trigger "<what fired>"`.
The message is `<Domain>: <files> — <trigger> — <agent> — <time>`. `git log -p core/DECISIONS.md` replaces `_archive/`
copies; `git blame` answers "which session changed INV-VENTURE-008 and what did it say before."

**The fence, made mechanical.** "The human drives git" holds for code and for the human-driven records repositories.
Agent commits are allowed only where a `.limo-memory-repo` marker file exists at the repository root. `git-init`
creates the marker; a human creates it by hand to opt an existing repository in. Without the marker `commit`
refuses and prints what to do. `commit` also stages only `core/` and never touches generated files.

**Which repository.** `limo_lint.py git-init <Domain>` decides: (a) `limo-populated/` already a repo → enable
with the marker only if a human says so; (b) core/ inside an enclosing repo that *ignores* `limo-populated/`
(the Venture pattern) → create a nested memory repo, safe; (c) core/ *tracked* by an enclosing repo (ASENT,
Legal, Finance, Research records) → refuse, because a nested repo would hide memory from that repository —
the human adds the marker at that root if they want agent commits there; (d) no repo → create one.

**Stale locks (the actual blocker).** A commit from the Cowork sandbox leaves `HEAD.lock` / `index.lock` behind
when the mount does not permit deletion, and every later git call fails on them. The tool: probes whether it can
unlink inside `.git/` and refuses to run git at all if not ("commit from the Mac or Codex, or grant delete
permission"); removes any `*.lock` older than 120 s with no `git` process running; retries three times; and
sweeps locks it left after its own commit. `GIT_OPTIONAL_LOCKS=0`, `core.fsmonitor=false`, `core.filemode=false`
are set on every call. Worktree `.git` files that point at Mac paths (`/Users/…`) are remapped onto the mount so
the sandbox can resolve them. **Verified 2026-09-15:** an unintended commit on the Research-Experiment records worktree from
the sandbox left `HEAD.lock` and `next-index-100.lock`; both were cleared and the commit reverted with `reset --mixed`
once delete permission was granted — that incident is why the marker rule and the unlink probe exist.

**Concurrency.** Two agents on one domain work in separate worktrees (`git worktree add`), each committing its own
lane; conflicts surface as merge conflicts, not silent overwrites. Nothing is pushed anywhere unless a human does it.

**State on 2026-09-15.** Memory repos initialised (marker present, agent commits enabled): 3d printing, Health,
INVEST, LIFE, Photography, Contracts, n8n, Automation, Venture (nested; the Venture code repo ignores `limo-populated/`).
Human-driven, no marker: ASENT, Legal, Finance (memory tracked in the domain repo), Research and Research-Experiment (records
repo + worktree, "The human drives git").

---

## Infrastructure Integration `[Infra]`

*Added v2.4 (A1, A2, A8); corrected v2.5 against the live-stack record. Sources of truth, in order: `infra/SERVICE_CATALOG.md`
(container list, gotchas, dated changes), `infra/MEMORY_ARCHITECTURE.md` (the routing rule), `infra/EC2_DETAILS.md` (endpoints, keys — never
copied into this file), `shared/SESSION_BOOT_PROTOCOL.md`, `shared/MEMORY_CLASSES.md`, `shared/SYNC_AND_WRITE_BOUNDARIES.md`.
This section describes the database tier as documented on 2026-06-16 and later; it was **not** verified against the running box on 2026-09-15
(the sandbox cannot reach port 22, and the `neo4j-events` MCP connector did not connect) — see `limo_lint.py infra`.*

LIMO is the architecture diagram; `shared/SESSION_BOOT_PROTOCOL.md` is the deployment guide; `infra/MEMORY_ARCHITECTURE.md` is the
routing rule for where a fact goes:

| Layer (MEMORY_ARCHITECTURE) | Store | Holds | LIMO files it replaces or complements |
|:--|:--|:--|:--|
| **Nouns** | Neo4j `Person` / `Property` nodes (curated writes) | stable entities and typed relationships | USER_PROFILE, KEY_PEOPLE |
| **Verbs** | Neo4j `Event` / `Measurement` nodes via the Events API (`event_log` / `event_query` over the `neo4j-events` MCP) | timestamped happenings, causal and sequenced | SESSION_DIARY (flat file becomes a stub) |
| **Vibes** | mem0 → pgvector `public.memories` (+ `memories_entities` for ranking) | fuzzy, narrative, preference facts | GOALS content, cross-domain insight |

**Rule of thumb:** a thing that *exists* → Neo4j noun; a thing that *happened* → Events API; a thing that is *true-ish and fuzzy* → mem0.
Curated governance (INVARIANTS, DECISIONS, NEVER_AGAIN, LEARNINGS, OPEN_ITEMS, STATUS_SNAPSHOT, SESSION_PROMPT) stays flat and in
context at every level.

**The stack as recorded (SERVICE_CATALOG, 2026-06-16 update):** n8n 2.25.7 (custom image with Python), `pgvector/pgvector:pg17`,
`neo4j:5` (floating minor), `qdrant/qdrant`, `redis:8`, MinIO, ntfy, SearXNG, and **mem0-api as a custom build of mem0ai 2.0.6**
(upgraded from 1.0.0b0). Two facts about that upgrade matter for LIMO: (1) **mem0 2.x has no graph backend** — it does not read or
write Neo4j; entity linking (spaCy) is a recall-ranking boost only. Any older note saying "mem0 auto-extracts entities into Neo4j"
describes the 1.x setup and is stale. (2) mem0 2.x `search()` / `get_all()` take entity ids via `filters={…}`; the external REST contract
(`/search`, `/memories`) was kept stable by a patch in `main.py`, so LIMO's SERVICES_GUIDE calls still work.

**Graphiti (optional, `[Infra]`).** If bi-temporal facts on the existing Neo4j are wanted — `valid_from` / `valid_to` on graph edges with
invalidate-not-delete, the engine half of the v2.5 line-tag convention — Graphiti (getzep) runs against Neo4j 5.26+ and is maintained.
It is an addition beside the Events API, not a replacement for anything running.

| LIMO concept | `[Core]` implementation | `[Infra]` implementation |
|:-------------|:------------------------|:-------------------------|
| Declarative memory | SESSION_PROMPT + SESSION_DIARY | SESSION_PROMPT + Events API |
| Behavioral memory | LEARNINGS + NEVER_AGAIN + INVARIANTS | unchanged — still flat, always in context |
| Episodic memory | raw transcripts + grep | Events API (verbs) + mem0 (vibes) |
| Identity / people | USER_PROFILE + KEY_PEOPLE | Neo4j nouns (Person / Property), flat files as the human-readable view |
| Working memory | STATUS_SNAPSHOT + OPEN_ITEMS | flat files + Postgres control plane (leases, retries, Agent Bus state) |
| Write-back triggers | all to flat files | governance → flat files; history → Events API; insight → mem0; nouns → deliberate graph write |
| Freshness guards | flat files | flat files (Events API handles its own currency) |
| Inter-agent messaging | `_messages/` | `_messages/` (D-LIMO-2026-09-15-01); Agent Bus is an optional transport |
| Node trust | n/a | Mac + EC2 are canonical-trusted file-layer nodes; office is a scoped worker with no full raw sync |

**Events API (A8):** use the `neo4j-events` MCP connector (`event_log`, then `event_query` to read back). A raw curl to the webhook returns
an empty 200 on failure as well as success. The patch endpoint takes `"updates"`, not `"patches"`. Endpoints and keys live in
`infra/EC2_DETAILS.md` / `infra/SERVICE_CATALOG.md` — never hardcode them from memory, never copy them into LIMO files.

**Drift to watch.** `shared/SESSION_BOOT_PROTOCOL.md` (2026-03-01) still says mem0 "replaces STATUS_SNAPSHOT + GOALS" and describes the
1.x graph behaviour; `LIMO/MY_SETUP.md` (2026-02-22) says mem0 "auto-extracts entities into Neo4j". Both predate the June upgrade.
`limo_lint.py infra` reports (a) which domains still carry a full SESSION_DIARY versus a stub, (b) the age of the boot protocol and
MY_SETUP relative to the catalog's last dated change, and (c) endpoint reachability when run with `--probe` from a machine that can reach the box.

---

## Write-Back Triggers (The Feedback Loop) `[Core]`

This is the behavioral adaptation loop. These updates happen IMMEDIATELY when the trigger fires — not at session end.

| File | Trigger | Action |
|:-----|:--------|:-------|
| `STATUS_SNAPSHOT.md` | Finish a sub-task or change focus | Update current phase, what's done, what's next |
| `DECISIONS.md` | Make a choice that rules out alternatives | Append with rationale + revisit triggers |
| `OPEN_ITEMS.md` | Discover new work or complete an item | Add/check off. Keep valid. |
| `LEARNINGS.md` | User corrects you, or a reusable insight emerges | Record immediately with "How to reuse" |
| `NEVER_AGAIN.md` | Avoidable failure occurs | Record with prevention gate + evidence signal |
| `SESSION_DIARY.md` | Meaningful milestone reached | One-line entry with timestamp |
| `CHECKPOINTS.md` | Problem solved, dead end hit, significant investigation completed, or session ends mid-work | Structured entry with golden path, dead-ends, evidence, tail marker |
| `INVARIANTS.md` | A new rule emerges that should never be broken | Append with enforcement |
| `KEY_PEOPLE.md` | New person introduced or status changes | Update or add entry |
| `ARCHITECTURE.md` | Module added/removed, file mapping changes, build config changes | Update module table and mapping |
| `USER_PROFILE.md` | Something changes the cross-domain story of who the user is | Update with session attribution |
| `_messages/` | Discover insight, evidence, or dependency relevant to a sibling domain | Drop a message file with appropriate priority |
| **SETTLED table** (v2.4) | A debated question resolves | Same turn: table at top of the file where it will be re-asked + mark superseded text in place + DECISIONS entry |
| **OWNERS.md** (v2.4, `[Agents]`) | A new agent or seat joins, or a file changes hands | Update the manifest before the new writer's first session |
| **Event API** (v2.4, `[Infra]`) | Milestone, deployment, discovery, blocker opened/resolved | `event_log` via MCP; blockers also go to OPEN_ITEMS |
| **BOOT_PACK.md** (v2.4) | Any of the above | Regenerate (`limo_lint.py bootpack`) — never edit by hand |
| **Compaction imminent / long step ahead** (v2.5, M5) | Context is about to be summarised, or ≥ N tool calls since the last write-back | Flush STATUS next-3 + blockers + one diary line, regenerate BOOT_PACK, commit |
| **Session end** (v2.5, M5) | Any session ends, cleanly or not | Same flush; hooks run it where available |
| **Collection append** (v2.5, M4) | Adding to DECISIONS / LEARNINGS / NEVER_AGAIN / INVARIANTS | Reconcile first: ADD / UPDATE (close old range + `supersedes:`) / NOOP |
| **Git commit** (v2.5, M7, `[Git]`) | Any core-file write-back above | `limo_lint.py commit <Domain> --agent <me> --trigger "<row name>"` |

**CRITICAL:** The write-back loop is what makes LIMO a living system. Without it, files go stale and the next session starts from outdated context.

---

## Freshness Guards `[Core]`

Every file has a freshness target. If a file's "Last updated" is older than its freshness target:
- Treat it as **hypothesis, not truth**
- Prefer regenerating from primary sources over trusting stale content
- Flag to the user: "This file is [X days] past its freshness target"

| File | Freshness target | Rationale |
|:-----|:----------------|:----------|
| STATUS_SNAPSHOT | 7 days | State changes fast |
| OPEN_ITEMS | 7 days | Tasks change fast |
| GOALS | 14 days | Objectives shift less frequently |
| SESSION_PROMPT | 14 days | Domain context changes moderately |
| INVARIANTS | 30 days | Rules change rarely |
| FOLDER_MAP | 30 days | Structure changes rarely |
| KEY_PEOPLE | 30 days | People change moderately |
| ARCHITECTURE | 90 days | System design changes slowly |
| START_HERE / AI_AGENTS_READ_FIRST | 30 days | Bootstrap changes rarely |
| LEARNINGS | 60 days | Insights accumulate slowly |
| BRAIN_TRANSFER | 60 days | Behavioral patterns are stable |
| BOOT_PROMPT | 90 days | Identity is stable |
| DECISIONS | 90 days | Decisions are durable |
| SESSION_DIARY | 180 days | It's a log |
| CHECKPOINTS | 180 days | It's a structured log |
| NEVER_AGAIN | 180 days | Failure gates are permanent |
| MEMORY_COMPRESSION | 180 days | Protocol changes rarely |
| OWNERS (v2.4) | 90 days | Write authority changes rarely |
| BOOT_PACK (v2.4) | regenerate at boot | Generated; stale = older than STATUS_SNAPSHOT |
| LIMO_FRAMEWORK.md itself (v2.4) | 180 days | The spec drifts from production; re-verify `Source:` lines |

**Enforcement (added v2.4, P1).** Freshness was a rule on the honour system; LIFE's core files were four
months stale and still described a resolved crisis, and nobody noticed because nobody ran the check.
`tools/limo_lint.py lint` walks every domain and prints the table of stale files, overdue open items,
broken cross-references, untraced numbers, oversized diaries, checkpoints without tail markers, and
missing OWNERS.md. Run it at boot (it is the last line of BOOT_PACK Part A) and on a schedule. Lint does not
fix anything; it makes the guard fire.

**Cross-artifact checks (v2.5, M8).** *Sources: spec-kit `/analyze` and `/converge`, Claude Code `/doctor`, Letta `/doctor`.* Lint also checks
what no single file can show: (a) **cross-ref** — every `D-`, `OI-`, `NA-`, `INV-`, `CP-`, `L-` ID mentioned anywhere in core is defined somewhere
in core (heading, list row or table row; struck-through counts); (b) **coherence** — each GOALS `[NEXT]` milestone is named in STATUS next-3 or
an active OPEN_ITEM; (c) **derivable** — ARCHITECTURE.md module paths that no longer exist on disk; (d) **line tags** — duplicate open entries,
dangling `supersedes:`, stale opinions; (e) **stalls** — claimed or started items with no diary or checkpoint mention after 7 days; (f) **pending** —
proposals sitting in `_pending/`. All WARN or INFO; nothing is auto-fixed.

---

## Tooling `[Core]`

*Added v2.4 (P1, P2, P5); extended v2.5 (M1–M8).* One script, standard library only, at `CLAUDE-PROJECTS/tools/limo_lint.py`, plus hook scripts in `tools/hooks/`.

| Command | Does | Writes | Level |
|:--------|:-----|:-------|:------|
| `lint [Domain …] [--full]` | Freshness (`modified:` > header > mtime), overdue and stalled open items, dangling bootstrap references, diary size, checkpoint tails and Class, untraced numbers, line tags, cross-refs, coherence, derivable paths, pending proposals, spec citations | stdout; exit 1 on OVERDUE/STALE/WARN | Core |
| `bootpack [Domain …]` | Part A (≤ 60 lines) + signpost index; exit 1 when over budget | `core/BOOT_PACK.md`, `core/TRIGGER_INDEX.md` via `all` | Core |
| `triggers "<request>" Domain` | Prints every NEVER_AGAIN / INVARIANT whose `Triggers:` match the request | stdout | Core |
| `ready Domain [--agent me]` | Open items with no open blockers, unclaimed or mine; blocked and taken listed separately | stdout | Agents |
| `reflect Domain` | Proposes merges, archives, moves for collection files | `core/_pending/reflect_<date>.md` only | Core |
| `deadends` | Cross-domain dead-end index | `shared/DEAD_END_INDEX.md` | Core |
| `agentsmd [Domain …]` | Portable orientation file from BOOT_PACK Part A + OWNERS.md | `limo-populated/AGENTS.md` | Core |
| `commit Domain --agent me --trigger "…"` | Commits `core/` only, in a marker-enabled memory repo, with stale-lock recovery | git history | Git |
| `git-init Domain` | Creates a nested memory repo where safe; refuses where memory is tracked by a human-driven repo | `limo-populated/.git`, `.gitignore`, `.limo-memory-repo` | Git |
| `infra [--probe]` | Diary migration state per domain, documentation drift vs `infra/SERVICE_CATALOG.md`, stale claims, optional endpoint reachability (no keys) | stdout | Infra |
| `all [Domain …]` | lint + bootpack + trigger index + deadends + agentsmd | the generated files above | Core |

Run from the workspace root. Runbook: `infra/runbooks/limo-lint.md`. Hooks (`tools/hooks/`): `limo-user-prompt.sh` runs `triggers` on every prompt
and injects hits; `limo-pre-compact.sh` prints the flush reminder and regenerates the pack; `limo-session-end.sh` regenerates the pack and commits.
Wire them in `.claude/settings.json` (snippet in `tools/hooks/README.md`).

---

## Domain Forking `[Core]`

When a domain grows too large or a subdomain needs its own session:

1. **Copy the LIMO core/** skeleton into the new domain folder
2. **Rewrite domain-specific files** (SESSION_PROMPT, GOALS, STATUS_SNAPSHOT, OPEN_ITEMS)
3. **Inherit behavioral files** (LEARNINGS, NEVER_AGAIN — mark inherited items)
4. **Archive originals** in `core/_archive/`
5. **Add cross-domain pointers** in both the parent and child domains
6. **Update FOLDER_MAP** in both domains

The new domain starts with the parent's behavioral knowledge but builds its own working memory from scratch. For complex domains with significant accumulated context, consider generating a session handover and/or cross-domain boot prompt (see Advanced Patterns).

---

## Anti-Patterns `[Core]`

These are things that break LIMO:

1. **Waiting until session end to update files.** The write-back loop must fire immediately. If the session crashes, updates are lost.
2. **Trusting inherited values without source verification.** Values drift through summaries. Always trace medical data, financial figures, dates to source documents.
3. **Loading entire episodic memory.** SESSION_DIARY and transcripts can be 100K+. Grep for what you need, don't load whole files.
4. **Re-litigating decisions.** If it's in DECISIONS.md with rationale and revisit triggers, don't reopen unless a trigger has fired.
5. **Writing stream-of-consciousness diary entries.** Milestones only. "Explored X, tried Y, found Z, decided W" → "Decided W because Z."
6. **Mixing domains.** If it belongs in another session, note it and redirect. Don't solve it here.
7. **Over-apologizing when corrected.** "Got it" + fix + move on. One sentence max.
8. **Asking permission to work.** Action over permission. If genuinely ambiguous between very different approaches, state which and why — don't ask.
9. **Mutating persistent files without explicit instruction.** Do not write to LIMO core files (DECISIONS, LEARNINGS, CHECKPOINTS, etc.) unless the user issues an explicit action command or a write-back trigger fires. Phrases like "LGTM", "sounds good", or "makes sense" are acknowledgments, not write permission.
10. **Pruning dead ends without extraction.** Dead-end explorations contain valuable negative evidence. Before compressing or removing them from CHECKPOINTS.md, extract the lesson into LEARNINGS.md or NEVER_AGAIN.md. A dead end with specific failure evidence is more valuable than a success without explanation.
11. **Unfocused repo exploration.** Don't survey an entire codebase when you need one file. Follow the exploration tier protocol: check orientation docs first, then root structure, then targeted dive, then broad survey only if sustained work requires it.
12. **Quoting a summary as a source.** A number in STATUS_SNAPSHOT or SESSION_PROMPT is a summary. Open the document in `Documents/` (the `[src:]` tag says which) and state its date. (v2.4)
13. **Hand-editing generated files.** BOOT_PACK.md and DEAD_END_INDEX.md are rebuilt by script; edits are lost on the next run and, worse, look authoritative until then. Fix the source file. (v2.4)
14. **Chaining headers.** Appending a new `Last updated` block under the old one turns a header into a log. Replace it; the log is SESSION_DIARY / Event API. (v2.4)
15. **Worker self-reporting.** A propose-only or local-model worker claiming "done" is a claim, not a record. The harness or the owning agent records what happened. (v2.4)
16. **Pushing the whole domain at boot.** Part A is 60 lines for a reason; if it needs more, the SETTLED tables or STATUS are too long, not the budget. (v2.5)
17. **Deleting a superseded line.** Close its `valid` range and point the successor at it. The benchmark leaders keep raw text; so does LIMO. (v2.5)
18. **Running git from an environment that cannot unlink lock files.** The tool refuses; do not work around it — commit from the Mac or Codex. (v2.5)
19. **Applying a reflect proposal without reading the source.** `_pending/` is an inbox, not an instruction. (v2.5)

---

## A9 Decisions (settled 2026-09-15)

*The spec had been deferring these two questions. the owner delegated the call to the drafting session's recommendation on 2026-09-15; recorded here so "future" stops being a decision by default. Revisit triggers are listed.*

### D-LIMO-2026-09-15-01 — `_messages/` is the permanent `[Agents]`-level message bus
- **Decision:** Flat-file `_messages/` per `shared/MESSAGE_BUS_CONVENTION.md` is the design, not a stopgap. Agent Bus is an optional `[Infra]` *transport* that may carry the same message bodies; it does not replace the folder.
- **Why:** Six months in production without a failure that the Bus would have fixed. Human-readable, greppable, audit trail by construction, works for any agent with file access — the same properties that justify LIMO itself. The Bus adds status tracking and queuing, which no domain has needed.
- **Alternatives rejected:** Migrate now (no driver); set a date (dates without drivers are the pattern this section exists to end).
- **Revisit triggers:** a cron-driven agent polls inboxes with no human in the loop; more than two domains need message threading or ack tracking in the same quarter; a message is lost or double-processed.

### D-LIMO-2026-09-15-02 — Spec verification is split: paths by lint, meaning by a human
- **Decision:** `limo_lint.py lint` checks that every path cited in a `Source:` line or backtick reference in this file exists. Whether the cited file still *says* what the spec claims is a human (or human-directed session) pass, due every 180 days or whenever lint reports a missing path, and recorded by updating `Last verified against production`.
- **Why:** Existence is mechanical and cheap; meaning is judgment. Automating the judgment half would produce a false sense of verification.
- **Revisit triggers:** the spec exceeds ~1,500 lines; a verification pass finds more than three stale `Source:` claims (then the cadence is too long).

---

## Version History

- **v2.5 (2026-09-15)** — field adaptations: pull-based boot pack, trigger injection, line validity and supersession, reconcile/reflect with `_pending/`, interruption hooks, ready/claim/stall, git write-ahead log (`[Git]` level), cross-artifact lint, generated AGENTS.md, `description:`/`modified:` frontmatter, `infra` check.
- **v2.4 (2026-09-15)** — production reconciliation: hybrid boot, memory classes, multi-agent ownership (OWNERS.md), SETTLED tables, records discipline, Director Layer, conformance levels, `limo_lint.py`, BOOT_PACK, source tags, dead-end index.
- **v2.3** — checkpoint protocol, deterministic recovery, mutation gating, exploration tiers.
- **v2.2** — inter-agent messaging bus, file versioning for read-only environments, organic growth signals.
- **v2.1 and earlier** — the core file set, write-back triggers, freshness guards, KEY_PEOPLE, memory compression, ARCHITECTURE.md, developed across five production domains.
