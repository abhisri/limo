# LIMO Multi-Domain Guide

**What this is:** A step-by-step guide for graduating from a single LIMO domain to a multi-domain ecosystem. This is optional — LIMO works perfectly well for one domain with just the 4 core files.

**When you need this:** You're running 2+ domains (e.g., Finance, Legal, Health, a coding project) and you want them to share identity, communicate with each other, and maintain consistent behavioral patterns across sessions.

**Prerequisites:** You've already set up at least one LIMO domain using `SKILL.md`. You understand the core framework from `LIMO_FRAMEWORK.md`.

---

## What Changes

Single-domain LIMO: your domain folder contains everything. The AI reads the files, does the work, updates the files.

Multi-domain LIMO: domains share a common root folder. Three files move to the root (shared identity). A message bus appears at root level. Domains can read each other's files but only write to their own.

That's it. The individual domain structure doesn't change at all.

---

## Step 1: Create a Common Root

Pick one folder that will hold all your domains. Everything goes under this root.

```
CLAUDE-PROJECTS/              ← This is your root
├── Domain-A/
│   └── limo-populated/core/...
├── Domain-B/
│   └── limo-populated/core/...
└── Domain-C/
    └── limo-populated/core/...
```

**Critical:** When you start an AI session, mount this root folder — not an individual domain subfolder. If a session mounts `CLAUDE-PROJECTS/Finance/` instead of `CLAUDE-PROJECTS/`, it can't see sibling domains or the shared bus.

---

## Step 2: Move Shared Identity to Root

Three files move from inside your domain to the root level. These are read+write for ALL sessions:

```
CLAUDE-PROJECTS/
├── USER_PROFILE.md           ← Who you are (all sessions read + write)
├── CLAUDE_BOOT_PROMPT.md     ← Who the AI is, working style
├── CLAUDE_BRAIN_TRANSFER.md  ← Communication patterns, corrections log
│
├── Finance/
│   └── limo-populated/core/...
└── Legal/
    └── limo-populated/core/...
```

**USER_PROFILE.md** is a narrative document about you — not a form. Any session updates it when something changes the cross-domain story of who you are. Health update in a Life session? Update the profile. Career change discussed in a Finance session? Update the profile.

**CLAUDE_BOOT_PROMPT.md** defines the AI's relationship with you — working style, personality, values. This is shared so every domain session has the same baseline personality.

**CLAUDE_BRAIN_TRANSFER.md** captures corrections and communication preferences. When you correct the AI in one domain, the correction applies everywhere.

If these files already exist inside a domain folder, move them to root. If they exist in multiple domains, merge them — keep the most complete version of each section.

---

## Step 3: Set Up the Message Bus

Create a `_messages/` folder at root with a `_processed/` subfolder:

```
CLAUDE-PROJECTS/
├── _messages/                ← Inter-agent message bus
│   └── _processed/           ← Handled messages (audit trail)
├── USER_PROFILE.md
├── CLAUDE_BOOT_PROMPT.md
├── CLAUDE_BRAIN_TRANSFER.md
├── Finance/
└── Legal/
```

Messages are markdown files. The filename encodes routing:

```
2026-02-20_from-Finance_to-Legal_insurance-update.md
```

Agents drop messages here when they discover something relevant to another domain. The recipient agent checks the inbox on boot, processes messages, and moves them to `_processed/`.

For the full message format, priority levels, and processing rules, see the **Inter-Agent Messaging** section in `LIMO_FRAMEWORK.md`.

---

## Step 4: Set Domain Boundaries

Each domain's `CONTEXT_RESTORE_PROTOCOL.md` needs a domain boundary section:

```markdown
## Domain Boundaries
- **Write to:** Finance/ only
- **Read from:** Legal/, LIFE/ (sibling domains)
- **Shared:** CLAUDE-PROJECTS/USER_PROFILE.md (read + write)
- **Messages:** Check CLAUDE-PROJECTS/_messages/ on boot
- **Redirect:** Cross-domain items noted and messaged to appropriate domain
```

Each domain's `OPEN_ITEMS.md` should have a Cross-Domain section:

```markdown
## Cross-Domain (note only — action belongs to other sessions)
- Insurance policy review → **Legal session**
- Tax implications of settlement → **Finance session**
```

When an agent encounters cross-domain work, it notes it in OPEN_ITEMS AND drops a message in `_messages/` so the target domain knows about it on next boot.

---

## Step 5: Update Existing Domains

For each existing domain:

1. Remove the local copies of USER_PROFILE, BOOT_PROMPT, BRAIN_TRANSFER (they're at root now)
2. Update `AI_AGENTS_READ_THIS_FIRST.md` to point to the root-level shared files
3. Update `FOLDER_MAP.md` to show the full multi-domain structure
4. Update `CONTEXT_RESTORE_PROTOCOL.md` with domain boundaries and inbox checking
5. Add sibling domain references to `START_HERE.md`

---

## Domain Forking

When a domain grows too large or a subdomain needs its own session:

1. Copy the LIMO `core/` skeleton into the new domain folder
2. Rewrite domain-specific files (SESSION_PROMPT, GOALS, STATUS_SNAPSHOT, OPEN_ITEMS)
3. Inherit behavioral files (LEARNINGS, NEVER_AGAIN — mark inherited items)
4. Archive originals in `core/_archive/`
5. Add cross-domain pointers in both parent and child
6. Drop a message in `_messages/` announcing the new domain to siblings

The new domain starts with the parent's behavioral knowledge but builds its own working memory from scratch.

---

## Memory Compression Across Domains

With multiple domains running over months, session diaries grow. Each domain should have a `MEMORY_COMPRESSION_PROTOCOL.md` (see `file_templates.md` for the template). The compression procedure:

1. Entries older than the domain's threshold get compressed to milestone-only format
2. Decisions extracted → DECISIONS.md
3. Insights extracted → LEARNINGS.md
4. Failures extracted → NEVER_AGAIN.md
5. Verbose versions archived in `_archive/`

Compression happens per-domain. The shared files (USER_PROFILE, BOOT_PROMPT, BRAIN_TRANSFER) compress naturally — they're living documents that get rewritten, not appended.

---

## Checklist

- [ ] Common root folder created
- [ ] USER_PROFILE.md at root
- [ ] CLAUDE_BOOT_PROMPT.md at root
- [ ] CLAUDE_BRAIN_TRANSFER.md at root
- [ ] `_messages/` and `_messages/_processed/` created
- [ ] Each domain's CONTEXT_RESTORE_PROTOCOL updated with boundaries
- [ ] Each domain's AI_AGENTS_READ_THIS_FIRST updated to point to root shared files
- [ ] Each domain's FOLDER_MAP updated
- [ ] Sessions mount the root folder, not individual domain subfolders
