"""FilesystemSkillLinkManager — enforces generic/pipeline skill distinction.

Reads skill manifests from the repo filesystem, then synchronises
symlinks in agent directories based on skill type:

- Generic skills (no ``skillset`` in metadata) → symlinks in all agent dirs
- Pipeline skills (``skillset`` set in metadata) → no symlinks in agent dirs

Replaces ``bin/maintain-symlinks.sh`` as the mechanism for keeping
agent skill directories current.
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import ValidationError

from practice.bc_discovery import skill_search_dirs
from practice.entities import SkillManifest, SkillType
from practice.frontmatter import parse_frontmatter
from practice.repositories import SkillLinkStatus, SyncResult

AGENT_SKILL_DIRS = [
    Path(".agents/skills"),
    Path(".claude/skills"),
    Path(".gemini/skills"),
    Path(".github/skills"),
]


class FilesystemSkillLinkManager:
    """Manages agent skill symlinks based on skill type from SKILL.md metadata."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def _agent_dirs(self) -> list[Path]:
        """Return agent skill directories that exist under repo_root."""
        return [
            self._repo_root / d
            for d in AGENT_SKILL_DIRS
            if (self._repo_root / d).is_dir()
        ]

    def _discover_skills(self) -> dict[str, tuple[SkillManifest, Path]]:
        """Return {skill_name: (manifest, skill_dir)} for all discovered skills."""
        result: dict[str, tuple[SkillManifest, Path]] = {}
        for search_dir in skill_search_dirs(self._repo_root):
            for skill_md in sorted(search_dir.rglob("SKILL.md")):
                fm = parse_frontmatter(skill_md)
                if not fm:
                    continue
                try:
                    manifest = SkillManifest.model_validate(fm)
                except (ValidationError, TypeError):
                    continue
                result[manifest.name] = (manifest, skill_md.parent)
        return result

    def sync(self, dry_run: bool = False) -> SyncResult:
        """Synchronise agent skill symlinks based on skill type.

        - Generic skills: create symlinks in all agent dirs (if absent or wrong)
        - Pipeline skills: remove any existing symlinks
        - Broken symlinks: remove
        """
        result = SyncResult()
        skills = self._discover_skills()
        agent_dirs = self._agent_dirs()

        # Handle all known skills
        for skill_name, (manifest, skill_dir) in skills.items():
            if manifest.skill_type == SkillType.GENERIC:
                for agent_dir in agent_dirs:
                    link = agent_dir / skill_name
                    if link.is_symlink() and link.resolve() == skill_dir.resolve():
                        result.add_ok(skill_name, "generic, already linked")
                    elif link.is_symlink():
                        # Wrong target — replace
                        if not dry_run:
                            link.unlink()
                            _make_relative_symlink(link, skill_dir)
                        result.add_linked(skill_name, "generic, re-linked")
                    else:
                        if not dry_run:
                            _make_relative_symlink(link, skill_dir)
                        result.add_linked(skill_name, "generic, linked")
            else:
                # Pipeline: remove any stale symlinks
                for agent_dir in agent_dirs:
                    link = agent_dir / skill_name
                    if link.is_symlink():
                        if not dry_run:
                            link.unlink()
                        result.add_unlinked(skill_name, "pipeline, symlink removed")

        # Remove broken symlinks pointing to nonexistent targets
        for agent_dir in agent_dirs:
            if not agent_dir.is_dir():
                continue
            for entry in agent_dir.iterdir():
                if entry.is_symlink() and not entry.resolve().exists():
                    if not dry_run:
                        entry.unlink()
                    result.add_removed(entry.name, "broken symlink removed")

        return result

    def status(self) -> list[SkillLinkStatus]:
        """Report current link state for all discovered skills."""
        skills = self._discover_skills()
        agent_dirs = self._agent_dirs()
        statuses = []

        for skill_name, (manifest, _skill_dir) in sorted(skills.items()):
            if manifest.skill_type == SkillType.GENERIC:
                # Linked if ALL agent dirs have a valid symlink
                is_linked = bool(agent_dirs) and all(
                    (d / skill_name).is_symlink()
                    and (d / skill_name).resolve().exists()
                    for d in agent_dirs
                )
            else:
                # Pipeline: correct state is not linked
                is_linked = False

            statuses.append(
                SkillLinkStatus(
                    skill=skill_name,
                    skill_type=manifest.skill_type.value,
                    linked=is_linked,
                )
            )

        return statuses


def _make_relative_symlink(link: Path, target: Path) -> None:
    """Create a symlink from link → target using a relative path."""
    rel = os.path.relpath(target, link.parent)
    link.symlink_to(rel)
