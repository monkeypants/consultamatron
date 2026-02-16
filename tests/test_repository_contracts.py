"""Repository contract tests.

Written against the protocol, not the implementation. Every
test here must pass for ANY conforming implementation. The
implementation is injected via parametrized fixtures in conftest.

Adding an implementation = adding one params entry in conftest.
Every contract test runs automatically.
"""

from __future__ import annotations

import json

from practice.entities import Confidence, EngagementStatus, ProjectStatus

from .conftest import (
    make_decision,
    make_engagement,
    make_engagement_entity,
    make_project,
    make_research,
    make_skillset,
    make_tour,
    make_tour_stop,
)

CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


# ---------------------------------------------------------------------------
# Skillset repository contracts
# ---------------------------------------------------------------------------


class TestSkillsetContract:
    def test_get_missing_returns_none(self, skillset_repo):
        assert skillset_repo.get("nonexistent") is None

    def test_list_all_empty(self, skillset_repo):
        assert skillset_repo.list_all() == []

    def test_round_trip_via_file(self, skillset_repo, tmp_config):
        """Seed the backing store and verify get/list work."""
        s = make_skillset(name="test-skillset")
        data = [s.model_dump(mode="json")]
        path = tmp_config.skillsets_root / "index.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

        assert skillset_repo.get("test-skillset") is not None
        assert skillset_repo.get("test-skillset").display_name == "Wardley Mapping"
        assert len(skillset_repo.list_all()) == 1

    def test_get_wrong_name_returns_none(self, skillset_repo, tmp_config):
        s = make_skillset(name="alpha")
        path = tmp_config.skillsets_root / "index.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps([s.model_dump(mode="json")]))

        assert skillset_repo.get("beta") is None


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
        assert got.skillset == "wardley-mapping"

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
        e = make_engagement(id="e1")
        engagement_log_repo.save(e)
        got = engagement_log_repo.get(CLIENT, "e1")
        assert got is not None
        assert got.title == e.title

    def test_save_appends(self, engagement_log_repo):
        engagement_log_repo.save(make_engagement(id="e1"))
        engagement_log_repo.save(make_engagement(id="e2"))
        assert len(engagement_log_repo.list_all(CLIENT)) == 2

    def test_client_isolation(self, engagement_log_repo):
        engagement_log_repo.save(make_engagement(id="e1", client="holloway-group"))
        engagement_log_repo.save(make_engagement(id="e2", client="meridian-health"))
        assert len(engagement_log_repo.list_all("holloway-group")) == 1
        assert len(engagement_log_repo.list_all("meridian-health")) == 1

    def test_fields_preserved(self, engagement_log_repo):
        fields = {"Skillset": "wardley-mapping", "Scope": "Full"}
        engagement_log_repo.save(make_engagement(id="e1", fields=fields))
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
# Tour manifest repository contracts (replace semantics)
# ---------------------------------------------------------------------------


class TestTourManifestContract:
    def test_get_missing_returns_none(self, tour_repo):
        assert tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor") is None

    def test_save_then_get(self, tour_repo):
        t = make_tour()
        tour_repo.save(t)
        got = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        assert got is not None
        assert got.title == "Investor Tour"
        assert len(got.stops) == 1

    def test_save_replaces(self, tour_repo):
        tour_repo.save(make_tour(stops=[make_tour_stop(order="1")]))
        tour_repo.save(
            make_tour(
                stops=[
                    make_tour_stop(order="1"),
                    make_tour_stop(order="2", title="Risk", atlas_source="atlas/risk/"),
                ]
            )
        )
        got = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        assert len(got.stops) == 2

    def test_different_tours_independent(self, tour_repo):
        tour_repo.save(make_tour(name="investor", title="Investor Tour"))
        tour_repo.save(make_tour(name="technical", title="Technical Tour"))
        inv = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        tech = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "technical")
        assert inv.title == "Investor Tour"
        assert tech.title == "Technical Tour"

    def test_project_isolation(self, tour_repo):
        tour_repo.save(make_tour(project_slug="maps-1"))
        assert tour_repo.get(CLIENT, ENGAGEMENT, "maps-2", "investor") is None

    def test_stops_round_trip(self, tour_repo):
        stops = [
            make_tour_stop(order="1", title="Overview"),
            make_tour_stop(order="2a", title="Risk A"),
            make_tour_stop(order="2b", title="Risk B"),
        ]
        tour_repo.save(make_tour(stops=stops))
        got = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        assert [s.order for s in got.stops] == ["1", "2a", "2b"]
        assert [s.title for s in got.stops] == ["Overview", "Risk A", "Risk B"]

    def test_list_all_empty(self, tour_repo):
        assert tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-1") == []

    def test_list_all_returns_all_tours(self, tour_repo):
        tour_repo.save(make_tour(name="investor", title="Investor Tour"))
        tour_repo.save(make_tour(name="technical", title="Technical Tour"))
        result = tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-1")
        assert len(result) == 2
        names = {t.name for t in result}
        assert names == {"investor", "technical"}

    def test_list_all_project_isolation(self, tour_repo):
        tour_repo.save(make_tour(project_slug="maps-1"))
        tour_repo.save(make_tour(project_slug="maps-2"))
        assert len(tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-1")) == 1
        assert len(tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-2")) == 1
