#!/usr/bin/env bash
# Shared helpers for LIMO hooks. Sourced, not executed.
# Finds the workspace root (folder containing tools/limo_lint.py) and the current domain from $PWD or $CLAUDE_PROJECT_DIR.
limo_root() {
  local d="${CLAUDE_PROJECT_DIR:-$PWD}"
  while [ "$d" != "/" ]; do
    [ -f "$d/tools/limo_lint.py" ] && { echo "$d"; return 0; }
    d="$(dirname "$d")"
  done
  return 1
}
limo_domain() {  # first path segment below root that has limo-populated/core
  local root="$1" d="${CLAUDE_PROJECT_DIR:-$PWD}"
  case "$d" in "$root"/*) ;; *) return 1;; esac
  local rel="${d#$root/}"
  local first="${rel%%/*}"
  [ -d "$root/$first/limo-populated/core" ] && { echo "$first"; return 0; }
  return 1
}
