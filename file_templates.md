# LIMO File Templates

Reference templates for every LIMO core file. Replace `[DOMAIN]` with the actual domain name
(e.g., Photography, LIFE, Legal, Career). Replace `[USER]` with the user's name.

---

## AI_AGENTS_READ_THIS_FIRST.md

```markdown
# [Domain Name] — AI Agents Read This First

You're continuing work on [1-sentence domain description].

## Read these files in order:
1. `CLAUDE_BOOT_PROMPT.md` — who [USER] is
2. `[DOMAIN]_SESSION_PROMPT.md` — domain context, current state, standing instructions
3. `CLAUDE_BRAIN_TRANSFER.md` — communication style, corrections log
4. `STATUS_SNAPSHOT.md` — what's happening NOW
5. `GOALS.md` — objectives and milestones
6. `OPEN_ITEMS.md` — what needs doing
7. `DECISIONS.md` — what's been decided (don't re-litigate)
8. `INVARIANTS.md` — rules that never break
9. `SESSION_DIARY.md` — session history and milestones

## Three Rules
1. Write LEARNINGS.md and NEVER_AGAIN.md IN REAL TIME when corrections or insights happen
2. Action over permission — do the work, don't ask if you should
3. Trust files over chat — if files and conversation conflict, files are source of truth

## Episodic recall
For deep history beyond what's in SESSION_DIARY.md, grep raw transcripts. Don't load whole.
```

---

## START_HERE.md

```markdown
# [Domain Name] — Start Here

## What this is
[2-3 sentences describing what this domain covers and why it exists as a separate LIMO domain.]

## Architecture note
This is one domain in a multi-session LIMO architecture:
- **Shared root files:** USER_PROFILE.md, CLAUDE_BOOT_PROMPT.md, CLAUDE_BRAIN_TRANSFER.md
- **This domain:** [Domain]/limo-populated/core/ (YOU ARE HERE)
- **Sibling domains:** [List other domains if they exist]

## 4-tier memory model
| Tier | What | Where |
|:-----|:-----|:------|
| Procedural | Model capabilities | Built into weights |
| Declarative | Facts + history | BOOT_PROMPT + SESSION_PROMPT + SESSION_DIARY |
| Behavioral | Learned patterns | BRAIN_TRANSFER + LEARNINGS + NEVER_AGAIN |
| Episodic | Specific recall | Raw transcripts (grep, don't load) |

## Read order
Follow the numbered list in AI_AGENTS_READ_THIS_FIRST.md.

## Domain boundary rules
- **Write to:** [Domain]/ only
- **Read from:** [List sibling domain folders] (sibling domains)
- **Shared:** CLAUDE-PROJECTS/USER_PROFILE.md (read + write, all sessions)
- **Redirect:** If [USER] raises items belonging to other domains, note and suggest raising in appropriate session.
```

---

## [DOMAIN]_SESSION_PROMPT.md

```markdown
# [Domain Name] Session Prompt

Last updated: [DATE]
Freshness target: 14 days

## 1. [Primary aspect of domain]
[Detailed current state, history, key facts]

## 2. [Second aspect]
[Details]

## 3. [Third aspect]
[Details]

...continue as needed...

## N. Standing Instructions
- [Rule 1: Domain-specific behavior rule]
- [Rule 2]
- [Rule 3]
```

**Population guidance:** This is the MOST IMPORTANT file. It should be 150-400 lines covering
everything a cold-start AI needs to be competent in this domain. Write it as a comprehensive
briefing document, not a sparse outline. Use numbered sections. Include standing instructions
as the final section.

---

## STATUS_SNAPSHOT.md

```markdown
# Status Snapshot — [Domain Name]

Last updated: [DATE]
Freshness target: 7 days

## Goal (1 line)
[Single sentence describing the domain's current primary objective]

## Current phase
[What stage of work are we in]

## What's done
- [Completed item 1]
- [Completed item 2]

## What's next (top 3)
1. [Priority 1]
2. [Priority 2]
3. [Priority 3]

## Blockers
- [What's preventing progress, if anything]

## Latest artifacts
- [Path/to/recently/created/files]

## Risks / gotchas
- [Things that could go wrong or need watching]
```

---

## GOALS.md

```markdown
# Goals — [Domain Name]

Last updated: [DATE]
Freshness target: 14 days

## North Star
[1-2 sentence ultimate objective for this domain]

## Objectives
- O1: [Specific objective]
- O2: [Specific objective]
- O3: [Specific objective]

## Milestones
- M1: [DONE] [Description]
- M2: [NEXT] [Description]
- M3: [PENDING] [Description]
- M4: [FUTURE] [Description]

## Non-Goals
- [What this domain is explicitly NOT trying to do]
- [Scope boundary that prevents creep]
- [Thing that sounds related but is out of scope]

## Constraints
- [Budget/financial constraint]
- [Time constraint]
- [Health/physical constraint]
- [Dependencies on other domains]
```

---

## OPEN_ITEMS.md

```markdown
# Open Items — [Domain Name]

Last updated: [DATE]
Freshness target: 7 days

## Active

- OI-[D]-001 | [Owner] | [Due date] | [Priority] | [Description] | [Context / success criteria]
- OI-[D]-002 | [Owner] | [Due date] | [Priority] | [Description] | [Context / success criteria]

## Parking Lot

- OI-[D]-P01 | [Owner] | DEFERRED | [Description] | [Why deferred]

## Cross-Domain (note only — action belongs to other sessions)

- [Item description] → **[Which session] session**
```

**Priority levels:** URGENT, HIGH, MEDIUM, LOW, OPEN, WAITING
**Status tags:** Active items are being worked. Parking Lot items are deferred with reason.

---

## DECISIONS.md

```markdown
# Decisions — [Domain Name]

Last updated: [DATE]
Freshness target: 90 days

## Log

### D-[D]-001 — [Decision title]
- Decision: [What was decided]
- Why: [Reasoning — be specific]
- Alternatives rejected: [What was considered and ruled out, and why]
- Evidence: [What data/documents/analysis supports this — optional, but prevents re-litigation]
- Revisit triggers: [What would reopen this decision]
- Origin: [Which session/conversation/date this was decided]
```

---

## INVARIANTS.md

```markdown
# Invariants — [Domain Name]

Last updated: [DATE]
Freshness target: 30 days

## Enforcement rule
If an invariant conflicts with a plan: **stop**, log the conflict, and resolve before proceeding.

## INV-[D]-001 — Read workspace files before acting
Read CLAUDE_BOOT_PROMPT.md + STATUS_SNAPSHOT.md before substantive work. Don't make claims based on stale memory.

## INV-[D]-002 — Action over permission
Default to doing the work, not asking if you should. Ask only when genuinely ambiguous between very different approaches.

## INV-[D]-003 — Trust corrections immediately
When [USER] corrects a fact, interpretation, or framing: update immediately, acknowledge in one sentence max, continue.

## INV-[D]-004 — Files are source of truth
If chat history contradicts core files (STATUS_SNAPSHOT, DECISIONS, etc.), trust the files. Update files when corrections are made.

## INV-[D]-005 — Milestone-only diary updates
Session diary entries should be meaningful milestones, not stream-of-consciousness. Decision made, artifact produced, blocker found/removed.

## INV-[D]-006 — Write only to [Domain]/
This session reads from sibling folders but writes exclusively to [Domain]/. Cross-domain items get noted and redirected.

## INV-[D]-007 — Unreadable input → blocker writeback
If any input cannot be parsed (encrypted, corrupted, unsupported format): stop attempting workarounds, write a BLOCKER entry to OPEN_ITEMS.md + note in STATUS_SNAPSHOT.md, and continue with remaining inputs.

[Add domain-specific invariants below]
```

---

## LEARNINGS.md

```markdown
# Learnings — [Domain Name]

Last updated: [DATE]
Freshness target: 60 days

## Inherited (universal, from other domains)

[Seed with relevant learnings from existing domains if applicable]

## [Domain]-specific

[Leave empty if no learnings yet — these are earned in real time during sessions]

### L-[D]-001 — [Title]
- Context: [What happened]
- Observation: [The insight]
- Why it matters: [What goes wrong if this is forgotten]
- How to reuse: [Practical application for future sessions]
```

---

## NEVER_AGAIN.md

```markdown
# Never Again — [Domain Name]

Last updated: [DATE]
Freshness target: 180 days

## Inherited (universal behavioral gates)

### NA-[D]-001 — Never ask "would you like me to..."
- Prevention gate: Just do the work. Ask only when genuinely ambiguous between very different approaches.
- Evidence signal: Finding yourself typing "Would you like..." or "Should I..." or "Shall I..."
- Fix: Delete the question, replace with the action.

### NA-[D]-002 — Never interpret broad statements as emotional
- Prevention gate: When [USER] says something that sounds emotional or broad, check the last 2-3 messages for a specific practical referent.
- Evidence signal: [USER]'s statement references something that COULD be literal.
- Fix: Ask yourself "is this about a specific thing?" before launching into encouragement.

## [Domain]-specific gates

[Leave empty if no failures yet — these are earned through real mistakes]

### NA-[D]-0XX — [Title]
- Symptom: [What went wrong]
- Root cause: [Why it happened]
- Prevention gate: [The rule that prevents recurrence]
- Evidence signal: [How to detect you're about to make this mistake again]
- Fix: [What to do instead]
```

---

## KEY_PEOPLE.md (optional — include when domain involves people)

```markdown
# Key People — [Domain Name]

Last updated: [DATE]
Freshness target: 30 days

## [Group 1 Name]

### [Person Name]
- Role: [Their function/title]
- Relationship: [To the user]
- Contact: [Phone/email if relevant]
- Last status: [Most recent known state]
- Notes: [Critical context]

## [Group 2 Name]
...
```

---

## CONTEXT_RESTORE_PROTOCOL.md

```markdown
# Context Restore Protocol — [Domain Name]

## Purpose
Make work restartable. Any new session should reconstruct full context fast, avoid repeating mistakes, and continue with minimal drift.

## Startup Checklist — STRICT ORDER

### Phase 1: Identity + History (declarative memory)
1. Read `CLAUDE_BOOT_PROMPT.md` — who [USER] is
2. Read `[DOMAIN]_SESSION_PROMPT.md` — domain context, current state, standing instructions
3. Read `SESSION_DIARY.md` — session milestones, progression

### Phase 2: Behavioral Adaptation (learned patterns)
4. Read `CLAUDE_BRAIN_TRANSFER.md` — corrections log, communication style
5. Read `LEARNINGS.md` — reusable insights
6. Read `NEVER_AGAIN.md` — failure gates

### Phase 3: Current State (working memory)
7. Read `STATUS_SNAPSHOT.md` — what's happening NOW
8. Read `GOALS.md` — objectives and milestones
9. Read `OPEN_ITEMS.md` — what's next / blocked
10. Read `DECISIONS.md` — what's already been decided
11. Read `INVARIANTS.md` — rules that never break

### Phase 4: Begin Work
12. Pick the top OPEN item, or respond to [USER]'s request
13. Run `date -u` to establish temporal context

## Write-Back Triggers

| File | Trigger | Action |
|:-----|:--------|:-------|
| `STATUS_SNAPSHOT.md` | Finish a sub-task or change focus | Update current phase, what's done, what's next |
| `DECISIONS.md` | Make a choice that rules out alternatives | Append with rationale + revisit triggers |
| `OPEN_ITEMS.md` | Discover new work or complete an item | Add/check off |
| `LEARNINGS.md` | [USER] corrects you, or a reusable insight emerges | Record immediately with "How to reuse" |
| `NEVER_AGAIN.md` | Avoidable failure occurs | Record with prevention gate + evidence signal |
| `SESSION_DIARY.md` | Meaningful milestone reached | One-line entry with timestamp |

**CRITICAL:** Write to LEARNINGS.md and NEVER_AGAIN.md IN REAL TIME. Do NOT wait until session end.

## Freshness Guard
If a file's "Last updated" is older than its freshness target, treat it as hypothesis, not truth.

## Domain Boundaries
- **Write to:** [Domain]/ only
- **Read from:** [List sibling domains] (sibling domains)
- **Shared:** CLAUDE-PROJECTS/USER_PROFILE.md (read + write)
- **Redirect:** Cross-domain items noted and suggested for appropriate session.

## Large File Handling
- If any file is too large to load: read last 200 lines first, or grep for keywords. Don't try to load whole files.
- For raw transcripts: grep for keywords, never load whole file.
```

---

## SESSION_DIARY.md

```markdown
# Session Diary — [Domain Name]

**Purpose**: Crash-recovery journal. If this session dies or a new session starts cold, reading this file + the other LIMO core files should give the new "you" enough context to resume seamlessly.

Last updated: [DATE]
Freshness target: 180 days

## How to Use This File (for a fresh session)
1. Read START_HERE.md first (domain context, read order, rules)
2. Read this diary. The latest session section is your ground truth.
3. Read OPEN_ITEMS.md and DECISIONS.md for what's pending and decided.
4. You are now caught up.

## Session Log

### Session [D]1 — [DATE] (LIMO scaffolding)
**[TIMESTAMP] — Domain scaffolded via LIMO framework.**
Created [X] core files. Domain covers: [brief description]. Initial goals, open items, and decisions populated from user interview.
```

**Note:** When SESSION_DIARY.md grows large, use the MEMORY_COMPRESSION_PROTOCOL to compress older entries. For advanced session handover and cross-domain boot prompt templates, see `advanced_patterns.md`.

---

## FOLDER_MAP.md

```markdown
# Folder Map — [Domain Name]

Last updated: [DATE]
Freshness target: 30 days

## Structure

```
[Domain]/
├── limo-populated/
│   └── core/                    ← LIMO memory files (YOU ARE HERE)
│       ├── AI_AGENTS_READ_THIS_FIRST.md
│       ├── START_HERE.md
│       ├── [DOMAIN]_SESSION_PROMPT.md  ← Primary domain knowledge
│       ├── STATUS_SNAPSHOT.md          ← Current state
│       ├── GOALS.md                    ← Objectives + milestones
│       ├── OPEN_ITEMS.md              ← Action items
│       ├── DECISIONS.md               ← Settled decisions
│       ├── INVARIANTS.md              ← Unbreakable rules
│       ├── LEARNINGS.md               ← Reusable insights
│       ├── NEVER_AGAIN.md             ← Failure gates
│       ├── CONTEXT_RESTORE_PROTOCOL.md
│       ├── FOLDER_MAP.md              ← This file
│       ├── SESSION_DIARY.md           ← Crash-recovery journal
│       └── _archive/                  ← Old file versions
│
├── [domain-specific folders as needed]
│   └── ...
│
└── [_inbox/]                           ← Staging area for incoming files
```

## Sibling Domains
[List paths to other LIMO domains at same level under CLAUDE-PROJECTS/]

## Shared Root Files
- `CLAUDE-PROJECTS/USER_PROFILE.md`
- `CLAUDE-PROJECTS/CLAUDE_BOOT_PROMPT.md`
- `CLAUDE-PROJECTS/CLAUDE_BRAIN_TRANSFER.md`
```

---

## MEMORY_COMPRESSION_PROTOCOL.md (optional — for domains with 5+ expected sessions)

```markdown
# Memory Compression Protocol — [Domain Name]

Last updated: [DATE]
Freshness target: 180 days

## Philosophy
Human memory compresses naturally. Raw experiences → key moments → lessons → identity.
LIMO should do the same.

## When to compress
- Manual trigger: User requests cleanup
- Domain-specific cadence: Every [5-10] sessions, review SESSION_DIARY for compressible entries

## What survives indefinitely
- Decisions and their reasoning (→ DECISIONS.md)
- Key milestones with dates (→ SESSION_DIARY.md, compressed)
- People introduced with roles (→ KEY_PEOPLE.md)
- Errors and their fixes (→ NEVER_AGAIN.md)
- Reusable insights (→ LEARNINGS.md)

## What compresses (detail → summary)
- Multi-step work sequences → single milestone line
- Exploration that led to decisions → just the decision
- Debugging/troubleshooting details → just the fix and lesson

## What gets pruned
- Dead-end explorations that led nowhere
- Superseded information (old values replaced by new)
- Redundant entries (same milestone noted multiple ways)

## Compression procedure
1. Read SESSION_DIARY.md
2. For entries older than [threshold]:
   a. Extract any un-captured decisions → DECISIONS.md
   b. Extract any un-captured insights → LEARNINGS.md
   c. Extract any un-captured failures → NEVER_AGAIN.md
   d. Compress the diary entry to milestone-only format
3. Archive verbose version in _archive/ if needed

## Anti-patterns
- Don't compress entries less than [2 weeks] old — too soon to know what matters
- Don't delete without extracting — the insight might be buried in the details
- Don't compress if you can't verify the summary captures the essential facts
```
