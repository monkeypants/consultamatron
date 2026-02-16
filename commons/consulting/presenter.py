"""Consulting project presenter.

Minimal presenter for the engagement lifecycle skillset.
Consulting projects are orchestration — their deliverables are
the projects they spawn, not standalone artifacts.
"""

from __future__ import annotations

from pathlib import Path

from practice.content import ProjectContribution
from practice.entities import Project


class ConsultingProjectPresenter:
    """Assembles consulting lifecycle artifacts into structured content."""

    def __init__(self, workspace_root: Path) -> None:
        self._ws_root = workspace_root

    def present(self, project: Project) -> ProjectContribution:
        return ProjectContribution(
            slug=project.slug,
            title=project.slug,
            skillset=project.skillset,
            status=project.status.value,
            overview_md="",
            sections=[],
        )
