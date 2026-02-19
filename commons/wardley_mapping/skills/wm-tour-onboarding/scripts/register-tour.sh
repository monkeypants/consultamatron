#!/usr/bin/env bash
#
# Register the onboarding tour manifest for a Wardley Mapping project.
#
# Usage:
#   wm-tour-onboarding/scripts/register-tour.sh --client CLIENT --project PROJECT \
#     --title "TITLE" --stops 'JSON_ARRAY'
#
# The --stops argument is a JSON array of tour stops. Each stop must have
# order, title, and atlas_source fields:
#   [{"order":"1","title":"The landscape","atlas_source":"atlas/overview/"}]
#
# Files modified by this script:
#   clients/{client}/projects/{slug}/presentations/onboarding/manifest.json
#     — Tour manifest (replaced entirely on each call)
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

REPO_DIR="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

CLIENT="" PROJECT="" TITLE="" STOPS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)  CLIENT="$2"; shift 2 ;;
    --project) PROJECT="$2"; shift 2 ;;
    --title)   TITLE="$2"; shift 2 ;;
    --stops)   STOPS="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$PROJECT" || -z "$TITLE" || -z "$STOPS" ]]; then
  echo "Usage: $0 --client CLIENT --project PROJECT --title TITLE --stops JSON" >&2
  exit 1
fi

exec uv run --project "$REPO_DIR" practice tour register \
  --client "$CLIENT" \
  --project "$PROJECT" \
  --name onboarding \
  --title "$TITLE" \
  --stops "$STOPS"
