#!/usr/bin/env bash
#
# Maintain agent skill symlinks and instruction-file aliases.
#
# Skills are discovered from four locations:
#   skills/                          (repo-root generic skills)
#   personal/                        (full scan — skills/ and skillsets/)
#   partnerships/*/                  (full scan — skills/ and skillsets/)
#   commons/*/*/skillsets/            (only skillset-owned skills)
#
# This script finds every directory containing a SKILL.md under those
# locations and creates symlinks in .claude/skills/, .agents/skills/,
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

# Parallel indexed arrays — bash 3.2 compatible (no declare -A).
SKILL_NAMES=()
SKILL_DIRS=()

_add_skill() {
    local name="$1" dir="$2"
    local i count=${#SKILL_NAMES[@]}
    for (( i=0; i<count; i++ )); do
        if [ "${SKILL_NAMES[$i]}" = "$name" ]; then
            SKILL_DIRS[$i]="$dir"
            return
        fi
    done
    SKILL_NAMES+=("$name")
    SKILL_DIRS+=("$dir")
}

_scan_skills() {
    local search_root="$1"
    local skill_md skill_dir skill_name
    while IFS= read -r skill_md; do
        skill_dir="$(dirname "$skill_md")"
        skill_name="$(basename "$skill_dir")"
        _add_skill "$skill_name" "$skill_dir"
    done < <(find "$search_root" -name SKILL.md -not -path '*/references/*' -not -path '*/assets/*' 2>/dev/null)
}

# Repo-root generic skills
[ -d "skills" ] && _scan_skills "skills"

# Personal — full scan (skills/ and skillsets/)
[ -d "personal" ] && _scan_skills "personal"

# Partnerships — full scan per slug
if [ -d "partnerships" ]; then
    for partner_dir in partnerships/*/; do
        [ -d "$partner_dir" ] && _scan_skills "$partner_dir"
    done
fi

# Commons — only skillset-owned skills (not top-level skills/)
if [ -d "commons" ]; then
    for repo_dir in commons/*/*/; do
        [ -d "$repo_dir" ] || continue
        skillsets_dir="${repo_dir}skillsets"
        [ -d "$skillsets_dir" ] && _scan_skills "$skillsets_dir"
    done
fi

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
    count=${#SKILL_NAMES[@]}
    for (( i=0; i<count; i++ )); do
        skill_name="${SKILL_NAMES[$i]}"
        skill_dir="${SKILL_DIRS[$i]}"
        # Compute relative path from agent_dir to skill_dir
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
