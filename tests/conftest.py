"""Shared fixtures and entity builders for the cli test suite."""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from consulting.entities import DecisionEntry, EngagementEntry
from practice.discovery import PipelineStage
from practice.entities import (
    Confidence,
    Project,
    ProjectStatus,
    ResearchTopic,
    Skillset,
)
from wardley_mapping.types import TourManifest, TourStop
from bin.cli.infrastructure.json_entity_store import JsonEntityStore
from bin.cli.infrastructure.json_repos import (
    JsonDecisionRepository,
    JsonEngagementRepository,
    JsonProjectRepository,
    JsonResearchTopicRepository,
    JsonSkillsetRepository,
    JsonTourManifestRepository,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_config(tmp_path):
    """Config pointing at a fresh temp directory."""
    return Config(
        repo_root=tmp_path,
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
def engagement_repo(request, tmp_config):
    if request.param == "json":
        return JsonEngagementRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def research_repo(request, tmp_config):
    if request.param == "json":
        return JsonResearchTopicRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def tour_repo(request, tmp_config):
    if request.param == "json":
        return JsonTourManifestRepository(tmp_config.workspace_root)


@pytest.fixture(params=["json"])
def project_store(request, tmp_path):
    if request.param == "json":
        return JsonEntityStore(
            model=Project,
            key_field="slug",
            path_resolver=lambda f: (
                tmp_path / "clients" / f["client"] / "projects" / "index.json"
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
                / "projects"
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
DEFAULT_DATE = date(2025, 6, 1)
DEFAULT_TIMESTAMP = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)


def make_skillset(**overrides) -> Skillset:
    defaults = dict(
        name="wardley-mapping",
        display_name="Wardley Mapping",
        description="Strategic mapping methodology.",
        pipeline=[
            PipelineStage(
                order=1,
                skill="wm-research",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Project kickoff",
            ),
        ],
        slug_pattern="maps-{n}",
    )
    return Skillset(**(defaults | overrides))


def make_project(**overrides) -> Project:
    defaults = dict(
        slug=DEFAULT_PROJECT,
        client=DEFAULT_CLIENT,
        skillset="wardley-mapping",
        status=ProjectStatus.PLANNING,
        created=DEFAULT_DATE,
    )
    return Project(**(defaults | overrides))


def make_decision(**overrides) -> DecisionEntry:
    defaults = dict(
        id=str(uuid.uuid4()),
        client=DEFAULT_CLIENT,
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
        date=DEFAULT_DATE,
        timestamp=DEFAULT_TIMESTAMP,
        title="Client onboarded",
        fields={},
    )
    return EngagementEntry(**(defaults | overrides))


def make_research(**overrides) -> ResearchTopic:
    defaults = dict(
        filename="market-position.md",
        client=DEFAULT_CLIENT,
        topic="Market position",
        date=DEFAULT_DATE,
        confidence=Confidence.MEDIUM,
    )
    return ResearchTopic(**(defaults | overrides))


def make_tour_stop(**overrides) -> TourStop:
    defaults = dict(
        order="1",
        title="Overview",
        atlas_source="atlas/overview/",
    )
    return TourStop(**(defaults | overrides))


def make_tour(**overrides) -> TourManifest:
    defaults = dict(
        name="investor",
        client=DEFAULT_CLIENT,
        project_slug=DEFAULT_PROJECT,
        title="Investor Tour",
        stops=[make_tour_stop()],
    )
    return TourManifest(**(defaults | overrides))


# ---------------------------------------------------------------------------
# Wardley Mapping pipeline — the five stages a map engagement walks through
# ---------------------------------------------------------------------------

WM_PIPELINE = [
    PipelineStage(
        order=1,
        skill="wm-research",
        prerequisite_gate="resources/index.md",
        produces_gate="brief.agreed.md",
        description="Stage 1: Project brief agreed",
    ),
    PipelineStage(
        order=2,
        skill="wm-needs",
        prerequisite_gate="brief.agreed.md",
        produces_gate="needs/needs.agreed.md",
        description="Stage 2: User needs agreed",
    ),
    PipelineStage(
        order=3,
        skill="wm-chain",
        prerequisite_gate="needs/needs.agreed.md",
        produces_gate="chain/supply-chain.agreed.md",
        description="Stage 3: Supply chain agreed",
    ),
    PipelineStage(
        order=4,
        skill="wm-evolve",
        prerequisite_gate="chain/supply-chain.agreed.md",
        produces_gate="evolve/map.agreed.owm",
        description="Stage 4: Evolution map agreed",
    ),
    PipelineStage(
        order=5,
        skill="wm-strategy",
        prerequisite_gate="evolve/map.agreed.owm",
        produces_gate="strategy/map.agreed.owm",
        description="Stage 5: Strategy map agreed",
    ),
]


BMC_PIPELINE = [
    PipelineStage(
        order=1,
        skill="bmc-research",
        prerequisite_gate="resources/index.md",
        produces_gate="brief.agreed.md",
        description="Stage 1: Project brief agreed",
    ),
    PipelineStage(
        order=2,
        skill="bmc-segments",
        prerequisite_gate="brief.agreed.md",
        produces_gate="segments/segments.agreed.md",
        description="Stage 2: Customer segments agreed",
    ),
    PipelineStage(
        order=3,
        skill="bmc-canvas",
        prerequisite_gate="segments/segments.agreed.md",
        produces_gate="canvas.agreed.md",
        description="Stage 3: Business Model Canvas agreed",
    ),
]


def _write_skillsets(skillsets_root, skillsets):
    """Write skillset manifests to the test workspace index."""
    index = skillsets_root / "index.json"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(
        json.dumps([s.model_dump(mode="json") for s in skillsets], indent=2) + "\n"
    )


def seed_wardley_mapping(skillsets_root):
    """Write the wardley-mapping skillset manifest to a test workspace.

    The five-stage pipeline mirrors the real skillset: research, needs,
    chain, evolution, strategy. Each stage's description is the decision
    title that marks it complete — this is how GetProjectProgress matches
    decisions against pipeline stages.
    """
    skillset = Skillset(
        name="wardley-mapping",
        display_name="Wardley Mapping",
        description=(
            "Strategic mapping from user needs through supply chain"
            " to evolution positioning and strategic annotation."
        ),
        pipeline=WM_PIPELINE,
        slug_pattern="maps-{n}",
    )
    _write_skillsets(skillsets_root, [skillset])


def seed_bmc_skillset(skillsets_root):
    """Write the business-model-canvas skillset manifest."""
    skillset = Skillset(
        name="business-model-canvas",
        display_name="Business Model Canvas",
        description="Nine-block business model analysis.",
        pipeline=BMC_PIPELINE,
        slug_pattern="bmc-{n}",
    )
    _write_skillsets(skillsets_root, [skillset])


def seed_all_skillsets(skillsets_root):
    """Write both wardley-mapping and business-model-canvas skillsets."""
    wm = Skillset(
        name="wardley-mapping",
        display_name="Wardley Mapping",
        description=(
            "Strategic mapping from user needs through supply chain"
            " to evolution positioning and strategic annotation."
        ),
        pipeline=WM_PIPELINE,
        slug_pattern="maps-{n}",
    )
    bmc = Skillset(
        name="business-model-canvas",
        display_name="Business Model Canvas",
        description="Nine-block business model analysis.",
        pipeline=BMC_PIPELINE,
        slug_pattern="bmc-{n}",
    )
    _write_skillsets(skillsets_root, [wm, bmc])
