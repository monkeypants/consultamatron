#!/usr/bin/env bash
#
# Record that the Business Model Canvas project brief has been agreed
# and activate the project.
#
# Usage:
#   bmc-research/scripts/record-brief-agreed.sh --client CLIENT --engagement ENGAGEMENT \
#     --project PROJECT --field "Scope=..." --field "Focus areas=..."
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/{slug}/decisions.json — Decision log (append:
#                                                                      "Stage 1: Project brief agreed")
#   clients/{client}/engagements/{engagement}/projects.json        — Project registry
#                                                                      (status -> elaboration)
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

# Record the brief agreement decision
CMD=($CLI decision record \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" \
  --title "Stage 1: Project brief agreed" \
  --field "Agreed=Business Model Canvas project scope signed off by client")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
"${CMD[@]}"

# Activate the project
$CLI project update-status \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" --status elaboration
