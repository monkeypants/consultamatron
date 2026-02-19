"""Shared fixtures and entity builders for the cli test suite."""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from consulting.entities import DecisionEntry, EngagementEntry
from practice.discovery import PipelineStage
from practice.entities import (
    ActorGoal,
    Confidence,
    Engagement,
    EngagementDashboard,
    EngagementStatus,
    KnowledgePack,
    NextAction,
    Profile,
    Project,
    ProjectPipelinePosition,
    ProjectStatus,
    ResearchTopic,
    SkillsetSource,
    Skillset,
    SourceType,
)
from bin.cli.infrastructure.json_entity_store import JsonEntityStore
from bin.cli.infrastructure.json_repos import (
    JsonDecisionRepository,
    JsonEngagementEntityRepository,
    JsonEngagementLogRepository,
    JsonProjectRepository,
    JsonResearchTopicRepository,
    JsonSkillsetRepository,
)


_REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_config(tmp_path):
    """Config with real repo_root for BC discovery, temp workspace for isolation."""
    return Config(
        repo_root=_REPO_ROOT,
        workspace_root=tmp_path / "clients",
        skillsets_root=tmp_path / "skillsets",
    )


@pytest.fixture
def container(tmp_config):
    """Fully wired container against a temp workspace."""
    return Container(tmp_config)


# -- Parametrized repository fixtures (one per protocol) -------------------
# Adding an implementation = adding one elif + one params entry.


@pytest.fixture(params=["json"])
def skillset_repo(request, tmp_config):
    if request.param == "json":
        return JsonSkillsetRepository(tmp_config.skillsets_root)


@pytest.fixture(params=["json"])
def project_repo(request, tmp_config):
    if request.param == "json":
        return JsonProjectRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def decision_repo(request, tmp_config):
    if request.param == "json":
        return JsonDecisionRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def engagement_log_repo(request, tmp_config):
    if request.param == "json":
        return JsonEngagementLogRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def engagement_entity_repo(request, tmp_config):
    if request.param == "json":
        return JsonEngagementEntityRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def research_repo(request, tmp_config):
    if request.param == "json":
        return JsonResearchTopicRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def project_store(request, tmp_path):
    if request.param == "json":
        return JsonEntityStore(
            model=Project,
            key_field="slug",
            path_resolver=lambda f: (
                tmp_path
                / "clients"
                / f["client"]
                / "engagements"
                / f["engagement"]
                / "projects.json"
            ),
        )


@pytest.fixture(params=["json"])
def decision_store(request, tmp_path):
    if request.param == "json":
        return JsonEntityStore(
            model=DecisionEntry,
            key_field="id",
            path_resolver=lambda f: (
                tmp_path
                / "clients"
                / f["client"]
                / "engagements"
                / f["engagement"]
                / f["project_slug"]
                / "decisions.json"
            ),
            append_only=True,
        )


# ---------------------------------------------------------------------------
# Entity builders — sensible defaults, override what you care about
# ---------------------------------------------------------------------------

DEFAULT_CLIENT = "holloway-group"
DEFAULT_PROJECT = "maps-1"
DEFAULT_ENGAGEMENT = "strat-1"
DEFAULT_DATE = date(2025, 6, 1)
DEFAULT_TIMESTAMP = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def make_skillset(**overrides) -> Skillset:
    defaults = dict(
        name="test-skillset",
        display_name="Test Skillset",
        description="Test methodology.",
        pipeline=[
            PipelineStage(
                order=1,
                skill="test-stage-1",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Project kickoff",
            ),
        ],
        slug_pattern="test-{n}",
        problem_domain="Testing",
        deliverables=["Test deliverables"],
        value_proposition="Test value.",
        classification=["test"],
        evidence=[],
    )
    return Skillset(**(defaults | overrides))


def make_prospectus(**overrides) -> Skillset:
    defaults = dict(
        name="competitive-analysis",
        display_name="Competitive Analysis",
        description="Market positioning methodology.",
        pipeline=[],
        slug_pattern="comp-{n}",
        problem_domain="Market positioning",
        deliverables=["Competitor landscape report"],
        value_proposition="Know your rivals.",
        classification=["strategy", "market-analysis"],
        evidence=["Porter's Five Forces"],
    )
    return Skillset(**(defaults | overrides))


def make_project(**overrides) -> Project:
    defaults = dict(
        slug=DEFAULT_PROJECT,
        client=DEFAULT_CLIENT,
        engagement=DEFAULT_ENGAGEMENT,
        skillset="test-skillset",
        status=ProjectStatus.PLANNING,
        created=DEFAULT_DATE,
    )
    return Project(**(defaults | overrides))


def make_decision(**overrides) -> DecisionEntry:
    defaults = dict(
        id=str(uuid.uuid4()),
        client=DEFAULT_CLIENT,
        engagement=DEFAULT_ENGAGEMENT,
        project_slug=DEFAULT_PROJECT,
        date=DEFAULT_DATE,
        timestamp=DEFAULT_TIMESTAMP,
        title="Stage 1: Project brief agreed",
        fields={"Scope": "Freight operations"},
    )
    return DecisionEntry(**(defaults | overrides))


def make_engagement(**overrides) -> EngagementEntry:
    defaults = dict(
        id=str(uuid.uuid4()),
        client=DEFAULT_CLIENT,
        engagement=DEFAULT_ENGAGEMENT,
        date=DEFAULT_DATE,
        timestamp=DEFAULT_TIMESTAMP,
        title="Client onboarded",
        fields={},
    )
    return EngagementEntry(**(defaults | overrides))


def make_engagement_entity(**overrides) -> Engagement:
    defaults = dict(
        slug=DEFAULT_ENGAGEMENT,
        client=DEFAULT_CLIENT,
        status=EngagementStatus.PLANNING,
        allowed_sources=["commons", "personal"],
        created=DEFAULT_DATE,
    )
    return Engagement(**(defaults | overrides))


def make_skillset_source(**overrides) -> SkillsetSource:
    defaults = dict(
        slug="commons",
        source_type=SourceType.COMMONS,
        skillset_names=["test-skillset"],
    )
    return SkillsetSource(**(defaults | overrides))


def make_research(**overrides) -> ResearchTopic:
    defaults = dict(
        filename="market-position.md",
        client=DEFAULT_CLIENT,
        topic="Market position",
        date=DEFAULT_DATE,
        confidence=Confidence.MEDIUM,
    )
    return ResearchTopic(**(defaults | overrides))


def make_profile(**overrides) -> Profile:
    defaults = dict(
        name="test-profile",
        display_name="Test Profile",
        description="A test profile.",
        skillsets=["test-skillset"],
    )
    return Profile(**(defaults | overrides))


def make_pipeline_position(**overrides) -> ProjectPipelinePosition:
    defaults = dict(
        project_slug=DEFAULT_PROJECT,
        skillset="test-skillset",
        current_stage=1,
        total_stages=3,
        completed_gates=[],
        next_gate="brief.agreed.md",
    )
    return ProjectPipelinePosition(**(defaults | overrides))


def make_engagement_dashboard(**overrides) -> EngagementDashboard:
    defaults = dict(
        engagement_slug=DEFAULT_ENGAGEMENT,
        status="active",
        projects=[],
    )
    return EngagementDashboard(**(defaults | overrides))


def make_next_action(**overrides) -> NextAction:
    defaults = dict(
        skill="wm-research",
        project_slug=DEFAULT_PROJECT,
        reason="Run wm-research for maps-1",
        prerequisite_exists=True,
    )
    return NextAction(**(defaults | overrides))


def make_actor_goal(**overrides) -> ActorGoal:
    defaults = dict(
        actor="skill author",
        goal="understand conformance requirements for a new BC",
    )
    return ActorGoal(**(defaults | overrides))


def make_knowledge_pack(**overrides) -> KnowledgePack:
    defaults = dict(
        name="platform-architecture",
        purpose="Architectural knowledge for extending Consultamatron.",
        actor_goals=[make_actor_goal()],
        triggers=["adding a new bounded context"],
    )
    return KnowledgePack(**(defaults | overrides))


def _write_skillsets(skillsets_root, skillsets):
    """Write skillset manifests to the test workspace index."""
    index = skillsets_root / "index.json"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        json.dumps([s.model_dump(mode="json") for s in skillsets], indent=2) + "\n"
    )


def seed_all_skillsets(skillsets_root):
    """Write all discovered skillsets to a test workspace."""
    from bin.cli.infrastructure.code_skillset_repository import CodeSkillsetRepository

    repo = CodeSkillsetRepository(_REPO_ROOT)
    _write_skillsets(skillsets_root, repo.list_all())
