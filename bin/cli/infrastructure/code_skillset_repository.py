"""Skillset repository that aggregates PIPELINES from BC modules.

Discovers bounded context packages from three source containers
(commons, personal, partnerships) using shared directory scanning.
"""

from __future__ import annotations

from pathlib import Path

from practice.bc_discovery import collect_pipelines, source_container_dirs
from practice.entities import Pipeline


class CodeSkillsetRepository:
    """Aggregates PIPELINES from all three source containers."""

    def __init__(self, repo_root: Path) -> None:
        self._pipelines: list[Pipeline] = []
        for container_dir in source_container_dirs(repo_root):
            self._pipelines.extend(collect_pipelines(container_dir))

    def get(self, name: str) -> Pipeline | None:
        for p in self._pipelines:
            if p.name == name:
                return p
        return None

    def list_all(self) -> list[Pipeline]:
        return list(self._pipelines)
