"""Business Model Canvas project presenter.

Assembles workspace artifacts for a BMC project into a
ProjectContribution that any renderer can consume without knowing
the skillset internals.
"""

from __future__ import annotations

from pathlib import Path

from practice.content import ContentPage, ProjectContribution, ProjectSection
from practice.entities import Project


def _read_md(path: Path) -> str:
    """Read a markdown file and return its text, or empty string."""
    if path.is_file():
        return path.read_text()
    return ""


class BmcProjectPresenter:
    """Assembles BMC workspace artifacts into structured content."""

    def __init__(self, workspace_root: Path) -> None:
        self._ws_root = workspace_root

    def present(
        self,
        project: Project,
    ) -> ProjectContribution:
        proj_dir = (
            self._ws_root
            / project.client
            / "engagements"
            / project.engagement
            / project.slug
        )

        has_brief = (proj_dir / "brief.agreed.md").is_file()
        has_segments = (proj_dir / "segments" / "segments.agreed.md").is_file()
        has_canvas = (proj_dir / "canvas.agreed.md").is_file()
        has_decisions = (proj_dir / "decisions.md").is_file()

        pages: list[ContentPage] = []

        if has_canvas:
            pages.append(
                ContentPage(
                    title="Business Model Canvas",
                    slug="canvas",
                    body_md=_read_md(proj_dir / "canvas.agreed.md"),
                )
            )
        if has_segments:
            pages.append(
                ContentPage(
                    title="Customer Segments",
                    slug="segments",
                    body_md=_read_md(proj_dir / "segments" / "segments.agreed.md"),
                )
            )
        if has_brief:
            pages.append(
                ContentPage(
                    title="Project Brief",
                    slug="brief",
                    body_md=_read_md(proj_dir / "brief.agreed.md"),
                )
            )
        if has_decisions:
            pages.append(
                ContentPage(
                    title="Decisions",
                    slug="decisions",
                    body_md=_read_md(proj_dir / "decisions.md"),
                )
            )

        # Overview content is the canvas if available
        overview_md = _read_md(proj_dir / "canvas.agreed.md") if has_canvas else ""

        sections: list[ProjectSection] = []
        if pages:
            sections.append(
                ProjectSection(
                    label="Analysis",
                    slug="analysis",
                    description="Business model analysis artifacts",
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
