#!/usr/bin/env bash
#
# Record that user needs have been agreed for a Wardley Mapping project.
#
# Usage:
#   wm-needs/scripts/record-agreement.sh --client CLIENT --engagement ENGAGEMENT \
#     --project PROJECT --field "Users=..." --field "Scope=..."
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/{slug}/decisions.json — Decision log (append:
#                                                                      "Stage 2: User needs agreed")
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

REPO_DIR="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

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

CMD=(uv run --project "$REPO_DIR" practice decision record \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" \
  --title "Stage 2: User needs agreed" \
  --field "Agreed=User needs document signed off by client")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
exec "${CMD[@]}"
