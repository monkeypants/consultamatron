"""Observation routing tests — allow list policy and use case integration.

Tests verify the security boundary (deny-all, allow-some) and the
aggregation/routing use cases that depend on it.
"""

from __future__ import annotations

import pytest

import json

from bin.cli.di import Container
from bin.cli.dtos import AggregateNeedsBriefRequest, RouteObservationsRequest
from bin.cli.usecases import AggregateNeedsBriefUseCase, RouteObservationsUseCase
from consulting.dtos import CreateEngagementRequest, InitializeWorkspaceRequest
from practice.entities import SourceType
from practice.exceptions import NotFoundError

from .conftest import (
    DEFAULT_CLIENT,
    DEFAULT_ENGAGEMENT,
    make_engagement_entity,
    make_project,
    make_skillset_source,
)

CLIENT = DEFAULT_CLIENT
ENGAGEMENT = DEFAULT_ENGAGEMENT

_NEED_TEMPLATE = """\
---
slug: {slug}
owner_type: {owner_type}
owner_ref: {owner_ref}
level: {level}
need: {need}
rationale: Test rationale
lifecycle_moment: research
served: false
---
"""


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


# ---------------------------------------------------------------------------
# AggregateNeedsBrief — integration tests
# ---------------------------------------------------------------------------


def _init(di, client=CLIENT):
    di.initialize_workspace_usecase.execute(InitializeWorkspaceRequest(client=client))


def _ensure_engagement(di, client=CLIENT, engagement=ENGAGEMENT):
    if di.engagement_entities.get(client, engagement) is None:
        di.create_engagement_usecase.execute(
            CreateEngagementRequest(client=client, slug=engagement)
        )


@pytest.mark.doctrine
class TestAggregateNeedsBrief:
    """Integration tests for needs aggregation use case."""

    @pytest.fixture
    def di(self, tmp_config, tmp_path):
        """Container with needs_reader overridden to use tmp_path."""
        from bin.cli.infrastructure.filesystem_needs_reader import (
            FilesystemNeedsReader,
        )

        c = Container(tmp_config)
        # Override needs_reader so type-level needs scan tmp_path, not real repo
        reader = FilesystemNeedsReader(
            repo_root=tmp_path,
            workspace_root=tmp_config.workspace_root,
        )
        c.needs_reader = reader
        c.aggregate_needs_brief_usecase = AggregateNeedsBriefUseCase(
            engagements=c.engagement_entities,
            projects=c.projects,
            sources=c.sources,
            needs_reader=reader,
            pack_nudger=c.pack_nudger,
        )
        return c

    def test_zero_needs_returns_empty_with_destinations(self, di):
        """Zero needs → empty brief, destinations still populated."""
        _init(di)
        _ensure_engagement(di)
        resp = di.aggregate_needs_brief_usecase.execute(
            AggregateNeedsBriefRequest(client=CLIENT, engagement=ENGAGEMENT)
        )
        assert resp.needs == []
        # Minimum destinations: personal + client + practice
        dest_types = {d.owner_type for d in resp.destinations}
        assert "personal" in dest_types
        assert "client" in dest_types
        assert "practice" in dest_types

    def test_type_level_need_appears_in_brief(self, di, tmp_path):
        """Type-level need file → appears in brief."""
        _init(di)
        _ensure_engagement(di)
        needs_dir = tmp_path / "docs" / "observation-needs"
        needs_dir.mkdir(parents=True, exist_ok=True)
        (needs_dir / "client.md").write_text(
            _NEED_TEMPLATE.format(
                slug="client-type-need",
                owner_type="client",
                owner_ref="client",
                level="type",
                need="Watch for strategic gaps",
            )
        )
        resp = di.aggregate_needs_brief_usecase.execute(
            AggregateNeedsBriefRequest(client=CLIENT, engagement=ENGAGEMENT)
        )
        slugs = [n.slug for n in resp.needs]
        assert "client-type-need" in slugs

    def test_instance_level_need_appears_alongside_type(self, di, tmp_config, tmp_path):
        """Instance-level need file → appears alongside type-level."""
        _init(di)
        _ensure_engagement(di)
        # Type-level need
        type_dir = tmp_path / "docs" / "observation-needs"
        type_dir.mkdir(parents=True, exist_ok=True)
        (type_dir / "client.md").write_text(
            _NEED_TEMPLATE.format(
                slug="type-need",
                owner_type="client",
                owner_ref="client",
                level="type",
                need="Type-level need",
            )
        )
        # Instance-level need
        inst_dir = tmp_config.workspace_root / CLIENT / "observation-needs"
        inst_dir.mkdir(parents=True, exist_ok=True)
        (inst_dir / "instance-need.md").write_text(
            _NEED_TEMPLATE.format(
                slug="instance-need",
                owner_type="client",
                owner_ref=CLIENT,
                level="instance",
                need="Instance-level need",
            )
        )
        resp = di.aggregate_needs_brief_usecase.execute(
            AggregateNeedsBriefRequest(client=CLIENT, engagement=ENGAGEMENT)
        )
        slugs = [n.slug for n in resp.needs]
        assert "type-need" in slugs
        assert "instance-need" in slugs

    def test_destinations_include_personal_and_client(self, di):
        """Destinations include personal and client."""
        _init(di)
        _ensure_engagement(di)
        resp = di.aggregate_needs_brief_usecase.execute(
            AggregateNeedsBriefRequest(client=CLIENT, engagement=ENGAGEMENT)
        )
        dest_pairs = {(d.owner_type, d.owner_ref) for d in resp.destinations}
        assert ("personal", "personal") in dest_pairs
        assert ("client", CLIENT) in dest_pairs

    def test_nonexistent_engagement_raises(self, di):
        """Nonexistent engagement → NotFoundError."""
        _init(di)
        with pytest.raises(NotFoundError):
            di.aggregate_needs_brief_usecase.execute(
                AggregateNeedsBriefRequest(client=CLIENT, engagement="nonexistent")
            )


# ---------------------------------------------------------------------------
# RouteObservations — integration tests
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestRouteObservations:
    """Integration tests for observation routing use case."""

    @pytest.fixture
    def di(self, tmp_config, tmp_path):
        from bin.cli.infrastructure.filesystem_needs_reader import (
            FilesystemNeedsReader,
        )
        from bin.cli.infrastructure.filesystem_observation_writer import (
            FilesystemObservationWriter,
        )

        c = Container(tmp_config)
        reader = FilesystemNeedsReader(
            repo_root=tmp_path,
            workspace_root=tmp_config.workspace_root,
        )
        writer = FilesystemObservationWriter(
            repo_root=tmp_path,
            workspace_root=tmp_config.workspace_root,
        )
        c.needs_reader = reader
        c.observation_writer = writer
        c.aggregate_needs_brief_usecase = AggregateNeedsBriefUseCase(
            engagements=c.engagement_entities,
            projects=c.projects,
            sources=c.sources,
            needs_reader=reader,
            pack_nudger=c.pack_nudger,
        )
        c.route_observations_usecase = RouteObservationsUseCase(
            engagements=c.engagement_entities,
            projects=c.projects,
            sources=c.sources,
            observation_writer=writer,
        )
        return c

    def test_observation_to_allowed_destination_routed(self, di):
        """Observation to allowed destination → routed."""
        _init(di)
        _ensure_engagement(di)
        obs = [
            {
                "slug": "test-obs",
                "source_inflection": "gatepoint",
                "need_refs": ["some-need"],
                "content": "An observation.",
                "destinations": [
                    {"owner_type": "client", "owner_ref": CLIENT},
                ],
            }
        ]
        resp = di.route_observations_usecase.execute(
            RouteObservationsRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                observations=json.dumps(obs),
            )
        )
        assert resp.routed == 1
        assert resp.rejected == 0

    def test_observation_to_commons_rejected(self, di):
        """Observation to commons skillset → rejected."""
        _init(di)
        _ensure_engagement(di)
        obs = [
            {
                "slug": "commons-obs",
                "source_inflection": "gatepoint",
                "need_refs": [],
                "content": "Should be rejected.",
                "destinations": [
                    {"owner_type": "skillset", "owner_ref": "wardley-mapping"},
                ],
            }
        ]
        resp = di.route_observations_usecase.execute(
            RouteObservationsRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                observations=json.dumps(obs),
            )
        )
        assert resp.routed == 0
        assert resp.rejected == 1

    def test_zero_observations_succeeds(self, di):
        """Zero observations → succeeds with both counts 0."""
        _init(di)
        _ensure_engagement(di)
        resp = di.route_observations_usecase.execute(
            RouteObservationsRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                observations="[]",
            )
        )
        assert resp.routed == 0
        assert resp.rejected == 0

    def test_fan_out_with_partial_eligibility(self, di):
        """Fan-out: eligible delivered, ineligible rejected."""
        _init(di)
        _ensure_engagement(di)
        obs = [
            {
                "slug": "mixed-obs",
                "source_inflection": "review",
                "need_refs": [],
                "content": "Mixed routing.",
                "destinations": [
                    {"owner_type": "client", "owner_ref": CLIENT},
                    {"owner_type": "skillset", "owner_ref": "wardley-mapping"},
                ],
            }
        ]
        resp = di.route_observations_usecase.execute(
            RouteObservationsRequest(
                client=CLIENT,
                engagement=ENGAGEMENT,
                observations=json.dumps(obs),
            )
        )
        assert resp.routed == 1
        assert resp.rejected == 1
