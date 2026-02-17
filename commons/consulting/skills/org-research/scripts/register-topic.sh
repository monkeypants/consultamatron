#!/usr/bin/env bash
#
# Register a research topic in the client's structured manifest.
#
# Usage:
#   org-research/scripts/register-topic.sh --client CLIENT \
#     --topic TOPIC --filename FILENAME --confidence CONFIDENCE
#
# CONFIDENCE must be one of: High, Medium-High, Medium, Low
#
# Files modified by this script:
#   clients/{client}/resources/index.json  — Research topic manifest (append)
#
# The files listed above are JSON documents managed by the practice
# CLI (bin/cli/). Agents may read these files directly for inspection.
# Do not edit them by hand — use the CLI to ensure validation, timestamps,
# and cross-file consistency are maintained.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

CLIENT="" TOPIC="" FILENAME="" CONFIDENCE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)     CLIENT="$2"; shift 2 ;;
    --topic)      TOPIC="$2"; shift 2 ;;
    --filename)   FILENAME="$2"; shift 2 ;;
    --confidence) CONFIDENCE="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [[ -z "$CLIENT" || -z "$TOPIC" || -z "$FILENAME" || -z "$CONFIDENCE" ]]; then
  echo "Usage: $0 --client CLIENT --topic TOPIC --filename FILENAME --confidence CONFIDENCE" >&2
  exit 1
fi

exec uv run --project "$REPO_DIR" practice research add \
  --client "$CLIENT" \
  --topic "$TOPIC" \
  --filename "$FILENAME" \
  --confidence "$CONFIDENCE"
