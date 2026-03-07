"""Shared fixtures and entity builders for the cli test suite."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from practice.bc_discovery import discover_all_bc_modules
from practice.entities import DecisionEntry, EngagementEntry
from practice.discovery import PipelineStage
from practice.entities import (
    ActorGoal,
    CompilationState,
    Confidence,
    Engagement,
    EngagementDashboard,
    EngagementStatus,
    ItemFreshness,
    KnowledgePack,
    NextAction,
    Observation,
    ObservationNeed,
    PackFreshness,
    Pipeline,
    Profile,
    Project,
    ProjectPipelinePosition,
    ProjectStatus,
    ResearchTopic,
    RoutingAllowList,
    RoutingDestination,
    SkillManifest,
    SkillsetSource,
    Skillset,
    SourceType,
)
from click.testing import CliRunner

from bin.cli.infrastructure.json_entity_store import JsonEntityStore
from bin.cli.infrastructure.json_repos import (
    JsonDecisionRepository,
    JsonEngagementEntityRepository,
    JsonEngagementLogRepository,
    JsonProjectRepository,
    JsonResearchTopicRepository,
)


_REPO_ROOT = Path(__file__).resolve().parent.parent
_HAS_BC_PACKAGES = bool(discover_all_bc_modules(_REPO_ROOT))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def requires_bc_packages():
    """Skip the test when no BC packages are installed (e.g. CI without commons/)."""
    if not _HAS_BC_PACKAGES:
        pytest.skip("No BC packages installed")


@pytest.fixture
def tmp_config(tmp_path):
    """Config with real repo_root for BC discovery, temp workspace for isolation."""
    return Config(
        repo_root=_REPO_ROOT,
        workspace_root=tmp_path / "clients",
    )


@pytest.fixture
def container(tmp_config, requires_bc_packages):
    """Fully wired container against a temp workspace."""
    return Container(tmp_config)


@pytest.fixture
def run(tmp_config, monkeypatch, requires_bc_packages):
    """Invoke CLI commands against a temp workspace with skillsets auto-discovered."""
    from bin.cli.main import cli

    monkeypatch.setattr(
        "bin.cli.main.Config",
        type(
            "Config",
            (),
            {"from_repo_root": staticmethod(lambda _: tmp_config)},
        ),
    )
    runner = CliRunner()
    return lambda *args: runner.invoke(cli, list(args))


# -- Parametrized repository fixtures (one per protocol) -------------------
# Adding an implementation = adding one elif + one params entry.


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


@pytest.fixture(params=["filesystem"])
def needs_reader(request, tmp_path):
    if request.param == "filesystem":
        from bin.cli.infrastructure.filesystem_needs_reader import FilesystemNeedsReader

        return FilesystemNeedsReader(
            repo_root=tmp_path,
            workspace_root=tmp_path / "clients",
        )


@pytest.fixture(params=["filesystem"])
def observation_writer(request, tmp_path):
    if request.param == "filesystem":
        from bin.cli.infrastructure.filesystem_observation_writer import (
            FilesystemObservationWriter,
        )

        return FilesystemObservationWriter(
            repo_root=tmp_path,
            workspace_root=tmp_path / "clients",
        )


@pytest.fixture(params=["filesystem"])
def pending_store(request, tmp_path):
    if request.param == "filesystem":
        from bin.cli.infrastructure.filesystem_pending_store import (
            FilesystemPendingObservationStore,
        )

        return FilesystemPendingObservationStore(
            workspace_root=tmp_path / "clients",
        )


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


def make_pipeline(**overrides) -> Pipeline:
    defaults = dict(
        name="test-skillset",
        display_name="Test Skillset",
        description="Test methodology.",
        stages=[
            PipelineStage(
                order=1,
                skill="test-stage-1",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Project kickoff",
            ),
        ],
        slug_pattern="test-{n}",
    )
    return Pipeline(**(defaults | overrides))


def make_skillset(**overrides) -> Skillset:
    defaults = dict(
        name="test-skillset",
        display_name="Test Skillset",
        description="Test methodology.",
        pipelines=[make_pipeline()],
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
        pipelines=[
            make_pipeline(
                name="competitive-analysis", stages=[], slug_pattern="comp-{n}"
            )
        ],
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


def make_engagement_entry(**overrides) -> EngagementEntry:
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


def make_skill_manifest(**overrides) -> SkillManifest:
    defaults = dict(
        name="test-skill",
        description="A test skill for conformance.",
        metadata=dict(
            author="monkeypants",
            version="0.1",
            freedom="medium",
        ),
    )
    merged = defaults | overrides
    return SkillManifest.model_validate(merged)


def make_observation_need(**overrides) -> ObservationNeed:
    defaults = dict(
        slug="client-strategic-gaps",
        owner_type="client",
        owner_ref="holloway-group",
        level="type",
        need="Watch for strategic gaps in freight operations",
        rationale="Improves next engagement scoping",
        lifecycle_moment="research",
        served=False,
    )
    return ObservationNeed(**(defaults | overrides))


def make_routing_destination(**overrides) -> RoutingDestination:
    defaults = dict(
        owner_type="client",
        owner_ref="holloway-group",
    )
    return RoutingDestination(**(defaults | overrides))


def make_routing_allow_list(**overrides) -> RoutingAllowList:
    defaults = dict(
        destinations=[make_routing_destination()],
    )
    return RoutingAllowList(**(defaults | overrides))


def make_observation(**overrides) -> Observation:
    defaults = dict(
        slug="freight-digital-gap",
        source_inflection="gatepoint",
        need_refs=["client-strategic-gaps"],
        content="Digital platform trails industry evolution by two stages.",
        destinations=[make_routing_destination()],
    )
    return Observation(**(defaults | overrides))


# ---------------------------------------------------------------------------
# Freshness value object builders
# ---------------------------------------------------------------------------


def make_item_freshness(**overrides) -> ItemFreshness:
    defaults = dict(
        name="test-item",
        is_composite=False,
        state="clean",
    )
    return ItemFreshness(**(defaults | overrides))


def make_pack_freshness(**overrides) -> PackFreshness:
    defaults = dict(
        pack_root="/tmp/test-pack",
        compilation_state=CompilationState.CLEAN,
        items=[make_item_freshness()],
    )
    return PackFreshness(**(defaults | overrides))


# ---------------------------------------------------------------------------
# Filesystem helpers for freshness tests
# ---------------------------------------------------------------------------


def write_pack(tmp_path, name, items, *, bytecode=None, children=None, manifest=None):
    """Create a pack directory with content-hash-based bytecode.

    items: dict of {name: content} — creates {name}.md files
    bytecode: dict of {name: content} — creates _bytecode/{name}.md
              wrapped in frontmatter with the correct source_hash
              computed from the corresponding source item.
              If a name appears in bytecode but not in items or
              children, it is written as-is (orphan test case).
    children: list of (name, items, bytecode) tuples — nested packs
    manifest: dict of frontmatter keys — defaults to name + purpose
    Returns the pack root Path.
    """
    from practice.content_hash import hash_children, hash_content
    from practice.frontmatter import format_frontmatter

    manifest = manifest or {"name": "test", "purpose": "Test pack."}
    pack_root = tmp_path / name
    pack_root.mkdir(parents=True, exist_ok=True)

    # Write index.md (manifest)
    fm = "---\n" + "\n".join(f"{k}: {v}" for k, v in manifest.items()) + "\n---\n"
    (pack_root / "index.md").write_text(fm)

    # Write items
    for item_name, content in items.items():
        (pack_root / f"{item_name}.md").write_text(content)

    # Collect child names for bytecode hash computation
    child_names = set()

    # Write children (nested packs) — before bytecode so composite hashes work
    if children is not None:
        for child_name, child_items, child_bytecode in children:
            child_names.add(child_name)
            child_root = pack_root / child_name
            child_root.mkdir(exist_ok=True)
            (child_root / "index.md").write_text(
                "---\nname: child\npurpose: Child pack.\n---\n"
            )
            for item_name, content in child_items.items():
                (child_root / f"{item_name}.md").write_text(content)
            if child_bytecode is not None:
                child_bc = child_root / "_bytecode"
                child_bc.mkdir(exist_ok=True)
                for bc_name, content in child_bytecode.items():
                    source_hash = hash_content(child_items.get(bc_name, content))
                    (child_bc / f"{bc_name}.md").write_text(
                        format_frontmatter({"source_hash": source_hash}, content)
                    )

    # Write bytecode with correct source_hash frontmatter
    if bytecode is not None:
        bc_dir = pack_root / "_bytecode"
        bc_dir.mkdir(exist_ok=True)
        for bc_name, content in bytecode.items():
            if bc_name in items:
                # Leaf item — hash from source content
                source_hash = hash_content(items[bc_name])
                (bc_dir / f"{bc_name}.md").write_text(
                    format_frontmatter({"source_hash": source_hash}, content)
                )
            elif bc_name in child_names:
                # Composite item — hash from child bytecode dir
                child_bc_dir = pack_root / bc_name / "_bytecode"
                if child_bc_dir.is_dir():
                    source_hash = hash_children(child_bc_dir)
                    (bc_dir / f"{bc_name}.md").write_text(
                        format_frontmatter({"source_hash": source_hash}, content)
                    )
                else:
                    (bc_dir / f"{bc_name}.md").write_text(content)
            else:
                # Orphan or raw — write as-is
                (bc_dir / f"{bc_name}.md").write_text(content)

    return pack_root


class StubCompiler:
    """Deterministic compiler for testing pack-and-wrap orchestration."""

    def __init__(self):
        self.calls: list[Path] = []

    def compile(self, item_path: Path, pack_root: Path) -> str:
        self.calls.append(item_path)
        return f"Summary of {item_path.stem}"
