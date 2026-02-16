"""Six Simple Rules Complexity Audit project presenter.

Assembles workspace artifacts for a complexity audit project into a
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


_RULE_FILES = [
    ("Rule 1: Understand What People Really Do", "rule1-understanding"),
    ("Rule 2: Reinforce Integrators", "rule2-integrators"),
    ("Rule 3: Increase Total Quantity of Power", "rule3-power"),
    ("Rule 4: Extend the Shadow of the Future", "rule4-future"),
    ("Rule 5: Increase Reciprocity", "rule5-reciprocity"),
    ("Rule 6: Reward Those Who Cooperate", "rule6-rewards"),
]


class CaProjectPresenter:
    """Assembles complexity audit workspace artifacts into structured content."""

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
        has_diagnostics = (proj_dir / "diagnostics.agreed.md").is_file()
        has_audit = (proj_dir / "audit.agreed.md").is_file()
        has_decisions = (proj_dir / "decisions.md").is_file()

        pages: list[ContentPage] = []

        if has_audit:
            pages.append(
                ContentPage(
                    title="Audit Report",
                    slug="audit",
                    body_md=_read_md(proj_dir / "audit.agreed.md"),
                )
            )
        if has_diagnostics:
            pages.append(
                ContentPage(
                    title="Diagnostics Summary",
                    slug="diagnostics",
                    body_md=_read_md(proj_dir / "diagnostics.agreed.md"),
                )
            )

        # Individual rule diagnostics
        diag_dir = proj_dir / "diagnostics"
        for title, slug in _RULE_FILES:
            path = diag_dir / f"{slug}.agreed.md"
            if path.is_file():
                pages.append(
                    ContentPage(
                        title=title,
                        slug=slug,
                        body_md=_read_md(path),
                    )
                )

        if has_brief:
            pages.append(
                ContentPage(
                    title="Audit Brief",
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

        overview_md = _read_md(proj_dir / "audit.agreed.md") if has_audit else ""

        sections: list[ProjectSection] = []
        if pages:
            sections.append(
                ProjectSection(
                    label="Complexity Audit",
                    slug="audit",
                    description="Organisational complexity audit artifacts",
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
