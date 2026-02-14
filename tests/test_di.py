"""DI container and config tests.

Config.from_repo_root produces correct paths. The container
wires repos that actually work against the filesystem. Protocol
conformance and usecase wiring are tested implicitly by the
usecase and CLI test suites.
"""

from __future__ import annotations

from pathlib import Path

from bin.cli.config import Config


class TestConfig:
    def test_from_repo_root(self):
        config = Config.from_repo_root(Path("/repo"))
        assert config.repo_root == Path("/repo")
        assert config.workspace_root == Path("/repo/clients")
        assert config.skillsets_root == Path("/repo/skillsets")

    def test_frozen(self):
        config = Config.from_repo_root(Path("/repo"))
        try:
            config.workspace_root = Path("/other")  # type: ignore[misc]
            assert False, "Should have raised"
        except AttributeError:
            pass


class TestContainerUsable:
    """Repos from the container work against the temp workspace."""

    def test_round_trip_through_container(self, container):
        from .conftest import make_project

        container.projects.save(make_project())
        got = container.projects.get("holloway-group", "maps-1")
        assert got is not None
        assert got.slug == "maps-1"
