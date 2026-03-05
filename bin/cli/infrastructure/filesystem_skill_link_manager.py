"""FilesystemSkillLinkManager — enforces generic/pipeline skill distinction.

Reads skill manifests from the repo filesystem, then synchronises
symlinks in agent directories based on skill type:

- Generic skills (no ``skillset`` in metadata) → symlinks in all agent dirs
- Pipeline skills (``skillset`` set in metadata) → no symlinks in agent dirs

Replaces ``bin/maintain-symlinks.sh`` as the mechanism for keeping
agent skill directories current.
"""

from __future__ import annotations

from pathlib import Path

from practice.entities import SkillType
from practice.repositories import SkillLinkManager, SkillLinkStatus, SyncResult

from bin.cli.infrastructure.filesystem_skill_manifest_repository import (
    FilesystemSkillManifestRepository,
)

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
        self._manifest_repo = FilesystemSkillManifestRepository(repo_root)

    def _agent_dirs(self) -> list[Path]:
        """Return agent skill directories that exist under repo_root."""
        return [
            self._repo_root / d
            for d in AGENT_SKILL_DIRS
            if (self._repo_root / d).is_dir()
        ]

    def _skill_path(self, skill_name: str) -> Path | None:
        """Return the directory containing SKILL.md for a given skill name."""
        manifest = self._manifest_repo.get(skill_name)
        if manifest is None:
            return None
        for agent_dir_rel in AGENT_SKILL_DIRS:
            agent_dir = self._repo_root / agent_dir_rel
            if not agent_dir.is_dir():
                continue
            # Search all SKILL.md paths discovered
        # Re-scan to find the actual path for this manifest
        from practice.bc_discovery import skill_search_dirs
        for search_dir in skill_search_dirs(self._repo_root):
            for skill_md in search_dir.rglob("SKILL.md"):
                if skill_md.parent.name == skill_name:
                    from practice.frontmatter import parse_frontmatter
                    from pydantic import ValidationError
                    from practice.entities import SkillManifest
                    fm = parse_frontmatter(skill_md)
                    if not fm:
                        continue
                    try:
                        m = SkillManifest.model_validate(fm)
                    except (ValidationError, TypeError):
                        continue
                    if m.name == skill_name:
                        return skill_md.parent
        return None

    def _all_skill_dirs(self) -> dict[str, Path]:
        """Return {skill_name: skill_dir} for all discovered skills."""
        from practice.bc_discovery import skill_search_dirs
        from practice.frontmatter import parse_frontmatter
        from pydantic import ValidationError
        from practice.entities import SkillManifest

        result: dict[str, Path] = {}
        for search_dir in skill_search_dirs(self._repo_root):
            for skill_md in sorted(search_dir.rglob("SKILL.md")):
                fm = parse_frontmatter(skill_md)
                if not fm:
                    continue
                try:
                    m = SkillManifest.model_validate(fm)
                except (ValidationError, TypeError):
                    continue
                result[m.name] = skill_md.parent
        return result

    def sync(self, dry_run: bool = False) -> SyncResult:
        """Synchronise agent skill symlinks based on skill type.

        - Generic skills: create symlinks in all agent dirs (if absent)
        - Pipeline skills: remove any existing symlinks
        - Broken symlinks: remove
        """
        result = SyncResult()
        manifests = self._manifest_repo.list_all()
        skill_dirs = self._all_skill_dirs()
        agent_dirs = self._agent_dirs()

        known_skill_names = {m.name for m in manifests}

        # Step 1: handle known skills
        for manifest in manifests:
            skill_dir = skill_dirs.get(manifest.name)
            if skill_dir is None:
                continue

            if manifest.skill_type == SkillType.GENERIC:
                for agent_dir in agent_dirs:
                    link = agent_dir / manifest.name
                    if link.is_symlink() and link.resolve() == skill_dir.resolve():
                        result.add_ok(manifest.name, "generic, already linked")
                    elif link.is_symlink():
                        # Points somewhere wrong — replace
                        if not dry_run:
                            link.unlink()
                            _make_relative_symlink(link, skill_dir)
                        result.add_linked(
                            manifest.name,
                            f"generic, re-linked (was wrong target)",
                        )
                    else:
                        if not dry_run:
                            _make_relative_symlink(link, skill_dir)
                        result.add_linked(manifest.name, "generic, linked")
            else:
                # Pipeline: remove any stale symlinks
                for agent_dir in agent_dirs:
                    link = agent_dir / manifest.name
                    if link.is_symlink():
                        if not dry_run:
                            link.unlink()
                        result.add_unlinked(manifest.name, "pipeline, symlink removed")

        # Step 2: remove broken symlinks (pointing to unknown/nonexistent targets)
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
        manifests = self._manifest_repo.list_all()
        agent_dirs = self._agent_dirs()
        statuses = []

        for manifest in manifests:
            is_linked = False
            if manifest.skill_type == SkillType.GENERIC:
                # Generic: linked if all agent dirs have a valid symlink
                if agent_dirs:
                    is_linked = all(
                        (d / manifest.name).is_symlink()
                        and (d / manifest.name).resolve().exists()
                        for d in agent_dirs
                    )
                # If there are no agent dirs at all, treat as not linked
            # Pipeline: linked = False is the correct state (no symlinks)
            # but we report linked=True if any stale symlink exists
            elif manifest.skill_type == SkillType.PIPELINE:
                is_linked = any(
                    (d / manifest.name).is_symlink() for d in agent_dirs
                )
                # For pipeline, linked=True means something is wrong
                # We use linked=False as "correct state" per protocol
                is_linked = False  # pipelines are never "correctly linked"

            statuses.append(
                SkillLinkStatus(
                    skill=manifest.name,
                    skill_type=manifest.skill_type.value,
                    linked=is_linked,
                )
            )

        return statuses


def _make_relative_symlink(link: Path, target: Path) -> None:
    """Create a relative symlink from link to target."""
    rel_target = Path(
        "../" * len(link.parent.relative_to(link.parent.anchor).parts)
    )
    # Use os.path.relpath for simplicity
    import os
    rel = os.path.relpath(target, link.parent)
    link.symlink_to(rel)
