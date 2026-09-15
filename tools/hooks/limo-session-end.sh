#!/usr/bin/env bash
# Claude Code SessionEnd hook (LIMO v2.5, M5): regenerate the pack and commit whatever the session wrote.
set -u
. "$(dirname "$0")/limo-common.sh"
root="$(limo_root)" || exit 0
dom="$(limo_domain "$root")" || exit 0
cd "$root" || exit 0
python3 tools/limo_lint.py all "$dom" >/dev/null 2>&1
python3 tools/limo_lint.py commit "$dom" --agent claude-code --trigger "session end" >/dev/null 2>&1 || true
