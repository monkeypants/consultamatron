"""Tests for BmcProjectPresenter.

Verifies content assembly from workspace files into ProjectContribution
entities without involving any rendering infrastructure.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from business_model_canvas.presenter import BmcProjectPresenter

CLIENT = "test-corp"
SLUG = "bmc-1"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _make_project(**overrides) -> Project:
    defaults = dict(
        slug=SLUG,
        client=CLIENT,
        engagement="strat-1",
        skillset="business-model-canvas",
        status=ProjectStatus.ELABORATION,
        created=date(2025, 6, 1),
    )
    return Project(**(defaults | overrides))


# ---------------------------------------------------------------------------
# Presenter contract (doctrine gate)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPresenterContract:
    """BmcProjectPresenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        client = "presenter-test"
        slug = "test-1"

        proj_dir = tmp_path / client / "engagements" / "strat-1" / slug
        _write(proj_dir / "brief.agreed.md", "# Brief\n\nMinimal conformance test.")

        presenter = BmcProjectPresenter(workspace_root=tmp_path)
        project = Project(
            slug=slug,
            client=client,
            engagement="strat-1",
            skillset="business-model-canvas",
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )

        result = presenter.present(project)

        assert isinstance(result, ProjectContribution)
        assert result.slug == slug
        assert result.skillset == "business-model-canvas"
        assert isinstance(result.sections, list)


# ---------------------------------------------------------------------------
# Fully equipped workspace
# ---------------------------------------------------------------------------


@pytest.fixture
def full_workspace(tmp_path):
    """Workspace with all BMC stages."""
    ws = tmp_path / CLIENT
    proj = ws / "engagements" / "strat-1" / SLUG

    _write(proj / "brief.agreed.md", "# BMC Brief\n\nBusiness model analysis.")
    _write(
        proj / "segments" / "segments.agreed.md",
        "# Customer Segments\n\n- Enterprise\n- SMB",
    )
    _write(
        proj / "canvas.agreed.md",
        "# Business Model Canvas\n\n## Value Propositions\n\nFreight visibility.",
    )
    _write(proj / "decisions.md", "# Decisions\n\n## D-001\n\nProject created.")

    return tmp_path


class TestFullWorkspace:
    """Fully equipped BMC project."""

    def test_has_analysis_section(self, full_workspace):
        presenter = BmcProjectPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        assert len(contrib.sections) == 1
        assert contrib.sections[0].label == "Analysis"

    def test_all_pages_present(self, full_workspace):
        presenter = BmcProjectPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        slugs = [p.slug for p in contrib.sections[0].pages]
        assert slugs == ["canvas", "segments", "brief", "decisions"]

    def test_overview_is_canvas(self, full_workspace):
        presenter = BmcProjectPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        assert "Value Propositions" in contrib.overview_md

    def test_no_hero_figure(self, full_workspace):
        presenter = BmcProjectPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        assert contrib.hero_figure is None

    def test_canvas_content(self, full_workspace):
        presenter = BmcProjectPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        canvas_page = contrib.sections[0].pages[0]
        assert "Freight visibility" in canvas_page.body_md


class TestMinimalWorkspace:
    """BMC project with only a brief."""

    def test_single_page(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "engagements" / "strat-1" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nMinimal.")

        presenter = BmcProjectPresenter(workspace_root=tmp_path)
        contrib = presenter.present(_make_project())
        assert len(contrib.sections) == 1
        assert len(contrib.sections[0].pages) == 1
        assert contrib.sections[0].pages[0].slug == "brief"

    def test_no_overview_without_canvas(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "engagements" / "strat-1" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nMinimal.")

        presenter = BmcProjectPresenter(workspace_root=tmp_path)
        contrib = presenter.present(_make_project())
        assert contrib.overview_md == ""


class TestEmptyWorkspace:
    """BMC project with no artifacts."""

    def test_no_sections(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "engagements" / "strat-1" / SLUG
        proj.mkdir(parents=True)

        presenter = BmcProjectPresenter(workspace_root=tmp_path)
        contrib = presenter.present(_make_project())
        assert contrib.sections == []
