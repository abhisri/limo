#!/usr/bin/env bash
set -euo pipefail
DIR="${1:-.}"
OUT="${2:-EVIDENCE_INDEX.csv}"
echo "file_path,sha256" > "$OUT"
while IFS= read -r -d '' f; do
  h="$(sha256sum "$f" | awk '{print $1}')"
  echo ""$f",$h" >> "$OUT"
done < <(find "$DIR" -type f -print0)
echo "Wrote $OUT"
