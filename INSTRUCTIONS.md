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

## Tips

- **Don't over-update.** Only update files at milestones (decision made, task done, blocker hit), not after every small step.
- **Trust the files.** If the AI's chat memory contradicts the LIMO files, the files win. That's the whole point.
- **Keep it lean.** Core LIMO is ~11 files. Resist the urge to add more. The constraint is a feature.
- **Review periodically.** Skim the files every few sessions to make sure they reflect reality. Stale files are worse than no files.
- **Use NEVER_AGAIN.md liberally.** Every time you catch the AI repeating a mistake, add it. This is the highest-value file over time.
- **Advanced patterns are earned.** Don't add session handover templates or cross-domain boot prompts until you actually need them. See `advanced_patterns.md` when you do.
