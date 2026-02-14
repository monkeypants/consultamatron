#!/usr/bin/env bash
#
# Record that the strategy map has been agreed for a Wardley Mapping project.
#
# Usage:
#   wm-strategy/scripts/record-agreement.sh --client CLIENT --project PROJECT \
#     --field "Key plays=..." --field "Priorities=..." --field "Deferred=..."
#
# Files modified by this script:
#   clients/{client}/projects/{slug}/decisions.json  — Decision log (append:
#                                                      "Stage 5: Strategy map agreed")
#
# The files listed above are JSON documents managed by the consultamatron
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

CLIENT="" PROJECT=""
FIELDS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)  CLIENT="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --field)   FIELDS+=("$2"); shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$PROJECT" ]]; then
  echo "Usage: $0 --client CLIENT --project PROJECT [--field Key=Value ...]" >&2
  exit 1
fi

CMD=(uv run --project "$REPO_DIR" consultamatron decision record \
  --client "$CLIENT" --project "$PROJECT" \
  --title "Stage 5: Strategy map agreed" \
  --field "Agreed=Strategy-annotated Wardley Map signed off")
for f in "${FIELDS[@]}"; do
  CMD+=(--field "$f")
done
exec "${CMD[@]}"
