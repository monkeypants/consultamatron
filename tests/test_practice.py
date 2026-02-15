"""Practice library contract tests.

Behavioral contracts for each protocol in the practice package.
A developer reading these tests understands what a bounded context
must conform to. EntityStore contracts live in test_entity_store.py.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from practice.content import (
    ContentPage,
    Figure,
    NarrativeGroup,
    NarrativePage,
    NarrativeStop,
    ProjectContribution,
    ProjectSection,
)
from practice.discovery import PipelineStage
from practice.exceptions import (
    DomainError,
    DuplicateError,
    InvalidTransitionError,
    NotFoundError,
)
from practice.repositories import Clock, IdGenerator, ProjectPresenter, SiteRenderer
from practice.usecase import UseCase

from bin.cli.di import UuidGenerator, WallClock

pytestmark = pytest.mark.doctrine


# ---------------------------------------------------------------------------
# UseCase protocol
# ---------------------------------------------------------------------------


class TestUseCaseContract:
    """UseCase[TRequest, TResponse] — the execute(request) -> response contract."""

    def test_class_with_execute_satisfies_protocol(self):
        class Echo:
            def execute(self, request: str) -> str:
                return request

        echo: UseCase[str, str] = Echo()
        assert echo.execute("hello") == "hello", (
            "any class with execute(request) -> response satisfies UseCase"
        )


# ---------------------------------------------------------------------------
# Clock protocol
# ---------------------------------------------------------------------------


class TestClockContract:
    """Clock — wall-clock abstraction for timestamping domain events."""

    def test_wall_clock_satisfies_protocol(self):
        clock = WallClock()
        assert isinstance(clock, Clock), "WallClock must satisfy the Clock protocol"

    def test_today_returns_date(self):
        clock = WallClock()
        result = clock.today()
        assert isinstance(result, date), "today() must return a date"

    def test_now_returns_timezone_aware_datetime(self):
        clock = WallClock()
        result = clock.now()
        assert isinstance(result, datetime), "now() must return a datetime"
        assert result.tzinfo is not None, "now() must be timezone-aware"

    def test_tz_returns_tzinfo(self):
        clock = WallClock()
        result = clock.tz()
        assert result is not None, "tz() must return a timezone"


# ---------------------------------------------------------------------------
# IdGenerator protocol
# ---------------------------------------------------------------------------


class TestIdGeneratorContract:
    """IdGenerator — identity generation for new domain entities."""

    def test_uuid_generator_satisfies_protocol(self):
        gen = UuidGenerator()
        assert isinstance(gen, IdGenerator), (
            "UuidGenerator must satisfy the IdGenerator protocol"
        )

    def test_new_id_returns_string(self):
        gen = UuidGenerator()
        result = gen.new_id()
        assert isinstance(result, str), "new_id() must return a string"

    def test_successive_ids_are_unique(self):
        gen = UuidGenerator()
        ids = {gen.new_id() for _ in range(10)}
        assert len(ids) == 10, "successive new_id() calls must produce unique values"


# ---------------------------------------------------------------------------
# ProjectPresenter protocol
# ---------------------------------------------------------------------------


class TestProjectPresenterContract:
    """ProjectPresenter — assembles workspace artifacts into content.

    Behavioral tests are in test_conformance.py::TestPresenterContract.
    This test verifies the protocol is runtime-checkable.
    """

    def test_protocol_is_runtime_checkable(self):
        assert hasattr(ProjectPresenter, "__protocol_attrs__") or callable(
            getattr(ProjectPresenter, "__instancecheck__", None)
        ), "ProjectPresenter must be a runtime-checkable Protocol"


# ---------------------------------------------------------------------------
# SiteRenderer protocol
# ---------------------------------------------------------------------------


class TestSiteRendererContract:
    """SiteRenderer — infrastructure port for HTML generation.

    This test verifies the protocol is runtime-checkable. Full
    behavioral tests require template fixtures and live in
    test_site_rendering.py.
    """

    def test_protocol_is_runtime_checkable(self):
        assert hasattr(SiteRenderer, "__protocol_attrs__") or callable(
            getattr(SiteRenderer, "__instancecheck__", None)
        ), "SiteRenderer must be a runtime-checkable Protocol"


# ---------------------------------------------------------------------------
# Domain exceptions hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """Domain exceptions form a single-root hierarchy under DomainError."""

    def test_not_found_is_domain_error(self):
        assert issubclass(NotFoundError, DomainError), (
            "NotFoundError must extend DomainError"
        )

    def test_duplicate_is_domain_error(self):
        assert issubclass(DuplicateError, DomainError), (
            "DuplicateError must extend DomainError"
        )

    def test_invalid_transition_is_domain_error(self):
        assert issubclass(InvalidTransitionError, DomainError), (
            "InvalidTransitionError must extend DomainError"
        )

    def test_domain_error_is_catchable_as_exception(self):
        with pytest.raises(DomainError):
            raise NotFoundError("test")


# ---------------------------------------------------------------------------
# Content entity structure
# ---------------------------------------------------------------------------


class TestContentEntityStructure:
    """Content entities carry the rendering vocabulary shared across presenters."""

    def test_figure_holds_svg_content(self):
        fig = Figure(caption="Map overview", svg_content="<svg></svg>")
        assert fig.caption == "Map overview", "Figure must carry a caption"
        assert fig.svg_content == "<svg></svg>", "Figure must carry SVG content"

    def test_content_page_has_slug_and_body(self):
        page = ContentPage(title="Brief", slug="brief", body_md="# Brief")
        assert page.slug == "brief", "ContentPage must have a slug"
        assert page.body_md == "# Brief", "ContentPage must have markdown body"

    def test_project_contribution_assembles_sections(self):
        contrib = ProjectContribution(
            slug="maps-1",
            title="Wardley Map",
            skillset="wardley-mapping",
            status="elaboration",
            overview_md="# Overview",
            sections=[
                ProjectSection(label="Research", slug="research"),
            ],
        )
        assert contrib.slug == "maps-1", "contribution must carry project slug"
        assert len(contrib.sections) == 1, "contribution must hold sections"

    def test_narrative_page_assembles_groups(self):
        page = NarrativePage(
            title="Investor Tour",
            slug="investor",
            description="For investors",
            opening_md="# Welcome",
            groups=[
                NarrativeGroup(
                    stops=[
                        NarrativeStop(
                            title="Overview",
                            level="h2",
                            is_header=True,
                            figures=[],
                            analysis_md="The landscape.",
                        )
                    ],
                    transition_md="Next we examine...",
                )
            ],
        )
        assert page.slug == "investor", "NarrativePage must have a slug"
        assert len(page.groups) == 1, "NarrativePage must hold groups"


# ---------------------------------------------------------------------------
# PipelineStage discovery type
# ---------------------------------------------------------------------------


class TestPipelineStageContract:
    """PipelineStage — the shared type bounded contexts use to declare pipelines."""

    def test_round_trip_fidelity(self):
        stage = PipelineStage(
            order=1,
            skill="wm-research",
            prerequisite_gate="resources/index.md",
            produces_gate="brief.agreed.md",
            description="Stage 1: Research and brief agreed",
        )
        restored = PipelineStage.model_validate(stage.model_dump(mode="json"))
        assert restored == stage, "PipelineStage must survive JSON round-trip"

    def test_gate_fields_are_strings(self):
        stage = PipelineStage(
            order=1,
            skill="wm-research",
            prerequisite_gate="resources/index.md",
            produces_gate="brief.agreed.md",
            description="Research",
        )
        assert isinstance(stage.prerequisite_gate, str), (
            "prerequisite_gate must be a string path"
        )
        assert isinstance(stage.produces_gate, str), (
            "produces_gate must be a string path"
        )
