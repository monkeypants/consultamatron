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

import pytest

from bin.cli.di import Container
from bin.cli.dtos import (
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
    RegisterTourRequest,
    TourStopInput,
    UpdateProjectStatusRequest,
)

from .conftest import seed_wardley_mapping

# ---------------------------------------------------------------------------
# Fixtures and helpers
# ---------------------------------------------------------------------------

CLIENT = "holloway-group"


@pytest.fixture
def di(tmp_config):
    """Container with the wardley-mapping skillset available."""
    seed_wardley_mapping(tmp_config.skillsets_root)
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


def _activate(di, client=CLIENT, slug="maps-1"):
    """Transition a project from planned to active."""
    return di.update_project_status_usecase.execute(
        UpdateProjectStatusRequest(client=client, project_slug=slug, status="active")
    )


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
        with pytest.raises(ValueError, match="already exists"):
            _init(di)


# ---------------------------------------------------------------------------
# RegisterProject
# ---------------------------------------------------------------------------


class TestRegisterProject:
    """Register a consulting project, seeding decision log and engagement."""

    def test_registration_echoes_details(self, di):
        _init(di)
        resp = _register(di)
        assert resp.client == CLIENT
        assert resp.slug == "maps-1"
        assert resp.skillset == "wardley-mapping"

    def test_project_entity_created_as_planned(self, di):
        _init(di)
        _register(di)
        project = di.projects.get(CLIENT, "maps-1")
        assert project is not None
        assert project.status.value == "planned"
        assert project.skillset == "wardley-mapping"

    def test_project_created_decision_seeded(self, di):
        _init(di)
        _register(di)
        decisions = di.decisions.list_all(CLIENT, "maps-1")
        assert len(decisions) == 1
        assert decisions[0].title == "Project created"
        assert decisions[0].fields["Skillset"] == "wardley-mapping"
        assert decisions[0].fields["Scope"] == "Freight operations and digital platform"

    def test_engagement_entry_logged(self, di):
        _init(di)
        _register(di)
        titles = [e.title for e in di.engagement.list_all(CLIENT)]
        assert "Project registered: maps-1" in titles

    def test_two_projects_coexist(self, di):
        _init(di)
        _register(di, slug="maps-1", scope="Freight operations")
        _register(di, slug="maps-2", scope="Warehouse logistics")
        assert len(di.projects.list_all(CLIENT)) == 2

    def test_unknown_skillset_rejected(self, di):
        _init(di)
        with pytest.raises(ValueError, match="Unknown skillset"):
            di.register_project_usecase.execute(
                RegisterProjectRequest(
                    client=CLIENT,
                    slug="tarot-1",
                    skillset="tarot-reading",
                    scope="Divination services",
                )
            )

    def test_duplicate_slug_rejected(self, di):
        _init(di)
        _register(di)
        with pytest.raises(ValueError, match="already exists"):
            _register(di)


# ---------------------------------------------------------------------------
# UpdateProjectStatus
# ---------------------------------------------------------------------------


class TestUpdateProjectStatus:
    """Transition projects through planned, active, complete, reviewed."""

    def test_planned_to_active(self, di):
        _init(di)
        _register(di)
        resp = _activate(di)
        assert resp.status == "active"

    def test_transition_persists(self, di):
        _init(di)
        _register(di)
        _activate(di)
        assert di.projects.get(CLIENT, "maps-1").status.value == "active"

    def test_full_lifecycle(self, di):
        _init(di)
        _register(di)
        for status in ("active", "complete", "reviewed"):
            di.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="maps-1", status=status
                )
            )
        assert di.projects.get(CLIENT, "maps-1").status.value == "reviewed"

    def test_skipping_a_step_rejected(self, di):
        _init(di)
        _register(di)
        with pytest.raises(ValueError, match="Invalid transition"):
            di.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="maps-1", status="complete"
                )
            )

    def test_reversing_status_rejected(self, di):
        _init(di)
        _register(di)
        _activate(di)
        with pytest.raises(ValueError, match="Invalid transition"):
            di.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="maps-1", status="planned"
                )
            )

    def test_nonexistent_project_rejected(self, di):
        _init(di)
        with pytest.raises(ValueError, match="not found"):
            di.update_project_status_usecase.execute(
                UpdateProjectStatusRequest(
                    client=CLIENT, project_slug="phantom-1", status="active"
                )
            )


# ---------------------------------------------------------------------------
# RecordDecision
# ---------------------------------------------------------------------------


class TestRecordDecision:
    """Append timestamped decisions to a project's log."""

    def test_returns_generated_id(self, di):
        _init(di)
        _register(di)
        resp = di.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                project_slug="maps-1",
                title="Stage 1: Research and brief agreed",
                fields={"Scope": "Freight division"},
            )
        )
        assert resp.decision_id  # non-empty UUID

    def test_decision_persists_with_fields(self, di):
        _init(di)
        _register(di)
        resp = di.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                project_slug="maps-1",
                title="Stage 2: User needs agreed",
                fields={
                    "Users": "Freight customers, Fleet operators, Regulatory bodies"
                },
            )
        )
        got = di.decisions.get(CLIENT, "maps-1", resp.decision_id)
        assert got.title == "Stage 2: User needs agreed"
        assert "Fleet operators" in got.fields["Users"]

    def test_decisions_accumulate(self, di):
        _init(di)
        _register(di)
        for title in [
            "Stage 1: Research and brief agreed",
            "Stage 2: User needs agreed",
            "Stage 3: Supply chain agreed",
        ]:
            di.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        # +1 for the "Project created" decision seeded by registration
        assert len(di.decisions.list_all(CLIENT, "maps-1")) == 4

    def test_nonexistent_project_rejected(self, di):
        _init(di)
        with pytest.raises(ValueError, match="not found"):
            di.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    project_slug="phantom-1",
                    title="Stage 1: Research and brief agreed",
                    fields={},
                )
            )


# ---------------------------------------------------------------------------
# AddEngagementEntry
# ---------------------------------------------------------------------------


class TestAddEngagementEntry:
    """Append timestamped entries to the client engagement log."""

    def test_returns_generated_id(self, di):
        _init(di)
        resp = di.add_engagement_entry_usecase.execute(
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

    def test_entry_persists(self, di):
        _init(di)
        di.add_engagement_entry_usecase.execute(
            AddEngagementEntryRequest(
                client=CLIENT,
                title="Research findings presented",
                fields={},
            )
        )
        titles = [e.title for e in di.engagement.list_all(CLIENT)]
        assert "Research findings presented" in titles

    def test_nonexistent_client_rejected(self, di):
        with pytest.raises(ValueError, match="not found"):
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

    def test_echoes_filename(self, di):
        _init(di)
        resp = di.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Technology stack and build-vs-buy decisions",
                filename="technology-landscape.md",
                confidence="Medium",
            )
        )
        assert resp.filename == "technology-landscape.md"

    def test_topic_persists_with_confidence(self, di):
        _init(di)
        di.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Market position in Australian freight",
                filename="market-position.md",
                confidence="High",
            )
        )
        got = di.research.get(CLIENT, "market-position.md")
        assert got is not None
        assert got.confidence.value == "High"

    def test_duplicate_filename_rejected(self, di):
        _init(di)
        di.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Regulatory environment",
                filename="regulatory.md",
                confidence="Medium",
            )
        )
        with pytest.raises(ValueError, match="already exists"):
            di.register_research_topic_usecase.execute(
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

    def test_returns_stop_count(self, di):
        _init(di)
        _register(di)
        resp = di.register_tour_usecase.execute(
            RegisterTourRequest(
                client=CLIENT,
                project_slug="maps-1",
                name="investor",
                title="Investor Briefing: Strategic Position and Defensibility",
                stops=[
                    TourStopInput(
                        order="1",
                        title="Strategic Overview",
                        atlas_source="atlas/overview/",
                    ),
                    TourStopInput(
                        order="2",
                        title="Competitive Moats",
                        atlas_source="atlas/bottlenecks/",
                    ),
                    TourStopInput(
                        order="3",
                        title="Evolution Programme",
                        atlas_source="atlas/movement/",
                    ),
                ],
            )
        )
        assert resp.stop_count == 3
        assert resp.name == "investor"

    def test_tour_persists(self, di):
        _init(di)
        _register(di)
        di.register_tour_usecase.execute(
            RegisterTourRequest(
                client=CLIENT,
                project_slug="maps-1",
                name="executive",
                title="Executive Summary: Risk and Opportunity",
                stops=[
                    TourStopInput(
                        order="1",
                        title="Landscape",
                        atlas_source="atlas/overview/",
                    ),
                    TourStopInput(
                        order="2",
                        title="Risk Profile",
                        atlas_source="atlas/risk/",
                    ),
                ],
            )
        )
        got = di.tours.get(CLIENT, "maps-1", "executive")
        assert got is not None
        assert len(got.stops) == 2
        assert got.stops[1].atlas_source == "atlas/risk/"

    def test_nonexistent_project_rejected(self, di):
        _init(di)
        with pytest.raises(ValueError, match="not found"):
            di.register_tour_usecase.execute(
                RegisterTourRequest(
                    client=CLIENT,
                    project_slug="phantom-1",
                    name="investor",
                    title="Phantom Tour",
                    stops=[
                        TourStopInput(
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

    def test_empty_registry(self, di):
        _init(di)
        resp = di.list_projects_usecase.execute(ListProjectsRequest(client=CLIENT))
        assert resp.projects == []

    def test_one_project(self, di):
        _init(di)
        _register(di)
        resp = di.list_projects_usecase.execute(ListProjectsRequest(client=CLIENT))
        assert len(resp.projects) == 1
        assert resp.projects[0].slug == "maps-1"
        assert resp.projects[0].skillset == "wardley-mapping"
        assert resp.projects[0].status == "planned"

    def test_filter_by_status(self, di):
        _init(di)
        _register(di, slug="maps-1", scope="Freight operations")
        _register(di, slug="maps-2", scope="Warehouse logistics")
        _activate(di, slug="maps-2")
        resp = di.list_projects_usecase.execute(
            ListProjectsRequest(client=CLIENT, status="active")
        )
        assert len(resp.projects) == 1
        assert resp.projects[0].slug == "maps-2"


# ---------------------------------------------------------------------------
# GetProject
# ---------------------------------------------------------------------------


class TestGetProject:
    """Retrieve a single project by slug."""

    def test_not_found(self, di):
        _init(di)
        resp = di.get_project_usecase.execute(
            GetProjectRequest(client=CLIENT, slug="nonexistent")
        )
        assert resp.project is None

    def test_found(self, di):
        _init(di)
        _register(di)
        resp = di.get_project_usecase.execute(
            GetProjectRequest(client=CLIENT, slug="maps-1")
        )
        assert resp.project is not None
        assert resp.project.slug == "maps-1"
        assert resp.project.status == "planned"


# ---------------------------------------------------------------------------
# GetProjectProgress
# ---------------------------------------------------------------------------


class TestGetProjectProgress:
    """Match decisions against the skillset pipeline to report progress."""

    def test_no_decisions_all_stages_pending(self, di):
        _init(di)
        _register(di)
        resp = di.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        assert len(resp.stages) == 5
        assert all(not s.completed for s in resp.stages)
        assert resp.current_stage == "wm-research"
        assert resp.next_prerequisite == "resources/index.md"

    def test_first_stage_completed_advances_current(self, di):
        _init(di)
        _register(di)
        di.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                project_slug="maps-1",
                title="Stage 1: Research and brief agreed",
                fields={"Scope": "Freight division"},
            )
        )
        resp = di.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        assert resp.stages[0].completed is True
        assert resp.stages[0].skill == "wm-research"
        assert resp.stages[1].completed is False
        assert resp.current_stage == "wm-needs"
        assert resp.next_prerequisite == "brief.agreed.md"

    def test_all_five_stages_completed(self, di):
        _init(di)
        _register(di)
        for title in [
            "Stage 1: Research and brief agreed",
            "Stage 2: User needs agreed",
            "Stage 3: Supply chain agreed",
            "Stage 4: Evolution map agreed",
            "Stage 5: Strategy map agreed",
        ]:
            di.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        resp = di.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        assert all(s.completed for s in resp.stages)
        assert resp.current_stage is None
        assert resp.next_prerequisite is None

    def test_stages_report_skill_names(self, di):
        """Each stage carries the skill that executes it."""
        _init(di)
        _register(di)
        resp = di.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        skills = [s.skill for s in resp.stages]
        assert skills == [
            "wm-research",
            "wm-needs",
            "wm-chain",
            "wm-evolve",
            "wm-strategy",
        ]

    @pytest.mark.parametrize(
        "stage_decisions, expected_current, expected_gate",
        [
            pytest.param(
                ["Stage 1: Research and brief agreed"],
                "wm-needs",
                "brief.agreed.md",
                id="research-complete→needs",
            ),
            pytest.param(
                [
                    "Stage 1: Research and brief agreed",
                    "Stage 2: User needs agreed",
                ],
                "wm-chain",
                "needs/needs.agreed.md",
                id="needs-complete→chain",
            ),
            pytest.param(
                [
                    "Stage 1: Research and brief agreed",
                    "Stage 2: User needs agreed",
                    "Stage 3: Supply chain agreed",
                ],
                "wm-evolve",
                "chain/supply-chain.agreed.md",
                id="chain-complete→evolve",
            ),
            pytest.param(
                [
                    "Stage 1: Research and brief agreed",
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
                    "Stage 1: Research and brief agreed",
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
        self, di, stage_decisions, expected_current, expected_gate
    ):
        """Each stage decision advances the pipeline to the next skill."""
        _init(di)
        _register(di)
        for title in stage_decisions:
            di.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        resp = di.get_project_progress_usecase.execute(
            GetProjectProgressRequest(client=CLIENT, project_slug="maps-1")
        )
        assert resp.current_stage == expected_current
        assert resp.next_prerequisite == expected_gate

    def test_nonexistent_project_rejected(self, di):
        _init(di)
        with pytest.raises(ValueError, match="not found"):
            di.get_project_progress_usecase.execute(
                GetProjectProgressRequest(client=CLIENT, project_slug="phantom-1")
            )


# ---------------------------------------------------------------------------
# ListDecisions
# ---------------------------------------------------------------------------


class TestListDecisions:
    """List a project's decision log."""

    def test_registration_seeds_one_decision(self, di):
        _init(di)
        _register(di)
        resp = di.list_decisions_usecase.execute(
            ListDecisionsRequest(client=CLIENT, project_slug="maps-1")
        )
        assert len(resp.decisions) == 1
        assert resp.decisions[0].title == "Project created"

    def test_recorded_decisions_appear(self, di):
        _init(di)
        _register(di)
        di.record_decision_usecase.execute(
            RecordDecisionRequest(
                client=CLIENT,
                project_slug="maps-1",
                title="Stage 1: Research and brief agreed",
                fields={"Scope": "Freight division"},
            )
        )
        resp = di.list_decisions_usecase.execute(
            ListDecisionsRequest(client=CLIENT, project_slug="maps-1")
        )
        titles = [d.title for d in resp.decisions]
        assert "Project created" in titles
        assert "Stage 1: Research and brief agreed" in titles


# ---------------------------------------------------------------------------
# ListResearchTopics
# ---------------------------------------------------------------------------


class TestListResearchTopics:
    """List the client's research manifest."""

    def test_empty_manifest(self, di):
        _init(di)
        resp = di.list_research_topics_usecase.execute(
            ListResearchTopicsRequest(client=CLIENT)
        )
        assert resp.topics == []

    def test_registered_topics_appear(self, di):
        _init(di)
        di.register_research_topic_usecase.execute(
            RegisterResearchTopicRequest(
                client=CLIENT,
                topic="Partnerships and fleet suppliers",
                filename="partnerships-suppliers.md",
                confidence="Medium-High",
            )
        )
        resp = di.list_research_topics_usecase.execute(
            ListResearchTopicsRequest(client=CLIENT)
        )
        assert len(resp.topics) == 1
        assert resp.topics[0].topic == "Partnerships and fleet suppliers"
        assert resp.topics[0].confidence == "Medium-High"
