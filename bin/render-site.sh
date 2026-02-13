#!/usr/bin/env bash
#
# Generate a static HTML site from a Wardley Mapping workspace.
#
# Usage:
#   bin/render-site.sh maps/{org-slug}/
#
# Requires: pandoc, node (for OWM rendering)

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

if [ ! -f "$WS/1-research/summary.md" ]; then
    echo "Error: no 1-research/summary.md in workspace. Run wm-research first." >&2
    exit 1
fi

if ! command -v pandoc >/dev/null 2>&1; then
    echo "Error: pandoc is required but not found." >&2
    echo "Install: brew install pandoc  (macOS) or apt install pandoc  (Debian/Ubuntu)" >&2
    exit 1
fi

# Extract org display name from H1 of decisions.md, fallback to directory name
ORG_NAME=""
if [ -f "$WS/decisions.md" ]; then
    ORG_NAME="$(sed -n 's/^# .*— *//p' "$WS/decisions.md" | head -1)"
fi
if [ -z "$ORG_NAME" ]; then
    ORG_NAME="$(basename "$WS")"
fi

SITE="$WS/site"

# ── Phase 1: Detect completed stages ─────────────────────────────────

HAS_STAGE1=false
HAS_STAGE2=false
HAS_STAGE3=false
HAS_STAGE4=false
HAS_STAGE5=false

[ -f "$WS/1-research/summary.md" ]              && HAS_STAGE1=true
[ -f "$WS/2-needs/needs.agreed.md" ]             && HAS_STAGE2=true
[ -f "$WS/3-chain/supply-chain.agreed.md" ]      && HAS_STAGE3=true
[ -f "$WS/4-evolve/map.agreed.owm" ]             && HAS_STAGE4=true
[ -f "$WS/5-strategy/map.agreed.owm" ]           && HAS_STAGE5=true

echo "Workspace: $WS ($ORG_NAME)"
echo "Stages:  1=$HAS_STAGE1 2=$HAS_STAGE2 3=$HAS_STAGE3 4=$HAS_STAGE4 5=$HAS_STAGE5"

# ── Phase 2: Render OWM → SVG ────────────────────────────────────────

while IFS= read -r owm_file; do
    svg_file="${owm_file%.owm}.svg"
    if [ ! -f "$svg_file" ] || [ "$owm_file" -nt "$svg_file" ]; then
        echo "Rendering $owm_file → SVG"
        "$SCRIPT_DIR/ensure-owm.sh" "$owm_file" >/dev/null
    fi
done <<EOF
$(find "$WS" -name '*.owm' -type f 2>/dev/null)
EOF

# ── Phase 3: Build site directory ─────────────────────────────────────

rm -rf "$SITE"
mkdir -p "$SITE/research"
cp "$SCRIPT_DIR/site.css" "$SITE/style.css"

# ── Helpers ───────────────────────────────────────────────────────────

# Preprocess box-drawing trees: wrap contiguous runs of lines containing
# box-drawing characters (├ │ └ ─) in fenced code blocks so pandoc
# preserves whitespace.
preprocess_trees() {
    awk '
    /[├│└─┌┐┬┤┼┘┴]/ {
        if (!in_tree) { print "```"; in_tree = 1 }
        print
        next
    }
    {
        if (in_tree) { print "```"; in_tree = 0 }
        print
    }
    END { if (in_tree) print "```" }
    '
}

# Preprocess key-value lines: insert blank line before **Label**: lines
# that follow a non-blank line, so pandoc treats each as a separate <p>.
preprocess_kv() {
    awk '
    /^\*\*[^*]+\*\*:/ {
        if (prev != "" && prev !~ /^[[:space:]]*$/) print ""
        print
        prev = $0
        next
    }
    { print; prev = $0 }
    '
}

# Convert markdown to HTML fragment via pandoc, stripping the first H1
# (the page wrapper provides the canonical H1)
md_to_html() {
    preprocess_kv | preprocess_trees | pandoc -f markdown -t html5 --syntax-highlighting=none \
        | awk '!done && /<h1[^>]*>.*<\/h1>/ { done=1; next } { print }'
}

# Embed an SVG file inline in a <figure>
embed_svg() {
    local svg_path="$1"
    local caption="${2:-}"
    if [ -f "$svg_path" ]; then
        echo '<figure>'
        sed 's/<svg /<svg style="max-width:100%;height:auto" /' "$svg_path"
        if [ -n "$caption" ]; then
            echo "<figcaption>$caption</figcaption>"
        fi
        echo '</figure>'
    fi
}

# Generate navigation HTML
nav_html() {
    local active="$1"
    local nav='<nav>'

    nav="$nav <a href=\"index.html\""
    [ "$active" = "index" ] && nav="$nav class=\"active\""
    nav="$nav>Overview</a>"

    if [ "$HAS_STAGE5" = true ]; then
        nav="$nav <a href=\"strategy.html\""
        [ "$active" = "strategy" ] && nav="$nav class=\"active\""
        nav="$nav>Strategy</a>"
    fi

    if [ "$HAS_STAGE4" = true ]; then
        nav="$nav <a href=\"map.html\""
        [ "$active" = "map" ] && nav="$nav class=\"active\""
        nav="$nav>Map</a>"
    fi

    if [ "$HAS_STAGE3" = true ]; then
        nav="$nav <a href=\"supply-chain.html\""
        [ "$active" = "supply-chain" ] && nav="$nav class=\"active\""
        nav="$nav>Supply Chain</a>"
    fi

    if [ "$HAS_STAGE2" = true ]; then
        nav="$nav <a href=\"needs.html\""
        [ "$active" = "needs" ] && nav="$nav class=\"active\""
        nav="$nav>Needs</a>"
    fi

    nav="$nav <a href=\"research.html\""
    [ "$active" = "research" ] && nav="$nav class=\"active\""
    nav="$nav>Research</a>"

    nav="$nav <a href=\"decisions.html\""
    [ "$active" = "decisions" ] && nav="$nav class=\"active\""
    nav="$nav>Decisions</a>"

    nav="$nav</nav>"
    echo "$nav"
}

# Wrap pandoc HTML fragment in a full page
# Args: page_title active_nav_item
# Reads HTML body from stdin
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

# Wrap a research sub-page (needs breadcrumb, different style.css path)
wrap_research_subpage() {
    local title="$1"
    local body
    body="$(cat)"
    local nav
    nav="$(nav_html "research")"
    # Fix style.css path for subdirectory
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

# ── Phase 4: Generate pages ───────────────────────────────────────────

echo "Generating pages..."

# -- Index page --
{
    # Hero: best available map SVG
    if [ "$HAS_STAGE5" = true ] && [ -f "$WS/5-strategy/map.svg" ]; then
        embed_svg "$WS/5-strategy/map.svg" "Strategy map"
    elif [ "$HAS_STAGE4" = true ] && [ -f "$WS/4-evolve/map.svg" ]; then
        embed_svg "$WS/4-evolve/map.svg" "Evolution map"
    elif [ -f "$WS/1-research/landscape.svg" ]; then
        embed_svg "$WS/1-research/landscape.svg" "Landscape sketch (approximate)"
    fi

    # Decisions summary
    if [ -f "$WS/decisions.md" ]; then
        cat "$WS/decisions.md" | md_to_html
    fi
} | wrap_page "Overview" "index" > "$SITE/index.html"
echo "  index.html"

# -- Decisions page --
if [ -f "$WS/decisions.md" ]; then
    cat "$WS/decisions.md" | md_to_html | wrap_page "Decisions" "decisions" > "$SITE/decisions.html"
    echo "  decisions.html"
fi

# -- Research pages --
# Build task list (slug|title pairs) once for TOC and sub-page navigation
TASK_LIST=""
TASK_COUNT=0
if [ -d "$WS/1-research/tasks" ]; then
    for task_file in "$WS/1-research/tasks/"*.md; do
        [ -f "$task_file" ] || continue
        slug="$(basename "$task_file" .md)"
        task_title="$(sed -n 's/^# *//p' "$task_file" | head -1)"
        if [ -z "$task_title" ]; then
            task_title="$slug"
        fi
        task_title="${task_title% — $ORG_NAME}"
        TASK_LIST="$TASK_LIST$slug|$task_title
"
        TASK_COUNT=$((TASK_COUNT + 1))
    done
fi
TOTAL_PAGES=$((TASK_COUNT + 1))

# Helper: emit the research TOC as an <ol>
# Args: prefix (empty or "../"), active_slug (empty for summary page)
research_toc() {
    local prefix="$1"
    local active_slug="$2"
    echo '<nav class="toc" aria-label="Research sections">'
    echo '<ol>'
    if [ -z "$active_slug" ]; then
        echo "<li class=\"active\">Synthesis</li>"
    else
        echo "<li><a href=\"${prefix}research.html\">Synthesis</a></li>"
    fi
    echo "$TASK_LIST" | while IFS='|' read -r slug title; do
        [ -z "$slug" ] && continue
        if [ "$slug" = "$active_slug" ]; then
            echo "<li class=\"active\">$title</li>"
        else
            echo "<li><a href=\"${prefix}research/$slug.html\">$title</a></li>"
        fi
    done
    echo '</ol>'
    echo '</nav>'
}

# -- Research summary page (1 of N) --
{
    research_toc "" ""
    cat "$WS/1-research/summary.md" | md_to_html
} | wrap_page "Research" "research" > "$SITE/research.html"
echo "  research.html"

# -- Research sub-pages (2..N of N) --
PAGE_NUM=1
echo "$TASK_LIST" | while IFS='|' read -r slug title; do
    [ -z "$slug" ] && continue
    PAGE_NUM=$((PAGE_NUM + 1))
    {
        research_toc "../" "$slug"
        cat "$WS/1-research/tasks/$slug.md" | md_to_html
    } | wrap_research_subpage "$title" > "$SITE/research/$slug.html"
    echo "  research/$slug.html"
done

# -- Needs page --
if [ "$HAS_STAGE2" = true ]; then
    cat "$WS/2-needs/needs.agreed.md" | md_to_html | wrap_page "User Needs" "needs" > "$SITE/needs.html"
    echo "  needs.html"
fi

# -- Supply chain page --
if [ "$HAS_STAGE3" = true ]; then
    cat "$WS/3-chain/supply-chain.agreed.md" | md_to_html | wrap_page "Supply Chain" "supply-chain" > "$SITE/supply-chain.html"
    echo "  supply-chain.html"
fi

# -- Map page (stage 4) --
if [ "$HAS_STAGE4" = true ]; then
    {
        if [ -f "$WS/4-evolve/map.svg" ]; then
            embed_svg "$WS/4-evolve/map.svg" "Evolution map"
        fi

        # Include assessment files
        if [ -d "$WS/4-evolve/assessments" ]; then
            for assess_file in "$WS/4-evolve/assessments/"*.md; do
                [ -f "$assess_file" ] || continue
                cat "$assess_file" | md_to_html
                echo "<hr>"
            done
        fi
    } | wrap_page "Evolution Map" "map" > "$SITE/map.html"
    echo "  map.html"
fi

# -- Strategy page (stage 5) --
if [ "$HAS_STAGE5" = true ]; then
    {
        if [ -f "$WS/5-strategy/map.svg" ]; then
            embed_svg "$WS/5-strategy/map.svg" "Strategy map"
        fi

        # Include play files
        if [ -d "$WS/5-strategy/plays" ]; then
            for play_file in "$WS/5-strategy/plays/"*.md; do
                [ -f "$play_file" ] || continue
                cat "$play_file" | md_to_html
                echo "<hr>"
            done
        fi
    } | wrap_page "Strategy" "strategy" > "$SITE/strategy.html"
    echo "  strategy.html"
fi

echo ""
echo "Site generated: $SITE/"
echo "Open: $SITE/index.html"
