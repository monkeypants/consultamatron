"""SkillManifestRepository backed by SKILL.md files on disk.

Scans ``commons/``, ``personal/``, and ``partnerships/{slug}/`` for
``**/SKILL.md`` files, parses their YAML frontmatter, and validates
each via ``SkillManifest.model_validate()``.  Invalid manifests are
silently skipped.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from practice.bc_discovery import source_container_dirs
from practice.entities import SkillManifest
from practice.frontmatter import parse_frontmatter


class FilesystemSkillManifestRepository:
    """Aggregates SKILL.md manifests from all source containers."""

    def __init__(self, repo_root: Path) -> None:
        self._manifests: list[SkillManifest] = []
        for container_dir in source_container_dirs(repo_root):
            for skill_md in sorted(container_dir.rglob("SKILL.md")):
                fm = parse_frontmatter(skill_md)
                if not fm:
                    continue
                try:
                    manifest = SkillManifest.model_validate(fm)
                except (ValidationError, TypeError):
                    continue
                self._manifests.append(manifest)

    def get(self, name: str) -> SkillManifest | None:
        for m in self._manifests:
            if m.name == name:
                return m
        return None

    def list_all(self) -> list[SkillManifest]:
        return list(self._manifests)
