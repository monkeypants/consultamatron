#!/usr/bin/env bash
#
# Record that a post-implementation review has been completed.
# Logs the review in the engagement history and marks the project
# as reviewed.
#
# Usage:
#   review/scripts/record-review.sh --client CLIENT --engagement ENGAGEMENT \
#     --project PROJECT \
#     --field "Projects reviewed=..." --field "Issues raised=..." \
#     --field "Key findings=..."
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/engagement-log.json — Engagement log (append:
#                                                                    "Post-implementation review")
#   clients/{client}/engagements/{engagement}/projects.json       — Project registry
#                                                                    (status -> reviewed)
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

REPO_DIR="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
CLI="uv run --project $REPO_DIR practice"

CLIENT="" ENGAGEMENT="" PROJECT=""
FIELDS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)     CLIENT="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --project)    PROJECT="$2"; shift 2 ;;
    --field)   FIELDS+=("$2"); shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$ENGAGEMENT" || -z "$PROJECT" ]]; then
  echo "Usage: $0 --client CLIENT --engagement ENGAGEMENT --project PROJECT [--field Key=Value ...]" >&2
  exit 1
fi

# Log the review in engagement history
CMD=($CLI engagement add \
  --client "$CLIENT" --engagement "$ENGAGEMENT" \
  --title "Post-implementation review")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
"${CMD[@]}"

# Mark the project as reviewed
$CLI project update-status \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" --status review
