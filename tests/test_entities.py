"""Entity tests.

Serialisation fidelity, default values, and domain-specific
semantics. Pydantic handles validation — the usecase and repository
tests exercise those paths with better diagnostics than we could
provide here.
"""

from __future__ import annotations

from practice.entities import EngagementStatus, Pipeline, PipelineTrigger, Skillset

from .conftest import (
    make_engagement_entity,
    make_pipeline,
    make_project,
    make_prospectus,
    make_skillset,
)


# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------


class TestDefaults:
    def test_project_notes_defaults_empty(self):
        p = make_project()
        assert p.notes == ""

    def test_project_pipeline_defaults_empty(self):
        p = make_project()
        assert p.pipeline == ""

    def test_engagement_notes_defaults_empty(self):
        e = make_engagement_entity()
        assert e.notes == ""

    def test_engagement_allowed_sources_defaults_to_commons_and_personal(self):
        e = make_engagement_entity()
        assert e.allowed_sources == ["commons", "personal"]


class TestProjectPipeline:
    """Project records which pipeline within the skillset it uses."""

    def test_project_stores_pipeline(self):
        p = make_project(pipeline="create")
        assert p.pipeline == "create"


# ---------------------------------------------------------------------------
# Pipeline entity
# ---------------------------------------------------------------------------


class TestPipelineEntity:
    """Pipeline serialises, round-trips, and reports implementation status."""

    def test_pipeline_round_trip(self):
        p = make_pipeline()
        dumped = p.model_dump(mode="json")
        restored = Pipeline.model_validate(dumped)
        assert restored == p

    def test_is_implemented_with_stages(self):
        p = make_pipeline()
        assert p.is_implemented is True

    def test_is_not_implemented_without_stages(self):
        p = make_pipeline(stages=[])
        assert p.is_implemented is False


class TestPipelineTrigger:
    """PipelineTrigger round-trips through JSON."""

    def test_round_trip(self):
        t = PipelineTrigger(
            need="Map supply chain", circumstance="New client engagement"
        )
        dumped = t.model_dump(mode="json")
        restored = PipelineTrigger.model_validate(dumped)
        assert restored == t


# ---------------------------------------------------------------------------
# Skillset entity
# ---------------------------------------------------------------------------


class TestSkillsetImplementation:
    """is_implemented delegates to pipelines."""

    def test_implemented_with_pipeline(self):
        s = make_skillset()
        assert s.is_implemented is True

    def test_not_implemented_without_pipeline(self):
        s = make_prospectus()
        assert s.is_implemented is False

    def test_empty_pipelines_is_not_implemented(self):
        s = make_skillset(pipelines=[])
        assert s.is_implemented is False

    def test_pipelines_contains_pipeline_objects(self):
        s = make_skillset()
        assert len(s.pipelines) > 0
        assert isinstance(s.pipelines[0], Pipeline)


class TestSkillsetGetPipeline:
    """Skillset.get_pipeline retrieves a pipeline by name."""

    def test_get_pipeline(self):
        s = Skillset(
            name="wardley-mapping",
            display_name="Wardley Mapping",
            description="Strategic mapping.",
            pipelines=[
                make_pipeline(name="create"),
                make_pipeline(name="refine"),
            ],
        )
        p = s.get_pipeline("create")
        assert p is not None
        assert p.name == "create"

    def test_get_pipeline_unknown(self):
        s = Skillset(
            name="wardley-mapping",
            display_name="Wardley Mapping",
            description="Strategic mapping.",
            pipelines=[
                make_pipeline(name="create"),
                make_pipeline(name="refine"),
            ],
        )
        assert s.get_pipeline("nonexistent") is None


# ---------------------------------------------------------------------------
# EngagementStatus lifecycle
# ---------------------------------------------------------------------------


class TestEngagementStatus:
    """EngagementStatus lifecycle transitions."""

    def test_planning_next_is_active(self):
        assert EngagementStatus.PLANNING.next() == EngagementStatus.ACTIVE

    def test_active_next_is_review(self):
        assert EngagementStatus.ACTIVE.next() == EngagementStatus.REVIEW

    def test_review_next_is_closed(self):
        assert EngagementStatus.REVIEW.next() == EngagementStatus.CLOSED

    def test_closed_next_is_none(self):
        assert EngagementStatus.CLOSED.next() is None

    def test_full_lifecycle(self):
        status = EngagementStatus.PLANNING
        visited = [status]
        while (nxt := status.next()) is not None:
            visited.append(nxt)
            status = nxt
        assert len(visited) == 4
