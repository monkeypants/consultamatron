"""Test Method project presenter."""

from __future__ import annotations

from pathlib import Path

from practice.content import ProjectContribution
from practice.entities import Project


class TestMethodPresenter:
    """Assembles Test Method workspace artifacts into structured content."""

    def __init__(self, workspace_root: Path) -> None:
        self._ws_root = workspace_root

    def present(self, project: Project) -> ProjectContribution:
        return ProjectContribution(
            slug=project.slug,
            title=project.slug,
            skillset=project.skillset,
            status=project.status.value,
            hero_figure=None,
            overview_md="",
            sections=[],
        )
