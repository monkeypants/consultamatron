"""Repository contract tests.

Written against the protocol, not the implementation. Every
test here must pass for ANY conforming implementation. The
implementation is injected via parametrized fixtures in conftest.

Adding an implementation = adding one params entry in conftest.
Every contract test runs automatically.
"""

from __future__ import annotations

import pytest


from practice.entities import Confidence, EngagementStatus, ProjectStatus

from .conftest import (
    make_decision,
    make_engagement_entry,
    make_engagement_entity,
    make_observation,
    make_project,
    make_research,
    make_routing_destination,
)

pytestmark = pytest.mark.doctrine

CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


# ---------------------------------------------------------------------------
# Engagement entity repository contracts (mutable CRUD)
# ---------------------------------------------------------------------------


class TestEngagementEntityContract:
    def test_get_missing_returns_none(self, engagement_entity_repo):
        assert engagement_entity_repo.get(CLIENT, "nonexistent") is None

    def test_list_all_empty(self, engagement_entity_repo):
        assert engagement_entity_repo.list_all(CLIENT) == []

    def test_save_then_get(self, engagement_entity_repo):
        e = make_engagement_entity()
        engagement_entity_repo.save(e)
        got = engagement_entity_repo.get(CLIENT, ENGAGEMENT)
        assert got is not None
        assert got.slug == ENGAGEMENT
        assert got.status == EngagementStatus.PLANNING

    def test_save_then_list_all(self, engagement_entity_repo):
        engagement_entity_repo.save(make_engagement_entity(slug="strat-1"))
        engagement_entity_repo.save(make_engagement_entity(slug="strat-2"))
        assert len(engagement_entity_repo.list_all(CLIENT)) == 2

    def test_save_existing_updates(self, engagement_entity_repo):
        engagement_entity_repo.save(
            make_engagement_entity(status=EngagementStatus.PLANNING)
        )
        engagement_entity_repo.save(
            make_engagement_entity(status=EngagementStatus.ACTIVE)
        )
        got = engagement_entity_repo.get(CLIENT, ENGAGEMENT)
        assert got.status == EngagementStatus.ACTIVE
        assert len(engagement_entity_repo.list_all(CLIENT)) == 1

    def test_client_isolation(self, engagement_entity_repo):
        engagement_entity_repo.save(make_engagement_entity(client="holloway-group"))
        engagement_entity_repo.save(make_engagement_entity(client="meridian-health"))
        assert len(engagement_entity_repo.list_all("holloway-group")) == 1
        assert len(engagement_entity_repo.list_all("meridian-health")) == 1

    def test_allowed_sources_preserved(self, engagement_entity_repo):
        engagement_entity_repo.save(
            make_engagement_entity(allowed_sources=["commons", "partner-x"])
        )
        got = engagement_entity_repo.get(CLIENT, ENGAGEMENT)
        assert got.allowed_sources == ["commons", "partner-x"]


# ---------------------------------------------------------------------------
# Project repository contracts
# ---------------------------------------------------------------------------


class TestProjectContract:
    def test_get_missing_returns_none(self, project_repo):
        assert project_repo.get(CLIENT, ENGAGEMENT, "nonexistent") is None

    def test_list_all_empty(self, project_repo):
        assert project_repo.list_all(CLIENT) == []

    def test_save_then_get(self, project_repo):
        p = make_project()
        project_repo.save(p)
        got = project_repo.get(CLIENT, ENGAGEMENT, "maps-1")
        assert got is not None
        assert got.slug == "maps-1"
        assert got.skillset == "test-skillset"

    def test_save_then_list_all(self, project_repo):
        project_repo.save(make_project(slug="maps-1"))
        project_repo.save(make_project(slug="maps-2"))
        assert len(project_repo.list_all(CLIENT)) == 2

    def test_save_existing_updates(self, project_repo):
        project_repo.save(make_project(status=ProjectStatus.PLANNING))
        project_repo.save(make_project(status=ProjectStatus.ELABORATION))
        got = project_repo.get(CLIENT, ENGAGEMENT, "maps-1")
        assert got.status == ProjectStatus.ELABORATION
        assert len(project_repo.list_all(CLIENT)) == 1

    def test_list_filtered_by_skillset(self, project_repo):
        project_repo.save(make_project(slug="maps-1", skillset="wardley-mapping"))
        project_repo.save(
            make_project(slug="canvas-1", skillset="business-model-canvas")
        )
        result = project_repo.list_filtered(
            CLIENT, ENGAGEMENT, skillset="wardley-mapping"
        )
        assert len(result) == 1
        assert result[0].slug == "maps-1"

    def test_list_filtered_by_status(self, project_repo):
        project_repo.save(make_project(slug="maps-1", status=ProjectStatus.PLANNING))
        project_repo.save(make_project(slug="maps-2", status=ProjectStatus.ELABORATION))
        result = project_repo.list_filtered(
            CLIENT, ENGAGEMENT, status=ProjectStatus.ELABORATION
        )
        assert len(result) == 1
        assert result[0].slug == "maps-2"

    def test_list_filtered_no_match(self, project_repo):
        project_repo.save(make_project(status=ProjectStatus.PLANNING))
        result = project_repo.list_filtered(
            CLIENT, ENGAGEMENT, status=ProjectStatus.IMPLEMENTATION
        )
        assert result == []

    def test_list_filtered_no_filters_returns_all(self, project_repo):
        project_repo.save(make_project(slug="maps-1"))
        project_repo.save(make_project(slug="maps-2"))
        assert len(project_repo.list_filtered(CLIENT, ENGAGEMENT)) == 2

    def test_delete_existing(self, project_repo):
        project_repo.save(make_project())
        assert project_repo.delete(CLIENT, ENGAGEMENT, "maps-1") is True
        assert project_repo.get(CLIENT, ENGAGEMENT, "maps-1") is None

    def test_delete_missing(self, project_repo):
        assert project_repo.delete(CLIENT, ENGAGEMENT, "nope") is False

    def test_client_isolation(self, project_repo):
        project_repo.save(make_project(client="holloway-group"))
        project_repo.save(make_project(client="meridian-health"))
        assert len(project_repo.list_all("holloway-group")) == 1
        assert len(project_repo.list_all("meridian-health")) == 1

    def test_engagement_isolation(self, project_repo):
        project_repo.save(make_project(engagement="strat-1"))
        project_repo.save(make_project(engagement="strat-2"))
        assert len(project_repo.list_filtered(CLIENT, "strat-1")) == 1
        assert len(project_repo.list_filtered(CLIENT, "strat-2")) == 1
        # list_all spans all engagements
        assert len(project_repo.list_all(CLIENT)) == 2

    def test_client_exists_false_initially(self, project_repo):
        assert project_repo.client_exists(CLIENT) is False

    def test_client_exists_true_after_save(self, project_repo):
        project_repo.save(make_project())
        assert project_repo.client_exists(CLIENT) is True


# ---------------------------------------------------------------------------
# Decision repository contracts (immutable, append-only)
# ---------------------------------------------------------------------------


class TestDecisionContract:
    def test_get_missing_returns_none(self, decision_repo):
        assert decision_repo.get(CLIENT, ENGAGEMENT, "maps-1", "no-such-id") is None

    def test_list_all_empty(self, decision_repo):
        assert decision_repo.list_all(CLIENT, ENGAGEMENT, "maps-1") == []

    def test_save_then_get(self, decision_repo):
        d = make_decision(id="d1")
        decision_repo.save(d)
        got = decision_repo.get(CLIENT, ENGAGEMENT, "maps-1", "d1")
        assert got is not None
        assert got.title == d.title

    def test_save_appends(self, decision_repo):
        decision_repo.save(
            make_decision(id="d1", title="Stage 1: Research and brief agreed")
        )
        decision_repo.save(make_decision(id="d2", title="Stage 2: User needs agreed"))
        all_entries = decision_repo.list_all(CLIENT, ENGAGEMENT, "maps-1")
        assert len(all_entries) == 2

    def test_list_filtered_by_title(self, decision_repo):
        decision_repo.save(
            make_decision(id="d1", title="Stage 1: Research and brief agreed")
        )
        decision_repo.save(make_decision(id="d2", title="Stage 2: User needs agreed"))
        result = decision_repo.list_filtered(
            CLIENT,
            ENGAGEMENT,
            "maps-1",
            title="Stage 1: Research and brief agreed",
        )
        assert len(result) == 1
        assert result[0].id == "d1"

    def test_list_filtered_no_filter_returns_all(self, decision_repo):
        decision_repo.save(make_decision(id="d1"))
        decision_repo.save(make_decision(id="d2"))
        assert len(decision_repo.list_filtered(CLIENT, ENGAGEMENT, "maps-1")) == 2

    def test_project_isolation(self, decision_repo):
        decision_repo.save(make_decision(id="d1", project_slug="maps-1"))
        decision_repo.save(make_decision(id="d2", project_slug="maps-2"))
        assert len(decision_repo.list_all(CLIENT, ENGAGEMENT, "maps-1")) == 1
        assert len(decision_repo.list_all(CLIENT, ENGAGEMENT, "maps-2")) == 1

    def test_client_isolation(self, decision_repo):
        decision_repo.save(make_decision(id="d1", client="holloway-group"))
        decision_repo.save(make_decision(id="d2", client="meridian-health"))
        assert len(decision_repo.list_all("holloway-group", ENGAGEMENT, "maps-1")) == 1
        assert len(decision_repo.list_all("meridian-health", ENGAGEMENT, "maps-1")) == 1

    def test_fields_preserved(self, decision_repo):
        fields = {"Users": "CTO, VP Eng", "Scope": "Platform only"}
        decision_repo.save(make_decision(id="d1", fields=fields))
        got = decision_repo.get(CLIENT, ENGAGEMENT, "maps-1", "d1")
        assert got.fields == fields


# ---------------------------------------------------------------------------
# Engagement log repository contracts (immutable, append-only)
# ---------------------------------------------------------------------------


class TestEngagementLogContract:
    def test_get_missing_returns_none(self, engagement_log_repo):
        assert engagement_log_repo.get(CLIENT, "no-such-id") is None

    def test_list_all_empty(self, engagement_log_repo):
        assert engagement_log_repo.list_all(CLIENT) == []

    def test_save_then_get(self, engagement_log_repo):
        e = make_engagement_entry(id="e1")
        engagement_log_repo.save(e)
        got = engagement_log_repo.get(CLIENT, "e1")
        assert got is not None
        assert got.title == e.title

    def test_save_appends(self, engagement_log_repo):
        engagement_log_repo.save(make_engagement_entry(id="e1"))
        engagement_log_repo.save(make_engagement_entry(id="e2"))
        assert len(engagement_log_repo.list_all(CLIENT)) == 2

    def test_client_isolation(self, engagement_log_repo):
        engagement_log_repo.save(
            make_engagement_entry(id="e1", client="holloway-group")
        )
        engagement_log_repo.save(
            make_engagement_entry(id="e2", client="meridian-health")
        )
        assert len(engagement_log_repo.list_all("holloway-group")) == 1
        assert len(engagement_log_repo.list_all("meridian-health")) == 1

    def test_fields_preserved(self, engagement_log_repo):
        fields = {"Skillset": "wardley-mapping", "Scope": "Full"}
        engagement_log_repo.save(make_engagement_entry(id="e1", fields=fields))
        got = engagement_log_repo.get(CLIENT, "e1")
        assert got.fields == fields


# ---------------------------------------------------------------------------
# Research topic repository contracts (mutable)
# ---------------------------------------------------------------------------


class TestResearchTopicContract:
    def test_get_missing_returns_none(self, research_repo):
        assert research_repo.get(CLIENT, "nonexistent.md") is None

    def test_list_all_empty(self, research_repo):
        assert research_repo.list_all(CLIENT) == []

    def test_save_then_get(self, research_repo):
        r = make_research()
        research_repo.save(r)
        got = research_repo.get(CLIENT, "market-position.md")
        assert got is not None
        assert got.topic == "Market position"

    def test_save_existing_updates(self, research_repo):
        research_repo.save(make_research(confidence=Confidence.LOW))
        research_repo.save(make_research(confidence=Confidence.HIGH))
        got = research_repo.get(CLIENT, "market-position.md")
        assert got.confidence == Confidence.HIGH
        assert len(research_repo.list_all(CLIENT)) == 1

    def test_exists_false_initially(self, research_repo):
        assert research_repo.exists(CLIENT, "market-position.md") is False

    def test_exists_true_after_save(self, research_repo):
        research_repo.save(make_research())
        assert research_repo.exists(CLIENT, "market-position.md") is True

    def test_client_isolation(self, research_repo):
        research_repo.save(make_research(client="holloway-group"))
        research_repo.save(make_research(client="meridian-health"))
        assert len(research_repo.list_all("holloway-group")) == 1
        assert len(research_repo.list_all("meridian-health")) == 1


# ---------------------------------------------------------------------------
# NeedsReader contract tests
# ---------------------------------------------------------------------------

_NEED_FRONTMATTER = """\
---
slug: strategic-gaps
owner_type: client
owner_ref: client
level: type
need: Watch for strategic gaps
rationale: Improves scoping
lifecycle_moment: research
served: false
---
Body prose about the need.
"""


@pytest.mark.doctrine
class TestNeedsReaderContract:
    """NeedsReader implementations must satisfy these contracts."""

    def test_empty_dir_returns_empty(self, needs_reader):
        assert needs_reader.type_level_needs("client") == []

    def test_type_level_need_from_file(self, needs_reader, tmp_path):
        needs_dir = tmp_path / "docs" / "observation-needs"
        needs_dir.mkdir(parents=True)
        (needs_dir / "client.md").write_text(_NEED_FRONTMATTER)

        result = needs_reader.type_level_needs("client")
        assert len(result) == 1
        assert result[0].slug == "strategic-gaps"
        assert result[0].level == "type"
        assert result[0].owner_type == "client"

    def test_instance_needs_from_client_dir(self, needs_reader, tmp_path):
        needs_dir = tmp_path / "clients" / "holloway-group" / "observation-needs"
        needs_dir.mkdir(parents=True)
        (needs_dir / "freight-gaps.md").write_text(
            _NEED_FRONTMATTER.replace("slug: strategic-gaps", "slug: freight-gaps")
            .replace("level: type", "level: instance")
            .replace("owner_ref: client", "owner_ref: holloway-group")
        )

        result = needs_reader.instance_needs("client", "holloway-group")
        assert len(result) == 1
        assert result[0].slug == "freight-gaps"
        assert result[0].level == "instance"

    def test_missing_client_dir_returns_empty(self, needs_reader):
        result = needs_reader.instance_needs("client", "nonexistent-corp")
        assert result == []

    def test_multiple_files_returns_all(self, needs_reader, tmp_path):
        needs_dir = tmp_path / "clients" / "holloway-group" / "observation-needs"
        needs_dir.mkdir(parents=True)
        for i in range(3):
            (needs_dir / f"need-{i}.md").write_text(
                _NEED_FRONTMATTER.replace("slug: strategic-gaps", f"slug: need-{i}")
                .replace("level: type", "level: instance")
                .replace("owner_ref: client", "owner_ref: holloway-group")
            )

        result = needs_reader.instance_needs("client", "holloway-group")
        assert len(result) == 3


# ---------------------------------------------------------------------------
# ObservationWriter contract tests
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestObservationWriterContract:
    """ObservationWriter implementations must satisfy these contracts."""

    def test_write_creates_file_in_client_dir(self, observation_writer, tmp_path):
        obs = make_observation(
            destinations=[
                make_routing_destination(
                    owner_type="client", owner_ref="holloway-group"
                )
            ]
        )
        observation_writer.write(obs)
        obs_dir = tmp_path / "clients" / "holloway-group" / "observations"
        assert obs_dir.is_dir()
        files = list(obs_dir.glob("*.md"))
        assert len(files) == 1

    def test_slug_round_trips_through_frontmatter(self, observation_writer, tmp_path):
        from practice.frontmatter import parse_frontmatter

        obs = make_observation(
            slug="test-obs",
            destinations=[
                make_routing_destination(
                    owner_type="client", owner_ref="holloway-group"
                )
            ],
        )
        observation_writer.write(obs)
        obs_dir = tmp_path / "clients" / "holloway-group" / "observations"
        files = list(obs_dir.glob("*.md"))
        fm = parse_frontmatter(files[0])
        assert fm["slug"] == "test-obs"

    def test_fan_out_to_multiple_destinations(self, observation_writer, tmp_path):
        obs = make_observation(
            destinations=[
                make_routing_destination(
                    owner_type="client", owner_ref="holloway-group"
                ),
                make_routing_destination(owner_type="personal", owner_ref="personal"),
            ]
        )
        observation_writer.write(obs)
        client_dir = tmp_path / "clients" / "holloway-group" / "observations"
        personal_dir = tmp_path / "personal" / "observations"
        assert len(list(client_dir.glob("*.md"))) == 1
        assert len(list(personal_dir.glob("*.md"))) == 1


# ---------------------------------------------------------------------------
# PendingObservationStore contract tests
# ---------------------------------------------------------------------------


_PENDING_OBS_TEMPLATE = """\
---
slug: {slug}
source_inflection: gatepoint
need_refs: [{need_refs}]
---
{content}
"""


@pytest.mark.doctrine
class TestPendingObservationStoreContract:
    """PendingObservationStore implementations must satisfy these contracts."""

    def test_empty_dir_returns_empty(self, pending_store):
        result = pending_store.read_pending(CLIENT, ENGAGEMENT)
        assert result == []

    def test_write_then_read_returns_observation(self, pending_store, tmp_path):
        pending_dir = (
            tmp_path
            / "clients"
            / CLIENT
            / "engagements"
            / ENGAGEMENT
            / ".observations-pending"
        )
        pending_dir.mkdir(parents=True)
        (pending_dir / "test-obs.md").write_text(
            _PENDING_OBS_TEMPLATE.format(
                slug="test-obs",
                need_refs="some-need",
                content="An observation.",
            )
        )
        result = pending_store.read_pending(CLIENT, ENGAGEMENT)
        assert len(result) == 1
        assert result[0].slug == "test-obs"
        assert result[0].need_refs == ["some-need"]
        assert result[0].content == "An observation."

    def test_clear_pending_removes_files(self, pending_store, tmp_path):
        pending_dir = (
            tmp_path
            / "clients"
            / CLIENT
            / "engagements"
            / ENGAGEMENT
            / ".observations-pending"
        )
        pending_dir.mkdir(parents=True)
        (pending_dir / "test-obs.md").write_text(
            _PENDING_OBS_TEMPLATE.format(
                slug="test-obs",
                need_refs="some-need",
                content="An observation.",
            )
        )
        pending_store.clear_pending(CLIENT, ENGAGEMENT)
        assert not list(pending_dir.glob("*.md"))

    def test_nonexistent_dir_returns_empty(self, pending_store):
        result = pending_store.read_pending("no-such-client", "no-such-engagement")
        assert result == []
