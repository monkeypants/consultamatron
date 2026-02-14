"""DI container and config tests.

Verify wiring: every container attribute satisfies its protocol,
and Config.from_repo_root produces correct paths.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.repositories import (
    DecisionRepository,
    EngagementRepository,
    ProjectRepository,
    ResearchTopicRepository,
    SiteRenderer,
    SkillsetRepository,
    TourManifestRepository,
)


class TestConfig:
    def test_from_repo_root(self):
        config = Config.from_repo_root(Path("/repo"))
        assert config.repo_root == Path("/repo")
        assert config.workspace_root == Path("/repo/clients")
        assert config.skillsets_root == Path("/repo/skillsets")

    def test_frozen(self):
        config = Config.from_repo_root(Path("/repo"))
        try:
            config.workspace_root = Path("/other")  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestContainerProtocolConformance:
    """Every container attribute satisfies its protocol."""

    def test_skillsets(self, container):
        assert isinstance(container.skillsets, SkillsetRepository)

    def test_projects(self, container):
        assert isinstance(container.projects, ProjectRepository)

    def test_decisions(self, container):
        assert isinstance(container.decisions, DecisionRepository)

    def test_engagement(self, container):
        assert isinstance(container.engagement, EngagementRepository)

    def test_research(self, container):
        assert isinstance(container.research, ResearchTopicRepository)

    def test_tours(self, container):
        assert isinstance(container.tours, TourManifestRepository)

    def test_site_renderer(self, container):
        assert isinstance(container.site_renderer, SiteRenderer)


class TestContainerUsecaseWiring:
    """Every usecase attribute exists and is callable."""

    USECASE_ATTRS = [
        "initialize_workspace_usecase",
        "register_project_usecase",
        "update_project_status_usecase",
        "record_decision_usecase",
        "add_engagement_entry_usecase",
        "register_research_topic_usecase",
        "register_tour_usecase",
        "list_projects_usecase",
        "get_project_usecase",
        "get_project_progress_usecase",
        "list_decisions_usecase",
        "list_research_topics_usecase",
        "render_site_usecase",
    ]

    @pytest.mark.parametrize("attr", USECASE_ATTRS)
    def test_usecase_exists_and_has_execute(self, container, attr):
        usecase = getattr(container, attr)
        assert callable(getattr(usecase, "execute", None))


class TestContainerUsable:
    """Repos from the container work against the temp workspace."""

    def test_round_trip_through_container(self, container):
        from .conftest import make_project

        container.projects.save(make_project())
        got = container.projects.get("holloway-group", "maps-1")
        assert got is not None
        assert got.slug == "maps-1"
