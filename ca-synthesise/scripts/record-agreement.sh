#!/usr/bin/env bash
#
# Record that the audit report has been agreed and advance the project
# to implementation.
#
# Usage:
#   ca-synthesise/scripts/record-agreement.sh --client CLIENT \
#     --engagement ENGAGEMENT --project PROJECT \
#     --field "Recommendations=..." --field "Phases=..."
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/{slug}/decisions.json — Decision log (append:
#                                                                      "Stage 9: Audit report agreed")
#   clients/{client}/engagements/{engagement}/projects.json        — Project registry
#                                                                      (status -> implementation)
#
# The files listed above are JSON documents managed by the consultamatron
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

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

CLI="uv run --project $REPO_DIR consultamatron"

# Record the audit report agreement decision
CMD=($CLI decision record \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" \
  --title "Stage 9: Audit report agreed" \
  --field "Agreed=Final audit report signed off by client")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
"${CMD[@]}"

# Terminal interactive gate — transition to implementation
$CLI project update-status \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" --status implementation
