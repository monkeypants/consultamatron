"""Wardley Mapping usecase tests."""

from __future__ import annotations

import pytest

from bin.cli.di import Container
from bin.cli.dtos import (
    CreateEngagementRequest,
    GetProjectProgressRequest,
    InitializeWorkspaceRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
)
from practice.exceptions import NotFoundError
from wardley_mapping.dtos import RegisterTourRequest
from wardley_mapping.types import TourStop

CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


@pytest.fixture
def di(tmp_config):
    return Container(tmp_config)


@pytest.fixture
def workspace(di):
    di.initialize_workspace_usecase.execute(InitializeWorkspaceRequest(client=CLIENT))
    return di


@pytest.fixture
def project(workspace):
    workspace.create_engagement_usecase.execute(
        CreateEngagementRequest(client=CLIENT, slug=ENGAGEMENT)
    )
    workspace.register_project_usecase.execute(
        RegisterProjectRequest(
            client=CLIENT,
            engagement=ENGAGEMENT,
            slug="maps-1",
            skillset="wardley-mapping",
            scope="Freight operations",
        )
    )
    return workspace


# ---------------------------------------------------------------------------
# RegisterTour
# ---------------------------------------------------------------------------


class TestRegisterTour:
    """Register curated presentation tours for specific audiences."""

    def test_returns_stop_count(self, project):
        resp = project.register_tour_usecase.execute(
            RegisterTourRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
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
                engagement=ENGAGEMENT,
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
        got = project.tours.get(CLIENT, ENGAGEMENT, "maps-1", "executive")
        assert got is not None
        assert len(got.stops) == 2
        assert got.stops[1].atlas_source == "atlas/risk/"

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.register_tour_usecase.execute(
                RegisterTourRequest(
                    client=CLIENT,
                    engagement=ENGAGEMENT,
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
# GetProjectProgress (WM pipeline specifics)
# ---------------------------------------------------------------------------


class TestGetProjectProgress:
    """Match decisions against the WM pipeline to report progress."""

    def test_no_decisions_all_stages_pending(self, project):
        resp = project.get_project_progress_usecase.execute(
            GetProjectProgressRequest(
                client=CLIENT, engagement=ENGAGEMENT, project_slug="maps-1"
            )
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
                id="research-complete->needs",
            ),
            pytest.param(
                [
                    "Stage 1: Project brief agreed",
                    "Stage 2: User needs agreed",
                ],
                "wm-chain",
                "needs/needs.agreed.md",
                id="needs-complete->chain",
            ),
            pytest.param(
                [
                    "Stage 1: Project brief agreed",
                    "Stage 2: User needs agreed",
                    "Stage 3: Supply chain agreed",
                ],
                "wm-evolve",
                "chain/supply-chain.agreed.md",
                id="chain-complete->evolve",
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
                id="evolve-complete->strategy",
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
                id="strategy-complete->done",
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
                    engagement=ENGAGEMENT,
                    project_slug="maps-1",
                    title=title,
                    fields={},
                )
            )
        resp = project.get_project_progress_usecase.execute(
            GetProjectProgressRequest(
                client=CLIENT, engagement=ENGAGEMENT, project_slug="maps-1"
            )
        )
        assert resp.current_stage == expected_current
        assert resp.next_prerequisite == expected_gate

    def test_nonexistent_project_rejected(self, workspace):
        with pytest.raises(NotFoundError, match="not found"):
            workspace.get_project_progress_usecase.execute(
                GetProjectProgressRequest(
                    client=CLIENT, engagement=ENGAGEMENT, project_slug="phantom-1"
                )
            )
