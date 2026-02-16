"""Tests for SkillsetEngineeringPresenter."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from skillset_engineering.presenter import SkillsetEngineeringPresenter

CLIENT = "test-corp"
SLUG = "skillset-1"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _make_project(**overrides) -> Project:
    defaults = dict(
        slug=SLUG,
        client=CLIENT,
        engagement="strat-1",
        skillset="new-skillset",
        status=ProjectStatus.ELABORATION,
        created=date(2025, 6, 1),
    )
    return Project(**(defaults | overrides))


# ---------------------------------------------------------------------------
# Presenter contract (doctrine gate)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPresenterContract:
    """SkillsetEngineeringPresenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        presenter = SkillsetEngineeringPresenter(workspace_root=tmp_path)
        project = Project(
            slug="test-1",
            client="presenter-test",
            engagement="strat-1",
            skillset="new-skillset",
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )
        result = presenter.present(project)
        assert isinstance(result, ProjectContribution)
        assert result.slug == "test-1"
        assert result.skillset == "new-skillset"
        assert isinstance(result.sections, list)


# ---------------------------------------------------------------------------
# Fully equipped workspace
# ---------------------------------------------------------------------------


@pytest.fixture
def full_workspace(tmp_path):
    ws = tmp_path / CLIENT
    proj = ws / "engagements" / "strat-1" / SLUG

    _write(proj / "brief.agreed.md", "# Skillset Brief\n\nNew methodology.")
    _write(
        proj / "research" / "synthesis.agreed.md",
        "# Domain Research\n\n## Findings\n\nKey insight.",
    )
    _write(
        proj / "design" / "design.agreed.md",
        "# Pipeline Design\n\n## Stages\n\n1. Research\n2. Analyse",
    )
    _write(
        proj / "implementation.agreed.md",
        "# Implementation\n\nBC package created. Conformance tests pass.",
    )

    return tmp_path


class TestFullWorkspace:
    def test_has_engineering_section(self, full_workspace):
        presenter = SkillsetEngineeringPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        assert len(contrib.sections) == 1
        assert contrib.sections[0].label == "Engineering"

    def test_all_pages_present(self, full_workspace):
        presenter = SkillsetEngineeringPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        slugs = [p.slug for p in contrib.sections[0].pages]
        assert slugs == ["design", "research", "brief", "implementation"]

    def test_overview_is_design(self, full_workspace):
        presenter = SkillsetEngineeringPresenter(workspace_root=full_workspace)
        contrib = presenter.present(_make_project())
        assert "Pipeline Design" in contrib.overview_md


class TestEmptyWorkspace:
    def test_no_sections(self, tmp_path):
        proj = tmp_path / CLIENT / "engagements" / "strat-1" / SLUG
        proj.mkdir(parents=True)
        presenter = SkillsetEngineeringPresenter(workspace_root=tmp_path)
        contrib = presenter.present(_make_project())
        assert contrib.sections == []
