"""Wardley Mapping JSON infrastructure tests.

Path conventions, format, and resilience for tour manifests.
"""

from __future__ import annotations

import json

from wardley_mapping.infrastructure import JsonTourManifestRepository

from .conftest import make_tour

ENGAGEMENT = "strat-1"


class TestPathConventions:
    def test_tour_manifest(self, tmp_config):
        repo = JsonTourManifestRepository(tmp_config.workspace_root)
        repo.save(
            make_tour(client="holloway-group", project_slug="maps-1", name="investor")
        )
        expected = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "maps-1"
            / "presentations"
            / "investor"
            / "manifest.json"
        )
        assert expected.exists()


class TestJsonFormat:
    def test_tour_manifest_is_object_not_array(self, tmp_config):
        repo = JsonTourManifestRepository(tmp_config.workspace_root)
        repo.save(make_tour())
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "maps-1"
            / "presentations"
            / "investor"
            / "manifest.json"
        )
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)


class TestMissingFileResilience:
    def test_mkdir_p_on_deep_save(self, tmp_config):
        """Saving to a deeply nested path creates all intermediates."""
        repo = JsonTourManifestRepository(tmp_config.workspace_root)
        repo.save(make_tour())
        path = (
            tmp_config.workspace_root
            / "holloway-group"
            / "engagements"
            / ENGAGEMENT
            / "maps-1"
            / "presentations"
            / "investor"
            / "manifest.json"
        )
        assert path.exists()
