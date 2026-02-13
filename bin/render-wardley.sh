#!/usr/bin/env bash
#
# Render a Wardley Mapping project into HTML pages.
#
# Called by render-site.sh with the project directory and site output dir.
# Not intended to be run standalone.
#
# Usage:
#   bin/render-wardley.sh <project-dir> <site-project-dir> <org-name>
#
# Requires: pandoc, node (for OWM rendering)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

PROJECT="$1"
SITE_DIR="$2"
ORG_NAME="$3"
PROJECT_NAME="$(basename "$PROJECT")"

mkdir -p "$SITE_DIR"

# Source shared helpers
. "$SCRIPT_DIR/site-helpers.sh"

# ── Detect completed stages ──────────────────────────────────────────

HAS_BRIEF=false
HAS_NEEDS=false
HAS_CHAIN=false
HAS_EVOLVE=false
HAS_STRATEGY=false

[ -f "$PROJECT/brief.agreed.md" ]                && HAS_BRIEF=true
[ -f "$PROJECT/needs/needs.agreed.md" ]          && HAS_NEEDS=true
[ -f "$PROJECT/chain/supply-chain.agreed.md" ]   && HAS_CHAIN=true
[ -f "$PROJECT/evolve/map.agreed.owm" ]          && HAS_EVOLVE=true
[ -f "$PROJECT/strategy/map.agreed.owm" ]        && HAS_STRATEGY=true

echo "    Stages: brief=$HAS_BRIEF needs=$HAS_NEEDS chain=$HAS_CHAIN evolve=$HAS_EVOLVE strategy=$HAS_STRATEGY"

# ── Render OWM → SVG ────────────────────────────────────────────────

while IFS= read -r owm_file; do
    [ -z "$owm_file" ] && continue
    svg_file="${owm_file%.owm}.svg"
    if [ ! -f "$svg_file" ] || [ "$owm_file" -nt "$svg_file" ]; then
        echo "    Rendering $owm_file → SVG"
        "$SCRIPT_DIR/ensure-owm.sh" "$owm_file" >/dev/null
    fi
done <<EOF
$(find "$PROJECT" -name '*.owm' -type f 2>/dev/null)
EOF

# ── Navigation ───────────────────────────────────────────────────────

nav_html() {
    local active="$1"
    local nav='<nav>'

    nav="$nav <a href=\"index.html\""
    [ "$active" = "index" ] && nav="$nav class=\"active\""
    nav="$nav>Overview</a>"

    if [ "$HAS_STRATEGY" = true ]; then
        nav="$nav <a href=\"strategy.html\""
        [ "$active" = "strategy" ] && nav="$nav class=\"active\""
        nav="$nav>Strategy</a>"
    fi

    if [ "$HAS_EVOLVE" = true ]; then
        nav="$nav <a href=\"map.html\""
        [ "$active" = "map" ] && nav="$nav class=\"active\""
        nav="$nav>Map</a>"
    fi

    if [ "$HAS_CHAIN" = true ]; then
        nav="$nav <a href=\"supply-chain.html\""
        [ "$active" = "supply-chain" ] && nav="$nav class=\"active\""
        nav="$nav>Supply Chain</a>"
    fi

    if [ "$HAS_NEEDS" = true ]; then
        nav="$nav <a href=\"needs.html\""
        [ "$active" = "needs" ] && nav="$nav class=\"active\""
        nav="$nav>Needs</a>"
    fi

    if [ "$HAS_BRIEF" = true ]; then
        nav="$nav <a href=\"brief.html\""
        [ "$active" = "brief" ] && nav="$nav class=\"active\""
        nav="$nav>Brief</a>"
    fi

    if [ -f "$PROJECT/decisions.md" ]; then
        nav="$nav <a href=\"decisions.html\""
        [ "$active" = "decisions" ] && nav="$nav class=\"active\""
        nav="$nav>Decisions</a>"
    fi

    nav="$nav</nav>"
    echo "$nav"
}

wrap_page() {
    local title="$1"
    local active="$2"
    local body
    body="$(cat)"
    local nav
    nav="$(nav_html "$active")"

    cat <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title — $PROJECT_NAME — $ORG_NAME</title>
<link rel="stylesheet" href="../style.css">
</head>
<body>
$nav
<h1>$title</h1>
$body
</body>
</html>
HTMLEOF
}

# ── Generate pages ───────────────────────────────────────────────────

# Index page
{
    if [ "$HAS_STRATEGY" = true ] && [ -f "$PROJECT/strategy/map.svg" ]; then
        embed_svg "$PROJECT/strategy/map.svg" "Strategy map"
    elif [ "$HAS_EVOLVE" = true ] && [ -f "$PROJECT/evolve/map.svg" ]; then
        embed_svg "$PROJECT/evolve/map.svg" "Evolution map"
    elif [ -f "$PROJECT/landscape.svg" ]; then
        embed_svg "$PROJECT/landscape.svg" "Landscape sketch (approximate)"
    fi

    if [ -f "$PROJECT/decisions.md" ]; then
        cat "$PROJECT/decisions.md" | md_to_html
    fi
} | wrap_page "Overview" "index" > "$SITE_DIR/index.html"
echo "    index.html"

# Brief page
if [ "$HAS_BRIEF" = true ]; then
    cat "$PROJECT/brief.agreed.md" | md_to_html | wrap_page "Project Brief" "brief" > "$SITE_DIR/brief.html"
    echo "    brief.html"
fi

# Decisions page
if [ -f "$PROJECT/decisions.md" ]; then
    cat "$PROJECT/decisions.md" | md_to_html | wrap_page "Decisions" "decisions" > "$SITE_DIR/decisions.html"
    echo "    decisions.html"
fi

# Needs page
if [ "$HAS_NEEDS" = true ]; then
    cat "$PROJECT/needs/needs.agreed.md" | md_to_html | wrap_page "User Needs" "needs" > "$SITE_DIR/needs.html"
    echo "    needs.html"
fi

# Supply chain page
if [ "$HAS_CHAIN" = true ]; then
    cat "$PROJECT/chain/supply-chain.agreed.md" | md_to_html | wrap_page "Supply Chain" "supply-chain" > "$SITE_DIR/supply-chain.html"
    echo "    supply-chain.html"
fi

# Map page (evolve)
if [ "$HAS_EVOLVE" = true ]; then
    {
        if [ -f "$PROJECT/evolve/map.svg" ]; then
            embed_svg "$PROJECT/evolve/map.svg" "Evolution map"
        fi
        if [ -d "$PROJECT/evolve/assessments" ]; then
            for assess_file in "$PROJECT/evolve/assessments/"*.md; do
                [ -f "$assess_file" ] || continue
                cat "$assess_file" | md_to_html
                echo "<hr>"
            done
        fi
    } | wrap_page "Evolution Map" "map" > "$SITE_DIR/map.html"
    echo "    map.html"
fi

# Strategy page
if [ "$HAS_STRATEGY" = true ]; then
    {
        if [ -f "$PROJECT/strategy/map.svg" ]; then
            embed_svg "$PROJECT/strategy/map.svg" "Strategy map"
        fi
        if [ -d "$PROJECT/strategy/plays" ]; then
            for play_file in "$PROJECT/strategy/plays/"*.md; do
                [ -f "$play_file" ] || continue
                cat "$play_file" | md_to_html
                echo "<hr>"
            done
        fi
    } | wrap_page "Strategy" "strategy" > "$SITE_DIR/strategy.html"
    echo "    strategy.html"
fi
