"""Entity tests.

Serialisation fidelity, default values, and domain-specific
semantics. Pydantic handles validation — the usecase and repository
tests exercise those paths with better diagnostics than we could
provide here.
"""

from __future__ import annotations

from practice.entities import EngagementStatus

from .conftest import (
    make_engagement_entity,
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

    def test_engagement_notes_defaults_empty(self):
        e = make_engagement_entity()
        assert e.notes == ""

    def test_engagement_allowed_sources_defaults_to_commons_and_personal(self):
        e = make_engagement_entity()
        assert e.allowed_sources == ["commons", "personal"]


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
