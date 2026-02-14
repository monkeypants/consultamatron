#!/usr/bin/env bash
#
# Generate a static HTML site from a client workspace.
#
# Usage:
#   bin/render-site.sh clients/{org-slug}/
#
# Thin wrapper: extracts the client slug and calls the CLI.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Extract client slug from path like "clients/duckitandrun/"
CLIENT="$(basename "${1%/}")"

exec uv run --project "$REPO_DIR" consultamatron site render "$CLIENT"
