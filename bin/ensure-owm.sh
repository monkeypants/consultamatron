#!/usr/bin/env bash
#
# Ensure cli-owm is available. Installs via npm if missing.
# Renders an OWM file to SVG if a path is given.
#
# Usage:
#   bin/ensure-owm.sh                  # just check / install
#   bin/ensure-owm.sh map.owm          # check / install, then render to SVG

set -euo pipefail

if command -v owm >/dev/null 2>&1; then
    : # already installed globally
elif npx --no-install cli-owm --version >/dev/null 2>&1; then
    : # available via npx cache
else
    echo "cli-owm not found. Installing..."
    npm install -g cli-owm
fi

if [ $# -gt 0 ]; then
    input="$1"
    output="${input%.owm}.svg"
    if command -v owm >/dev/null 2>&1; then
        owm "$input" -w 1000 -H 1200 -o "$output"
    else
        npx cli-owm "$input" -w 1000 -H 1200 -o "$output"
    fi
    echo "$output"
fi
