#!/usr/bin/env bash
# Claude Code UserPromptSubmit hook (LIMO v2.5, M2): run `limo_lint.py triggers` on every prompt and inject the hits.
# stdin: {"prompt": "...", ...}   stdout: text is added to Claude's context.
set -u
. "$(dirname "$0")/limo-common.sh"
root="$(limo_root)" || exit 0
dom="$(limo_domain "$root")" || exit 0
prompt="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null)"
[ -n "$prompt" ] || exit 0
out="$(cd "$root" && python3 tools/limo_lint.py triggers "$prompt" "$dom" 2>/dev/null)"
case "$out" in *"no gate matches"*|"") exit 0;; esac
printf '%s\n' "$out"
