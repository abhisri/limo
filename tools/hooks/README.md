# LIMO hooks (v2.5)

Shell hooks that make the write-back loop fire from the harness instead of from the agent's memory.
Standard library only; they call `tools/limo_lint.py`. They are no-ops outside a LIMO workspace or outside a domain folder.

| Hook | Claude Code event | Does |
|:--|:--|:--|
| `limo-session-start.sh` | `SessionStart` | regenerates BOOT_PACK for the current domain, prints the boot reminder and the banner line |
| `limo-user-prompt.sh` | `UserPromptSubmit` | runs `triggers "<prompt>" <Domain>` and injects every matching NEVER_AGAIN / INVARIANT in full (M2) |
| `limo-pre-compact.sh` | `PreCompact` | regenerates the pack and injects the "assume interruption" flush instruction (M5) |
| `limo-session-end.sh` | `SessionEnd` | `all` + `commit` for the current domain (M5, M7) |

Domain detection: the first folder below the workspace root that contains `limo-populated/core/`, based on `$CLAUDE_PROJECT_DIR` or `$PWD`.
Start Claude Code inside the domain folder (e.g. `cd ~/Downloads/CLAUDE-PROJECTS/Venture && claude`) for the hooks to know the domain.

## Wiring (`~/.claude/settings.json` or `<workspace>/.claude/settings.json`)

```json
{
  "hooks": {
    "SessionStart":     [{"hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/tools/hooks/limo-session-start.sh\""}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/tools/hooks/limo-user-prompt.sh\""}]}],
    "PreCompact":       [{"hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/tools/hooks/limo-pre-compact.sh\""}]}],
    "SessionEnd":       [{"hooks": [{"type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/tools/hooks/limo-session-end.sh\""}]}]
  }
}
```

If `$CLAUDE_PROJECT_DIR` is a domain folder rather than the workspace root, use the absolute path
`/path/to/your/workspace/tools/hooks/…` in the command strings instead.
Make the scripts executable once: `chmod +x tools/hooks/*.sh`.

## Codex / other agents

Codex reads `limo-populated/AGENTS.md` (generated) which tells it to run `triggers` itself before acting and to use
`limo_lint.py commit` for memory writes. There is no hook system to wire; the instruction is the mechanism.
primary-agent sessions do the same by instruction (`AI_AGENTS_READ_THIS_FIRST.md`).
