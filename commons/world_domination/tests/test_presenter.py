"""Tests for WorldDominationProjectPresenter."""

from __future__ import annotations

from datetime import date

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from world_domination.presenter import WorldDominationProjectPresenter


@pytest.mark.doctrine
class TestPresenterContract:
    """WorldDominationProjectPresenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        presenter = WorldDominationProjectPresenter(workspace_root=tmp_path)
        project = Project(
            slug="wd-1",
            client="test-corp",
            engagement="strat-1",
            skillset="world-domination",
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )
        result = presenter.present(project)
        assert isinstance(result, ProjectContribution)
        assert result.skillset == "world-domination"
