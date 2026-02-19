#!/usr/bin/env bash
#
# Update a project's status in the registry.
#
# Usage:
#   engage/scripts/update-status.sh --client CLIENT --engagement ENGAGEMENT \
#     --project PROJECT --status STATUS
#
# STATUS must be one of: planning, elaboration, implementation, review, closed
# Transitions are strictly ordered: planning -> elaboration -> implementation -> review -> closed
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/projects.json  — Project registry (status field updated)
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

REPO_DIR="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

CLIENT="" ENGAGEMENT="" PROJECT="" STATUS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)     CLIENT="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --project)    PROJECT="$2"; shift 2 ;;
    --status)  STATUS="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$ENGAGEMENT" || -z "$PROJECT" || -z "$STATUS" ]]; then
  echo "Usage: $0 --client CLIENT --engagement ENGAGEMENT --project PROJECT --status STATUS" >&2
  exit 1
fi

exec uv run --project "$REPO_DIR" practice project update-status \
  --client "$CLIENT" \
  --engagement "$ENGAGEMENT" \
  --project "$PROJECT" \
  --status "$STATUS"
