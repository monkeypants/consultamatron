#!/usr/bin/env bash
#
# Register a new consulting project for a client.
#
# Usage:
#   engage/scripts/register-project.sh --client CLIENT --engagement ENGAGEMENT \
#     --slug SLUG --skillset SKILLSET --scope "SCOPE" [--notes "NOTES"]
#
# Files modified by this script:
#   clients/{client}/engagements/{engagement}/projects.json       — Project registry (append)
#   clients/{client}/engagements/{engagement}/{slug}/decisions.json — Decision log (created with
#                                                                     "Project created" entry)
#   clients/{client}/engagements/{engagement}/engagement-log.json — Engagement log (append)
#
# The files listed above are JSON documents managed by the consultamatron
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

CLIENT="" ENGAGEMENT="" SLUG="" SKILLSET="" SCOPE="" NOTES=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)     CLIENT="$2"; shift 2 ;;
    --engagement) ENGAGEMENT="$2"; shift 2 ;;
    --slug)       SLUG="$2"; shift 2 ;;
    --skillset) SKILLSET="$2"; shift 2 ;;
    --scope)    SCOPE="$2"; shift 2 ;;
    --notes)    NOTES="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$ENGAGEMENT" || -z "$SLUG" || -z "$SKILLSET" || -z "$SCOPE" ]]; then
  echo "Usage: $0 --client CLIENT --engagement ENGAGEMENT --slug SLUG --skillset SKILLSET --scope SCOPE [--notes NOTES]" >&2
  exit 1
fi

exec uv run --project "$REPO_DIR" consultamatron project register \
  --client "$CLIENT" \
  --engagement "$ENGAGEMENT" \
  --slug "$SLUG" \
  --skillset "$SKILLSET" \
  --scope "$SCOPE" \
  --notes "$NOTES"
