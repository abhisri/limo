# LIMO File Templates

Reference templates for every LIMO core file. Replace `[DOMAIN]` with the actual domain name
(e.g., Photography, LIFE, Legal, Career). Replace `[USER]` with the user's name.

**v2.5 frontmatter — every core file starts with:**
```
description: <one line — what this file is for and when to open it; feeds the BOOT_PACK signposts>
modified: YYYY-MM-DD
```
**v2.5 line tags** (collection files: DECISIONS, LEARNINGS, NEVER_AGAIN, INVARIANTS, CHECKPOINTS): `{valid: 2026-03-19..}`
`{valid: 2026-03-19..2026-06-01}` `{supersedes: D-X-003}` `{class: fact|opinion|preference|episode|rule}` `{confidence: 0.7}`.
Never delete a superseded entry — close its range and point the successor at it. See LIMO_FRAMEWORK.md → Memory Line Conventions.

---

## AI_AGENTS_READ_THIS_FIRST.md

```markdown
# [Domain Name] — AI Agents Read This First

You're continuing work on [1-sentence domain description].

## Read these files in order:
1. `BOOT_PACK.md` — GENERATED digest: SETTLED tables, status, active items, gates, Documents/ tree, lint findings
2. `CLAUDE_BOOT_PROMPT.md` — who [USER] is
3. `[DOMAIN]_SESSION_PROMPT.md` — domain context, current state, standing instructions
4. `CLAUDE_BRAIN_TRANSFER.md` — communication style, corrections log
5. `OWNERS.md` — which files you may write, which you may only propose to
6. `DECISIONS.md` — what's been decided (don't re-litigate)
7. `INVARIANTS.md` — rules that never break
8. `STATUS_SNAPSHOT.md`, `GOALS.md`, `OPEN_ITEMS.md`, `CHECKPOINTS.md` — open in full only where BOOT_PACK points you

## Three Rules
1. Write LEARNINGS.md and NEVER_AGAIN.md IN REAL TIME when corrections or insights happen
2. Action over permission — do the work, don't ask if you should
3. Trust files over chat — if files and conversation conflict, files are source of truth

## Before asserting a fact
`ls -R ../Documents/` then grep before writing "you don't have", "you never mentioned", "X is missing".
Core files are summaries (every number carries a `[src:]` tag). Documents/ is the source.

## Episodic recall
Grep SESSION_DIARY.md / CHECKPOINTS.md (`checkpoint-tail:`) or query the Event API. Don't load whole files.
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

**Coding domain enhancement:** Add these sections when the domain involves a codebase:
```markdown
## Build status
- **Compiles:** [Yes/No + command]
- **Tests:** [X/Y suites pass. Note any failures with root cause.]

## Technical debt
- [Brief list of known debt: dead code, migration state, duplicate files, etc.]
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
<!-- v2.5 optional row tags: {blocked_by: OI-X-012} {claimed: agent YYYY-MM-DD} {started: YYYY-MM-DD}. `limo_lint.py ready` computes what is actionable; lint flags stalls after 7 days. -->

- OI-[D]-001 | [Owner] | [Due date] | [Priority] | [Description] | [Context / success criteria]
- OI-[D]-002 | [Owner] | [Due date] | [Priority] | [Description] | [Context / success criteria]

## Parking Lot

- OI-[D]-P01 | [Owner] | DEFERRED | [Description] | [Why deferred]

## Cross-Domain (note only — action belongs to other sessions)

- [Item description] → **[Which session] session**
```

**Priority levels:** URGENT, HIGH, MEDIUM, LOW, OPEN, WAITING
**Status tags:** Active items are being worked. Parking Lot items are deferred with reason.

**Coding domain enhancement:** For codebase domains, group active items by category:
```markdown
## Active

### Codebase Cleanup (do first)
- OI-[D]-010 | Owner | — | HIGH | Delete dead files in legacy directory | [Context]
- OI-[D]-011 | Owner | — | MED | Resolve duplicate .ts/.js pairs | [Context]

### Core Development
- OI-[D]-020 | Owner | — | HIGH | Implement [feature] | [Context]

### Documentation
- OI-[D]-030 | Owner | — | MED | Consolidate paper drafts | [Context]
```

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

## INV-[D]-008 — No persistent mutation without explicit instruction
Do not write to LIMO core files unless a write-back trigger has fired OR the user issues an explicit action command. Casual acknowledgment ("LGTM", "sounds good", "makes sense") is NOT write permission. If intent is ambiguous, ask ONE clarifying question — do not guess.

## INV-[D]-009 — Tiered exploration before deep-dive
Before exploring a codebase or file structure, follow the exploration tiers in order. Stop at the lowest tier that answers the question:
- Tier 0: Check for orientation docs (AGENTS.md, CLAUDE.md, .github/agents/*.agent.md, README)
- Tier 1: Root structural scan (top-level files, workflow configs, package manifests)
- Tier 2: Targeted deep-dive for the specific question at hand
- Tier 3: Broad survey — ONLY for sustained multi-session work requiring full codebase understanding

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
- Triggers: [keyword, another phrase, *.glob — words that, appearing in a request, must surface this gate; v2.5, optional but seed the violated ones]
- Symptom: [What went wrong]
- Root cause: [Why it happened]
- Prevention gate: [The rule that prevents recurrence]
- Evidence signal: [How to detect you're about to make this mistake again]
- Fix: [What to do instead]
```

---

## ARCHITECTURE.md (optional — include when domain involves a codebase)

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

### [Module 2 Name]
[What it does.]

## Module-to-File Mapping

| Module | File(s) | Status |
|:-------|:--------|:-------|
| [Module 1] | `src/path/to/file.ts` | ✅ Active |
| [Module 2] | `src/path/to/other.ts` | ✅ Active |
| [Module 3] | `legacy/old_file.ts` | ⚠️ Legacy — port to new arch |
| [Module 4] | — | 🔲 Not yet implemented |

## Key Concepts
- **[Concept 1]**: [1-sentence definition]
- **[Concept 2]**: [1-sentence definition]

## Build & Test
- **Build command:** `[command]`
- **Test command:** `[command]`
- **Key config files:** `[tsconfig.json, package.json, etc.]`
```

**Population guidance:** This file bridges the conceptual architecture to the actual code. The module-to-file mapping table is the highest-value section — it tells a cold-start agent exactly where to find things without exploring the whole codebase. Update the Status column as modules move between active/legacy/planned.

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

## CONTEXT_RESTORE_PROTOCOL.md — ⚠️ LEGACY (do not create for new domains; superseded in v2.4 by the spec's Layer 1 rules and `shared/SESSION_BOOT_PROTOCOL.md`)

```markdown
# Context Restore Protocol — [Domain Name]

## Purpose
Make work restartable. Any new session — on any platform, with any agent — should reconstruct full context fast, avoid repeating mistakes, and continue with minimal drift. This protocol is deterministic: follow it exactly, in order, no improvisation.

## Startup Checklist — STRICT ORDER

### Phase 0: Orientation (check for existing context)
0a. Check for orientation docs: `AGENTS.md`, `CLAUDE.md`, `.github/agents/*.agent.md` at project root
0b. If found, read them — they may override or supplement this protocol
0c. If not found, proceed with this protocol as-is

### Phase 1: Identity + History (declarative memory)
1. Read `CLAUDE_BOOT_PROMPT.md` — who [USER] is, working relationship
2. Read `[DOMAIN]_SESSION_PROMPT.md` — domain context, current state, standing instructions
3. Read `SESSION_DIARY.md` — session milestones, progression
   - If file is too large: read last 200 lines first, then grep for recent dates

### Phase 2: Behavioral Adaptation (learned patterns)
4. Read `CLAUDE_BRAIN_TRANSFER.md` — corrections log, communication style
5. Read `LEARNINGS.md` — reusable insights
6. Read `NEVER_AGAIN.md` — failure gates (these are HARD STOPS — treat as invariants)

### Phase 3: Current State (working memory)
7. Read `STATUS_SNAPSHOT.md` — what's happening NOW ← **primary restart artifact**
8. Read `GOALS.md` — objectives and milestones
9. Read `OPEN_ITEMS.md` — what's next / blocked
10. Read `DECISIONS.md` — what's already been decided (DO NOT re-litigate)
11. Read `INVARIANTS.md` — rules that never break

### Phase 4: Recovery Context (if resuming interrupted work)
12. Read `CHECKPOINTS.md` — grep for `checkpoint-tail:` to scan recent outcomes
    - If resuming a specific thread: read the last 2-3 full checkpoint entries
    - Pay special attention to DEAD-END entries — do not retry paths already ruled out
    - Note the **Agent** field — a dead end from a different agent may warrant re-evaluation

### Phase 5: Begin Work
13. Check `_messages/` inbox for inter-agent messages (if multi-domain)
14. Pick the top OPEN item, or respond to [USER]'s request
15. Run `date -u` to establish temporal context

## File Authority Hierarchy

When information conflicts between files, trust in this order:
1. **INVARIANTS.md** — absolute rules, never overridden
2. **NEVER_AGAIN.md** — hard failure gates
3. **DECISIONS.md** — settled decisions with rationale
4. **STATUS_SNAPSHOT.md** — current state (most recently updated wins)
5. **SESSION_DIARY.md / CHECKPOINTS.md** — historical record
6. **Chat history** — least authoritative; files override chat if they conflict

## Stale File Handling

If a file's "Last updated" is older than its freshness target:
- **Treat as hypothesis, not truth** — the information may have drifted
- **Flag to user:** "[File] is [X days] past its freshness target"
- **Do not silently act on stale data** — verify with user or primary sources first
- **Prefer regenerating** from primary sources over trusting stale content

## Write-Back Triggers

| File | Trigger | Action |
|:-----|:--------|:-------|
| `STATUS_SNAPSHOT.md` | Finish a sub-task or change focus | Update current phase, what's done, what's next |
| `DECISIONS.md` | Make a choice that rules out alternatives | Append with rationale + revisit triggers |
| `OPEN_ITEMS.md` | Discover new work or complete an item | Add/check off |
| `LEARNINGS.md` | [USER] corrects you, or a reusable insight emerges | Record immediately with "How to reuse" |
| `NEVER_AGAIN.md` | Avoidable failure occurs | Record with prevention gate + evidence signal |
| `SESSION_DIARY.md` | Meaningful milestone reached | One-line entry with timestamp |
| `CHECKPOINTS.md` | Problem solved, dead end hit, investigation completed, or session ends mid-work | Structured entry with golden path, dead-ends, evidence, and tail marker |

**CRITICAL:** Write to LEARNINGS.md, NEVER_AGAIN.md, and CHECKPOINTS.md IN REAL TIME. Do NOT wait until session end.

## Mutation Gating

Do not write to persistent memory files unless:
- A write-back trigger (above) has fired, OR
- The user issues an explicit action command (e.g., "update the status", "log this decision", "checkpoint this")

Phrases like "LGTM", "sounds good", or "makes sense" are acknowledgments — NOT write permission.
If intent is ambiguous, ask ONE clarifying question. Do not interpret casual agreement as instruction to mutate files.

## Domain Boundaries
- **Write to:** [Domain]/ only
- **Read from:** [List sibling domains] (sibling domains)
- **Shared:** CLAUDE-PROJECTS/USER_PROFILE.md (read + write)
- **Redirect:** Cross-domain items noted and suggested for appropriate session.

## Large File Handling
- If any file is too large to load: read last 200 lines first, or grep for keywords. Don't try to load whole files.
- For raw transcripts: grep for keywords, never load whole file.
- For CHECKPOINTS.md: grep for `checkpoint-tail:` lines to get a summary index, then read specific entries as needed.
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
│       ├── CHECKPOINTS.md            ← Structured progress: golden paths + dead ends
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

**Coding domain enhancement:** For domains with a codebase, the folder map should include the source tree with status annotations. Use these markers:
- `← ✅ ACTIVE` for current implementation files
- `← ⚠️ LEGACY` or `← ⚠️ DEAD CODE` for files that should be migrated or deleted
- `← 🔲 PLANNED` for directories/files that don't exist yet
- Brief inline comments explaining what each directory/file does

Also add a **Memory Tier Mapping** table showing which LIMO files serve which cognitive layer:
```markdown
## Memory Tier Mapping
| Tier | Files |
|:-----|:------|
| **Declarative** (facts, context) | SESSION_PROMPT, SESSION_DIARY, CHECKPOINTS, START_HERE, ARCHITECTURE |
| **Behavioral** (learned patterns) | LEARNINGS, NEVER_AGAIN, INVARIANTS |
| **Working** (current state) | STATUS_SNAPSHOT, GOALS, OPEN_ITEMS, DECISIONS |
| **Protocol** (how to operate) | AI_AGENTS_READ_THIS_FIRST, CONTEXT_RESTORE_PROTOCOL, MEMORY_COMPRESSION_PROTOCOL, FOLDER_MAP |
```

---

## Inter-Agent Message (for multi-domain ecosystems)

Messages live in `CLAUDE-PROJECTS/_messages/`. Each message is a standalone file.

**Filename:** `[DATE]_from-[SOURCE]_to-[TARGET]_[slug].md`

```markdown
# Message: [Short descriptive title]

| Field       | Value                          |
|:------------|:-------------------------------|
| From        | [Source domain name]           |
| To          | [Target domain name, or ALL]   |
| Date        | [YYYY-MM-DD HH:MM UTC]         |
| Priority    | [routine / important / urgent] |
| In-Reply-To | [filename of original message, or "—" if not a reply] |

## Context
[1-3 sentences: why this message exists. What was the agent doing when it realized
this information was relevant to the target domain?]

## Payload
[The actual information, insight, request, or question. Be specific and actionable.
Include data, evidence, or file references. Don't make the recipient agent guess
what you mean.]

## Suggested Action
[What the recipient agent should do with this. Examples:
- "Update DECISIONS.md with this evidence"
- "Consider for ARCHITECTURE.md module mapping"
- "Add to LEARNINGS.md — this pattern applies to your domain too"
- "FYI only — no action needed, just awareness"]

## References
- [Path to relevant file, e.g., `Research/limo-populated/core/DECISIONS.md#D-Research-003`]
- [Path to evidence, e.g., `Research/test-results/oracle-separation-proof.md`]
```

**Examples:**

Filename: `2026-02-20_from-Research_to-ASENT_oracle-separation-validates-embodiment47.md`
- Context: "While testing Research's oracle separation architecture, discovered that the strict
  separation between discoverer and oracle directly validates ASENT Embodiment 47's claim
  about symbolic reasoning requiring isolated evaluation contexts."
- Priority: important
- Suggested Action: "Add as supporting evidence to the non-provisional filing. Reference
  Research test results as empirical proof."

Filename: `2026-02-21_from-LIMO_to-ALL_compression-protocol-update.md`
- Context: "Updated the memory compression protocol based on real-world usage across 5 domains."
- Priority: routine
- Suggested Action: "FYI — review your MEMORY_COMPRESSION_PROTOCOL.md if it predates this update."

**Processing rules:**
- Recipient agent checks `_messages/` on boot, after standard LIMO startup
- Process by priority: urgent → important → routine
- After processing, move to `_messages/_processed/`
- Log in SESSION_DIARY: "Processed inter-agent message from [domain]: [title]"
- For urgent messages or irreversible actions: surface to user for confirmation first

---

## CHECKPOINTS.md

```markdown
# Checkpoints — [Domain Name]

**Purpose:** Structured record of solution paths taken and dead ends hit. Each entry captures enough context that any agent on any platform can understand what was tried, what worked, what failed, and what to do next.

Last updated: [DATE]
Freshness target: 180 days

## How to Use This File (for recovery)
1. Grep for `checkpoint-tail:` to scan all outcomes quickly
2. Read the last 2-3 full entries for current context
3. Before retrying a failed approach, check DEAD-END entries — don't re-walk closed paths
4. Note the Agent field — a dead end from one agent may warrant re-evaluation by another

## Design-Intent Anchor

### CP-[D]-000 — Design Intent Anchor
**Date:** [YYYY-MM-DD HH:MM UTC]
**Agent:** [Agent that performed the initial scaffolding / design review]
**Session:** [Session ID]
**Outcome:** ANCHOR

#### Original Design Intent
[What is this project/domain trying to achieve? State the goal in the designer's own terms,
not a reinterpretation. If a formal design doc exists, quote the key goals from it.]

#### Specified Components
[List every component, module, or capability the design calls for. For each:]
- **[Component name]**: [What the design says it should do] | Status: [IMPLEMENTED | NOT YET | PARTIAL]

#### Design Principles / Constraints
[Non-negotiable architectural choices from the original design. These are the rules that
distinguish "implementing the design" from "drifting into something else."]
- [Principle 1: e.g., "emergence-based reasoning, not solver-based"]
- [Principle 2: e.g., "no shaped patches — discovery from primitives only"]

#### Baseline Measurements
[If applicable: what does "working correctly per the design" look like? Test counts,
behavioral expectations, performance targets.]

#### Key Files
- `path/to/design_doc` — the authoritative source for this anchor
- `path/to/architecture` — system design reference

#### Drift Detection Rule
When a bug fix or new feature is proposed, check: does this implement something the design
already specifies, or does it patch around a missing component? If the latter, go back to
this anchor and implement the specified component instead.

<!-- checkpoint-tail: Design intent anchor — [1-sentence summary of what the design is trying to achieve] -->

## Checkpoint Log

### CP-[D]-001 — [Title: what was investigated/solved]
**Date:** [YYYY-MM-DD HH:MM UTC]
**Agent:** [Claude Code / Claude Cowork / Monday (ChatGPT) / Codex / Gemini / Human]
**Session:** [Session ID or "manual"]
**Outcome:** [SOLVED | DEAD-END | PARTIAL | PIVOT]
**Class:** [fabrication | scope-drift | tooling | data-quality | judgment | other]   ← v2.4; required when Outcome is DEAD-END

#### Golden Path
[The actual steps that produced the result. Specific, reproducible sequence — not "we investigated X."]

#### Dead-Ends / Abandoned Paths
- **Attempted:** [What was tried]
- **Failed because:** [Specific evidence — error messages, test results, logical contradiction]
- **Lesson:** [Why this is closed — don't retry without new evidence]

#### State + Evidence
- Files created/modified: [paths]
- Test results: [pass/fail counts]
- Commit: [hash + subject, if applicable]
- Measurements: [metrics, benchmarks — anything quantitative]

#### Tips & Insights
[Non-obvious discoveries a successor couldn't reconstruct from code alone.]

#### Next Actions
[Concrete follow-up — specific steps with enough context to execute, not vague "continue investigating."]

#### Key Files
- `path/to/file` — [why it matters for this thread]

<!-- checkpoint-tail: [1-sentence summary of this checkpoint] -->
```

**Outcome tags explained:**
- **SOLVED** — Problem fully resolved. Lead with Golden Path. The main value is the working sequence.
- **DEAD-END** — Investigation concluded without solution. Lead with Dead-Ends section — this IS the main value. Specific failure evidence prevents successor sessions from re-walking the path.
- **PARTIAL** — Progress made, not complete. Include both Golden Path (what worked so far) and Next Actions (what remains).
- **PIVOT** — Direction changed based on findings. Explain the trigger for the pivot and the new direction chosen.

**Examples:**

SOLVED entry:
```markdown
### CP-Research-042 — VV.24 16-Cell Regression Fix
**Date:** 2026-04-15 14:30 UTC
**Agent:** Claude Code
**Session:** a8a55bab
**Outcome:** SOLVED

#### Golden Path
FNAZ quarantine (programExprQuarantine.ts, 267 LOC) isolates unsound fact-assertions before they pollute soundFacts. Applied to discovery loop gate at L4_e0_SF.

#### Dead-Ends / Abandoned Paths
- **Attempted:** K-parameter tuning (K=3, then K=6)
- **Failed because:** FA1 requires K>=6 but pollution requires K<=3-4. No single K satisfies both.
- **Lesson:** The regression is architectural (missing quarantine), not parametric. Don't retry K tuning.

#### State + Evidence
- Files created: `src/programExprQuarantine.ts`
- Test results: 735/735 Tier A+B pass, Tier C preserved
- Commit: 156ba7e "VV.24: minimal FNAZ quarantine"

#### Tips & Insights
The fix was already in the original design doc (Research.docx, FNAZ pseudocode lines 1608-1725). The design was right — implementation had drifted.

#### Next Actions
1. Wire IWNF as pre-acceptance gate (VV.25 directive)
2. Full FNAZ + MLE strategy registry integration on experiment branch

#### Key Files
- `src/programExprQuarantine.ts` — the quarantine implementation
- `Research_Clean_Academic_Look.txt` — original design with FNAZ spec

<!-- checkpoint-tail: VV.24 resolved 16-cell regression via FNAZ quarantine (267 LOC), proving the fix was in the original design, not K-tuning -->
```

DEAD-END entry:
```markdown
### CP-Research-038 — K-Parameter Tuning for FA1/Pollution Tradeoff
**Date:** 2026-04-12 09:15 UTC
**Agent:** Claude Code
**Session:** a8a55bab
**Outcome:** DEAD-END
**Class:** judgment

#### Golden Path
[None — this was a dead end.]

#### Dead-Ends / Abandoned Paths
- **Attempted:** Set K=3 to prevent pollution (VV.20)
- **Failed because:** FA1 combos>=5 assertion fires — K=3 is too restrictive for complex proofs
- **Lesson:** K is a single knob controlling two opposing constraints

- **Attempted:** Revised K to 6 (VV.21)
- **Failed because:** Pollution returns at K=6 — the 4-input UNKNOWN technique fires on 5/6-atom cells
- **Lesson:** No single K value can satisfy both FA1 and pollution prevention simultaneously

#### State + Evidence
- Test results: VV.20 at K=3 breaks FA1; VV.21 at K=6 re-introduces pollution
- Measurements: K=3 → 12 FA1 failures; K=6 → 16-cell regression returns

#### Tips & Insights
This is a fundamental architectural conflict, not a tuning problem. The regression needs a quarantine mechanism (FNAZ from original design), not a parameter sweep.

#### Next Actions
1. Abandon K-tuning entirely
2. Investigate FNAZ quarantine from Research.docx original design

#### Key Files
- `Research_Clean_Academic_Look.txt` — lines 1608-1725 contain FNAZ pseudocode that may be the real fix

<!-- checkpoint-tail: K-tuning is a dead end — FA1 needs K>=6 but pollution needs K<=3-4, no single K works. Look at FNAZ quarantine instead. -->
```

---

## _pending/ (v2.5 — proposals inbox, one folder per domain)

`core/_pending/` holds `reflect_<date>.md` from `limo_lint.py reflect` and entries a propose-only worker wants promoted
(`<agent>_<date>_<slug>.md`, same entry format as the target file). Nothing in `_pending/` is truth. A human, or a session
told to, applies it to the source file and deletes the proposal. Lint reports how many proposals are waiting.

---

## OWNERS.md (v2.4 — required at `Agents` level; one-row version fine at `Core`)

```markdown
# Owners — [Domain Name]
Last updated: [DATE]
Level: [Core | Agents | Infra]

Read at boot. `others` = edit | propose | read.
propose = write your finding to your own diary/TODO file; the owner promotes it.
Truth is what the owner has promoted. Worker output is not truth.

| file / glob                 | owner        | others  |
|:----------------------------|:-------------|:--------|
| STATUS_SNAPSHOT.md          | cowork       | propose |
| DECISIONS.md                | cowork       | propose |
| OPEN_ITEMS.md               | cowork       | propose |
| SESSION_DIARY.md            | primary+owner  | read    |
| [DOMAIN]_SESSION_PROMPT.md  | primary+owner  | read    |
| INVARIANTS.md               | primary+owner  | propose |
| LEARNINGS.md                | shared       | edit    |
| NEVER_AGAIN.md              | shared       | edit    |
| CHECKPOINTS.md              | shared       | edit    |
| codex_session_diary.md      | codex        | read    |
| CODEX_TODO.md               | codex        | read    |
| BOOT_PACK.md                | generated    | read    |
| ../Documents/**             | owner         | read    |
```

At `Core` level with a single agent the whole file can be:

```markdown
# Owners — [Domain Name]
Last updated: [DATE]
Level: Core
| file / glob | owner  | others |
|:------------|:-------|:-------|
| *           | cowork | edit   |
| ../Documents/** | owner | read |
```

---

## SETTLED — DO NOT RE-LITIGATE table (v2.4 — goes at the TOP of whichever file the question will be re-asked in)

```markdown
## SETTLED — DO NOT RE-LITIGATE
| Question | Settled | Date | Where reasoning lives |
|:---------|:--------|:-----|:----------------------|
| [The question as it keeps being asked] | [The answer, with the operative figure] | [YYYY-MM-DD] | DECISIONS D-[D]-NNN |
```

Rules: written the same turn the debate resolves; superseded text elsewhere in the file is marked in
place (`~~old~~ → SUPERSEDED YYYY-MM-DD, see SETTLED`), not deleted; BOOT_PACK hoists every SETTLED
table in the domain to its first section.

---

## Source tag convention (v2.4)

In STATUS_SNAPSHOT, SESSION_PROMPT, GOALS and KEY_PEOPLE, every figure, date, quantity or lab value carries:

```
[src: Documents/<relative path>#YYYY-MM-DD]
```

`#date` is the date *of the source document*, not of the edit. Examples:

```
- Household setup cost to date: $12,400 [src: Documents/Household/PURCHASES_TRACKER.md#2026-08-09]
- ALT 40 U/L [src: Documents/Labs/2026-01-15_panel.pdf#2026-01-15]
- Authorized capital $100,000 [src: Documents/Incorporation/MOA_draft.docx#2026-03-19]
```

No document behind the number → write it as approximate and say where it came from: `~$1,000 (owner, from memory, 2026-09-15)`.
`limo_lint.py lint` reports bare numbers in those four files.

---

## AGENTS.md (v2.4 — optional, domain root, only when the domain is also a repository worked by CLI agents)

```markdown
# [Domain] — instructions for every agent seat

Read this file completely before the first action. Source of truth for who may write what: `limo-populated/core/OWNERS.md`.

## Boot
1. `limo-populated/core/BOOT_PACK.md`, then `[DOMAIN]_SESSION_PROMPT.md`.
2. If a lane has a resume README or checkpoint, resume from it, never from chat memory. State what you verified and what you did not.
3. `ls -R Documents/` before claiming anything is absent. Grep before asserting.

## Fences (violations are defects, not judgment calls)
- **[Owner] owns truth.** Files marked `propose` in OWNERS.md are written only via your own diary; the owner promotes.
- **The human drives git.** No commit / push / reset / checkout -- / clean / worktree remove. Hand exact commands.
- **Verify the checkout by path** (`git rev-parse --show-toplevel`), never by content.
- **Seat separation.** Designer ≠ reviewer; implementer ≠ approver. Never appoint your own reviewer. Disclose inherited context.
- **Reviewed bytes are pinned.** Corrections are separate previews, applied after checks pass and the record says so.
- **No claims beyond evidence.** Say which of protocol-validation / real-result every output is.

## Records discipline
- Trackers updated as work happens. `Last updated` headers replaced, never chained. Committed vs uncommitted stated with the hash.
- Large regenerable artifacts stay out of git; SHA-256 in the checkpoint instead.
- Every DEAD-END checkpoint carries a `Class:`.

## Quota routing
- Mechanical work (reruns, digests, regeneration, pre-commit checks) → subagent or script, never the main thread.
- Reserve-tier model → mechanical work only. Design, correction text, adjudication wait for the advanced model.
- Batch a task list; do not end a turn to ask "continue?" when the mandate already says so.

## When a decision is put to the human
Page one is plain English: what, why now, what is being decided, on yes / on no, risks, unknowns, cost, next step.
End with a numbered **"Your turn"** block of the exact actions requested.
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
