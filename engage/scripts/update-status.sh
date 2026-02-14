#!/usr/bin/env bash
#
# Update a project's status in the registry.
#
# Usage:
#   engage/scripts/update-status.sh --client CLIENT --project PROJECT --status STATUS
#
# STATUS must be one of: planned, active, complete, reviewed
# Transitions are strictly ordered: planned -> active -> complete -> reviewed
#
# Files modified by this script:
#   clients/{client}/projects/index.json  — Project registry (status field updated)
#
# The files listed above are JSON documents managed by the consultamatron
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

CLIENT="" PROJECT="" STATUS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)  CLIENT="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --status)  STATUS="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$PROJECT" || -z "$STATUS" ]]; then
  echo "Usage: $0 --client CLIENT --project PROJECT --status STATUS" >&2
  exit 1
fi

exec uv run --project "$REPO_DIR" consultamatron project update-status \
  --client "$CLIENT" \
  --project "$PROJECT" \
  --status "$STATUS"
