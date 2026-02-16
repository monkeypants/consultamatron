"""SkillsetRepository that merges commons and partnership skillsets.

Wraps the code-declared commons skillsets from CodeSkillsetRepository
and adds any skillsets discovered in partnership directories on the
filesystem.  Partnership skillsets are loaded from
``partners/{slug}/skillsets/index.json``.
"""

from __future__ import annotations

import json
from pathlib import Path

from consulting.repositories import SkillsetRepository
from practice.entities import Skillset


class CompositeSkillsetRepository:
    """SkillsetRepository merging commons and partnership skillsets."""

    def __init__(self, commons: SkillsetRepository, repo_root: Path) -> None:
        self._commons = commons
        self._partnership_skillsets = self._load_partnerships(repo_root)

    # -- SkillsetRepository protocol ----------------------------------------

    def get(self, name: str) -> Skillset | None:
        result = self._commons.get(name)
        if result is not None:
            return result
        for s in self._partnership_skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return self._commons.list_all() + list(self._partnership_skillsets)

    # -- Internals ----------------------------------------------------------

    @staticmethod
    def _load_partnerships(repo_root: Path) -> list[Skillset]:
        result: list[Skillset] = []
        partnerships_dir = repo_root / "partners"
        if not partnerships_dir.is_dir():
            return result
        for subdir in sorted(partnerships_dir.iterdir()):
            if not subdir.is_dir():
                continue
            index = subdir / "skillsets" / "index.json"
            if not index.is_file():
                continue
            data = json.loads(index.read_text(encoding="utf-8"))
            for entry in data:
                result.append(Skillset.model_validate(entry))
        return result
