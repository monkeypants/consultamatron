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
)
from bin.cli.infrastructure.json_store import read_json_array, read_json_object

from .conftest import make_project, make_research

ENGAGEMENT = "strat-1"


# ---------------------------------------------------------------------------
# Path conventions
# ---------------------------------------------------------------------------


class TestPathConventions:
    """Files land at the paths documented in config.py."""

    def test_projects_index(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project(client="holloway-group"))
        expected = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "projects.json"
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
            / "engagements"
            / ENGAGEMENT
            / "maps-1"
            / "decisions.json"
        )
        assert expected.exists()

    def test_engagement_file(self, tmp_config, engagement_log_repo):
        from .conftest import make_engagement

        engagement_log_repo.save(make_engagement(client="holloway-group"))
        expected = tmp_config.workspace_root / "holloway-group" / "engagement-log.json"
        assert expected.exists()

    def test_research_index(self, tmp_config):
        repo = JsonResearchTopicRepository(tmp_config.workspace_root)
        repo.save(make_research(client="holloway-group"))
        expected = (
            tmp_config.workspace_root / "holloway-group" / "resources" / "index.json"
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
        assert repo.get("new-name", ENGAGEMENT, "maps-1") is not None


# ---------------------------------------------------------------------------
# JSON format
# ---------------------------------------------------------------------------


class TestJsonFormat:
    def test_file_is_valid_json(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project())
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "projects.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, list)
        assert len(data) == 1

    def test_file_is_indented(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project())
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "projects.json"
        )
        text = path.read_text(encoding="utf-8")
        assert "\n  " in text  # indented with 2 spaces

    def test_file_ends_with_newline(self, tmp_config):
        repo = JsonProjectRepository(tmp_config.workspace_root)
        repo.save(make_project())
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "projects.json"
        )
        text = path.read_text(encoding="utf-8")
        assert text.endswith("\n")


# ---------------------------------------------------------------------------
# Missing file resilience
# ---------------------------------------------------------------------------


class TestMissingFileResilience:
    def testread_json_array_missing_file(self, tmp_path):
        result = read_json_array(tmp_path / "does-not-exist.json")
        assert result == []

    def testread_json_object_missing_file(self, tmp_path):
        result = read_json_object(tmp_path / "does-not-exist.json")
        assert result is None
