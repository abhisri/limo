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

For the full framework specification, read: `LIMO_FRAMEWORK.md` (v2.4). Templates: `file_templates.md`. Advanced patterns: `advanced_patterns.md`. (Paths are relative to the workspace root; the older `references/` layout is gone.)

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
7. **Codebase** — Does this domain involve building or maintaining a codebase? (triggers ARCHITECTURE.md creation)
8. **Existing decisions** — Has anything already been decided that shouldn't be re-litigated?
9. **Known mistakes/learnings** — Has the user learned anything the hard way already?
10. **Standing instructions** — Any rules that should always apply in this domain?
11. **Cross-domain connections** — Does this domain interact with other LIMO domains?
12. **Messaging** — Are there sibling domains that would benefit from receiving messages from this domain? (triggers `_messages/` setup)
13. **Conformance level** (v2.4/v2.5) — `Core` (one agent, markdown only), `Git` (markdown + a memory-only git repo at `limo-populated/` → run `tools/limo_lint.py git-init`), `Agents` (two or more agents or seats share the domain → triggers OWNERS.md), or `Infra` (the domain logs to the Event API / mem0 → SESSION_DIARY is a stub, boot points at `shared/SESSION_BOOT_PROTOCOL.md`). Levels stack. Default: `Git`; add `Agents` automatically if the user mentions Codex, Gemini, ChatGPT or a second seat.
14. **Documents folder** (v2.4) — Does the domain have source documents (contracts, reports, inventories, lab results)? Create `{Domain}/Documents/` and put them there, NOT in core/. Core files summarise; Documents/ is the source.

**Optional (ask if relevant):**

- **Design document / blueprint** — Is there an existing design doc, spec, or blueprint that defines what this project should be? (If yes, this becomes the basis for the Design-Intent Anchor checkpoint CP-000. Critical for preventing drift in multi-agent or long-running projects.)
- **Documents/files** — Does the user have existing files to organize into this domain?
- **Forking** — Is this being split off from an existing domain?
- **Predecessor sessions** — Has the user already had AI sessions on this topic?

**Reasonable defaults** (use when user doesn't specify):

- ID format: Sequential (`OI-X001`) for simple domains, date-stamped (`OI-X-20260218-01`) for complex/high-volume domains
- Freshness targets: Use the standard table from the framework spec
- Compression protocol: Include if the user expects 5+ sessions
- KEY_PEOPLE.md: Include only if the interview surfaces specific people
- OWNERS.md: Include at `Agents` level or above; at `Core` level a one-row manifest (`* | <agent> | edit`) is still cheap and lets lint run
- CONTEXT_RESTORE_PROTOCOL.md: **do not create** (legacy since v2.4). AI_AGENTS_READ_THIS_FIRST carries the boot order; at `Infra` level it points at `shared/SESSION_BOOT_PROTOCOL.md`

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
            ├── OWNERS.md                      ← write manifest (v2.4; required at Agents level)
            ├── BOOT_PACK.md                   ← GENERATED by tools/limo_lint.py bootpack (v2.4)
            ├── FOLDER_MAP.md
            ├── SESSION_DIARY.md               ← Session milestones
            ├── CHECKPOINTS.md                ← Structured progress: golden paths + dead ends
            ├── KEY_PEOPLE.md                  ← if domain involves people
            ├── ARCHITECTURE.md               ← if domain involves a codebase
            ├── MEMORY_COMPRESSION_PROTOCOL.md ← if expected 5+ sessions
            └── _archive/
```

**Domain-root files (v2.4):**
- `[Domain]/Documents/` — always create; source documents live here, never in core/
- `[Domain]/AGENTS.md` — only at `Agents` level when the domain is also a repository worked by CLI agents; generate from OWNERS.md + INVARIANTS.md using the template in `file_templates.md`

**Shared files/folders at root (create only if they don't exist):**
- `CLAUDE-PROJECTS/USER_PROFILE.md` (or OWNER_PROFILE.md if that already exists)
- `CLAUDE-PROJECTS/CLAUDE_BOOT_PROMPT.md` (if not already present)
- `CLAUDE-PROJECTS/CLAUDE_BRAIN_TRANSFER.md` (if not already present)
- `CLAUDE-PROJECTS/_messages/` (if sibling domains exist — create with `_processed/` subfolder)
- `CLAUDE-PROJECTS/_messages/_processed/` (for handled messages)

**Important prerequisite:** All LIMO domains must live under a common root folder. In tools like
Claude Cowork, each session mounts a specific folder — for inter-agent messaging and the shared
bus (USER_PROFILE, BOOT_PROMPT, BRAIN_TRANSFER, `_messages/`) to work, sessions must mount the
common root (e.g., `CLAUDE-PROJECTS/`) not individual domain subfolders. If a session mounts
`CLAUDE-PROJECTS/Research/` instead of `CLAUDE-PROJECTS/`, it won't see sibling domains or the message bus.

### Phase 3: Populate Files

Read the reference templates in `file_templates.md` for exact file formats. Each file should be
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

9. **CHECKPOINTS.md** — Create with the Design-Intent Anchor (CP-[D]-000) populated from the
   interview: what the project is trying to achieve, which components are specified in any
   existing design doc or blueprint, and the design principles that define "on track" vs
   "drifting." This anchor is the baseline all future checkpoints are measured against — it
   prevents agents from patching around missing components instead of implementing them.
   If the user describes specific past investigations with clear solved/failed outcomes,
   also create CP entries for those using the structured format (Golden Path, Dead-Ends,
   State + Evidence, tail marker).

10. **AI_AGENTS_READ_THIS_FIRST.md** — Numbered list of files to read, Three Rules, episodic
    recall instruction. This must be concise — under 30 lines.

11. **OWNERS.md** (v2.4) — Write manifest: file | owner | others (edit / propose / read). At `Agents`
    level the truth files (STATUS_SNAPSHOT, DECISIONS, OPEN_ITEMS, SESSION_DIARY, SESSION_PROMPT) are
    owned by one agent; every other agent is `propose`. Documents/** is owned by the human.

11b. **Source tags** (v2.4) — Every figure, date or quantity you write into STATUS_SNAPSHOT, SESSION_PROMPT,
    GOALS or KEY_PEOPLE carries `[src: Documents/<path>#YYYY-MM-DD]`. If the interview gave you a number
    with no document behind it, write it as approximate and say so.

12. **ARCHITECTURE.md** (if codebase domain) — System overview, module descriptions, module-to-file
    mapping table with status markers (✅ Active, ⚠️ Legacy, 🔲 Planned), build/test commands.
    This file should give a cold-start AI a mental model of the codebase without exploring blindly.
    Also enhance FOLDER_MAP.md with status annotations and STATUS_SNAPSHOT with build/test status.

### Phase 4: Wire Cross-Domain References

If other LIMO domains exist:

1. Add "Cross-Domain" section to the new domain's OPEN_ITEMS.md noting any items that belong
   to sibling domains
2. Add domain boundary rules to START_HERE.md and OWNERS.md (read from siblings, write only here)
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
7. Run `python3 tools/limo_lint.py lint "[Domain]"` — fix anything it reports (dangling references,
   missing OWNERS.md, untraced numbers, missing `description:` lines). Then `python3 tools/limo_lint.py all "[Domain]"`
   to generate BOOT_PACK.md, TRIGGER_INDEX.md and limo-populated/AGENTS.md. At `Git` level or above run
   `python3 tools/limo_lint.py git-init "[Domain]"` and then `commit "[Domain]" --agent scaffolder --trigger "scaffold"`. (v2.5)
8. Report to user: "[X] files created, domain [Name] is ready at level [Core/Agents/Infra]. Next
   session in this domain should read AI_AGENTS_READ_THIS_FIRST.md → BOOT_PACK.md to bootstrap."

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

For detailed file templates and formats, read: `file_templates.md`

Each template shows the exact markdown structure, field names, and example content.
For advanced patterns (session handover, cross-domain boot prompts), see `advanced_patterns.md`.

## Exploration Tiers (for codebase / file-heavy domains)

When scaffolding a domain that involves a codebase or large file structure, follow these tiers
in order. Stop at the lowest tier that gives you enough context. This preserves context budget
and prevents unfocused exploration.

**Tier 0 — Check for existing orientation docs**
Before exploring anything, look for files that another agent (or human) already created to
orient successors: `AGENTS.md`, `CLAUDE.md`, `.github/agents/*.agent.md`, `.cursor/rules`,
or any `README.md` at root. If found, read them — they often contain the exact information
you'd spend 10 minutes exploring to reconstruct.

**Tier 1 — Root structural scan**
Read top-level files only: `README.md`, `package.json` / `pyproject.toml` / `Cargo.toml`,
workflow configs (`.github/workflows/`), `tsconfig.json`, `docker-compose.yml`. This gives
you the tech stack, build commands, and project shape without reading any source code.

**Tier 2 — Targeted deep-dive**
Navigate to the specific directory or file relevant to the current task. Read only what you
need to answer the user's question or complete the immediate work. Do not wander.

**Tier 3 — Broad survey**
Full codebase exploration: module boundaries, cross-file dependencies, architecture patterns.
Use ONLY when the domain will have sustained multi-session work and needs a comprehensive
ARCHITECTURE.md. Even then, survey methodically (directory by directory) rather than randomly.

**When scaffolding a codebase domain:** Start at Tier 0. If no orientation docs exist, do
Tier 1 to populate the ARCHITECTURE.md module table. Do Tier 2 for specific modules the user
mentions. Do Tier 3 only if the user asks for a comprehensive architecture overview.

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
- **Don't create CONTEXT_RESTORE_PROTOCOL.md.** Legacy since v2.4; its rules live in the spec's Layer 1 and in `shared/SESSION_BOOT_PROTOCOL.md`.
- **Don't put source documents in core/.** Core is governance; `Documents/` is facts. A number in core without a `[src:]` tag is a lint finding.
- **Don't hand-write BOOT_PACK.md, TRIGGER_INDEX.md or limo-populated/AGENTS.md.** They are generated.
- **Don't leave a gate without `Triggers:` if the interview named a mistake that has actually happened.** A gate that fires only at boot is a title among forty.
- **Don't run git yourself.** `limo_lint.py commit` is the only sanctioned path; it refuses where a human drives git.
