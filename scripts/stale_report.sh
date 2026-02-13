#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-.}"
grep -R --line-number "Freshness target" "$ROOT" || true
