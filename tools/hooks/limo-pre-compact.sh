#!/usr/bin/env bash
# Claude Code PreCompact hook (LIMO v2.5, M5): context is about to be summarised — flush now.
set -u
. "$(dirname "$0")/limo-common.sh"
root="$(limo_root)" || exit 0
dom="$(limo_domain "$root")" || exit 0
(cd "$root" && python3 tools/limo_lint.py bootpack "$dom" >/dev/null 2>&1)
cat <<MSG
[LIMO] Context compaction imminent in domain "$dom". Before anything else: (1) update STATUS_SNAPSHOT.md "What's next (top 3)" and "Blockers", (2) add one milestone line to SESSION_DIARY.md (or event_log at Infra level), (3) run: python3 tools/limo_lint.py commit "$dom" --agent claude-code --trigger "pre-compact flush". Assume interruption.
MSG
