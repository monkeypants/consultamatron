"""Skillset repository that aggregates SKILLSETS from BC modules.

Discovers bounded context packages from three source containers
(commons, personal, partnerships) using shared directory scanning.
"""

from __future__ import annotations

from pathlib import Path

from practice.bc_discovery import collect_skillsets, source_container_dirs
from practice.entities import Skillset


class CodeSkillsetRepository:
    """Aggregates SKILLSETS from all three source containers."""

    def __init__(self, repo_root: Path) -> None:
        self._skillsets: list[Skillset] = []
        for container_dir in source_container_dirs(repo_root):
            self._skillsets.extend(collect_skillsets(container_dir))

    def get(self, name: str) -> Skillset | None:
        for s in self._skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return list(self._skillsets)
