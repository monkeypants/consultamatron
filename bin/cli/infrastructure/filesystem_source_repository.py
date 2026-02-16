"""SourceRepository that discovers partnerships from the filesystem.

Scans ``{repo_root}/partnerships/`` for subdirectories.  Each subdir
containing a ``skillsets/index.json`` is treated as a partnership source.
The commons source is synthesised from the injected SkillsetRepository.
"""

from __future__ import annotations

import json
from pathlib import Path

from consulting.repositories import SkillsetRepository
from practice.entities import SkillsetSource, SourceType


class FilesystemSourceRepository:
    """SourceRepository backed by filesystem scanning for partnerships."""

    def __init__(self, repo_root: Path, commons: SkillsetRepository) -> None:
        self._repo_root = repo_root
        self._commons = commons
        self._partnerships = self._scan_partnerships()

    # -- SourceRepository protocol ------------------------------------------

    def get(self, slug: str) -> SkillsetSource | None:
        if slug == "commons":
            return self._commons_source()
        if slug in self._partnerships:
            return SkillsetSource(
                slug=slug,
                source_type=SourceType.PARTNERSHIP,
                skillset_names=self._partnerships[slug],
            )
        return None

    def list_all(self) -> list[SkillsetSource]:
        sources = [self._commons_source()]
        for slug, names in self._partnerships.items():
            sources.append(
                SkillsetSource(
                    slug=slug,
                    source_type=SourceType.PARTNERSHIP,
                    skillset_names=names,
                )
            )
        return sources

    def skillset_source(self, skillset_name: str) -> str | None:
        for s in self._commons.list_all():
            if s.name == skillset_name:
                return "commons"
        for slug, names in self._partnerships.items():
            if skillset_name in names:
                return slug
        return None

    # -- Internals ----------------------------------------------------------

    def _scan_partnerships(self) -> dict[str, list[str]]:
        """Scan partnerships directory, returning {slug: [skillset_names]}."""
        result: dict[str, list[str]] = {}
        partnerships_dir = self._repo_root / "partnerships"
        if not partnerships_dir.is_dir():
            return result
        for subdir in sorted(partnerships_dir.iterdir()):
            if not subdir.is_dir():
                continue
            index = subdir / "skillsets" / "index.json"
            if not index.is_file():
                continue
            data = json.loads(index.read_text(encoding="utf-8"))
            result[subdir.name] = [entry["name"] for entry in data]
        return result

    def _commons_source(self) -> SkillsetSource:
        return SkillsetSource(
            slug="commons",
            source_type=SourceType.COMMONS,
            skillset_names=[s.name for s in self._commons.list_all()],
        )
