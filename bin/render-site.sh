#!/usr/bin/env bash
#
# Generate a static HTML site from a client workspace.
#
# Usage:
#   bin/render-site.sh clients/{org-slug}/
#
# Thin wrapper around the Python renderer.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

exec uv run --project "$REPO_DIR" python "$SCRIPT_DIR/render_site.py" "$@"
