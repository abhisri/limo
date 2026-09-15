#!/usr/bin/env bash
# Claude Code SessionStart hook (LIMO v2.5): regenerate the pack, print Part A, remind about the banner.
set -u
. "$(dirname "$0")/limo-common.sh"
root="$(limo_root)" || exit 0
dom="$(limo_domain "$root")" || exit 0
cd "$root" || exit 0
python3 tools/limo_lint.py bootpack "$dom" >/dev/null 2>&1
echo "[LIMO] Domain $dom. Read $dom/limo-populated/core/BOOT_PACK.md first. Start your first reply with: [LIMO: $dom booted from BOOT_PACK $(date +%F)]"
