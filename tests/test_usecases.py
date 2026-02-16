"""Usecase tests: the request/response seam.

The application boundary where Request DTOs enter, business logic
executes against repository protocols, and Response DTOs emerge.
Tests follow ZOMBIE ordering within each usecase: Zero state, One
operation, Many, Boundaries, Interface, Exceptions.

The sample data describes a consulting engagement with Holloway Group,
a freight logistics company commissioning a Wardley Map of their
operations. The practice proceeds through the standard pipeline:
research, needs, chain, evolution, strategy.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from bin.cli.dtos import (
    ListSkillsetsRequest,
    RegisterProspectusRequest,
    UpdateProspectusRequest,
)
from consulting.dtos import (
    AddEngagementEntryRequest,
    AddEngagementSourceRequest,
    CreateEngagementRequest,
    GetEngagementRequest,
    GetProjectRequest,
    InitializeWorkspaceRequest,
    ListDecisionsRequest,
    ListEngagementsRequest,
    ListProjectsRequest,
    ListResearchTopicsRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
    RegisterResearchTopicRequest,
    RemoveEngagementSourceRequest,
    UpdateProjectStatusRequest,
)
from consulting.entities import DecisionEntry
from practice.exceptions import DuplicateError, InvalidTransitionError, NotFoundError
from bin.cli.di import Container

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


@pytest.fixture
def di(tmp_config):
    """Container with skillsets auto-discovered from BC modules."""
    return Container(tmp_config)


def _init(di, client=CLIENT):
    """Initialize a client workspace. Returns the response."""
    return di.initialize_workspace_usecase.execute(
        InitializeWorkspaceRequest(client=client)
    )


def _ensure_engagement(di, client=CLIENT, engagement=ENGAGEMENT):
    """Create the engagement if it does not already exist."""
    if di.engagement_entities.get(client, engagement) is None:
        di.create_engagement_usecase.execute(
            CreateEngagementRequest(client=client, slug=engagement)
        )


def _register(
    di,
    client=CLIENT,
    engagement=ENGAGEMENT,
    slug="maps-1",
    scope="Freight operations and digital platform",
):
    """Register a wardley-mapping project. Workspace must exist."""
    _ensure_engagement(di, client, engagement)
    return di.register_project_usecase.execute(
        RegisterProjectRequest(
            client=client,
            engagement=engagement,
            slug=slug,
            skillset="wardley-mapping",
            scope=scope,
        )
    )


def _elaborate(di, client=CLIENT, engagement=ENGAGEMENT, slug="maps-1"):
    """Transition a project from planning to elaboration."""
    return di.update_project_status_usecase.execute(
        UpdateProjectStatusRequest(
            client=client,
            engagement=engagement,
            project_slug=slug,
            status="elaboration",
        )
    )


@pytest.fixture
def workspace(di):
    """Initialized Holloway Group workspace."""
    _init(di)
    return di


@pytest.fixture
def project(workspace):
    """Workspace with maps-1 registered as wardley-mapping."""
    _register(workspace)
    return workspace


# ---------------------------------------------------------------------------
# InitializeWorkspace
# ---------------------------------------------------------------------------


class TestInitializeWorkspace:
    """Create a client workspace with empty registries."""

    def test_new_workspace_echoes_client_slug(self, di):
        resp = _init(di)
        assert resp.client == CLIENT

    def test_onboarding_entry_logged(self, di):
        _init(di)
        entries = di.engagement_log.list_all(CLIENT)
        assert len(entries) == 1
        assert entries[0].title == "Client onboarded"

    def test_duplicate_workspace_rejected(self, di):
        _init(di)
        with pytest.raises(DuplicateError, match="already exists"):
            _init(di)


# ---------------------------------------------------------------------------
# RegisterProject
# ---------------------------------------------------------------------------


class TestRegisterProject:
    """Register a consulting project, seeding decision log and engagement."""

    def test_registration_echoes_details(self, workspace):
        resp = _register(workspace)
        assert resp.client == CLIENT
        assert resp.slug == "maps-1"
        assert resp.skillset == "wardley-mapping"

    def test_project_entity_created_in_planning(self, workspace):
        _register(workspace)
        project = workspace.projects.get(CLIENT, ENGAGEMENT, "maps-1")
        assert project is not None
        assert project.status.value == "planning"
        assert project.skillset == "wardley-mapping"

    def test_project_created_decision_seeded(self, workspace):
        _register(workspace)
        decisions = workspace.decisions.list_all(CLIENT, ENGAGEMENT, "maps-1")
        assert len(decisions) == 1
        assert decisions[0].title == "Project created"
        assert decisions[0].fields["Skillset"] == "wardley-mapping"
        assert decisions[0].fields["Scope"] == "Freight operations and digital platform"

    def test_engagement_entry_logged(self, workspace):
        _register(workspace)
        titles = [e.title for e in workspace.engagement_log.list_all(CLIENT)]
        assert "Project registered: maps-1" in titles

    def test_two_projects_coexist(self, workspace):
        _register(workspace, slug="maps-1", scope="Freight operations")
        _register(workspace, slug="maps-2", scope="Warehouse logistics")
        assert len(workspace.projects.list_all(CLIENT)) == 2

    def test_unknown_skillset_rejected(self, workspace):
        _ensure_engagement(workspace)
        with pytest.raises(NotFoundError, match="Unknown skillset"):
            workspace.register_project_usecase.execute(
                RegisterProjectRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    slug="tarot-1",
                    skillset="tarot-reading",
                    scope="Divination services",
                )
            )

    def test_duplicate_slug_rejected(self, workspace):
        _register(workspace)
        with pytest.raises(DuplicateError, match="already exists"):
            _register(workspace)

    def test_nonexistent_engagement_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="Engagement not found"):
            workspace.register_project_usecase.execute(
                RegisterProjectRequest(
                    client=CLIENT,
                    engagement="phantom",
                    slug="maps-1",
                    skillset="wardley-mapping",
                    scope="Test",
                )
            )

    def test_closed_engagement_rejected(self, workspace):
        from practice.entities import Engagement, EngagementStatus

        workspace.engagement_entities.save(
            Engagement(
                slug="closed-eng",
                client=CLIENT,
                status=EngagementStatus.CLOSED,
                allowed_sources=["commons"],
                created=workspace.clock.today(),
            )
        )
        with pytest.raises(InvalidTransitionError, match="must be planning or active"):
            workspace.register_project_usecase.execute(
                RegisterProjectRequest(
                    client=CLIENT,
                    engagement="closed-eng",
                    slug="maps-1",
                    skillset="wardley-mapping",
                    scope="Test",
                )
            )


# ---------------------------------------------------------------------------
# UpdateProjectStatus
# ---------------------------------------------------------------------------


class TestUpdateProjectStatus:
    """Transition projects through planning, elaboration, implementation, review."""

    def test_planning_to_elaboration(self, project):
        resp = _elaborate(project)
        assert resp.status == "elaboration"

    def test_transition_persists(self, project):
        _elaborate(project)
        assert (
            project.projects.get(CLIENT, ENGAGEMENT, "maps-1").status.value
            == "elaboration"
        )

    def test_full_lifecycle(self, project):
        for status in ("elaboration", "implementation", "review"):
            project.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    project_slug="maps-1",
                    status=status,
                )
            )
        assert (
            project.projects.get(CLIENT, ENGAGEMENT, "maps-1").status.value == "review"
        )

    def test_skipping_a_step_rejected(self, project):
        with pytest.raises(InvalidTransitionError, match="Invalid transition"):
            project.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    project_slug="maps-1",
                    status="implementation",
                )
            )

    def test_reversing_status_rejected(self, project):
        _elaborate(project)
        with pytest.raises(InvalidTransitionError, match="Invalid transition"):
            project.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    project_slug="maps-1",
                    status="planning",
                )
            )

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    project_slug="phantom-1",
                    status="elaboration",
                )
            )


# ---------------------------------------------------------------------------
# RecordDecision
# ---------------------------------------------------------------------------


class TestRecordDecision:
    """Append timestamped decisions to a project's log."""

    def test_returns_generated_id(self, project):
        resp = project.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                project_slug="maps-1",
                title="Stage 1: Project brief agreed",
                fields={"Scope": "Freight division"},
            )
        )
        assert resp.decision_id  # non-empty UUID

    def test_decision_persists_with_fields(self, project):
        resp = project.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                project_slug="maps-1",
                title="Stage 2: User needs agreed",
                fields={
                    "Users": "Freight customers, Fleet operators, Regulatory bodies"
                },
            )
        )
        got = project.decisions.get(CLIENT, ENGAGEMENT, "maps-1", resp.decision_id)
        assert got.title == "Stage 2: User needs agreed"
        assert "Fleet operators" in got.fields["Users"]

    def test_decisions_accumulate(self, project):
        for title in [
            "Stage 1: Project brief agreed",
            "Stage 2: User needs agreed",
            "Stage 3: Supply chain agreed",
        ]:
            project.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        # +1 for the "Project created" decision seeded by registration
        assert len(project.decisions.list_all(CLIENT, ENGAGEMENT, "maps-1")) == 4

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
                    project_slug="phantom-1",
                    title="Stage 1: Project brief agreed",
                    fields={},
                )
            )


# ---------------------------------------------------------------------------
# AddEngagementEntry
# ---------------------------------------------------------------------------


class TestAddEngagementEntry:
    """Append timestamped entries to the client engagement log."""

    def test_returns_generated_id(self, workspace):
        resp = workspace.add_engagement_entry_usecase.execute(
            AddEngagementEntryRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                title="Strategy workshop scheduled",
                fields={
                    "Date": "2025-07-15",
                    "Attendees": "COO, CTO, VP Engineering",
                },
            )
        )
        assert resp.entry_id  # non-empty UUID

    def test_entry_persists(self, workspace):
        workspace.add_engagement_entry_usecase.execute(
            AddEngagementEntryRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                title="Research findings presented",
                fields={},
            )
        )
        titles = [e.title for e in workspace.engagement_log.list_all(CLIENT)]
        assert "Research findings presented" in titles

    def test_nonexistent_client_rejected(self, di):
        with pytest.raises(NotFoundError, match="not found"):
            di.add_engagement_entry_usecase.execute(
                AddEngagementEntryRequest(
                    client="phantom-corp",
                    engagement=ENGAGEMENT,
                    title="Meeting scheduled",
                    fields={},
                )
            )


# ---------------------------------------------------------------------------
# RegisterResearchTopic
# ---------------------------------------------------------------------------


class TestRegisterResearchTopic:
    """Register research topics in the client's knowledge manifest."""

    def test_echoes_filename(self, workspace):
        resp = workspace.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Technology stack and build-vs-buy decisions",
                filename="technology-landscape.md",
                confidence="Medium",
            )
        )
        assert resp.filename == "technology-landscape.md"

    def test_topic_persists_with_confidence(self, workspace):
        workspace.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Market position in Australian freight",
                filename="market-position.md",
                confidence="High",
            )
        )
        got = workspace.research.get(CLIENT, "market-position.md")
        assert got is not None
        assert got.confidence.value == "High"

    def test_duplicate_filename_rejected(self, workspace):
        workspace.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Regulatory environment",
                filename="regulatory.md",
                confidence="Medium",
            )
        )
        with pytest.raises(DuplicateError, match="already exists"):
            workspace.register_research_topic_usecase.execute(
                RegisterResearchTopicRequest(
                    client=CLIENT,
                    topic="Updated regulatory analysis",
                    filename="regulatory.md",
                    confidence="High",
                )
            )


# ---------------------------------------------------------------------------
# ListProjects
# ---------------------------------------------------------------------------


class TestListProjects:
    """Query the project registry with optional filters."""

    def test_empty_registry(self, workspace):
        resp = workspace.list_projects_usecase.execute(
            ListProjectsRequest(client=CLIENT, engagement=ENGAGEMENT)
        )
        assert resp.projects == []

    def test_one_project(self, project):
        resp = project.list_projects_usecase.execute(
            ListProjectsRequest(client=CLIENT, engagement=ENGAGEMENT)
        )
        assert len(resp.projects) == 1
        assert resp.projects[0].slug == "maps-1"
        assert resp.projects[0].skillset == "wardley-mapping"
        assert resp.projects[0].status == "planning"

    def test_filter_by_status(self, workspace):
        _register(workspace, slug="maps-1", scope="Freight operations")
        _register(workspace, slug="maps-2", scope="Warehouse logistics")
        _elaborate(workspace, slug="maps-2")
        resp = workspace.list_projects_usecase.execute(
            ListProjectsRequest(
                client=CLIENT, engagement=ENGAGEMENT, status="elaboration"
            )
        )
        assert len(resp.projects) == 1
        assert resp.projects[0].slug == "maps-2"


# ---------------------------------------------------------------------------
# GetProject
# ---------------------------------------------------------------------------


class TestGetProject:
    """Retrieve a single project by slug."""

    def test_not_found(self, workspace):
        with pytest.raises(NotFoundError):
            workspace.get_project_usecase.execute(
                GetProjectRequest(
                    client=CLIENT, engagement=ENGAGEMENT, slug="nonexistent"
                )
            )

    def test_found(self, project):
        resp = project.get_project_usecase.execute(
            GetProjectRequest(client=CLIENT, engagement=ENGAGEMENT, slug="maps-1")
        )
        assert resp.project is not None
        assert resp.project.slug == "maps-1"
        assert resp.project.status == "planning"


# ---------------------------------------------------------------------------
# ListDecisions
# ---------------------------------------------------------------------------


class TestListDecisions:
    """List a project's decision log."""

    def test_registration_seeds_one_decision(self, project):
        resp = project.list_decisions_usecase.execute(
            ListDecisionsRequest(
                client=CLIENT, engagement=ENGAGEMENT, project_slug="maps-1"
            )
        )
        assert len(resp.decisions) == 1
        assert resp.decisions[0].title == "Project created"

    def test_recorded_decisions_appear(self, project):
        project.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                project_slug="maps-1",
                title="Stage 1: Project brief agreed",
                fields={"Scope": "Freight division"},
            )
        )
        resp = project.list_decisions_usecase.execute(
            ListDecisionsRequest(
                client=CLIENT, engagement=ENGAGEMENT, project_slug="maps-1"
            )
        )
        titles = [d.title for d in resp.decisions]
        assert "Project created" in titles
        assert "Stage 1: Project brief agreed" in titles

    def test_returns_chronological_order(self, project):
        """Decisions are returned sorted by timestamp, not insertion order."""
        # Save directly to repo in reverse chronological order
        project.decisions.save(
            DecisionEntry(
                id="late",
                client=CLIENT,
                engagement=ENGAGEMENT,
                project_slug="maps-1",
                date=datetime(2025, 6, 3, tzinfo=timezone.utc).date(),
                timestamp=datetime(2025, 6, 3, 14, 0, 0, tzinfo=timezone.utc),
                title="Third decision",
                fields={},
            )
        )
        project.decisions.save(
            DecisionEntry(
                id="early",
                client=CLIENT,
                engagement=ENGAGEMENT,
                project_slug="maps-1",
                date=datetime(2025, 6, 1, tzinfo=timezone.utc).date(),
                timestamp=datetime(2025, 6, 1, 9, 0, 0, tzinfo=timezone.utc),
                title="First decision",
                fields={},
            )
        )
        project.decisions.save(
            DecisionEntry(
                id="middle",
                client=CLIENT,
                engagement=ENGAGEMENT,
                project_slug="maps-1",
                date=datetime(2025, 6, 2, tzinfo=timezone.utc).date(),
                timestamp=datetime(2025, 6, 2, 11, 0, 0, tzinfo=timezone.utc),
                title="Second decision",
                fields={},
            )
        )
        resp = project.list_decisions_usecase.execute(
            ListDecisionsRequest(
                client=CLIENT, engagement=ENGAGEMENT, project_slug="maps-1"
            )
        )
        # Skip the "Project created" decision seeded by registration
        titles = [d.title for d in resp.decisions]
        assert titles.index("First decision") < titles.index("Second decision")
        assert titles.index("Second decision") < titles.index("Third decision")


# ---------------------------------------------------------------------------
# ListResearchTopics
# ---------------------------------------------------------------------------


class TestListResearchTopics:
    """List the client's research manifest."""

    def test_empty_manifest(self, workspace):
        resp = workspace.list_research_topics_usecase.execute(
            ListResearchTopicsRequest(client=CLIENT)
        )
        assert resp.topics == []

    def test_registered_topics_appear(self, workspace):
        workspace.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Partnerships and fleet suppliers",
                filename="partnerships-suppliers.md",
                confidence="Medium-High",
            )
        )
        resp = workspace.list_research_topics_usecase.execute(
            ListResearchTopicsRequest(client=CLIENT)
        )
        assert len(resp.topics) == 1
        assert resp.topics[0].topic == "Partnerships and fleet suppliers"
        assert resp.topics[0].confidence == "Medium-High"


# ---------------------------------------------------------------------------
# CreateEngagement
# ---------------------------------------------------------------------------


class TestCreateEngagement:
    """Create a new engagement with default commons source."""

    def test_echoes_details(self, workspace):
        resp = workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        assert resp.client == CLIENT
        assert resp.slug == "strat-2"
        assert resp.status == "planning"

    def test_persists_with_commons(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        eng = workspace.engagement_entities.get(CLIENT, "strat-2")
        assert eng is not None
        assert eng.allowed_sources == ["commons", "personal"]

    def test_logs_entry(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        titles = [e.title for e in workspace.engagement_log.list_all(CLIENT)]
        assert "Engagement created" in titles

    def test_duplicate_rejected(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        with pytest.raises(DuplicateError, match="already exists"):
            workspace.create_engagement_usecase.execute(
                CreateEngagementRequest(client=CLIENT, slug="strat-2")
            )

    def test_nonexistent_client_rejected(self, di):
        with pytest.raises(NotFoundError, match="not found"):
            di.create_engagement_usecase.execute(
                CreateEngagementRequest(client="phantom-corp", slug="strat-1")
            )


# ---------------------------------------------------------------------------
# GetEngagement
# ---------------------------------------------------------------------------


class TestGetEngagement:
    """Retrieve a single engagement."""

    def test_found(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        resp = workspace.get_engagement_usecase.execute(
            GetEngagementRequest(client=CLIENT, slug="strat-2")
        )
        assert resp.engagement.slug == "strat-2"
        assert resp.engagement.status == "planning"
        assert resp.engagement.allowed_sources == ["commons", "personal"]

    def test_not_found(self, workspace):
        with pytest.raises(NotFoundError):
            workspace.get_engagement_usecase.execute(
                GetEngagementRequest(client=CLIENT, slug="nonexistent")
            )


# ---------------------------------------------------------------------------
# ListEngagements
# ---------------------------------------------------------------------------


class TestListEngagements:
    """List engagements for a client."""

    def test_empty(self, workspace):
        resp = workspace.list_engagements_usecase.execute(
            ListEngagementsRequest(client=CLIENT)
        )
        assert resp.engagements == []

    def test_one(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        resp = workspace.list_engagements_usecase.execute(
            ListEngagementsRequest(client=CLIENT)
        )
        assert len(resp.engagements) == 1
        assert resp.engagements[0].slug == "strat-2"

    def test_many(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-3")
        )
        resp = workspace.list_engagements_usecase.execute(
            ListEngagementsRequest(client=CLIENT)
        )
        assert len(resp.engagements) == 2


# ---------------------------------------------------------------------------
# AddEngagementSource
# ---------------------------------------------------------------------------


class TestAddEngagementSource:
    """Add sources to an engagement's allowlist."""

    def test_already_present_rejected(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        with pytest.raises(DuplicateError, match="already allowed"):
            workspace.add_engagement_source_usecase.execute(
                AddEngagementSourceRequest(
                    client=CLIENT, engagement="strat-2", source="commons"
                )
            )

    def test_unknown_source_rejected(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        with pytest.raises(NotFoundError, match="Source not found"):
            workspace.add_engagement_source_usecase.execute(
                AddEngagementSourceRequest(
                    client=CLIENT, engagement="strat-2", source="nonexistent"
                )
            )

    def test_nonexistent_engagement_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="Engagement not found"):
            workspace.add_engagement_source_usecase.execute(
                AddEngagementSourceRequest(
                    client=CLIENT, engagement="phantom", source="commons"
                )
            )


# ---------------------------------------------------------------------------
# RemoveEngagementSource
# ---------------------------------------------------------------------------


class TestRemoveEngagementSource:
    """Remove sources from an engagement's allowlist."""

    def test_commons_cannot_be_removed(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        with pytest.raises(InvalidTransitionError, match="Cannot remove commons"):
            workspace.remove_engagement_source_usecase.execute(
                RemoveEngagementSourceRequest(
                    client=CLIENT, engagement="strat-2", source="commons"
                )
            )

    def test_personal_cannot_be_removed(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        with pytest.raises(InvalidTransitionError, match="Cannot remove personal"):
            workspace.remove_engagement_source_usecase.execute(
                RemoveEngagementSourceRequest(
                    client=CLIENT, engagement="strat-2", source="personal"
                )
            )

    def test_source_not_in_list_rejected(self, workspace):
        workspace.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-2")
        )
        with pytest.raises(NotFoundError, match="not in allowlist"):
            workspace.remove_engagement_source_usecase.execute(
                RemoveEngagementSourceRequest(
                    client=CLIENT, engagement="strat-2", source="partner-x"
                )
            )


# ---------------------------------------------------------------------------
# ListSkillsets (with filtering)
# ---------------------------------------------------------------------------


class TestListSkillsets:
    """List skillsets with optional implementation filter."""

    def test_all_skillsets_returned(self, di):
        from pathlib import Path

        from bin.cli.infrastructure.code_skillset_repository import (
            CodeSkillsetRepository,
        )

        repo_root = Path(__file__).resolve().parent.parent
        expected = {s.name for s in CodeSkillsetRepository(repo_root).list_all()}
        resp = di.list_skillsets_usecase.execute(ListSkillsetsRequest())
        names = {s.name for s in resp.skillsets}
        assert names == expected

    def test_filter_implemented(self, di):
        resp = di.list_skillsets_usecase.execute(
            ListSkillsetsRequest(implemented="true")
        )
        assert all(s.is_implemented for s in resp.skillsets)

    def test_filter_prospectus(self, di):
        resp = di.list_skillsets_usecase.execute(
            ListSkillsetsRequest(implemented="false")
        )
        assert all(not s.is_implemented for s in resp.skillsets)

    def test_skillset_info_has_new_fields(self, di):
        resp = di.list_skillsets_usecase.execute(ListSkillsetsRequest())
        for s in resp.skillsets:
            assert isinstance(s.is_implemented, bool)
            assert isinstance(s.problem_domain, str)
            assert isinstance(s.deliverables, list)
            assert isinstance(s.value_proposition, str)
            assert isinstance(s.classification, list)
            assert isinstance(s.evidence, list)


# ---------------------------------------------------------------------------
# RegisterProspectus
# ---------------------------------------------------------------------------


class TestRegisterProspectus:
    """Register a new skillset prospectus."""

    def test_registers_new_prospectus(self, di):
        resp = di.register_prospectus_usecase.execute(
            RegisterProspectusRequest(
                name="competitive-analysis",
                display_name="Competitive Analysis",
                description="Market positioning methodology.",
                slug_pattern="comp-{n}",
                problem_domain="Market positioning",
                value_proposition="Know your rivals.",
                deliverables="Competitor landscape report, Market gap analysis",
                classification="strategy, market-analysis",
                evidence="Porter's Five Forces",
            )
        )
        assert resp.name == "competitive-analysis"
        assert resp.init_path.endswith("__init__.py")

    def test_duplicate_name_rejected(self, di):
        with pytest.raises(DuplicateError, match="already exists"):
            di.register_prospectus_usecase.execute(
                RegisterProspectusRequest(
                    name="wardley-mapping",
                    display_name="Duplicate",
                    description="Already exists.",
                    slug_pattern="dup-{n}",
                )
            )

    def test_csv_fields_split_correctly(self, di):
        resp = di.register_prospectus_usecase.execute(
            RegisterProspectusRequest(
                name="test-method",
                display_name="Test Method",
                description="A test.",
                slug_pattern="test-{n}",
                deliverables="Report, Dashboard, Slides",
                classification="strategy, operations",
            )
        )
        # Verify round-trip by parsing the generated __init__.py
        from pathlib import Path

        from bin.cli.infrastructure.skillset_scaffold import _parse_current_skillset

        init_path = Path(resp.init_path)
        s = _parse_current_skillset(init_path, "test-method")
        assert s.deliverables == ["Report", "Dashboard", "Slides"]
        assert s.classification == ["strategy", "operations"]
        assert s.is_implemented is False


# ---------------------------------------------------------------------------
# UpdateProspectus
# ---------------------------------------------------------------------------


class TestUpdateProspectus:
    """Update an existing skillset prospectus.

    After registering a prospectus via the scaffold, the in-memory
    SkillsetRepository doesn't see it until a fresh Container is
    created (mirroring how the CLI re-discovers on each invocation).
    The happy-path test therefore tests the scaffold.update() directly.
    """

    def test_scaffold_updates_description(self, di):
        """Scaffold round-trips descriptive field updates."""
        from bin.cli.infrastructure.skillset_scaffold import _parse_current_skillset

        scaffold = di.scaffold
        scaffold.create(
            name="test-method",
            display_name="Test Method",
            description="Original.",
            slug_pattern="test-{n}",
            problem_domain="Testing",
        )
        updated = scaffold.update(name="test-method", description="Updated.")
        s = _parse_current_skillset(updated, "test-method")
        assert s.description == "Updated."
        assert s.display_name == "Test Method"  # unchanged
        assert s.problem_domain == "Testing"  # unchanged

    def test_nonexistent_skillset_rejected(self, di):
        with pytest.raises(NotFoundError, match="not found"):
            di.update_prospectus_usecase.execute(
                UpdateProspectusRequest(
                    name="phantom-method",
                    description="Nope.",
                )
            )

    def test_implemented_skillset_rejected(self, di):
        with pytest.raises(DuplicateError, match="implemented"):
            di.update_prospectus_usecase.execute(
                UpdateProspectusRequest(
                    name="wardley-mapping",
                    description="Cannot update implemented.",
                )
            )
