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

from wardley_mapping.dtos import RegisterTourRequest
from wardley_mapping.types import TourStop
from consulting.dtos import (
    AddEngagementEntryRequest,
    GetProjectProgressRequest,
    GetProjectRequest,
    InitializeWorkspaceRequest,
    ListDecisionsRequest,
    ListProjectsRequest,
    ListResearchTopicsRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
    RegisterResearchTopicRequest,
    UpdateProjectStatusRequest,
)
from consulting.entities import DecisionEntry
from practice.exceptions import DuplicateError, InvalidTransitionError, NotFoundError
from bin.cli.di import Container

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

CLIENT = "holloway-group"


@pytest.fixture
def di(tmp_config):
    """Container with skillsets auto-discovered from BC modules."""
    return Container(tmp_config)


def _init(di, client=CLIENT):
    """Initialize a client workspace. Returns the response."""
    return di.initialize_workspace_usecase.execute(
        InitializeWorkspaceRequest(client=client)
    )


def _register(
    di,
    client=CLIENT,
    slug="maps-1",
    scope="Freight operations and digital platform",
):
    """Register a wardley-mapping project. Workspace must exist."""
    return di.register_project_usecase.execute(
        RegisterProjectRequest(
            client=client,
            slug=slug,
            skillset="wardley-mapping",
            scope=scope,
        )
    )


def _elaborate(di, client=CLIENT, slug="maps-1"):
    """Transition a project from planning to elaboration."""
    return di.update_project_status_usecase.execute(
        UpdateProjectStatusRequest(
            client=client, project_slug=slug, status="elaboration"
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
        entries = di.engagement.list_all(CLIENT)
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
        project = workspace.projects.get(CLIENT, "maps-1")
        assert project is not None
        assert project.status.value == "planning"
        assert project.skillset == "wardley-mapping"

    def test_project_created_decision_seeded(self, workspace):
        _register(workspace)
        decisions = workspace.decisions.list_all(CLIENT, "maps-1")
        assert len(decisions) == 1
        assert decisions[0].title == "Project created"
        assert decisions[0].fields["Skillset"] == "wardley-mapping"
        assert decisions[0].fields["Scope"] == "Freight operations and digital platform"

    def test_engagement_entry_logged(self, workspace):
        _register(workspace)
        titles = [e.title for e in workspace.engagement.list_all(CLIENT)]
        assert "Project registered: maps-1" in titles

    def test_two_projects_coexist(self, workspace):
        _register(workspace, slug="maps-1", scope="Freight operations")
        _register(workspace, slug="maps-2", scope="Warehouse logistics")
        assert len(workspace.projects.list_all(CLIENT)) == 2

    def test_unknown_skillset_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="Unknown skillset"):
            workspace.register_project_usecase.execute(
                RegisterProjectRequest(
                    client=CLIENT,
                    slug="tarot-1",
                    skillset="tarot-reading",
                    scope="Divination services",
                )
            )

    def test_duplicate_slug_rejected(self, workspace):
        _register(workspace)
        with pytest.raises(DuplicateError, match="already exists"):
            _register(workspace)


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
        assert project.projects.get(CLIENT, "maps-1").status.value == "elaboration"

    def test_full_lifecycle(self, project):
        for status in ("elaboration", "implementation", "review"):
            project.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="maps-1", status=status
                )
            )
        assert project.projects.get(CLIENT, "maps-1").status.value == "review"

    def test_skipping_a_step_rejected(self, project):
        with pytest.raises(InvalidTransitionError, match="Invalid transition"):
            project.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="maps-1", status="implementation"
                )
            )

    def test_reversing_status_rejected(self, project):
        _elaborate(project)
        with pytest.raises(InvalidTransitionError, match="Invalid transition"):
            project.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="maps-1", status="planning"
                )
            )

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="phantom-1", status="elaboration"
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
                project_slug="maps-1",
                title="Stage 2: User needs agreed",
                fields={
                    "Users": "Freight customers, Fleet operators, Regulatory bodies"
                },
            )
        )
        got = project.decisions.get(CLIENT, "maps-1", resp.decision_id)
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
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        # +1 for the "Project created" decision seeded by registration
        assert len(project.decisions.list_all(CLIENT, "maps-1")) == 4

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
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
                title="Research findings presented",
                fields={},
            )
        )
        titles = [e.title for e in workspace.engagement.list_all(CLIENT)]
        assert "Research findings presented" in titles

    def test_nonexistent_client_rejected(self, di):
        with pytest.raises(NotFoundError, match="not found"):
            di.add_engagement_entry_usecase.execute(
                AddEngagementEntryRequest(
                    client="phantom-corp",
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
# RegisterTour
# ---------------------------------------------------------------------------


class TestRegisterTour:
    """Register curated presentation tours for specific audiences."""

    def test_returns_stop_count(self, project):
        resp = project.register_tour_usecase.execute(
            RegisterTourRequest(
                client=CLIENT,
                project_slug="maps-1",
                name="investor",
                title="Investor Briefing: Strategic Position and Defensibility",
                stops=[
                    TourStop(
                        order="1",
                        title="Strategic Overview",
                        atlas_source="atlas/overview/",
                    ),
                    TourStop(
                        order="2",
                        title="Competitive Moats",
                        atlas_source="atlas/bottlenecks/",
                    ),
                    TourStop(
                        order="3",
                        title="Evolution Programme",
                        atlas_source="atlas/movement/",
                    ),
                ],
            )
        )
        assert resp.stop_count == 3
        assert resp.name == "investor"

    def test_tour_persists(self, project):
        project.register_tour_usecase.execute(
            RegisterTourRequest(
                client=CLIENT,
                project_slug="maps-1",
                name="executive",
                title="Executive Summary: Risk and Opportunity",
                stops=[
                    TourStop(
                        order="1",
                        title="Landscape",
                        atlas_source="atlas/overview/",
                    ),
                    TourStop(
                        order="2",
                        title="Risk Profile",
                        atlas_source="atlas/risk/",
                    ),
                ],
            )
        )
        got = project.tours.get(CLIENT, "maps-1", "executive")
        assert got is not None
        assert len(got.stops) == 2
        assert got.stops[1].atlas_source == "atlas/risk/"

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.register_tour_usecase.execute(
                RegisterTourRequest(
                    client=CLIENT,
                    project_slug="phantom-1",
                    name="investor",
                    title="Phantom Tour",
                    stops=[
                        TourStop(
                            order="1",
                            title="Nothing",
                            atlas_source="atlas/void/",
                        )
                    ],
                )
            )


# ---------------------------------------------------------------------------
# ListProjects
# ---------------------------------------------------------------------------


class TestListProjects:
    """Query the project registry with optional filters."""

    def test_empty_registry(self, workspace):
        resp = workspace.list_projects_usecase.execute(
            ListProjectsRequest(client=CLIENT)
        )
        assert resp.projects == []

    def test_one_project(self, project):
        resp = project.list_projects_usecase.execute(ListProjectsRequest(client=CLIENT))
        assert len(resp.projects) == 1
        assert resp.projects[0].slug == "maps-1"
        assert resp.projects[0].skillset == "wardley-mapping"
        assert resp.projects[0].status == "planning"

    def test_filter_by_status(self, workspace):
        _register(workspace, slug="maps-1", scope="Freight operations")
        _register(workspace, slug="maps-2", scope="Warehouse logistics")
        _elaborate(workspace, slug="maps-2")
        resp = workspace.list_projects_usecase.execute(
            ListProjectsRequest(client=CLIENT, status="elaboration")
        )
        assert len(resp.projects) == 1
        assert resp.projects[0].slug == "maps-2"


# ---------------------------------------------------------------------------
# GetProject
# ---------------------------------------------------------------------------


class TestGetProject:
    """Retrieve a single project by slug."""

    def test_not_found(self, workspace):
        resp = workspace.get_project_usecase.execute(
            GetProjectRequest(client=CLIENT, slug="nonexistent")
        )
        assert resp.project is None

    def test_found(self, project):
        resp = project.get_project_usecase.execute(
            GetProjectRequest(client=CLIENT, slug="maps-1")
        )
        assert resp.project is not None
        assert resp.project.slug == "maps-1"
        assert resp.project.status == "planning"


# ---------------------------------------------------------------------------
# GetProjectProgress
# ---------------------------------------------------------------------------


class TestGetProjectProgress:
    """Match decisions against the skillset pipeline to report progress."""

    def test_no_decisions_all_stages_pending(self, project):
        resp = project.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        assert len(resp.stages) == 5
        assert all(not s.completed for s in resp.stages)
        assert resp.current_stage == "wm-research"
        assert resp.next_prerequisite == "resources/index.md"

    @pytest.mark.parametrize(
        "stage_decisions, expected_current, expected_gate",
        [
            pytest.param(
                ["Stage 1: Project brief agreed"],
                "wm-needs",
                "brief.agreed.md",
                id="research-complete→needs",
            ),
            pytest.param(
                [
                    "Stage 1: Project brief agreed",
                    "Stage 2: User needs agreed",
                ],
                "wm-chain",
                "needs/needs.agreed.md",
                id="needs-complete→chain",
            ),
            pytest.param(
                [
                    "Stage 1: Project brief agreed",
                    "Stage 2: User needs agreed",
                    "Stage 3: Supply chain agreed",
                ],
                "wm-evolve",
                "chain/supply-chain.agreed.md",
                id="chain-complete→evolve",
            ),
            pytest.param(
                [
                    "Stage 1: Project brief agreed",
                    "Stage 2: User needs agreed",
                    "Stage 3: Supply chain agreed",
                    "Stage 4: Evolution map agreed",
                ],
                "wm-strategy",
                "evolve/map.agreed.owm",
                id="evolve-complete→strategy",
            ),
            pytest.param(
                [
                    "Stage 1: Project brief agreed",
                    "Stage 2: User needs agreed",
                    "Stage 3: Supply chain agreed",
                    "Stage 4: Evolution map agreed",
                    "Stage 5: Strategy map agreed",
                ],
                None,
                None,
                id="strategy-complete→done",
            ),
        ],
    )
    def test_pipeline_advances_through_stages(
        self, project, stage_decisions, expected_current, expected_gate
    ):
        """Each stage decision advances the pipeline to the next skill."""
        for title in stage_decisions:
            project.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        resp = project.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        assert resp.current_stage == expected_current
        assert resp.next_prerequisite == expected_gate

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.get_project_progress_usecase.execute(
                GetProjectProgressRequest(client=CLIENT, project_slug="phantom-1")
            )


# ---------------------------------------------------------------------------
# ListDecisions
# ---------------------------------------------------------------------------


class TestListDecisions:
    """List a project's decision log."""

    def test_registration_seeds_one_decision(self, project):
        resp = project.list_decisions_usecase.execute(
            ListDecisionsRequest(client=CLIENT, project_slug="maps-1")
        )
        assert len(resp.decisions) == 1
        assert resp.decisions[0].title == "Project created"

    def test_recorded_decisions_appear(self, project):
        project.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                project_slug="maps-1",
                title="Stage 1: Project brief agreed",
                fields={"Scope": "Freight division"},
            )
        )
        resp = project.list_decisions_usecase.execute(
            ListDecisionsRequest(client=CLIENT, project_slug="maps-1")
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
                project_slug="maps-1",
                date=datetime(2025, 6, 2, tzinfo=timezone.utc).date(),
                timestamp=datetime(2025, 6, 2, 11, 0, 0, tzinfo=timezone.utc),
                title="Second decision",
                fields={},
            )
        )
        resp = project.list_decisions_usecase.execute(
            ListDecisionsRequest(client=CLIENT, project_slug="maps-1")
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
