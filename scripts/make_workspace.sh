#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./scripts/make_workspace.sh <workspace_name> [pack1 pack2 ...]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WS_DIR="$ROOT_DIR/workspaces/${1:-}"
shift || true

if [[ -z "${WS_DIR}" ]]; then
  echo "Workspace name required."
  exit 1
fi

mkdir -p "$WS_DIR"
cp -R "$ROOT_DIR/core/." "$WS_DIR/"

for pack in "$@"; do
  if [[ -d "$ROOT_DIR/packs/$pack" ]]; then
    mkdir -p "$WS_DIR/packs/$pack"
    cp -R "$ROOT_DIR/packs/$pack/." "$WS_DIR/packs/$pack/"
  else
    echo "Unknown pack: $pack"
    exit 1
  fi
done

echo "Created workspace at: $WS_DIR"
