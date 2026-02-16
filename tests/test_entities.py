"""Entity tests.

Serialisation fidelity, default values, and domain-specific
semantics. Pydantic handles validation — the usecase and repository
tests exercise those paths with better diagnostics than we could
provide here.
"""

from __future__ import annotations

from datetime import date

import pytest

from consulting.entities import DecisionEntry
from practice.discovery import PipelineStage
from practice.entities import EngagementStatus, ProjectStatus

from .conftest import (
    make_decision,
    make_engagement,
    make_engagement_entity,
    make_project,
    make_prospectus,
    make_research,
    make_skillset,
    make_skillset_source,
)


# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------


class TestDefaults:
    def test_project_notes_defaults_empty(self):
        p = make_project()
        assert p.notes == ""

    def test_engagement_notes_defaults_empty(self):
        e = make_engagement_entity()
        assert e.notes == ""

    def test_engagement_allowed_sources_defaults_to_commons_and_personal(self):
        e = make_engagement_entity()
        assert e.allowed_sources == ["commons", "personal"]


# ---------------------------------------------------------------------------
# Round-trip fidelity (model_dump -> model_validate)
# ---------------------------------------------------------------------------


class TestRoundTrip:
    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(make_project(), id="Project"),
            pytest.param(make_decision(), id="DecisionEntry"),
            pytest.param(make_engagement(), id="EngagementEntry"),
            pytest.param(make_research(), id="ResearchTopic"),
            pytest.param(make_skillset(), id="Skillset"),
            pytest.param(make_prospectus(), id="Skillset-prospectus"),
            pytest.param(make_engagement_entity(), id="Engagement"),
            pytest.param(make_skillset_source(), id="SkillsetSource"),
            pytest.param(
                PipelineStage(
                    order=1,
                    skill="wm-research",
                    prerequisite_gate="resources/index.md",
                    produces_gate="brief.agreed.md",
                    description="Kickoff",
                ),
                id="PipelineStage",
            ),
        ],
    )
    def test_json_round_trip(self, entity):
        cls = type(entity)
        dumped = entity.model_dump(mode="json")
        restored = cls.model_validate(dumped)
        assert restored == entity

    def test_date_serialises_as_iso_string(self):
        p = make_project(created=date(2025, 3, 15))
        dumped = p.model_dump(mode="json")
        assert dumped["created"] == "2025-03-15"

    def test_enum_serialises_as_value(self):
        p = make_project(status=ProjectStatus.ELABORATION)
        dumped = p.model_dump(mode="json")
        assert dumped["status"] == "elaboration"

    def test_fields_dict_preserved(self):
        d = make_decision(fields={"Users": "CTO, VP", "Scope": "Narrow"})
        dumped = d.model_dump(mode="json")
        restored = DecisionEntry.model_validate(dumped)
        assert restored.fields == {"Users": "CTO, VP", "Scope": "Narrow"}


# ---------------------------------------------------------------------------
# Entity-specific semantics
# ---------------------------------------------------------------------------


class TestSkillsetImplementation:
    """is_implemented reflects whether the pipeline has stages."""

    def test_implemented_with_pipeline(self):
        s = make_skillset()
        assert s.is_implemented is True

    def test_not_implemented_without_pipeline(self):
        s = make_prospectus()
        assert s.is_implemented is False

    def test_empty_pipeline_is_not_implemented(self):
        s = make_skillset(pipeline=[])
        assert s.is_implemented is False


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
