"""Tests for TestMethodPresenter."""

from __future__ import annotations

from datetime import date

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from test_method.presenter import TestMethodPresenter


@pytest.mark.doctrine
class TestPresenterContract:
    """TestMethodPresenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        presenter = TestMethodPresenter(workspace_root=tmp_path)
        project = Project(
            slug="test-1",
            client="test-corp",
            engagement="strat-1",
            skillset="test-method",
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )
        result = presenter.present(project)
        assert isinstance(result, ProjectContribution)
        assert result.slug == "test-1"
        assert result.skillset == "test-method"
        assert isinstance(result.sections, list)
