"""Observation routing tests — allow list policy and use case integration.

Tests verify the security boundary (deny-all, allow-some) and the
aggregation/routing use cases that depend on it.
"""

from __future__ import annotations

import pytest

from practice.entities import SourceType

from .conftest import (
    make_engagement_entity,
    make_project,
    make_skillset_source,
)


# ---------------------------------------------------------------------------
# Allow list builder — pure function, security boundary
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestBuildRoutingAllowList:
    """The allow list determines which destinations may receive observations.

    Policy: deny-all, allow-some. Personal, client, and practice are
    always allowed. Projects and engagement targets are allowed when
    the engagement config permits. Commons is never allowed.
    """

    def test_empty_engagement_has_personal_client_practice(self):
        """Minimum allow list: personal + client + practice."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[],
            sources=[],
        )
        dest_types = {(d.owner_type, d.owner_ref) for d in allow.destinations}
        assert ("personal", "personal") in dest_types
        assert ("client", engagement.client) in dest_types
        assert ("practice", "practice") in dest_types

    def test_one_project_adds_engagement_and_project(self):
        """A project adds engagement + project destinations."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        project = make_project(slug="maps-1", engagement=engagement.slug)
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[project],
            sources=[],
        )
        dest_types = {(d.owner_type, d.owner_ref) for d in allow.destinations}
        assert ("engagement", engagement.slug) in dest_types
        assert ("project", "maps-1") in dest_types

    def test_sibling_projects_both_allowed(self):
        """Cross-pollination: sibling projects within an engagement."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        p1 = make_project(slug="maps-1", engagement=engagement.slug)
        p2 = make_project(slug="canvas-1", engagement=engagement.slug)
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[p1, p2],
            sources=[],
        )
        dest_types = {(d.owner_type, d.owner_ref) for d in allow.destinations}
        assert ("project", "maps-1") in dest_types
        assert ("project", "canvas-1") in dest_types

    def test_partnership_source_allowed(self):
        """Partnership skillsets are allowed destinations."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        src = make_skillset_source(
            slug="partner-x",
            source_type=SourceType.PARTNERSHIP,
            skillset_names=["partner-skillset"],
        )
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[],
            sources=[src],
        )
        dest_types = {(d.owner_type, d.owner_ref) for d in allow.destinations}
        assert ("skillset", "partner-skillset") in dest_types

    def test_commons_source_never_allowed(self):
        """Commons skillsets are never allowed — they flow through MCP."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        src = make_skillset_source(
            slug="commons",
            source_type=SourceType.COMMONS,
            skillset_names=["wardley-mapping"],
        )
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[],
            sources=[src],
        )
        dest_types = {(d.owner_type, d.owner_ref) for d in allow.destinations}
        assert ("skillset", "wardley-mapping") not in dest_types

    def test_personal_source_skillsets_allowed(self):
        """Personal skillsets are allowed destinations."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        src = make_skillset_source(
            slug="personal",
            source_type=SourceType.PERSONAL,
            skillset_names=["my-method"],
        )
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[],
            sources=[src],
        )
        dest_types = {(d.owner_type, d.owner_ref) for d in allow.destinations}
        assert ("skillset", "my-method") in dest_types

    def test_no_duplicate_destinations(self):
        """Deduplication: same destination from multiple sources."""
        from practice.routing import build_routing_allow_list

        engagement = make_engagement_entity()
        src1 = make_skillset_source(
            slug="personal",
            source_type=SourceType.PERSONAL,
            skillset_names=["my-method"],
        )
        src2 = make_skillset_source(
            slug="personal",
            source_type=SourceType.PERSONAL,
            skillset_names=["my-method"],
        )
        allow = build_routing_allow_list(
            client=engagement.client,
            engagement=engagement,
            projects=[],
            sources=[src1, src2],
        )
        tuples = [(d.owner_type, d.owner_ref) for d in allow.destinations]
        assert len(tuples) == len(set(tuples))
