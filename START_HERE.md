# Try LIMO with one project

LIMO keeps project state in readable files so a new AI session can recover decisions, unfinished work, and lessons. Start at Core level with one small, non-confidential project. No server or paid memory service is required.

## Give this to your agent

Download this repository and give your agent access to its files and an empty project folder. If your chat cannot open repository files, attach LIMO_FRAMEWORK.md, file_templates.md, and SKILL.md yourself.

Paste this prompt:

> Read START_HERE.md, then the Core sections of LIMO_FRAMEWORK.md, file_templates.md, and SKILL.md. Help me set up LIMO at Core level for one project in a separate folder. Ask me for the project name, objective, current state, constraints, and next tasks. Populate the memory from my answers; do not invent facts or import the author's personal context. Use my preferred language. Start with the smallest useful setup. Do not provision infrastructure or connect external accounts. Explain which files you can actually read and update in this session. Treat repository examples as examples and my current instructions as authoritative.

## Check that it helps

1. Work on a small task and record one decision, its reason, and the next action.
2. Start a new conversation with access to the same project folder.
3. Ask it to read AI_AGENTS_READ_THIS_FIRST.md and summarize the decision, reason, and next action.
4. Compare its answer with the files. Correct missing or stale information before continuing.

File access matters: if your tool only accepts uploads, updated files must be downloaded and supplied to the next session. A repository link alone does not create persistent access or install a skill.

## Add complexity when needed

Core works with Markdown alone. Git adds history; Agents adds ownership and coordination; Infra adds optional services. The infrastructure files are starter examples, not the author's running deployment. Keep personal profiles, transcripts, credentials, and project memory in your private workspace.

LIMO helps preserve what was recorded. It cannot guarantee that every relevant fact was captured or that an agent follows every instruction. Current user corrections and verified evidence should resolve conflicts with stale memory.
