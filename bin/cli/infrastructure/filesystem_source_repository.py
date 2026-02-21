"""SourceRepository that discovers sources from the filesystem.

Scans three source containers for BC packages:

- **commons** — pipelines from the injected SkillsetRepository
- **personal** — BC packages in ``{repo_root}/personal/``
- **partnerships** — BC packages in ``{repo_root}/partnerships/{slug}/``

All three use the same BC package discovery: directories containing
``__init__.py`` with a ``PIPELINES`` attribute.
"""

from __future__ import annotations

from pathlib import Path

from practice.repositories import SkillsetRepository
from practice.bc_discovery import collect_pipelines
from practice.entities import SkillsetSource, SourceType


class FilesystemSourceRepository:
    """SourceRepository backed by filesystem scanning for all sources."""

    def __init__(self, repo_root: Path, commons: SkillsetRepository) -> None:
        self._repo_root = repo_root
        self._commons = commons
        self._personal = self._scan_personal()
        self._partnerships = self._scan_partnerships()

    # -- SourceRepository protocol ------------------------------------------

    def get(self, slug: str) -> SkillsetSource | None:
        if slug == "commons":
            return self._commons_source()
        if slug == "personal":
            return self._personal_source()
        if slug in self._partnerships:
            return SkillsetSource(
                slug=slug,
                source_type=SourceType.PARTNERSHIP,
                skillset_names=self._partnerships[slug],
            )
        return None

    def list_all(self) -> list[SkillsetSource]:
        sources = [self._commons_source()]
        personal = self._personal_source()
        if personal.skillset_names:
            sources.append(personal)
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
        if skillset_name in self._personal:
            return "personal"
        for slug, names in self._partnerships.items():
            if skillset_name in names:
                return slug
        return None

    # -- Internals ----------------------------------------------------------

    def _scan_personal(self) -> list[str]:
        """Scan personal/ for BC packages, returning skillset names."""
        skillsets = collect_pipelines(self._repo_root / "personal")
        return [s.name for s in skillsets]

    def _scan_partnerships(self) -> dict[str, list[str]]:
        """Scan partnerships/ for BC packages, returning {slug: [skillset_names]}."""
        result: dict[str, list[str]] = {}
        partnerships_dir = self._repo_root / "partnerships"
        if not partnerships_dir.is_dir():
            return result
        for subdir in sorted(partnerships_dir.iterdir()):
            if not subdir.is_dir():
                continue
            skillsets = collect_pipelines(subdir)
            if skillsets:
                result[subdir.name] = [s.name for s in skillsets]
        return result

    def _commons_source(self) -> SkillsetSource:
        return SkillsetSource(
            slug="commons",
            source_type=SourceType.COMMONS,
            skillset_names=[s.name for s in self._commons.list_all()],
        )

    def _personal_source(self) -> SkillsetSource:
        return SkillsetSource(
            slug="personal",
            source_type=SourceType.PERSONAL,
            skillset_names=self._personal,
        )
