#!/usr/bin/env bash
#
# Maintain agent skill symlinks and instruction-file aliases.
#
# Skills live inside BC packages across three source containers:
#   commons/       (committed)
#   partnerships/  (gitignored, per-engagement)
#   personal/      (gitignored, operator-private)
#
# This script finds every directory containing a SKILL.md under those
# containers and creates symlinks in .claude/skills/, .agents/skills/,
# .gemini/skills/, and .github/skills/ pointing to the actual location.
#
# It also maintains the instruction-file aliases:
#   CLAUDE.md, GEMINI.md → AGENTS.md

set -euo pipefail

cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"

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

# -- Instruction-file aliases -----------------------------------------------

ensure_link "CLAUDE.md" "AGENTS.md"
ensure_link "GEMINI.md" "AGENTS.md"

# -- Skill symlinks ---------------------------------------------------------

# Directories to search for SKILL.md files
SOURCE_DIRS=()
[ -d "commons" ]      && SOURCE_DIRS+=("commons")
[ -d "partnerships" ] && SOURCE_DIRS+=("partnerships")
[ -d "personal" ]     && SOURCE_DIRS+=("personal")

# Collect all skill directories (dirs containing SKILL.md)
declare -A SKILL_PATHS
for source_dir in "${SOURCE_DIRS[@]}"; do
    while IFS= read -r skill_md; do
        skill_dir="$(dirname "$skill_md")"
        skill_name="$(basename "$skill_dir")"
        SKILL_PATHS["$skill_name"]="$skill_dir"
    done < <(find "$source_dir" -name SKILL.md -not -path '*/references/*' -not -path '*/assets/*' 2>/dev/null)
done

# Create symlinks in each agent's skills directory
for agent_dir in .claude/skills .agents/skills .gemini/skills .github/skills; do
    $dry_run || mkdir -p "$agent_dir"

    # Remove stale symlinks (point to non-existent targets)
    if [ -d "$agent_dir" ]; then
        for link in "$agent_dir"/*; do
            [ -L "$link" ] && [ ! -e "$link" ] && {
                log "rm   $link (stale)"
                $dry_run || rm "$link"
                changes=$((changes + 1))
            }
        done
    fi

    # Create/fix symlinks for each discovered skill
    for skill_name in $(echo "${!SKILL_PATHS[@]}" | tr ' ' '\n' | sort); do
        skill_dir="${SKILL_PATHS[$skill_name]}"
        # Compute relative path from agent_dir to skill_dir
        # e.g. from .claude/skills/wm-research to commons/wardley_mapping/skills/wm-research
        target="$(python3 -c "
import os.path, sys
print(os.path.relpath(sys.argv[1], sys.argv[2]))
" "$skill_dir" "$agent_dir")"
        ensure_link "$agent_dir/$skill_name" "$target"
    done
done

if [ $changes -eq 0 ]; then
    log "ok   all symlinks are correct"
else
    verb="made"
    $dry_run && verb="would make"
    log "$verb $changes change(s)"
fi
