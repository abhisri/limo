#!/usr/bin/env bash
# Claude Code SessionStart hook (LIMO v2.5): regenerate the pack, print the boot reminder, the banner line and the attribution tag.
# stdin: {"session_id": "...", "cwd": "...", ...}
set -u
. "$(dirname "$0")/limo-common.sh"
root="$(limo_root)" || exit 0
dom="$(limo_domain "$root")" || exit 0
sid="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("session_id","")[:8])' 2>/dev/null)"
model="${LIMO_MODEL:-${ANTHROPIC_MODEL:-unknown}}"
agent="${LIMO_AGENT:-claude-code/$model}"
cd "$root" || exit 0
python3 tools/limo_lint.py bootpack "$dom" >/dev/null 2>&1
echo "[LIMO] Domain $dom. Read $dom/limo-populated/core/BOOT_PACK.md first. Start your first reply with: [LIMO: $dom booted from BOOT_PACK $(date +%F)]"
echo "[LIMO] Sign every entry and diary line you write with: {agent: $agent} {source: session:${sid:-unknown}}  — and use --agent \"$agent\" on limo_lint.py commit. If the model part is 'unknown', replace it with the model you are running as."
