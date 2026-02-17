"""Tests for CompetitiveAnalysisPresenter."""

from __future__ import annotations

from datetime import date

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from competitive_analysis.presenter import CompetitiveAnalysisPresenter


@pytest.mark.doctrine
class TestPresenterContract:
    """CompetitiveAnalysisPresenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        presenter = CompetitiveAnalysisPresenter(workspace_root=tmp_path)
        project = Project(
            slug="test-1",
            client="test-corp",
            engagement="strat-1",
            skillset="competitive-analysis",
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )
        result = presenter.present(project)
        assert isinstance(result, ProjectContribution)
        assert result.slug == "test-1"
        assert result.skillset == "competitive-analysis"
        assert isinstance(result.sections, list)
