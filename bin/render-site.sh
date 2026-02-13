#!/usr/bin/env bash
#
# Generate a static HTML site from a client workspace.
#
# Usage:
#   bin/render-site.sh clients/{org-slug}/
#
# Reads the project registry, dispatches to per-skillset renderers,
# and generates client-level pages (resources, engagement, project index).
#
# Requires: pandoc, node (for OWM rendering in Wardley projects)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Phase 0: Parse args, validate workspace ──────────────────────────

if [ $# -lt 1 ]; then
    echo "Usage: $0 <workspace-path>" >&2
    exit 1
fi

WS="${1%/}"

if [ ! -d "$WS" ]; then
    echo "Error: workspace directory not found: $WS" >&2
    exit 1
fi

if [ ! -f "$WS/resources/index.md" ]; then
    echo "Error: no resources/index.md in workspace. Run org-research first." >&2
    exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
    echo "Error: pandoc is required but not found." >&2
    echo "Install: brew install pandoc  (macOS) or apt install pandoc  (Debian/Ubuntu)" >&2
    exit 1
fi

# Extract org display name from engagement.md H1, fallback to directory name
ORG_NAME=""
if [ -f "$WS/engagement.md" ]; then
    ORG_NAME="$(sed -n 's/^# .*— *//p' "$WS/engagement.md" | head -1)"
fi
if [ -z "$ORG_NAME" ]; then
    ORG_NAME="$(basename "$WS")"
fi

SITE="$WS/site"

# Source shared helpers
. "$SCRIPT_DIR/site-helpers.sh"

# ── Phase 1: Build site directory ────────────────────────────────────

rm -rf "$SITE"
mkdir -p "$SITE/resources"
cp "$SCRIPT_DIR/site.css" "$SITE/style.css"

echo "Workspace: $WS ($ORG_NAME)"

# ── Phase 2: Client-level navigation ────────────────────────────────

# Collect project list for navigation
PROJECTS=""
if [ -d "$WS/projects" ]; then
    for proj_dir in "$WS/projects"/*/; do
        [ -d "$proj_dir" ] || continue
        proj_name="$(basename "$proj_dir")"
        [ "$proj_name" = "site" ] && continue
        PROJECTS="$PROJECTS $proj_name"
    done
fi

client_nav_html() {
    local active="$1"
    local nav='<nav>'

    nav="$nav <a href=\"index.html\""
    [ "$active" = "index" ] && nav="$nav class=\"active\""
    nav="$nav>Overview</a>"

    nav="$nav <a href=\"resources.html\""
    [ "$active" = "resources" ] && nav="$nav class=\"active\""
    nav="$nav>Research</a>"

    for proj_name in $PROJECTS; do
        nav="$nav <a href=\"$proj_name/index.html\""
        [ "$active" = "$proj_name" ] && nav="$nav class=\"active\""
        nav="$nav>$proj_name</a>"
    done

    if [ -f "$WS/engagement.md" ]; then
        nav="$nav <a href=\"engagement.html\""
        [ "$active" = "engagement" ] && nav="$nav class=\"active\""
        nav="$nav>Engagement</a>"
    fi

    nav="$nav</nav>"
    echo "$nav"
}

wrap_client_page() {
    local title="$1"
    local active="$2"
    local body
    body="$(cat)"
    local nav
    nav="$(client_nav_html "$active")"

    cat <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title — $ORG_NAME</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
$nav
<h1>$title</h1>
$body
</body>
</html>
HTMLEOF
}

wrap_research_subpage() {
    local title="$1"
    local body
    body="$(cat)"
    local nav
    nav="$(client_nav_html "resources")"
    nav="$(echo "$nav" | sed 's|href="|href="../|g')"

    cat <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title — $ORG_NAME</title>
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

# ── Phase 3: Generate client-level pages ─────────────────────────────

echo "Generating client pages..."

# Index page
{
    if [ -f "$WS/engagement.md" ]; then
        cat "$WS/engagement.md" | md_to_html
    fi
    if [ -f "$WS/projects/index.md" ]; then
        echo "<h2>Projects</h2>"
        cat "$WS/projects/index.md" | md_to_html
    fi
} | wrap_client_page "Overview" "index" > "$SITE/index.html"
echo "  index.html"

# Engagement page
if [ -f "$WS/engagement.md" ]; then
    cat "$WS/engagement.md" | md_to_html | wrap_client_page "Engagement History" "engagement" > "$SITE/engagement.html"
    echo "  engagement.html"
fi

# Research pages
TASK_LIST=""
TASK_COUNT=0
for res_file in "$WS/resources/"*.md; do
    [ -f "$res_file" ] || continue
    slug="$(basename "$res_file" .md)"
    [ "$slug" = "index" ] && continue
    res_title="$(sed -n 's/^# *//p' "$res_file" | head -1)"
    if [ -z "$res_title" ]; then
        res_title="$slug"
    fi
    TASK_LIST="$TASK_LIST$slug|$res_title
"
    TASK_COUNT=$((TASK_COUNT + 1))
done

research_toc() {
    local prefix="$1"
    local active_slug="$2"
    echo '<nav class="toc" aria-label="Research sections">'
    echo '<ol>'
    if [ -z "$active_slug" ]; then
        echo "<li class=\"active\">Synthesis</li>"
    else
        echo "<li><a href=\"${prefix}resources.html\">Synthesis</a></li>"
    fi
    echo "$TASK_LIST" | while IFS='|' read -r slug title; do
        [ -z "$slug" ] && continue
        if [ "$slug" = "$active_slug" ]; then
            echo "<li class=\"active\">$title</li>"
        else
            echo "<li><a href=\"${prefix}resources/$slug.html\">$title</a></li>"
        fi
    done
    echo '</ol>'
    echo '</nav>'
}

# Research summary page
{
    research_toc "" ""
    cat "$WS/resources/index.md" | md_to_html
} | wrap_client_page "Research" "resources" > "$SITE/resources.html"
echo "  resources.html"

# Research sub-pages
echo "$TASK_LIST" | while IFS='|' read -r slug title; do
    [ -z "$slug" ] && continue
    {
        research_toc "../" "$slug"
        cat "$WS/resources/$slug.md" | md_to_html
    } | wrap_research_subpage "$title" > "$SITE/resources/$slug.html"
    echo "  resources/$slug.html"
done

# ── Phase 4: Render projects ────────────────────────────────────────

for proj_name in $PROJECTS; do
    proj_dir="$WS/projects/$proj_name"
    site_proj_dir="$SITE/$proj_name"

    echo ""
    echo "Project: $proj_name"

    # Detect skillset from project slug convention or brief
    skillset=""
    case "$proj_name" in
        maps-*|map-*|wardley-*) skillset="wardley" ;;
        canvas-*|bmc-*)         skillset="bmc" ;;
    esac

    # Fallback: check for skillset-specific artifacts
    if [ -z "$skillset" ]; then
        if [ -d "$proj_dir/needs" ] || [ -d "$proj_dir/chain" ] || [ -d "$proj_dir/evolve" ]; then
            skillset="wardley"
        elif [ -d "$proj_dir/segments" ] || [ -f "$proj_dir/canvas.md" ] || [ -f "$proj_dir/canvas.agreed.md" ]; then
            skillset="bmc"
        fi
    fi

    case "$skillset" in
        wardley)
            "$SCRIPT_DIR/render-wardley.sh" "$proj_dir" "$site_proj_dir" "$ORG_NAME"
            ;;
        bmc)
            "$SCRIPT_DIR/render-bmc.sh" "$proj_dir" "$site_proj_dir" "$ORG_NAME"
            ;;
        *)
            echo "    Unknown skillset for $proj_name, skipping"
            ;;
    esac
done

echo ""
echo "Site generated: $SITE/"
echo "Open: $SITE/index.html"
