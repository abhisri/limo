# LIMO — LLM Interaction Memory OS

**Version:** 2.1 (Synthesized from four domain implementations; trimmed for generality)
**Author:** Abhishek Srivastava
**Last updated:** 2026-02-18

---

## What LIMO Is

LIMO is a filesystem-based persistent memory architecture for AI sessions. It solves the fundamental problem of LLM context windows: every new conversation starts from zero. LIMO gives each domain its own structured memory that survives across sessions, prevents repeated mistakes, and enables behavioral adaptation over time.

The name maps to how it works: just as a limousine carries passengers across destinations without them having to re-explain where they're going, LIMO carries context across sessions without the AI having to re-learn who you are and what you've decided.

---

## 4-Tier Memory Model

LIMO mirrors how human memory works:

| Tier | Human analogy | LIMO equivalent | Persistence |
|:-----|:-------------|:----------------|:------------|
| **Procedural** | Muscle memory, how-to | Model weights (not file-stored) | Permanent (built into model) |
| **Declarative** | Facts, identity, what happened | BOOT_PROMPT + SESSION_PROMPT + SESSION_DIARY | Updated per session |
| **Behavioral** | Learned preferences, instincts | BRAIN_TRANSFER + LEARNINGS + NEVER_AGAIN | Updated in real time |
| **Episodic** | Specific memories on demand | Raw transcripts (grepped, not loaded whole) | Append-only archive |

**Key insight:** Tiers 2 and 3 are the active memory. Tier 4 is recall — expensive to load, used only when deep context is needed. Tier 1 is the model itself.

---

## Architecture: System Bus

```
CLAUDE-PROJECTS/                          ← Root
├── USER_PROFILE.md                       ← Shared identity (all sessions read + write)
├── CLAUDE_BOOT_PROMPT.md                 ← Shared: who is this AI, working style
├── CLAUDE_BRAIN_TRANSFER.md              ← Shared: communication patterns, corrections
│
├── Domain-A/                             ← e.g., Finance, LIFE, Legal
│   └── limo-populated/
│       └── core/
│           ├── AI_AGENTS_READ_THIS_FIRST.md
│           ├── START_HERE.md
│           ├── [DOMAIN]_SESSION_PROMPT.md
│           ├── STATUS_SNAPSHOT.md
│           ├── GOALS.md
│           ├── OPEN_ITEMS.md
│           ├── DECISIONS.md
│           ├── INVARIANTS.md
│           ├── LEARNINGS.md
│           ├── NEVER_AGAIN.md
│           ├── KEY_PEOPLE.md             ← If domain involves people/relationships
│           ├── CONTEXT_RESTORE_PROTOCOL.md
│           ├── MEMORY_COMPRESSION_PROTOCOL.md
│           ├── FOLDER_MAP.md
│           ├── SESSION_DIARY.md          ← Session milestones (compress when large)
│           └── _archive/                 ← Old versions of core files
│
├── Domain-B/
│   └── limo-populated/core/...
│
└── Domain-C/
    └── limo-populated/core/...
```

**Domain boundary rules:**
- Each session WRITES only to its own domain folder
- Each session READS from sibling domains (cross-pollination)
- Shared files at root are read+write for all sessions
- Cross-domain items are noted and redirected to the appropriate session

---

## File Specifications

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
1. `CLAUDE_BOOT_PROMPT.md` — who the user is
2. `[DOMAIN]_SESSION_PROMPT.md` — domain context, current state
3. `CLAUDE_BRAIN_TRANSFER.md` — communication style, corrections log
4. `STATUS_SNAPSHOT.md` — what's happening NOW
5. `GOALS.md` — objectives and milestones
6. `OPEN_ITEMS.md` — what needs doing
7. `DECISIONS.md` — what's been decided (don't re-litigate)
8. `INVARIANTS.md` — rules that never break

## Three Rules
1. Write LEARNINGS.md and NEVER_AGAIN.md IN REAL TIME when corrections happen
2. Action over permission — do the work, don't ask if you should
3. Trust files over chat — if files and conversation conflict, files win

## Episodic recall
For deep history, grep SESSION_DIARY.md or raw transcripts. Don't load whole files.
```

#### START_HERE.md
**Purpose:** Richer orientation with architecture context, cross-domain reading rules, and the 4-tier memory model explanation.
**Freshness target:** 30 days

#### CONTEXT_RESTORE_PROTOCOL.md
**Purpose:** Deterministic startup checklist + write-back trigger table + freshness guard.
**Format:**
- **Startup Checklist** — Strict phase order (Identity → Behavioral → Working Memory → Begin Work)
- **Write-Back Triggers** — Table mapping: File | Trigger event | Action to take
- **Freshness Guard** — If a file's "Last updated" is older than its freshness target, treat as hypothesis
- **Domain Boundaries** — Write to own folder only, read from siblings
- **Episodic Memory** — How to access deep history (grep, not load)
- **Large File Handling** — If any file is too large to load: read last 200 lines first, or grep for keywords. Don't try to load whole files.

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

---

### Layer 4: Working Memory (what's happening NOW)

#### STATUS_SNAPSHOT.md
**Purpose:** Current state in 30 seconds of reading.
**Freshness target:** 7 days (during active work)
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
- Dead-end explorations that led nowhere
- Superseded information (old values replaced by new)
- Redundant entries (same milestone noted multiple ways)

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

---

### Advanced Patterns (for mature domains)

These patterns aren't part of the core scaffolding. They emerged from long-running, complex domains and are available when a domain earns the complexity.

**Session Handover:** When a long-running domain session ends or migrates, it can generate a handover document capturing what a successor needs: in-progress state, unwritten context that can't be reconstructed from files alone, mistakes made, and what's next. The format should fit the domain — a simple domain might need a one-page summary, a complex domain might need structured sections with decision trees. The key principle: anything that took multiple sessions to figure out should be written down so the successor doesn't re-derive it.

**Cross-domain Boot Prompts:** If Domain A accumulates significant context relevant to Domain B, it can generate a boot prompt for a new Domain B session. This is rare — most domains operate independently. When it applies, package only what's relevant to the target domain, not everything the source knows.

For detailed templates of both patterns (including a 12-section handover format and an 8-section boot prompt), see `references/advanced_patterns.md`.

---

## Write-Back Triggers (The Feedback Loop)

This is the behavioral adaptation loop. These updates happen IMMEDIATELY when the trigger fires — not at session end.

| File | Trigger | Action |
|:-----|:--------|:-------|
| `STATUS_SNAPSHOT.md` | Finish a sub-task or change focus | Update current phase, what's done, what's next |
| `DECISIONS.md` | Make a choice that rules out alternatives | Append with rationale + revisit triggers |
| `OPEN_ITEMS.md` | Discover new work or complete an item | Add/check off. Keep valid. |
| `LEARNINGS.md` | User corrects you, or a reusable insight emerges | Record immediately with "How to reuse" |
| `NEVER_AGAIN.md` | Avoidable failure occurs | Record with prevention gate + evidence signal |
| `SESSION_DIARY.md` | Meaningful milestone reached | One-line entry with timestamp |
| `INVARIANTS.md` | A new rule emerges that should never be broken | Append with enforcement |
| `KEY_PEOPLE.md` | New person introduced or status changes | Update or add entry |
| `USER_PROFILE.md` | Something changes the cross-domain story of who the user is | Update with session attribution |

**CRITICAL:** The write-back loop is what makes LIMO a living system. Without it, files go stale and the next session starts from outdated context.

---

## Freshness Guards

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
| START_HERE / AI_AGENTS_READ_FIRST | 30 days | Bootstrap changes rarely |
| LEARNINGS | 60 days | Insights accumulate slowly |
| BRAIN_TRANSFER | 60 days | Behavioral patterns are stable |
| BOOT_PROMPT | 90 days | Identity is stable |
| DECISIONS | 90 days | Decisions are durable |
| SESSION_DIARY | 180 days | It's a log |
| NEVER_AGAIN | 180 days | Failure gates are permanent |
| MEMORY_COMPRESSION | 180 days | Protocol changes rarely |

---

## Domain Forking

When a domain grows too large or a subdomain needs its own session:

1. **Copy the LIMO core/** skeleton into the new domain folder
2. **Rewrite domain-specific files** (SESSION_PROMPT, GOALS, STATUS_SNAPSHOT, OPEN_ITEMS)
3. **Inherit behavioral files** (LEARNINGS, NEVER_AGAIN — mark inherited items)
4. **Archive originals** in `core/_archive/`
5. **Add cross-domain pointers** in both the parent and child domains
6. **Update FOLDER_MAP** in both domains

The new domain starts with the parent's behavioral knowledge but builds its own working memory from scratch. For complex domains with significant accumulated context, consider generating a session handover and/or cross-domain boot prompt (see Advanced Patterns).

---

## Anti-Patterns

These are things that break LIMO:

1. **Waiting until session end to update files.** The write-back loop must fire immediately. If the session crashes, updates are lost.
2. **Trusting inherited values without source verification.** Values drift through summaries. Always trace medical data, financial figures, dates to source documents.
3. **Loading entire episodic memory.** SESSION_DIARY and transcripts can be 100K+. Grep for what you need, don't load whole files.
4. **Re-litigating decisions.** If it's in DECISIONS.md with rationale and revisit triggers, don't reopen unless a trigger has fired.
5. **Writing stream-of-consciousness diary entries.** Milestones only. "Explored X, tried Y, found Z, decided W" → "Decided W because Z."
6. **Mixing domains.** If it belongs in another session, note it and redirect. Don't solve it here.
7. **Over-apologizing when corrected.** "Got it" + fix + move on. One sentence max.
8. **Asking permission to work.** Action over permission. If genuinely ambiguous between very different approaches, state which and why — don't ask.

---

## Evolution Notes

LIMO evolved across four implementations:

**Photography (v1):** Established core structure — 12 files, phased boot sequence, write-back triggers, freshness guards. Sequential IDs (OI-P001).

**LIFE (v2):** Added North Star + Constraints to GOALS. Added "Alternatives rejected" and "Origin" to DECISIONS. Added "How to reuse" and "Severity" to LEARNINGS. Structured NEVER_AGAIN with Symptom → Root cause → Prevention gate → Evidence signal → Fix. Added Cross-Domain section to OPEN_ITEMS. Richer STATUS_SNAPSHOT with Blockers and Risks.

**Divorce/Legal (v3):** Added KEY_PEOPLE.md (structured people reference). Added MEMORY_COMPRESSION_PROTOCOL.md (memory aging). Streamlined bootstrap (numbered list, no phases). Date-stamped IDs (`D-L-20260215-01`). Explicit 4-tier memory model. File-level FOLDER_MAP. `_inbox/` staging area. Parking Lot in OPEN_ITEMS. Latest artifacts in STATUS_SNAPSHOT. Pre-domain history section in SESSION_DIARY. Episodic recall via grep.

**Finance (v4):** The most mature implementation. Introduced Evidence field in DECISIONS, "Why it matters" in LEARNINGS, session handover and cross-domain boot prompt patterns (now in Advanced Patterns), and demonstrated the full domain lifecycle from creation through forking. See `references/advanced_patterns.md` for Finance-specific patterns that complex domains may want to adopt.

This synthesized framework (v2.1) incorporates the universal patterns from all four implementations, with domain-specific advanced patterns available separately.
