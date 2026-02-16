"""Skillset Engineering project presenter.

Assembles workspace artifacts for a skillset engineering project into a
ProjectContribution that any renderer can consume.
"""

from __future__ import annotations

from pathlib import Path

from practice.content import ContentPage, ProjectContribution, ProjectSection
from practice.entities import Project


def _read_md(path: Path) -> str:
    if path.is_file():
        return path.read_text()
    return ""


class SkillsetEngineeringPresenter:
    """Assembles skillset engineering workspace artifacts into content."""

    def __init__(self, workspace_root: Path) -> None:
        self._ws_root = workspace_root

    def present(self, project: Project) -> ProjectContribution:
        proj_dir = (
            self._ws_root
            / project.client
            / "engagements"
            / project.engagement
            / project.slug
        )

        has_brief = (proj_dir / "brief.agreed.md").is_file()
        has_synthesis = (proj_dir / "research" / "synthesis.agreed.md").is_file()
        has_design = (proj_dir / "design" / "design.agreed.md").is_file()
        has_implementation = (proj_dir / "implementation.agreed.md").is_file()

        pages: list[ContentPage] = []

        if has_design:
            pages.append(
                ContentPage(
                    title="Pipeline Design",
                    slug="design",
                    body_md=_read_md(proj_dir / "design" / "design.agreed.md"),
                )
            )
        if has_synthesis:
            pages.append(
                ContentPage(
                    title="Domain Research",
                    slug="research",
                    body_md=_read_md(proj_dir / "research" / "synthesis.agreed.md"),
                )
            )
        if has_brief:
            pages.append(
                ContentPage(
                    title="Skillset Brief",
                    slug="brief",
                    body_md=_read_md(proj_dir / "brief.agreed.md"),
                )
            )
        if has_implementation:
            pages.append(
                ContentPage(
                    title="Implementation",
                    slug="implementation",
                    body_md=_read_md(proj_dir / "implementation.agreed.md"),
                )
            )

        overview_md = (
            _read_md(proj_dir / "design" / "design.agreed.md") if has_design else ""
        )

        sections: list[ProjectSection] = []
        if pages:
            sections.append(
                ProjectSection(
                    label="Engineering",
                    slug="engineering",
                    description="Skillset engineering artifacts",
                    pages=pages,
                )
            )

        return ProjectContribution(
            slug=project.slug,
            title=project.slug,
            skillset=project.skillset,
            status=project.status.value,
            hero_figure=None,
            overview_md=overview_md,
            sections=sections,
        )
