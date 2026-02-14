"""JSON infrastructure-specific tests.

These test the *how* of the JSON implementation: file paths,
directory structure, JSON format, missing-file resilience.
Contract tests (test_repository_contracts.py) test the *what*.
"""

from __future__ import annotations

import json

from bin.cli.infrastructure.json_repos import (
    JsonProjectRepository,
    JsonResearchTopicRepository,
    JsonTourManifestRepository,
)
from bin.cli.infrastructure.json_repos import _read_json_array, _read_json_object

from .conftest import make_project, make_research, make_tour


# ---------------------------------------------------------------------------
# Path conventions
# ---------------------------------------------------------------------------


class TestPathConventions:
    """Files land at the paths documented in config.py."""

    def test_projects_index(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project(client="holloway-group"))
        expected = (
            tmp_config.workspace_root / "holloway-group" / "projects" / "index.json"
        )
        assert expected.exists()

    def test_decisions_file(self, tmp_config, decision_repo):
        from .conftest import make_decision

        decision_repo.save(
            make_decision(client="holloway-group", project_slug="maps-1")
        )
        expected = (
            tmp_config.workspace_root
            / "holloway-group"
            / "projects"
            / "maps-1"
            / "decisions.json"
        )
        assert expected.exists()

    def test_engagement_file(self, tmp_config, engagement_repo):
        from .conftest import make_engagement

        engagement_repo.save(make_engagement(client="holloway-group"))
        expected = tmp_config.workspace_root / "holloway-group" / "engagement.json"
        assert expected.exists()

    def test_research_index(self, tmp_config):
        repo = JsonResearchTopicRepository(tmp_config.workspace_root)
        repo.save(make_research(client="holloway-group"))
        expected = (
            tmp_config.workspace_root / "holloway-group" / "resources" / "index.json"
        )
        assert expected.exists()

    def test_tour_manifest(self, tmp_config):
        repo = JsonTourManifestRepository(tmp_config.workspace_root)
        repo.save(
            make_tour(client="holloway-group", project_slug="maps-1", name="investor")
        )
        expected = (
            tmp_config.workspace_root
            / "holloway-group"
            / "projects"
            / "maps-1"
            / "presentations"
            / "investor"
            / "manifest.json"
        )
        assert expected.exists()


# ---------------------------------------------------------------------------
# Directory-as-identity
# ---------------------------------------------------------------------------


class TestDirectoryAsIdentity:
    def test_client_exists_is_directory_check(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        client_dir = tmp_config.workspace_root / "holloway-group"
        client_dir.mkdir(parents=True)
        assert repo.client_exists("holloway-group") is True

    def test_rename_directory_changes_client(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project(client="old-name"))
        assert repo.client_exists("old-name") is True

        old_dir = tmp_config.workspace_root / "old-name"
        new_dir = tmp_config.workspace_root / "new-name"
        old_dir.rename(new_dir)

        assert repo.client_exists("old-name") is False
        assert repo.client_exists("new-name") is True
        assert repo.get("new-name", "maps-1") is not None


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------


class TestJsonFormat:
    def test_file_is_valid_json(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project())
        path = tmp_config.workspace_root / "holloway-group" / "projects" / "index.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 1

    def test_file_is_indented(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project())
        path = tmp_config.workspace_root / "holloway-group" / "projects" / "index.json"
        text = path.read_text(encoding="utf-8")
        assert "\n  " in text  # indented with 2 spaces

    def test_file_ends_with_newline(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project())
        path = tmp_config.workspace_root / "holloway-group" / "projects" / "index.json"
        text = path.read_text(encoding="utf-8")
        assert text.endswith("\n")

    def test_tour_manifest_is_object_not_array(self, tmp_config):
        repo = JsonTourManifestRepository(tmp_config.workspace_root)
        repo.save(make_tour())
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "projects"
            / "maps-1"
            / "presentations"
            / "investor"
            / "manifest.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Missing file resilience
# ---------------------------------------------------------------------------


class TestMissingFileResilience:
    def test_read_json_array_missing_file(self, tmp_path):
        result = _read_json_array(tmp_path / "does-not-exist.json")
        assert result == []

    def test_read_json_object_missing_file(self, tmp_path):
        result = _read_json_object(tmp_path / "does-not-exist.json")
        assert result is None

    def test_mkdir_p_on_deep_save(self, tmp_config):
        """Saving to a deeply nested path creates all intermediates."""
        repo = JsonTourManifestRepository(tmp_config.workspace_root)
        repo.save(make_tour())
        # If we got here without error, mkdir -p worked.
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "projects"
            / "maps-1"
            / "presentations"
            / "investor"
            / "manifest.json"
        )
        assert path.exists()
