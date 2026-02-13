#!/usr/bin/env bash
#
# Render a Business Model Canvas project into HTML pages.
#
# Called by render-site.sh with the project directory and site output dir.
# Not intended to be run standalone.
#
# Usage:
#   bin/render-bmc.sh <project-dir> <site-project-dir> <org-name>
#
# Requires: pandoc

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
HAS_SEGMENTS=false
HAS_CANVAS=false

[ -f "$PROJECT/brief.agreed.md" ]              && HAS_BRIEF=true
[ -f "$PROJECT/segments/segments.agreed.md" ]  && HAS_SEGMENTS=true
[ -f "$PROJECT/canvas.agreed.md" ]             && HAS_CANVAS=true

echo "    Stages: brief=$HAS_BRIEF segments=$HAS_SEGMENTS canvas=$HAS_CANVAS"

# ── Navigation ───────────────────────────────────────────────────────

nav_html() {
    local active="$1"
    local nav='<nav>'

    nav="$nav <a href=\"index.html\""
    [ "$active" = "index" ] && nav="$nav class=\"active\""
    nav="$nav>Overview</a>"

    if [ "$HAS_CANVAS" = true ]; then
        nav="$nav <a href=\"canvas.html\""
        [ "$active" = "canvas" ] && nav="$nav class=\"active\""
        nav="$nav>Canvas</a>"
    fi

    if [ "$HAS_SEGMENTS" = true ]; then
        nav="$nav <a href=\"segments.html\""
        [ "$active" = "segments" ] && nav="$nav class=\"active\""
        nav="$nav>Segments</a>"
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
<nav class="breadcrumb"><a href="../index.html">$ORG_NAME</a> &rsaquo; $PROJECT_NAME</nav>
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
    echo ""
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

# Segments page
if [ "$HAS_SEGMENTS" = true ]; then
    cat "$PROJECT/segments/segments.agreed.md" | md_to_html | wrap_page "Customer Segments" "segments" > "$SITE_DIR/segments.html"
    echo "    segments.html"
fi

# Canvas page
if [ "$HAS_CANVAS" = true ]; then
    cat "$PROJECT/canvas.agreed.md" | md_to_html | wrap_page "Business Model Canvas" "canvas" > "$SITE_DIR/canvas.html"
    echo "    canvas.html"
fi
