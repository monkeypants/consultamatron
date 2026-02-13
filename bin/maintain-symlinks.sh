#!/usr/bin/env bash
#
# Ensure vendor-specific symlinks are in sync with canonical locations.
#
# Canonical layout:
#   AGENTS.md              project instructions
#   */SKILL.md             skills (any directory containing a SKILL.md)
#                          includes: org-research, engage, wm-*, bmc-*, editorial-voice
#
# Vendor expectations:
#   CLAUDE.md, GEMINI.md   → AGENTS.md
#   .claude/skills/*       → ../../{skill-dir}
#   .agents/skills/*       → ../../{skill-dir}
#   .github/skills/*       → ../../{skill-dir}
#   .gemini/skills/*       → ../../{skill-dir}

set -euo pipefail

cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

VENDOR_DIRS=".claude .agents .github .gemini"
dry_run=false

if [ "${1:-}" = "-n" ] || [ "${1:-}" = "--dry-run" ]; then
    dry_run=true
fi

changes=0

log() { printf '%s\n' "$*"; }

ensure_link() {
    link="$1"; target="$2"
    if [ -L "$link" ]; then
        current="$(readlink "$link")"
        if [ "$current" = "$target" ]; then
            return
        fi
        log "fix  $link -> $target  (was $current)"
        $dry_run || ln -sfn "$target" "$link"
    elif [ -e "$link" ]; then
        log "SKIP $link exists and is not a symlink"
        return
    else
        log "add  $link -> $target"
        $dry_run || ln -s "$target" "$link"
    fi
    changes=$((changes + 1))
}

remove_link() {
    link="$1"
    if [ -L "$link" ]; then
        log "rm   $link"
        $dry_run || rm "$link"
        changes=$((changes + 1))
    fi
}

# --- discover canonical skills ---

skills=""
for skill_md in */SKILL.md; do
    [ -f "$skill_md" ] || continue
    skills="$skills $(dirname "$skill_md")"
done

# --- instruction files ---

ensure_link "CLAUDE.md" "AGENTS.md"
ensure_link "GEMINI.md" "AGENTS.md"

# --- vendor skill symlinks ---

for vendor in $VENDOR_DIRS; do
    mkdir -p "$vendor/skills"

    # add or fix links for each canonical skill
    for name in $skills; do
        ensure_link "$vendor/skills/$name" "../../$name"
    done

    # remove stale links for skills that no longer exist
    for entry in "$vendor/skills/"*; do
        [ -e "$entry" ] || [ -L "$entry" ] || continue
        name="$(basename "$entry")"
        case " $skills " in
            *" $name "*) ;;  # still canonical
            *) remove_link "$entry" ;;
        esac
    done
done

if [ $changes -eq 0 ]; then
    log "ok   all symlinks are correct"
else
    verb="made"
    $dry_run && verb="would make"
    log "$verb $changes change(s)"
fi
