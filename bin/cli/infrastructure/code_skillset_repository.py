"""Skillset repository that aggregates SKILLSETS from BC modules.

Replaces JsonSkillsetRepository by reading skillset declarations
directly from bounded context packages instead of from a JSON file.
"""

from __future__ import annotations

from types import ModuleType

from practice.entities import Skillset


class CodeSkillsetRepository:
    """Aggregates SKILLSETS attributes from bounded context modules.

    Each module must export a SKILLSETS: list[Skillset] attribute.
    """

    def __init__(self, modules: list[ModuleType]) -> None:
        self._skillsets: list[Skillset] = []
        for module in modules:
            self._skillsets.extend(module.SKILLSETS)

    def get(self, name: str) -> Skillset | None:
        for s in self._skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return list(self._skillsets)
