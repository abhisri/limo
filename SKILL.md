---
name: limo-scaffolder
description: >
  Scaffold the LIMO (LLM Interaction Memory OS) persistent memory framework for any new domain.
  LIMO gives AI sessions filesystem-based memory that survives across conversations — preventing
  repeated mistakes, preserving decisions, and enabling behavioral adaptation over time.

  Use this skill whenever the user wants to: set up a new LIMO domain, create persistent memory
  for a new project or life area, initialize session memory for a new topic, bootstrap a domain
  with structured AI memory, or fork an existing domain into a sub-domain. Also trigger when the
  user says things like "I want Claude to remember across sessions", "set up memory for my
  [project/hobby/work]", "create a new domain", "I need persistent context for [topic]", or
  mentions "LIMO" in the context of setup or scaffolding.
---

# LIMO Scaffolder

Set up the LIMO persistent memory framework for any new domain. This skill interviews the user,
creates the complete file structure, populates domain-specific content, and wires up the boot
sequence with cross-domain references.

## What LIMO Is (for context)

LIMO is a filesystem-based persistent memory OS for AI sessions. It gives each domain (Finance,
Health, Legal, Photography, etc.) its own structured memory that survives across conversations.
The architecture has 4 tiers: procedural (model weights), declarative (boot prompt + session
diary), behavioral (learnings + never-again gates), and episodic (raw transcripts for grep).

For the full framework specification, read: `references/LIMO_FRAMEWORK.md`

## Workflow

### Phase 1: Interview

Before creating anything, understand what the user needs. The interview should feel like a
conversation, not a form. Ask questions naturally, and fill gaps with reasonable defaults.

**Required information:**

1. **Domain name** — What to call this area (e.g., "Photography", "LIFE", "Legal", "Career")
2. **Domain description** — One sentence: what does this domain cover?
3. **Current state** — Where is the user right now in this domain? What's been happening?
4. **Goals** — What's the North Star? What are the immediate objectives?
5. **Key constraints** — Budget, time, health, dependencies on other domains?
6. **Key people** — Are there important people to track? (triggers KEY_PEOPLE.md creation)
7. **Existing decisions** — Has anything already been decided that shouldn't be re-litigated?
8. **Known mistakes/learnings** — Has the user learned anything the hard way already?
9. **Standing instructions** — Any rules that should always apply in this domain?
10. **Cross-domain connections** — Does this domain interact with other LIMO domains?

**Optional (ask if relevant):**

- **Documents/files** — Does the user have existing files to organize into this domain?
- **Forking** — Is this being split off from an existing domain?
- **Predecessor sessions** — Has the user already had AI sessions on this topic?

**Reasonable defaults** (use when user doesn't specify):

- ID format: Sequential (`OI-X001`) for simple domains, date-stamped (`OI-X-20260218-01`) for complex/high-volume domains
- Freshness targets: Use the standard table from the framework spec
- Compression protocol: Include if the user expects 5+ sessions
- KEY_PEOPLE.md: Include only if the interview surfaces specific people

### Phase 2: Create Structure

After the interview, create the full LIMO structure. Do NOT ask for confirmation — just build it.

**Directory structure:**
```
CLAUDE-PROJECTS/
└── [Domain]/
    └── limo-populated/
        └── core/
            ├── AI_AGENTS_READ_THIS_FIRST.md
            ├── START_HERE.md
            ├── [DOMAIN]_SESSION_PROMPT.md
            ├── STATUS_SNAPSHOT.md
            ├── GOALS.md
            ├── OPEN_ITEMS.md
            ├── DECISIONS.md
            ├── INVARIANTS.md
            ├── LEARNINGS.md
            ├── NEVER_AGAIN.md
            ├── CONTEXT_RESTORE_PROTOCOL.md
            ├── FOLDER_MAP.md
            ├── SESSION_DIARY.md               ← Session milestones
            ├── KEY_PEOPLE.md                  ← if domain involves people
            ├── MEMORY_COMPRESSION_PROTOCOL.md ← if expected 5+ sessions
            └── _archive/
```

**Shared files at root (create only if they don't exist):**
- `CLAUDE-PROJECTS/USER_PROFILE.md` (or ABHI_PROFILE.md if that already exists)
- `CLAUDE-PROJECTS/CLAUDE_BOOT_PROMPT.md` (if not already present)
- `CLAUDE-PROJECTS/CLAUDE_BRAIN_TRANSFER.md` (if not already present)

### Phase 3: Populate Files

Read the reference templates in `references/` for exact file formats. Each file should be
populated with the interview content — NOT left as a blank template.

**Critical population rules:**

1. **[DOMAIN]_SESSION_PROMPT.md** is the most important file. This should be comprehensive —
   everything the AI needs to know to be competent in this domain. Numbered sections. Standing
   instructions. Domain-specific context. This file alone should make a cold-start AI useful.

2. **GOALS.md** must have a North Star, numbered objectives (O1, O2...), milestones with status
   tags ([DONE], [NEXT], [PENDING], [FUTURE]), non-goals (what's explicitly out of scope), and constraints.

3. **OPEN_ITEMS.md** should have at least 2-3 items from the interview. Use the format:
   `OI-[DOMAIN]-001 | Owner | Due date | Priority | Description | Context`

4. **DECISIONS.md** should capture anything already decided. Format:
   Decision + Why + Alternatives rejected + Evidence (optional) + Revisit triggers + Origin.

5. **INVARIANTS.md** must start with the enforcement rule: "If an invariant conflicts with a
   plan: stop, log the conflict, and resolve before proceeding." Then list domain-specific
   invariants plus universal ones (action over permission, trust files over chat, etc.).

6. **LEARNINGS.md** and **NEVER_AGAIN.md** — Seed from the interview if the user has known
   mistakes/insights. Otherwise leave with headers only (they'll be populated in real time
   during sessions).

7. **STATUS_SNAPSHOT.md** — Fill with current state from interview. Goal (1 line), current
   phase, what's done, what's next (top 3), blockers, risks.

8. **SESSION_DIARY.md** — Create the "Session L1" entry documenting this scaffolding session
   as the first milestone.

9. **AI_AGENTS_READ_THIS_FIRST.md** — Numbered list of files to read, Three Rules, episodic
   recall instruction. This must be concise — under 30 lines.

10. **CONTEXT_RESTORE_PROTOCOL.md** — Phased startup checklist, write-back trigger table,
    freshness guard, domain boundaries.

### Phase 4: Wire Cross-Domain References

If other LIMO domains exist:

1. Add "Cross-Domain" section to the new domain's OPEN_ITEMS.md noting any items that belong
   to sibling domains
2. Add domain boundary rules to CONTEXT_RESTORE_PROTOCOL.md (read from siblings, write only here)
3. Update the new domain's FOLDER_MAP.md to reference sibling domains
4. Update USER_PROFILE.md if the new domain reveals something cross-domain about the user

### Phase 5: Verify

After creating all files:

1. Count files created vs expected
2. Verify all cross-references resolve (files mentioned in START_HERE.md actually exist)
3. Check that SESSION_PROMPT has substantive content (not just headers)
4. Verify GOALS has North Star + at least 2 objectives
5. Verify INVARIANTS has the enforcement rule
6. Read AI_AGENTS_READ_THIS_FIRST.md and confirm it points to all critical files
7. Report to user: "[X] files created, domain [Name] is ready. Next session in this domain
   should read AI_AGENTS_READ_THIS_FIRST.md to bootstrap."

## Domain Forking (special case)

When the user wants to split a subdomain from an existing LIMO domain:

1. Read the parent domain's LIMO core files
2. Copy behavioral files (LEARNINGS, NEVER_AGAIN) — mark items as "Inherited from [parent]"
3. Do NOT copy working memory files (STATUS_SNAPSHOT, OPEN_ITEMS) — create fresh
4. Create new SESSION_PROMPT specific to the subdomain
5. Add "Pre-Domain History" section to SESSION_DIARY referencing the parent
6. Add cross-domain pointers in both parent and child OPEN_ITEMS
7. Archive any items moving from parent to child

## File Format Reference

For detailed file templates and formats, read: `references/file_templates.md`

Each template shows the exact markdown structure, field names, and example content.
For advanced patterns (session handover, cross-domain boot prompts), see `references/advanced_patterns.md`.

## Anti-Patterns to Avoid

When scaffolding:

- **Don't create empty templates.** Every file should have real content from the interview.
  A blank GOALS.md is worse than no GOALS.md — it signals "nothing to do."
- **Don't over-populate LEARNINGS and NEVER_AGAIN.** These are earned through sessions, not
  pre-loaded. Seed only if the user has genuine hard-won insights.
- **Don't make the SESSION_PROMPT generic.** This file is the soul of the domain. If it reads
  like it could apply to anyone, it's not specific enough.
- **Don't skip cross-domain wiring.** If sibling domains exist, the new domain needs to know
  about them and they need to know about it.
- **Don't ask "would you like me to create the files now?"** After the interview, just build.
