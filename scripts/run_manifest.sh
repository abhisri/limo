#!/usr/bin/env bash
set -euo pipefail
TS="$(date '+%Y%m%d_%H%M%S')"
OUT="${1:-run_manifest_${TS}.json}"
cat > "$OUT" <<EOF
{
  "timestamp": "$(date '+%Y-%m-%d %H:%M %Z')",
  "inputs": [],
  "outputs": [],
  "warnings": [],
  "tool_versions": {}
}
EOF
echo "Wrote $OUT"
