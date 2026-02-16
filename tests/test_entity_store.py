"""EntityStore contract tests — organised by design property, not CRUD operation.

Each test class teaches one design rule of the EntityStore protocol.
The tests use parametrized fixtures from conftest.py so every assertion
runs against every implementation backend.
"""

from __future__ import annotations

import pytest

from practice.entities import ProjectStatus
from practice.store import EntityStore

from .conftest import make_decision, make_project

pytestmark = pytest.mark.doctrine

ENGAGEMENT = "strat-1"


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """JsonEntityStore satisfies the EntityStore structural protocol."""

    def test_is_entity_store(self, project_store):
        assert isinstance(project_store, EntityStore), (
            "store must satisfy the EntityStore protocol"
        )


# ---------------------------------------------------------------------------
# Round-trip: save persists, get retrieves
# ---------------------------------------------------------------------------


class TestRoundTrip:
    """Save persists an entity; get retrieves it by identity filters."""

    def test_save_then_get_returns_equivalent_entity(self, project_store):
        original = make_project()
        project_store.save(original)
        got = project_store.get(
            {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "maps-1"}
        )
        assert got is not None, "get must return a saved entity"
        assert got.slug == original.slug, "retrieved entity must match saved slug"
        assert got.skillset == original.skillset, (
            "retrieved entity must preserve all fields"
        )

    def test_get_missing_returns_none(self, project_store):
        assert (
            project_store.get(
                {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "nope"}
            )
            is None
        ), "get on an empty store must return None"

    def test_get_wrong_key_returns_none(self, project_store):
        project_store.save(make_project(slug="maps-1"))
        assert (
            project_store.get(
                {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "maps-2"}
            )
            is None
        ), "get with non-matching key must return None even when store is non-empty"

    def test_delete_removes_entity(self, project_store):
        project_store.save(make_project())
        assert project_store.delete(
            {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "maps-1"}
        ), "delete must return True when entity existed"
        assert (
            project_store.get(
                {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "maps-1"}
            )
            is None
        ), "deleted entity must not be retrievable"

    def test_delete_missing_returns_false(self, project_store):
        assert not project_store.delete(
            {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "nope"}
        ), "delete must return False when no entity matched"


# ---------------------------------------------------------------------------
# Filter semantics: string key-value pairs composed with AND
# ---------------------------------------------------------------------------


class TestFilterSemantics:
    """Filters are string key-value pairs composed with AND logic.

    The central design move: scope fields (client) and domain fields
    (skillset, status) use the same filter mechanism. There is no
    separate concept of "scope" in the protocol — just filters.
    """

    def test_search_empty_store_returns_empty_list(self, project_store):
        assert (
            project_store.search({"client": "holloway-group", "engagement": ENGAGEMENT})
            == []
        ), "search on an empty store must return an empty list"

    def test_search_by_scope_returns_all_in_scope(self, project_store):
        project_store.save(make_project(slug="maps-1"))
        project_store.save(make_project(slug="maps-2"))
        results = project_store.search(
            {"client": "holloway-group", "engagement": ENGAGEMENT}
        )
        assert len(results) == 2, (
            "scope-only filter must return all entities in that scope"
        )

    def test_domain_filter_narrows_results(self, project_store):
        project_store.save(make_project(slug="maps-1", skillset="wardley-mapping"))
        project_store.save(
            make_project(slug="canvas-1", skillset="business-model-canvas")
        )
        results = project_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "skillset": "wardley-mapping",
            }
        )
        assert len(results) == 1, "domain filter must narrow results"
        assert results[0].slug == "maps-1", (
            "domain filter must return only matching entities"
        )

    def test_scope_and_domain_filters_compose_as_conjunction(self, project_store):
        project_store.save(
            make_project(
                slug="maps-1",
                skillset="wardley-mapping",
                status=ProjectStatus.PLANNING,
            )
        )
        project_store.save(
            make_project(
                slug="maps-2",
                skillset="wardley-mapping",
                status=ProjectStatus.ELABORATION,
            )
        )
        results = project_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "skillset": "wardley-mapping",
                "status": "planning",
            }
        )
        assert len(results) == 1, "multiple filters must compose as AND"
        assert results[0].slug == "maps-1", (
            "conjunction filter must return only the entity matching all filters"
        )

    def test_filter_with_no_match_returns_empty(self, project_store):
        project_store.save(make_project(status=ProjectStatus.PLANNING))
        results = project_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "status": "implementation",
            }
        )
        assert results == [], "filter that matches no entities must return empty list"

    def test_enum_fields_match_against_string_value(self, project_store):
        """Enum fields are str-based, so filters use the string value directly.

        ProjectStatus.ELABORATION.value == "elaboration", and filters
        pass the string "elaboration" — the store must match these.
        """
        project_store.save(make_project(slug="maps-1", status=ProjectStatus.PLANNING))
        project_store.save(
            make_project(slug="maps-2", status=ProjectStatus.ELABORATION)
        )
        results = project_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "status": "elaboration",
            }
        )
        assert len(results) == 1, (
            "enum filter must match against the enum's string value"
        )
        assert results[0].slug == "maps-2", (
            "enum filter must select the entity with the matching status"
        )


# ---------------------------------------------------------------------------
# Identity: key_field determines which entity gets replaced
# ---------------------------------------------------------------------------


class TestIdentity:
    """key_field determines which entity gets replaced on save.

    Same key + same scope = update. Same key + different scope =
    two separate entities (identity is scoped, not global).
    """

    def test_upsert_replaces_entity_with_same_key(self, project_store):
        project_store.save(make_project(status=ProjectStatus.PLANNING))
        project_store.save(make_project(status=ProjectStatus.ELABORATION))
        got = project_store.get(
            {"client": "holloway-group", "engagement": ENGAGEMENT, "slug": "maps-1"}
        )
        assert got.status == ProjectStatus.ELABORATION, (
            "second save with same key must replace the first"
        )
        all_results = project_store.search(
            {"client": "holloway-group", "engagement": ENGAGEMENT}
        )
        assert len(all_results) == 1, "upsert must not create a duplicate"

    def test_same_key_different_scope_are_separate_entities(self, project_store):
        project_store.save(make_project(slug="maps-1", client="holloway-group"))
        project_store.save(make_project(slug="maps-1", client="meridian-health"))
        holloway = project_store.search(
            {"client": "holloway-group", "engagement": ENGAGEMENT}
        )
        meridian = project_store.search(
            {"client": "meridian-health", "engagement": ENGAGEMENT}
        )
        assert len(holloway) == 1, (
            "same key in different scope must not collide (holloway)"
        )
        assert len(meridian) == 1, (
            "same key in different scope must not collide (meridian)"
        )


# ---------------------------------------------------------------------------
# Scoping: scope fields in the filter dict isolate entity namespaces
# ---------------------------------------------------------------------------


class TestScoping:
    """Scope fields in the filter dict isolate entity namespaces.

    Different client = different namespace. The store resolves
    to different files, so entities never leak across scopes.
    """

    def test_different_clients_are_isolated(self, project_store):
        project_store.save(make_project(client="holloway-group"))
        project_store.save(make_project(client="meridian-health"))
        assert (
            len(
                project_store.search(
                    {"client": "holloway-group", "engagement": ENGAGEMENT}
                )
            )
            == 1
        ), "client scope must isolate holloway-group entities"
        assert (
            len(
                project_store.search(
                    {"client": "meridian-health", "engagement": ENGAGEMENT}
                )
            )
            == 1
        ), "client scope must isolate meridian-health entities"

    def test_empty_scope_is_empty(self, project_store):
        project_store.save(make_project(client="holloway-group"))
        results = project_store.search(
            {"client": "meridian-health", "engagement": ENGAGEMENT}
        )
        assert results == [], "search in an unpopulated scope must return empty list"


# ---------------------------------------------------------------------------
# Append vs upsert: two save strategies contrasted
# ---------------------------------------------------------------------------


class TestAppendVsUpsert:
    """Two save strategies: upsert replaces by key_field, append always adds.

    Upsert (project_store) replaces on key match. Append (decision_store)
    creates a new entry even with duplicate keys — suitable for immutable
    event logs.
    """

    def test_upsert_replaces_on_key_match(self, project_store):
        project_store.save(make_project(status=ProjectStatus.PLANNING))
        project_store.save(make_project(status=ProjectStatus.ELABORATION))
        results = project_store.search(
            {"client": "holloway-group", "engagement": ENGAGEMENT}
        )
        assert len(results) == 1, "upsert must replace, not duplicate"

    def test_append_creates_separate_entries(self, decision_store):
        decision_store.save(make_decision(id="d1", title="Stage 1"))
        decision_store.save(make_decision(id="d2", title="Stage 2"))
        results = decision_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "project_slug": "maps-1",
            }
        )
        assert len(results) == 2, (
            "append_only store must create separate entries for each save"
        )

    def test_append_preserves_all_entries_even_with_same_key(self, decision_store):
        decision_store.save(make_decision(id="d1", title="First"))
        decision_store.save(make_decision(id="d1", title="Revised"))
        results = decision_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "project_slug": "maps-1",
            }
        )
        assert len(results) == 2, "append_only store must not deduplicate on key_field"

    def test_append_store_filters_by_domain_field(self, decision_store):
        decision_store.save(make_decision(id="d1", title="Stage 1: Research agreed"))
        decision_store.save(make_decision(id="d2", title="Stage 2: Needs agreed"))
        results = decision_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "project_slug": "maps-1",
                "title": "Stage 1: Research agreed",
            }
        )
        assert len(results) == 1, (
            "append_only store must still support filter narrowing"
        )
        assert results[0].id == "d1", (
            "append_only store filter must return the matching entry"
        )

    def test_append_store_scopes_by_project(self, decision_store):
        decision_store.save(make_decision(id="d1", project_slug="maps-1"))
        decision_store.save(make_decision(id="d2", project_slug="maps-2"))
        results = decision_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "project_slug": "maps-1",
            }
        )
        assert len(results) == 1, "append_only store must respect project_slug scoping"


# ---------------------------------------------------------------------------
# Boundaries: where the protocol's guarantees stop
# ---------------------------------------------------------------------------


class TestBoundaries:
    """Where the protocol's guarantees stop.

    These tests document edge cases and non-guarantees so that
    implementors know what they do NOT need to support.
    """

    def test_filter_on_nonexistent_field_excludes_entity(self, project_store):
        project_store.save(make_project())
        results = project_store.search(
            {
                "client": "holloway-group",
                "engagement": ENGAGEMENT,
                "nonexistent_field": "anything",
            }
        )
        assert results == [], (
            "filtering on a field the entity lacks must exclude it, not crash"
        )

    def test_missing_file_returns_empty(self, project_store):
        results = project_store.search(
            {"client": "no-such-client", "engagement": ENGAGEMENT}
        )
        assert results == [], (
            "store backed by a nonexistent file must return empty, not raise"
        )

    def test_get_with_partial_filters_returns_first_match(self, project_store):
        project_store.save(make_project(slug="maps-1"))
        project_store.save(make_project(slug="maps-2"))
        got = project_store.get({"client": "holloway-group", "engagement": ENGAGEMENT})
        assert got is not None, (
            "get with partial filters must return a match when multiple exist"
        )
