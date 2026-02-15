"""EntityStore proof — Project reimplemented against the generic protocol.

Demonstrates that JsonEntityStore[Project] covers every operation
currently served by JsonProjectRepository, validating the generic
protocol design from #44.

Each test maps to a specific TestProjectContract test, showing the
old API call and its EntityStore equivalent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bin.cli.entities import Project, ProjectStatus
from bin.cli.infrastructure.json_entity_store import JsonEntityStore
from bin.cli.store import EntityStore

from .conftest import make_project


def _project_store(workspace_root: Path) -> JsonEntityStore[Project]:
    """Factory matching JsonProjectRepository's path layout."""
    return JsonEntityStore(
        model=Project,
        key_field="slug",
        path_resolver=lambda f: workspace_root
        / f["client"]
        / "projects"
        / "index.json",
    )


@pytest.fixture
def store(tmp_path) -> JsonEntityStore[Project]:
    return _project_store(tmp_path / "clients")


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestProtocolConformance:
    """JsonEntityStore satisfies the EntityStore protocol."""

    def test_is_entity_store(self, store):
        assert isinstance(store, EntityStore)


# ---------------------------------------------------------------------------
# get — replaces ProjectRepository.get(client, slug)
# ---------------------------------------------------------------------------


class TestGet:
    def test_missing_returns_none(self, store):
        # Was: project_repo.get("holloway-group", "nonexistent")
        assert store.get({"client": "holloway-group", "slug": "nonexistent"}) is None

    def test_save_then_get(self, store):
        # Was: project_repo.save(p); project_repo.get("holloway-group", "maps-1")
        store.save(make_project())
        got = store.get({"client": "holloway-group", "slug": "maps-1"})
        assert got is not None
        assert got.slug == "maps-1"
        assert got.skillset == "wardley-mapping"

    def test_wrong_slug_returns_none(self, store):
        store.save(make_project(slug="maps-1"))
        assert store.get({"client": "holloway-group", "slug": "maps-2"}) is None


# ---------------------------------------------------------------------------
# search — replaces list_all(client) and list_filtered(client, ...)
# ---------------------------------------------------------------------------


class TestSearch:
    def test_empty_scope_returns_empty(self, store):
        # Was: project_repo.list_all("holloway-group")
        assert store.search({"client": "holloway-group"}) == []

    def test_list_all_by_scope(self, store):
        store.save(make_project(slug="maps-1"))
        store.save(make_project(slug="maps-2"))
        assert len(store.search({"client": "holloway-group"})) == 2

    def test_filter_by_skillset(self, store):
        # Was: project_repo.list_filtered("holloway-group", skillset="wardley-mapping")
        store.save(make_project(slug="maps-1", skillset="wardley-mapping"))
        store.save(make_project(slug="canvas-1", skillset="business-model-canvas"))
        result = store.search(
            {"client": "holloway-group", "skillset": "wardley-mapping"}
        )
        assert len(result) == 1
        assert result[0].slug == "maps-1"

    def test_filter_by_status(self, store):
        # Was: project_repo.list_filtered("holloway-group", status=ProjectStatus.ELABORATION)
        store.save(make_project(slug="maps-1", status=ProjectStatus.PLANNING))
        store.save(make_project(slug="maps-2", status=ProjectStatus.ELABORATION))
        result = store.search({"client": "holloway-group", "status": "elaboration"})
        assert len(result) == 1
        assert result[0].slug == "maps-2"

    def test_filter_no_match(self, store):
        store.save(make_project(status=ProjectStatus.PLANNING))
        result = store.search({"client": "holloway-group", "status": "implementation"})
        assert result == []

    def test_no_filters_beyond_scope_returns_all(self, store):
        # Was: project_repo.list_filtered("holloway-group") with no optional args
        store.save(make_project(slug="maps-1"))
        store.save(make_project(slug="maps-2"))
        assert len(store.search({"client": "holloway-group"})) == 2

    def test_combined_filters(self, store):
        store.save(
            make_project(
                slug="maps-1",
                skillset="wardley-mapping",
                status=ProjectStatus.PLANNING,
            )
        )
        store.save(
            make_project(
                slug="maps-2",
                skillset="wardley-mapping",
                status=ProjectStatus.ELABORATION,
            )
        )
        result = store.search(
            {
                "client": "holloway-group",
                "skillset": "wardley-mapping",
                "status": "planning",
            }
        )
        assert len(result) == 1
        assert result[0].slug == "maps-1"


# ---------------------------------------------------------------------------
# save — replaces ProjectRepository.save(project)
# ---------------------------------------------------------------------------


class TestSave:
    def test_upsert_updates_existing(self, store):
        # Was: save twice with same slug, different status
        store.save(make_project(status=ProjectStatus.PLANNING))
        store.save(make_project(status=ProjectStatus.ELABORATION))
        got = store.get({"client": "holloway-group", "slug": "maps-1"})
        assert got.status == ProjectStatus.ELABORATION
        assert len(store.search({"client": "holloway-group"})) == 1


# ---------------------------------------------------------------------------
# delete — replaces ProjectRepository.delete(client, slug)
# ---------------------------------------------------------------------------


class TestDelete:
    def test_delete_existing(self, store):
        store.save(make_project())
        assert store.delete({"client": "holloway-group", "slug": "maps-1"}) is True
        assert store.get({"client": "holloway-group", "slug": "maps-1"}) is None

    def test_delete_missing(self, store):
        assert store.delete({"client": "holloway-group", "slug": "nope"}) is False


# ---------------------------------------------------------------------------
# Scoping — replaces client isolation and client_exists
# ---------------------------------------------------------------------------


class TestScoping:
    def test_client_isolation(self, store):
        store.save(make_project(client="holloway-group"))
        store.save(make_project(client="meridian-health"))
        assert len(store.search({"client": "holloway-group"})) == 1
        assert len(store.search({"client": "meridian-health"})) == 1

    def test_client_exists_as_usecase_logic(self, store):
        # Was: project_repo.client_exists("holloway-group")
        # Now: usecase checks search result
        assert store.search({"client": "holloway-group"}) == []
        store.save(make_project())
        assert store.search({"client": "holloway-group"}) != []


# ---------------------------------------------------------------------------
# Decision proof — append-only store with project scoping
# ---------------------------------------------------------------------------


class TestDecisionProof:
    """Verify the append_only flag works for immutable entity patterns."""

    @pytest.fixture
    def decision_store(self, tmp_path):
        from bin.cli.entities import DecisionEntry

        return JsonEntityStore(
            model=DecisionEntry,
            key_field="id",
            path_resolver=lambda f: (
                tmp_path
                / "clients"
                / f["client"]
                / "projects"
                / f["project_slug"]
                / "decisions.json"
            ),
            append_only=True,
        )

    def test_append_creates_separate_entries(self, decision_store):
        from .conftest import make_decision

        decision_store.save(make_decision(id="d1", title="Stage 1"))
        decision_store.save(make_decision(id="d2", title="Stage 2"))
        result = decision_store.search(
            {"client": "holloway-group", "project_slug": "maps-1"}
        )
        assert len(result) == 2

    def test_search_by_title(self, decision_store):
        from .conftest import make_decision

        decision_store.save(make_decision(id="d1", title="Stage 1: Research agreed"))
        decision_store.save(make_decision(id="d2", title="Stage 2: Needs agreed"))
        result = decision_store.search(
            {
                "client": "holloway-group",
                "project_slug": "maps-1",
                "title": "Stage 1: Research agreed",
            }
        )
        assert len(result) == 1
        assert result[0].id == "d1"

    def test_project_isolation(self, decision_store):
        from .conftest import make_decision

        decision_store.save(make_decision(id="d1", project_slug="maps-1"))
        decision_store.save(make_decision(id="d2", project_slug="maps-2"))
        assert (
            len(
                decision_store.search(
                    {"client": "holloway-group", "project_slug": "maps-1"}
                )
            )
            == 1
        )
