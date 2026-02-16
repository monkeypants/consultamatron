"""Commons-only SourceRepository implementation.

Returns a single "commons" source containing all skillsets from
the wrapped SkillsetRepository. Replaced by a composite
implementation when partnership discovery is added.
"""

from __future__ import annotations

from consulting.repositories import SkillsetRepository
from practice.entities import SkillsetSource, SourceType


class CommonsSourceRepository:
    """SourceRepository backed by a single commons source."""

    def __init__(self, skillsets: SkillsetRepository) -> None:
        self._skillsets = skillsets

    def get(self, slug: str) -> SkillsetSource | None:
        if slug == "commons":
            return self._commons()
        return None

    def list_all(self) -> list[SkillsetSource]:
        return [self._commons()]

    def skillset_source(self, skillset_name: str) -> str | None:
        for s in self._skillsets.list_all():
            if s.name == skillset_name:
                return "commons"
        return None

    def _commons(self) -> SkillsetSource:
        return SkillsetSource(
            slug="commons",
            source_type=SourceType.COMMONS,
            skillset_names=[s.name for s in self._skillsets.list_all()],
        )
