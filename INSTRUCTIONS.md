# INSTRUCTIONS — How to Use LIMO with Your AI Agent

This guide covers setup for every major AI coding/work tool. The core idea is the same everywhere: **put the LIMO files where your agent can see them, and tell it to read them first.**

---

## Quick Setup (All Tools)

### Step 1: Copy core files into your project

```bash
cp -r core/ your-project/limo/
```

Or just drop the `core/` folder alongside your existing project files.

### Step 2: Bootstrap the agent

At the start of your first session, paste this to your AI agent:

```
This project uses LIMO (LLM Interaction Memory OS) for persistent working memory.

Before doing any work, read the following files in order:
1. core/CONTEXT_RESTORE_PROTOCOL.md  (how to restore context)
2. core/STATUS_SNAPSHOT.md            (current state)
3. core/GOALS.md                      (what we're building toward)
4. core/OPEN_ITEMS.md                 (what's next)
5. core/INVARIANTS.md                 (rules that must hold)
6. core/NEVER_AGAIN.md                (mistakes not to repeat)
7. core/DECISIONS.md                  (what we already decided)

After each meaningful step (decision made, task completed, blocker hit), update:
- STATUS_SNAPSHOT.md  → current state
- OPEN_ITEMS.md       → what's next
- DECISIONS.md        → if you made a choice
- LEARNINGS.md        → if you learned something reusable
- SESSION_DIARY.md    → one-line milestone entry

These files ARE the project memory. Trust them over chat history.
```

### Step 3: On every subsequent session

Paste this shorter prompt:

```
This project uses LIMO for working memory. Start by reading core/CONTEXT_RESTORE_PROTOCOL.md, then follow the startup checklist. Pick up where the last session left off.
```

That's it for basic setup. Below are tool-specific details.

---

## Claude (claude.ai / Claude Desktop / Cowork)

**Where to put files:** Upload the `core/` folder contents, or if using Cowork/Desktop with a project folder, just include them in the folder you select.

**Session start:** Paste the bootstrap prompt above, or simply say: *"Read all the files in core/ starting with CONTEXT_RESTORE_PROTOCOL.md and resume work."*

**On context limit:** When Claude hits the context limit and a new session starts, it may show a summary of the prior conversation. Ignore the summary for project state — tell the new session to read the LIMO files instead. The files are the source of truth, not the AI's memory of the conversation.

**Tip:** Claude is good about maintaining files if you remind it. If it forgets to update, say: *"Update the LIMO files before we continue."*

---

## Claude Code (CLI)

**Where to put files:** Place `core/` in your project root. Claude Code auto-reads project files.

**Best practice:** Add the bootstrap prompt to your `CLAUDE.md` file (Claude Code's project instructions):

```markdown
## LIMO Workspace

This project uses LIMO for persistent memory. At session start:
1. Read core/CONTEXT_RESTORE_PROTOCOL.md
2. Follow the startup checklist
3. After each milestone, update STATUS_SNAPSHOT, OPEN_ITEMS, DECISIONS, and SESSION_DIARY

Trust LIMO files over chat history for project state.
```

**On context compaction:** Claude Code compacts context when it gets long. The LIMO files survive compaction because they're on disk. When you see the compaction notice, the agent can re-read the files and continue.

---

## OpenAI Codex (CLI agent)

**Where to put files:** Place `core/` in your repository root. Codex operates on your repo files directly.

**Session start:** In your first prompt or in your Codex instructions file, include the bootstrap prompt above.

**How it works with Codex:** Codex runs in a sandboxed environment and can read/write files in your repo. It will read the LIMO files, do its work, and update them. When you review the Codex output, you'll see the updated LIMO files in the diff alongside the code changes.

**Tip:** Since Codex works asynchronously, the updated LIMO files in each run serve as a "handoff note" for the next run.

---

## ChatGPT (with Code Interpreter / Canvas / Projects)

**Where to put files:** Upload the `core/` files to the conversation, or if using a ChatGPT Project, add them to the project's knowledge files.

**Session start:** After uploading, paste the bootstrap prompt. ChatGPT will read the files and follow the protocol.

**Limitation:** ChatGPT can't write back to your local filesystem (unless you download updated files). Workaround: at the end of each session, ask ChatGPT to give you the updated files to download and replace in your project. Or copy the updated content manually.

**With Projects:** If you put LIMO files in a ChatGPT Project's knowledge, they persist across conversations in that project. However, ChatGPT can't edit knowledge files directly — you'll need to update them yourself based on what the AI tells you changed.

---

## Cursor / Windsurf / AI-Powered Editors

**Where to put files:** Place `core/` in your project root — the AI in these editors can read project files.

**For Cursor specifically:** You can add LIMO instructions to your `.cursorrules` or `.cursor/rules` file:

```
This project uses LIMO for working memory. Before starting work, read all files
in core/ starting with CONTEXT_RESTORE_PROTOCOL.md. After each significant change,
update STATUS_SNAPSHOT.md and OPEN_ITEMS.md. Trust these files over conversation history.
```

**For Windsurf:** Similar approach — add to your project-level AI instructions.

**How it works:** The AI reads your project files, sees the LIMO workspace, and maintains it as you work. Since these editors have persistent file access, the write-back loop works naturally.

---

## Google Gemini (with Google AI Studio / Vertex)

**Where to put files:** Upload the `core/` files or paste their contents into your prompt.

**Session start:** Include the bootstrap prompt along with the file contents.

**Note:** Like ChatGPT, Gemini doesn't have persistent file access in most interfaces. You'll need to manage the file updates yourself, or use an environment (like a Colab notebook or Vertex AI agent) where file read/write is available.

---

## Any Other LLM or Agent Framework

LIMO works with any LLM that can read text. The pattern is always:

1. **Make the files accessible** — whether that's uploading them, putting them in a project folder, or pasting them into the prompt.
2. **Tell the agent to read them first** — use the bootstrap prompt above.
3. **Tell the agent to update them** — the update triggers are in `CONTEXT_RESTORE_PROTOCOL.md`.
4. **On new sessions, re-read** — the files are the memory, not the conversation history.

If your tool can read/write files: the agent maintains LIMO automatically.
If your tool can only read: you update the files manually based on the agent's output.

---

## Domain Adaptation (Optional)

After basic setup, you can specialize LIMO for your domain:

```bash
# Copy a domain pack alongside core
cp -r packs/coding/ your-project/limo/domain/    # or: finance, research, operations
```

Then tell your agent: *"We're using the coding domain pack. Read the files in domain/ for additional templates and checklists."*

See `packs/` for available domains, or create your own by following `llm-workspace-kit/prompts/DOMAIN_ADAPTER_INSTRUCTIONS.md`.

---

## Multi-Agent Mode (Optional)

If you're running two agents (e.g., one for deep work, one for oversight):

1. Copy `addons/multi_agent/` into your workspace
2. Assign roles: **Worker** (proposes changes) and **Coordinator** (promotes changes into truth files)
3. Use the role-specific prompts in `llm-workspace-kit/prompts/`:
   - `WORKER_AGENT_PROMPT.md` for the deep-work agent
   - `COORDINATOR_AGENT_PROMPT.md` for the oversight agent

The Worker writes proposals; the Coordinator reviews and applies them. This prevents one agent from accidentally overwriting another's decisions.

---

## Tips

- **Don't over-update.** Only update files at milestones (decision made, task done, blocker hit), not after every small step.
- **Trust the files.** If the AI's chat memory contradicts the LIMO files, the files win. That's the whole point.
- **Keep it small.** LIMO is 8 files. Resist the urge to add more. The constraint is a feature.
- **Review periodically.** Skim the files every few sessions to make sure they accurately reflect reality. Stale files are worse than no files.
- **Use NEVER_AGAIN.md liberally.** Every time you catch the AI repeating a mistake, add it. This is the highest-value file over time.
