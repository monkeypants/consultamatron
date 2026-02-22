"""Skillset repository that aggregates Skillsets from BC modules.

Discovers bounded context packages from all source containers
(commons submodules, personal, partnerships) using shared directory scanning.
"""

from __future__ import annotations

from pathlib import Path

from practice.bc_discovery import bc_package_dirs, collect_skillset_objects
from practice.entities import Skillset


class CodeSkillsetRepository:
    """Aggregates Skillsets from all BC package directories."""

    def __init__(self, repo_root: Path) -> None:
        self._skillsets: list[Skillset] = []
        for pkg_dir in bc_package_dirs(repo_root):
            self._skillsets.extend(collect_skillset_objects(pkg_dir))

    def get(self, name: str) -> Skillset | None:
        for s in self._skillsets:
            if s.name == name:
                return s
        return None

    def list_all(self) -> list[Skillset]:
        return list(self._skillsets)
