#!/usr/bin/env bash
#
# Shared helper functions for site rendering scripts.
# Sourced by render-site.sh, render-wardley.sh, render-bmc.sh.

# Preprocess box-drawing trees: wrap contiguous runs of lines containing
# box-drawing characters (├ │ └ ─) in fenced code blocks so pandoc
# preserves whitespace.
preprocess_trees() {
    awk '
    /^```/ {
        if (in_tree) { print "```"; in_tree = 0 }
        in_fence = !in_fence
        print
        next
    }
    in_fence { print; next }
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
