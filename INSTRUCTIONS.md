# INSTRUCTIONS — How to Use LIMO with Your AI Agent

This guide covers setup for every major AI tool. The core idea is the same everywhere: **put the LIMO files where your agent can see them, and tell it to read them first.**

---

## Quick Setup (All Tools)

### Step 1: Set up a new domain

Share `LIMO_FRAMEWORK.md` and `file_templates.md` with your AI agent and tell it:

```
Set up LIMO for [my project/domain].
```

The agent will interview you about the domain, create the file tree, and populate every file with real content from your conversation. (If you're using Claude, share `SKILL.md` too — it has a step-by-step scaffolding workflow.)

### Step 2: Work normally — the agent maintains the files

Once LIMO is set up, your domain will have ~11 Markdown files. The agent knows when to update which files (it's defined in `CONTEXT_RESTORE_PROTOCOL.md`). After each meaningful step — decision made, task completed, blocker hit — the agent updates the relevant files.

### Step 3: On every new session

Tell the new agent:

```
Read AI_AGENTS_READ_THIS_FIRST.md and follow the restore protocol.
```

The agent reads the files, reconstructs full context, and picks up where the last session left off.

That's it. Below are tool-specific details.

---

## Claude (claude.ai / Claude Desktop / Cowork)

**Where to put files:** If using Cowork or Claude Desktop with a project folder, include the LIMO domain folder in the folder you select. Otherwise, upload the files to the conversation.

**First session:** Share `LIMO_FRAMEWORK.md` and `file_templates.md` (and `SKILL.md` for the scaffolding workflow) and say: *"Set up LIMO for [my project]."*

**Subsequent sessions:** Say: *"Read AI_AGENTS_READ_THIS_FIRST.md and resume work."*

**On context limit:** When Claude hits the context limit and a new session starts, it may show a conversation summary. Ignore the summary for project state — tell the new session to read the LIMO files. The files are the source of truth, not the AI's memory.

---

## Claude Code (CLI)

**Where to put files:** Place the LIMO domain folder in your project root. Claude Code auto-reads project files.

**Best practice:** Add LIMO instructions to your `CLAUDE.md` file:

```markdown
## LIMO Workspace

This project uses LIMO for persistent memory. At session start:
1. Read AI_AGENTS_READ_THIS_FIRST.md
2. Follow the startup checklist in CONTEXT_RESTORE_PROTOCOL.md
3. After each milestone, update STATUS_SNAPSHOT, OPEN_ITEMS, DECISIONS, and SESSION_DIARY

Trust LIMO files over chat history for project state.
```

**On context compaction:** Claude Code compacts context when it gets long. LIMO files survive compaction because they're on disk. When you see the compaction notice, the agent re-reads the files and continues.

---

## OpenAI Codex (CLI agent)

**Where to put files:** Place the LIMO domain folder in your repository root. Codex operates on your repo files directly.

**Session start:** In your first prompt or Codex instructions file, include the bootstrap prompt from Step 3 above.

**How it works:** Codex runs in a sandboxed environment and can read/write files in your repo. It reads the LIMO files, does its work, and updates them. When you review the Codex output, you'll see the updated LIMO files in the diff alongside code changes.

**Tip:** Since Codex works asynchronously, the updated LIMO files in each run serve as a handoff note for the next run.

---

## ChatGPT (with Code Interpreter / Canvas / Projects)

**Where to put files:** Upload the LIMO files to the conversation, or if using a ChatGPT Project, add them to the project's knowledge files.

**Session start:** After uploading, paste the bootstrap prompt. ChatGPT will read the files and follow the protocol.

**Limitation:** ChatGPT can't write back to your local filesystem. Workaround: at the end of each session, ask ChatGPT to give you the updated files to download and replace in your project.

**With Projects:** If you add LIMO files to a ChatGPT Project's knowledge, they persist across conversations. However, ChatGPT can't edit knowledge files directly — you'll need to update them based on what the AI tells you changed.

---

## Cursor / Windsurf / AI-Powered Editors

**Where to put files:** Place the LIMO domain folder in your project root — the AI in these editors can read project files.

**For Cursor:** Add LIMO instructions to your `.cursorrules` or `.cursor/rules` file:

```
This project uses LIMO for working memory. Before starting work, read
AI_AGENTS_READ_THIS_FIRST.md and follow the restore protocol. After each
significant change, update STATUS_SNAPSHOT.md and OPEN_ITEMS.md. Trust
these files over conversation history.
```

**For Windsurf:** Similar approach — add to your project-level AI instructions.

**How it works:** The AI reads your project files, sees the LIMO workspace, and maintains it as you work. Since these editors have persistent file access, the write-back loop works naturally.

---

## Google Gemini / Any Other LLM

LIMO works with any LLM that can read text. The pattern is always:

1. **Make the files accessible** — upload them, put them in a project folder, or paste them into the prompt.
2. **Tell the agent to read them first** — use the bootstrap prompt from Step 3.
3. **Tell the agent to update them** — the triggers are in `CONTEXT_RESTORE_PROTOCOL.md`.
4. **On new sessions, re-read** — the files are the memory, not the conversation history.

If your tool can read/write files: the agent maintains LIMO automatically.
If your tool can only read: you update the files manually based on the agent's output.

---

## Progressive Discovery — Expanding LIMO Capabilities

LIMO has three tiers. Users start with Tier 1 (just the core files). Tiers 2 and 3 are optional expansions that the AI session should **offer when the need becomes apparent** — not dump on the user upfront.

Think of it like setting up a smart home: you start with the speaker, and the app offers to connect a doorbell when it notices you have one. LIMO works the same way. The AI detects signals that the user would benefit from an expansion, and offers it.

### Tier 2: Multi-Domain Ecosystem

**What it adds:** Shared identity files at a common root, a `_messages/` bus for inter-agent communication, domain boundary rules, and cross-domain awareness.

**When to offer it — trigger signals:**

- The user mentions a second domain: *"I also have a Finance project"* or *"I use LIMO for my legal case too"*
- The user asks about sharing context across domains: *"Can my Legal session know about the financial stuff?"*
- The user manually relays information between domains: *"In my other session, we decided X — can you note that here?"*
- You notice cross-domain items accumulating in OPEN_ITEMS.md
- The user has multiple LIMO domain folders visible in the workspace

**How to offer it:**

> "I notice you're running LIMO in multiple domains. Right now they're independent — each session starts cold without knowing what the others have done. LIMO has a multi-domain setup where your domains share identity and can message each other directly. Want me to set that up? I'd create a shared root folder with your profile and a message bus. Takes about 5 minutes."

**What to do:** Read `MULTI_DOMAIN_GUIDE.md` and follow the steps. The guide walks through creating the shared root, moving identity files, setting up `_messages/`, and updating each domain's boundary rules.

### Tier 3: Infrastructure Backend

**What it adds:** Optional server-side services — semantic memory (mem0), knowledge graph (Neo4j), workflow automation (n8n), and real-time task dispatch (Agent Bus).

**When to offer specific components:**

| Signal | Component to offer |
|:-------|:-------------------|
| User asks "what did we figure out about X months ago?" and grep isn't enough | **mem0** — semantic memory search |
| User tracks many people with complex relationships across domains | **Neo4j** — knowledge graph |
| User wants scheduled tasks, automated workflows, or webhook triggers | **n8n** — workflow automation |
| User wants real-time cross-agent task dispatch with state tracking | **Agent Bus** (requires n8n) |
| User says "I wish the AI could remember everything" or "searching old sessions is painful" | **mem0** as a starting point |
| User has 5+ domains with heavy cross-domain traffic | **Full stack** |

**How to offer it:**

> "You keep needing to search across months of session history, and grepping the diary isn't cutting it. LIMO can optionally connect to a semantic memory service called mem0 — it lets you search your accumulated knowledge by meaning, not just keywords. It runs on a small server ($10-15/month). I can walk you through setting one up if you're interested — I'd help you pick a cloud provider, provision a server, and set everything up via SSH. You don't need to know how servers work; I'll guide you through it."

Only offer one component at a time. Start with the one that solves the user's most visible pain. Don't suggest the full stack unless they're clearly ready for it.

**What to do:** Read `INFRASTRUCTURE_GUIDE.md` for the conceptual overview and the `infra/` directory for starter configs. If the user says yes:

1. Help them choose a cloud provider (suggest beginner-friendly options like DigitalOcean or Hetzner)
2. Walk them through creating an account and provisioning a server (the user does the clicking — you tell them what to click)
3. Have them give you SSH access (IP address, username, private key path)
4. SSH into the server and set up the stack using the configs in `infra/`
5. Verify services are running
6. Configure the LIMO domain to connect to the new services

Read `infra/setup.md` for the full server setup procedure.

### What NOT to do

- **Don't mention tiers unprompted.** The user doesn't need to know LIMO has tiers. They need to know their AI can do more when they're ready.
- **Don't explain the architecture.** Say what it does for them, not how it works internally.
- **Don't offer Tier 3 before Tier 2 is running.** Multi-domain should be working before adding infrastructure. Exception: a single-domain user with a clear mem0 use case.
- **Don't push.** If the user says "maybe later" or "I'm fine with files," respect that. The files-only version is complete and works great.

---

## Tips

- **Don't over-update.** Only update files at milestones (decision made, task done, blocker hit), not after every small step.
- **Trust the files.** If the AI's chat memory contradicts the LIMO files, the files win. That's the whole point.
- **Keep it lean.** Core LIMO is ~11 files. Resist the urge to add more. The constraint is a feature.
- **Review periodically.** Skim the files every few sessions to make sure they reflect reality. Stale files are worse than no files.
- **Use NEVER_AGAIN.md liberally.** Every time you catch the AI repeating a mistake, add it. This is the highest-value file over time.
- **Advanced patterns are earned.** Don't add session handover templates or cross-domain boot prompts until you actually need them. See `advanced_patterns.md` when you do.
