"""Tests for ConsultingProjectPresenter."""

from __future__ import annotations

from datetime import date

import pytest

from practice.content import ProjectContribution
from practice.entities import Project, ProjectStatus
from consulting.presenter import ConsultingProjectPresenter


@pytest.mark.doctrine
class TestPresenterContract:
    """ConsultingProjectPresenter produces valid ProjectContribution."""

    def test_produces_project_contribution(self, tmp_path):
        presenter = ConsultingProjectPresenter(workspace_root=tmp_path)
        project = Project(
            slug="consult-1",
            client="test-corp",
            engagement="strat-1",
            skillset="consulting",
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )
        result = presenter.present(project)
        assert isinstance(result, ProjectContribution)
        assert result.skillset == "consulting"
