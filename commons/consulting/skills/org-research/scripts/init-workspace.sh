#!/usr/bin/env bash
#
# Initialize a new client workspace with structured accounting files.
#
# Usage:
#   org-research/scripts/init-workspace.sh --client CLIENT
#
# Files modified by this script:
#   clients/{client}/projects/index.json   — Project registry (created empty)
#   clients/{client}/engagement.json       — Engagement log (created with
#                                            "Client onboarded" entry)
#   clients/{client}/resources/index.json  — Research topic manifest (created empty)
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

CLIENT=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client) CLIENT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" ]]; then
  echo "Usage: $0 --client CLIENT" >&2
  exit 1
fi

exec uv run --project "$REPO_DIR" practice project init --client "$CLIENT"
