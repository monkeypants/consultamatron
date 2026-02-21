"""Skillset repository that aggregates PIPELINES from BC modules.

Discovers bounded context packages from all source containers
(commons submodules, personal, partnerships) using shared directory scanning.
"""

from __future__ import annotations

from pathlib import Path

from practice.bc_discovery import bc_package_dirs, collect_pipelines
from practice.entities import Pipeline


class CodeSkillsetRepository:
    """Aggregates PIPELINES from all BC package directories."""

    def __init__(self, repo_root: Path) -> None:
        self._pipelines: list[Pipeline] = []
        for pkg_dir in bc_package_dirs(repo_root):
            self._pipelines.extend(collect_pipelines(pkg_dir))

    def get(self, name: str) -> Pipeline | None:
        for p in self._pipelines:
            if p.name == name:
                return p
        return None

    def list_all(self) -> list[Pipeline]:
        return list(self._pipelines)
