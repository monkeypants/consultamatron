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
HAS_ATLAS=false
HAS_PRESENTATIONS=false

[ -f "$PROJECT/brief.agreed.md" ]                && HAS_BRIEF=true
[ -f "$PROJECT/needs/needs.agreed.md" ]          && HAS_NEEDS=true
[ -f "$PROJECT/chain/supply-chain.agreed.md" ]   && HAS_CHAIN=true
[ -f "$PROJECT/evolve/map.agreed.owm" ]          && HAS_EVOLVE=true
[ -f "$PROJECT/strategy/map.agreed.owm" ]        && HAS_STRATEGY=true
[ -d "$PROJECT/atlas" ]                          && HAS_ATLAS=true
[ -d "$PROJECT/presentations" ]                  && HAS_PRESENTATIONS=true

HAS_ANALYSIS=false
if [ "$HAS_BRIEF" = true ] || [ "$HAS_NEEDS" = true ] || \
   [ "$HAS_CHAIN" = true ] || [ "$HAS_EVOLVE" = true ] || \
   [ "$HAS_STRATEGY" = true ] || [ -f "$PROJECT/decisions.md" ]; then
    HAS_ANALYSIS=true
fi

echo "    Stages: brief=$HAS_BRIEF needs=$HAS_NEEDS chain=$HAS_CHAIN evolve=$HAS_EVOLVE strategy=$HAS_STRATEGY"
echo "    Extras: atlas=$HAS_ATLAS presentations=$HAS_PRESENTATIONS"

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

# ── Backward compatibility gate ──────────────────────────────────────
# If no atlas or presentations exist, use the legacy flat layout.

if [ "$HAS_ATLAS" = false ] && [ "$HAS_PRESENTATIONS" = false ]; then
    # Legacy flat navigation and page generation
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
<nav class="breadcrumb"><a href="../index.html">$ORG_NAME</a> &rsaquo; $PROJECT_NAME</nav>
$nav
<h1>$title</h1>
$body
</body>
</html>
HTMLEOF
    }

    # Index page
    {
        if [ "$HAS_STRATEGY" = true ] && [ -f "$PROJECT/strategy/map.svg" ]; then
            embed_svg "$PROJECT/strategy/map.svg" "Strategy map"
        elif [ "$HAS_EVOLVE" = true ] && [ -f "$PROJECT/evolve/map.svg" ]; then
            embed_svg "$PROJECT/evolve/map.svg" "Evolution map"
        elif [ -f "$PROJECT/landscape.svg" ]; then
            embed_svg "$PROJECT/landscape.svg" "Landscape sketch (approximate)"
        fi
    } | wrap_page "Overview" "index" > "$SITE_DIR/index.html"
    echo "    index.html"

    if [ "$HAS_BRIEF" = true ]; then
        md_to_html < "$PROJECT/brief.agreed.md" | wrap_page "Project Brief" "brief" > "$SITE_DIR/brief.html"
        echo "    brief.html"
    fi
    if [ -f "$PROJECT/decisions.md" ]; then
        md_to_html < "$PROJECT/decisions.md" | wrap_page "Decisions" "decisions" > "$SITE_DIR/decisions.html"
        echo "    decisions.html"
    fi
    if [ "$HAS_NEEDS" = true ]; then
        md_to_html < "$PROJECT/needs/needs.agreed.md" | wrap_page "User Needs" "needs" > "$SITE_DIR/needs.html"
        echo "    needs.html"
    fi
    if [ "$HAS_CHAIN" = true ]; then
        md_to_html < "$PROJECT/chain/supply-chain.agreed.md" | wrap_page "Supply Chain" "supply-chain" > "$SITE_DIR/supply-chain.html"
        echo "    supply-chain.html"
    fi
    if [ "$HAS_EVOLVE" = true ]; then
        {
            [ -f "$PROJECT/evolve/map.svg" ] && embed_svg "$PROJECT/evolve/map.svg" "Evolution map"
            if [ -d "$PROJECT/evolve/assessments" ]; then
                for f in "$PROJECT/evolve/assessments/"*.md; do
                    [ -f "$f" ] || continue
                    md_to_html < "$f"; echo "<hr>"
                done
            fi
        } | wrap_page "Evolution Map" "map" > "$SITE_DIR/map.html"
        echo "    map.html"
    fi
    if [ "$HAS_STRATEGY" = true ]; then
        {
            [ -f "$PROJECT/strategy/map.svg" ] && embed_svg "$PROJECT/strategy/map.svg" "Strategy map"
            if [ -d "$PROJECT/strategy/plays" ]; then
                for f in "$PROJECT/strategy/plays/"*.md; do
                    [ -f "$f" ] || continue
                    md_to_html < "$f"; echo "<hr>"
                done
            fi
        } | wrap_page "Strategy" "strategy" > "$SITE_DIR/strategy.html"
        echo "    strategy.html"
    fi

    exit 0
fi

# ══════════════════════════════════════════════════════════════════════
# Three-tier IA: Presentations / Atlas / Analysis
# ══════════════════════════════════════════════════════════════════════

# ── Navigation ───────────────────────────────────────────────────────

project_nav_html() {
    local active="$1"
    local depth="$2"  # 0 = project root, 1 = section page
    local prefix=""
    [ "$depth" -eq 1 ] && prefix="../"

    local nav='<nav>'

    nav="$nav <a href=\"${prefix}index.html\""
    [ "$active" = "index" ] && nav="$nav class=\"active\""
    nav="$nav>Overview</a>"

    if [ "$HAS_PRESENTATIONS" = true ]; then
        nav="$nav <a href=\"${prefix}presentations/index.html\""
        [ "$active" = "presentations" ] && nav="$nav class=\"active\""
        nav="$nav>Presentations</a>"
    fi

    if [ "$HAS_ATLAS" = true ]; then
        nav="$nav <a href=\"${prefix}atlas/index.html\""
        [ "$active" = "atlas" ] && nav="$nav class=\"active\""
        nav="$nav>Atlas</a>"
    fi

    if [ "$HAS_ANALYSIS" = true ]; then
        nav="$nav <a href=\"${prefix}analysis/index.html\""
        [ "$active" = "analysis" ] && nav="$nav class=\"active\""
        nav="$nav>Analysis</a>"
    fi

    nav="$nav</nav>"
    echo "$nav"
}

# ── Page wrapper ─────────────────────────────────────────────────────

wrap_project_page() {
    local title="$1"
    local active="$2"
    local depth="$3"  # 0 = project root, 1 = section page
    local body
    body="$(cat)"
    local nav
    nav="$(project_nav_html "$active" "$depth")"

    local css_path="../style.css"
    local crumb="<nav class=\"breadcrumb\"><a href=\"../index.html\">$ORG_NAME</a> &rsaquo; $PROJECT_NAME</nav>"
    if [ "$depth" -eq 1 ]; then
        css_path="../../style.css"
        crumb="<nav class=\"breadcrumb\"><a href=\"../../index.html\">$ORG_NAME</a> &rsaquo; <a href=\"../index.html\">$PROJECT_NAME</a></nav>"
    fi

    cat <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>$title — $PROJECT_NAME — $ORG_NAME</title>
<link rel="stylesheet" href="$css_path">
</head>
<body>
$crumb
$nav
<h1>$title</h1>
$body
</body>
</html>
HTMLEOF
}

# ── Manifest parser ──────────────────────────────────────────────────
# Reads a tour manifest.md and outputs normalized rows:
#   order|section_title|atlas_dir|map_files
# atlas_dir is relative to project (e.g. atlas/overview/)
# map_files is comma-separated SVG filenames, or empty for defaults

parse_manifest() {
    local manifest="$1"
    awk -F'|' '
    # Skip non-table lines, header separator, and header row
    !/^\|/ { next }
    /^\|[-| ]+\|$/ { next }

    # Detect header row (contains letters but no atlas/)
    !header_seen && !/atlas\// { header_seen = 1; next }

    {
        # Count and extract trimmed fields
        n = 0
        for (i = 2; i <= NF - 1; i++) {
            n++
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
            col[n] = $i
        }

        order = col[1]

        # Find atlas column (contains "atlas/")
        atlas_col = 0
        for (i = 2; i <= n; i++) {
            if (col[i] ~ /^atlas\//) { atlas_col = i; break }
        }

        atlas_dir = ""
        title = ""
        map_files = ""

        if (atlas_col > 0) {
            atlas_dir = col[atlas_col]
            # Remove trailing slash for consistency, then re-add
            sub(/\/$/, "", atlas_dir)
            atlas_dir = atlas_dir "/"
        }

        if (n >= 5 && atlas_col == 3) {
            # Format A: order|title|atlas|map|analysis (5 cols)
            title = col[2]
            map_files = col[4]
        } else if (n == 4 && atlas_col == 3) {
            # Format B: order|slug|atlas|label (4 cols, atlas=3)
            title = col[4]
        } else if (n == 4 && atlas_col == 2) {
            # Format C: order|atlas|slug|title (4 cols, atlas=2)
            title = col[4]
        } else if (atlas_col == 0) {
            # Header row (empty atlas) - title from col 2
            title = col[2]
        } else {
            # Fallback: title is col 2
            title = col[2]
        }

        # Normalize map_files: keep only .svg references
        if (map_files != "" && map_files !~ /\.svg/) {
            map_files = ""
        }

        printf "%s|%s|%s|%s\n", order, title, atlas_dir, map_files
    }
    ' "$manifest"
}

# ── Tour page renderer ───────────────────────────────────────────────

render_tour_page() {
    local tour_dir="$1"       # e.g. $PROJECT/presentations/investor
    local tour_name="$2"      # e.g. investor
    local output_file="$3"    # e.g. $SITE_DIR/presentations/investor.html

    local manifest="$tour_dir/manifest.md"
    [ -f "$manifest" ] || return

    # Extract H1 title from manifest
    local page_title
    page_title="$(sed -n 's/^# *//p' "$manifest" | head -1)"
    [ -z "$page_title" ] && page_title="$(echo "$tour_name" | sed 's/.*/\u&/')"

    # Parse manifest into normalized rows
    local rows
    rows="$(parse_manifest "$manifest")"

    # Collect unique base orders (groups)
    local groups=""
    local prev_base=""
    while IFS='|' read -r order title atlas_dir map_files; do
        local base
        base="$(echo "$order" | sed 's/[a-z]*$//')"
        if [ "$base" != "$prev_base" ]; then
            groups="${groups:+$groups }$base"
            prev_base="$base"
        fi
    done <<EOF
$rows
EOF

    # Collect transition files sorted numerically
    local transitions=""
    if [ -d "$tour_dir/transitions" ]; then
        transitions="$(ls "$tour_dir/transitions/"*.md 2>/dev/null | sort)"
    fi

    # Build the page body
    {
        # Opening
        if [ -f "$tour_dir/opening.md" ]; then
            echo '<div class="tour-section">'
            md_to_html < "$tour_dir/opening.md"
            echo '</div>'
        fi

        # Iterate through groups with interleaved transitions
        local trans_idx=0
        local trans_count=0
        local trans_files=""

        # Store transition files in a temp approach (bash 3.2 compat)
        if [ -n "$transitions" ]; then
            trans_files="$transitions"
            trans_count="$(echo "$trans_files" | wc -l | tr -d ' ')"
        fi

        local group_num=0
        for base in $groups; do
            group_num=$((group_num + 1))

            echo '<div class="tour-section">'

            # Get rows for this group
            local group_rows
            group_rows="$(echo "$rows" | awk -F'|' -v base="$base" '{
                b = $1; sub(/[a-z]*$/, "", b)
                if (b == base) print
            }')"

            # Count rows in group
            local row_count
            row_count="$(echo "$group_rows" | wc -l | tr -d ' ')"

            # Render each row in the group
            local is_first=true
            while IFS='|' read -r order title atlas_dir map_files; do
                [ -z "$order" ] && continue

                # Determine heading level
                local hlevel="h2"
                local has_suffix=false
                echo "$order" | grep -q '[a-z]$' && has_suffix=true

                if [ "$has_suffix" = true ]; then
                    hlevel="h3"
                fi

                # Header row (no atlas source) → just heading
                if [ -z "$atlas_dir" ]; then
                    echo "<$hlevel>$title</$hlevel>"
                    is_first=false
                    continue
                fi

                echo "<$hlevel>$title</$hlevel>"

                # Embed SVG(s)
                local atlas_path="$PROJECT/$atlas_dir"
                if [ -n "$map_files" ] && echo "$map_files" | grep -q ','; then
                    # Multiple SVGs (e.g. layers)
                    local IFS_SAVE="$IFS"
                    IFS=','
                    for svg_name in $map_files; do
                        svg_name="$(echo "$svg_name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
                        local svg_path="$atlas_path$svg_name"
                        [ -f "$svg_path" ] && embed_svg "$svg_path" ""
                    done
                    IFS="$IFS_SAVE"
                elif [ -n "$map_files" ] && echo "$map_files" | grep -q '\.svg'; then
                    # Single explicit SVG
                    local svg_name
                    svg_name="$(echo "$map_files" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
                    [ -f "$atlas_path$svg_name" ] && embed_svg "$atlas_path$svg_name" ""
                else
                    # Default: look for map.svg
                    [ -f "${atlas_path}map.svg" ] && embed_svg "${atlas_path}map.svg" ""
                fi

                # Embed analysis
                if [ -f "${atlas_path}analysis.md" ]; then
                    md_to_html < "${atlas_path}analysis.md"
                fi

                is_first=false
            done <<ROWEOF
$group_rows
ROWEOF

            echo '</div>'

            # Emit transition after this group
            trans_idx=$((trans_idx + 1))
            if [ -n "$trans_files" ]; then
                local trans_file
                trans_file="$(echo "$trans_files" | sed -n "${trans_idx}p")"
                if [ -n "$trans_file" ] && [ -f "$trans_file" ]; then
                    echo '<div class="tour-section">'
                    md_to_html < "$trans_file"
                    echo '</div>'
                fi
            fi
        done
    } | wrap_project_page "$page_title" "presentations" 1 > "$output_file"
    echo "    presentations/$tour_name.html"
}

# ── Presentations index ──────────────────────────────────────────────

render_presentations_index() {
    local output_file="$SITE_DIR/presentations/index.html"

    {
        echo '<ul class="section-list">'
        for tour_dir in "$PROJECT/presentations"/*/; do
            [ -d "$tour_dir" ] || continue
            local tour_name
            tour_name="$(basename "$tour_dir")"
            local manifest="$tour_dir/manifest.md"
            [ -f "$manifest" ] || continue

            # Extract title from H1
            local title
            title="$(sed -n 's/^# *//p' "$manifest" | head -1)"
            [ -z "$title" ] && title="$tour_name"

            # Extract description from opening.md second paragraph
            local desc=""
            if [ -f "$tour_dir/opening.md" ]; then
                desc="$(awk '
                    /^[[:space:]]*$/ { para++; next }
                    para == 1 && !/^#/ {
                        line = (line ? line " " : "") $0
                    }
                    para >= 2 { exit }
                    END { print line }
                ' "$tour_dir/opening.md")"
            fi

            echo "<li><a href=\"$tour_name.html\">$title</a>"
            if [ -n "$desc" ]; then
                echo "<span class=\"desc\">$desc</span>"
            fi
            echo "</li>"
        done
        echo '</ul>'
    } | wrap_project_page "Presentations" "presentations" 1 > "$output_file"
    echo "    presentations/index.html"
}

# ── Atlas view page renderer ─────────────────────────────────────────

render_atlas_view_page() {
    local view_dir="$1"       # e.g. $PROJECT/atlas/overview
    local view_name="$2"      # e.g. overview
    local output_file="$3"    # e.g. $SITE_DIR/atlas/overview.html

    [ -f "$view_dir/analysis.md" ] || return

    # Derive title from view name
    local title
    title="$(echo "$view_name" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"

    {
        # Embed SVGs - check for multiple SVGs (layers case)
        local svg_count=0
        for svg_file in "$view_dir/"*.svg; do
            [ -f "$svg_file" ] || continue
            svg_count=$((svg_count + 1))
        done

        if [ "$svg_count" -gt 1 ]; then
            # Multiple SVGs (layers, etc.)
            for svg_file in "$view_dir/"*.svg; do
                [ -f "$svg_file" ] || continue
                local caption
                caption="$(basename "$svg_file" .svg | sed 's/-/ /g')"
                embed_svg "$svg_file" "$caption"
            done
        elif [ -f "$view_dir/map.svg" ]; then
            embed_svg "$view_dir/map.svg" ""
        else
            # Single non-standard SVG name
            for svg_file in "$view_dir/"*.svg; do
                [ -f "$svg_file" ] || continue
                embed_svg "$svg_file" ""
                break
            done
        fi

        # Analysis
        md_to_html < "$view_dir/analysis.md"
    } | wrap_project_page "$title" "atlas" 1 > "$output_file"
    echo "    atlas/$view_name.html"
}

# ── Atlas index ──────────────────────────────────────────────────────

atlas_view_category() {
    local name="$1"
    case "$name" in
        overview|layers|teams|flows)
            echo "structural" ;;
        bottlenecks|shared-components|need-*|anchor-*)
            echo "connectivity" ;;
        play-*|sourcing|evolution-mismatch|pipelines)
            echo "strategic" ;;
        movement|inertia|forces|risk|doctrine)
            echo "dynamic" ;;
        *)
            echo "strategic" ;;
    esac
}

render_atlas_index() {
    local output_file="$SITE_DIR/atlas/index.html"

    # Collect views that have analysis.md
    local views=""
    for view_dir in "$PROJECT/atlas"/*/; do
        [ -d "$view_dir" ] || continue
        local vname
        vname="$(basename "$view_dir")"
        [ -f "$view_dir/analysis.md" ] || continue
        views="${views:+$views }$vname"
    done

    {
        local cat_name cat_label
        for cat_name in structural connectivity strategic dynamic; do
            case "$cat_name" in
                structural)  cat_label="Structural" ;;
                connectivity) cat_label="Connectivity" ;;
                strategic)   cat_label="Strategic" ;;
                dynamic)     cat_label="Dynamic" ;;
            esac

            # Filter views for this category
            local cat_views=""
            for v in $views; do
                if [ "$(atlas_view_category "$v")" = "$cat_name" ]; then
                    cat_views="${cat_views:+$cat_views }$v"
                fi
            done

            [ -z "$cat_views" ] && continue

            echo '<div class="atlas-category">'
            echo "<h2>$cat_label</h2>"
            echo '<ul>'
            for v in $cat_views; do
                local label
                label="$(echo "$v" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)}1')"
                echo "<li><a href=\"$v.html\">$label</a></li>"
            done
            echo '</ul>'
            echo '</div>'
        done
    } | wrap_project_page "Atlas" "atlas" 1 > "$output_file"
    echo "    atlas/index.html"
}

# ── Analysis section TOC ─────────────────────────────────────────────

analysis_toc_html() {
    local active="$1"
    local toc='<nav class="toc"><ol>'

    if [ "$HAS_STRATEGY" = true ]; then
        toc="$toc<li"
        [ "$active" = "strategy" ] && toc="$toc class=\"active\""
        toc="$toc><a href=\"strategy.html\">Strategy</a></li>"
    fi
    if [ "$HAS_EVOLVE" = true ]; then
        toc="$toc<li"
        [ "$active" = "map" ] && toc="$toc class=\"active\""
        toc="$toc><a href=\"map.html\">Evolution Map</a></li>"
    fi
    if [ "$HAS_CHAIN" = true ]; then
        toc="$toc<li"
        [ "$active" = "supply-chain" ] && toc="$toc class=\"active\""
        toc="$toc><a href=\"supply-chain.html\">Supply Chain</a></li>"
    fi
    if [ "$HAS_NEEDS" = true ]; then
        toc="$toc<li"
        [ "$active" = "needs" ] && toc="$toc class=\"active\""
        toc="$toc><a href=\"needs.html\">User Needs</a></li>"
    fi
    if [ "$HAS_BRIEF" = true ]; then
        toc="$toc<li"
        [ "$active" = "brief" ] && toc="$toc class=\"active\""
        toc="$toc><a href=\"brief.html\">Project Brief</a></li>"
    fi
    if [ -f "$PROJECT/decisions.md" ]; then
        toc="$toc<li"
        [ "$active" = "decisions" ] && toc="$toc class=\"active\""
        toc="$toc><a href=\"decisions.html\">Decisions</a></li>"
    fi

    toc="$toc</ol></nav>"
    echo "$toc"
}

# ── Analysis page helper ─────────────────────────────────────────────

render_analysis_page() {
    local title="$1"
    local active="$2"
    local output_file="$3"
    # body comes from stdin

    {
        analysis_toc_html "$active"
        cat
    } | wrap_project_page "$title" "analysis" 1 > "$output_file"
}

# ── Generate three-tier pages ────────────────────────────────────────

# Presentations
if [ "$HAS_PRESENTATIONS" = true ]; then
    mkdir -p "$SITE_DIR/presentations"
    render_presentations_index
    for tour_dir in "$PROJECT/presentations"/*/; do
        [ -d "$tour_dir" ] || continue
        tour_name="$(basename "$tour_dir")"
        render_tour_page "$tour_dir" "$tour_name" "$SITE_DIR/presentations/$tour_name.html"
    done
fi

# Atlas
if [ "$HAS_ATLAS" = true ]; then
    mkdir -p "$SITE_DIR/atlas"
    render_atlas_index
    for view_dir in "$PROJECT/atlas"/*/; do
        [ -d "$view_dir" ] || continue
        view_name="$(basename "$view_dir")"
        [ -f "$view_dir/analysis.md" ] || continue
        render_atlas_view_page "$view_dir" "$view_name" "$SITE_DIR/atlas/$view_name.html"
    done
fi

# Analysis
if [ "$HAS_ANALYSIS" = true ]; then
    mkdir -p "$SITE_DIR/analysis"

    # Analysis index
    {
        analysis_toc_html ""
    } | wrap_project_page "Analysis" "analysis" 1 > "$SITE_DIR/analysis/index.html"
    echo "    analysis/index.html"

    # Strategy page
    if [ "$HAS_STRATEGY" = true ]; then
        {
            [ -f "$PROJECT/strategy/map.svg" ] && embed_svg "$PROJECT/strategy/map.svg" "Strategy map"
            if [ -d "$PROJECT/strategy/plays" ]; then
                for f in "$PROJECT/strategy/plays/"*.md; do
                    [ -f "$f" ] || continue
                    md_to_html < "$f"; echo "<hr>"
                done
            fi
        } | render_analysis_page "Strategy" "strategy" "$SITE_DIR/analysis/strategy.html"
        echo "    analysis/strategy.html"
    fi

    # Map page (evolve)
    if [ "$HAS_EVOLVE" = true ]; then
        {
            [ -f "$PROJECT/evolve/map.svg" ] && embed_svg "$PROJECT/evolve/map.svg" "Evolution map"
            if [ -d "$PROJECT/evolve/assessments" ]; then
                for f in "$PROJECT/evolve/assessments/"*.md; do
                    [ -f "$f" ] || continue
                    md_to_html < "$f"; echo "<hr>"
                done
            fi
        } | render_analysis_page "Evolution Map" "map" "$SITE_DIR/analysis/map.html"
        echo "    analysis/map.html"
    fi

    # Supply chain page
    if [ "$HAS_CHAIN" = true ]; then
        md_to_html < "$PROJECT/chain/supply-chain.agreed.md" \
            | render_analysis_page "Supply Chain" "supply-chain" "$SITE_DIR/analysis/supply-chain.html"
        echo "    analysis/supply-chain.html"
    fi

    # Needs page
    if [ "$HAS_NEEDS" = true ]; then
        md_to_html < "$PROJECT/needs/needs.agreed.md" \
            | render_analysis_page "User Needs" "needs" "$SITE_DIR/analysis/needs.html"
        echo "    analysis/needs.html"
    fi

    # Brief page
    if [ "$HAS_BRIEF" = true ]; then
        md_to_html < "$PROJECT/brief.agreed.md" \
            | render_analysis_page "Project Brief" "brief" "$SITE_DIR/analysis/brief.html"
        echo "    analysis/brief.html"
    fi

    # Decisions page
    if [ -f "$PROJECT/decisions.md" ]; then
        md_to_html < "$PROJECT/decisions.md" \
            | render_analysis_page "Decisions" "decisions" "$SITE_DIR/analysis/decisions.html"
        echo "    analysis/decisions.html"
    fi
fi

# Project index
{
    # Hero map
    if [ "$HAS_STRATEGY" = true ] && [ -f "$PROJECT/strategy/map.svg" ]; then
        embed_svg "$PROJECT/strategy/map.svg" "Strategy map"
    elif [ "$HAS_EVOLVE" = true ] && [ -f "$PROJECT/evolve/map.svg" ]; then
        embed_svg "$PROJECT/evolve/map.svg" "Evolution map"
    elif [ -f "$PROJECT/landscape.svg" ]; then
        embed_svg "$PROJECT/landscape.svg" "Landscape sketch (approximate)"
    fi

    # Section routing
    echo '<ul class="section-list">'
    if [ "$HAS_PRESENTATIONS" = true ]; then
        echo '<li><a href="presentations/index.html">Presentations</a>'
        echo '<span class="desc">Curated tours of the strategy map for different audiences</span></li>'
    fi
    if [ "$HAS_ATLAS" = true ]; then
        echo '<li><a href="atlas/index.html">Atlas</a>'
        echo '<span class="desc">Analytical views derived from the comprehensive strategy map</span></li>'
    fi
    if [ "$HAS_ANALYSIS" = true ]; then
        echo '<li><a href="analysis/index.html">Analysis</a>'
        echo '<span class="desc">Pipeline stages from brief through strategy</span></li>'
    fi
    echo '</ul>'
} | wrap_project_page "Overview" "index" 0 > "$SITE_DIR/index.html"
echo "    index.html"
