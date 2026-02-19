#!/usr/bin/env bash
#
# Record an iteration update to a Wardley Map.
#
# Usage:
#   wm-iterate/scripts/record-update.sh --client CLIENT --engagement ENGAGEMENT \
#     --project PROJECT --title "TITLE" [--field "Key=Value" ...]
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/{slug}/decisions.json — Decision log (append)
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

REPO_DIR="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

CLIENT="" ENGAGEMENT="" PROJECT="" TITLE=""
FIELDS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)     CLIENT="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --project)    PROJECT="$2"; shift 2 ;;
    --title)   TITLE="$2"; shift 2 ;;
    --field)   FIELDS+=("$2"); shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$ENGAGEMENT" || -z "$PROJECT" || -z "$TITLE" ]]; then
  echo "Usage: $0 --client CLIENT --engagement ENGAGEMENT --project PROJECT --title TITLE [--field Key=Value ...]" >&2
  exit 1
fi

CMD=(uv run --project "$REPO_DIR" practice decision record \
  --client "$CLIENT" --engagement "$ENGAGEMENT" --project "$PROJECT" \
  --title "$TITLE")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
exec "${CMD[@]}"
