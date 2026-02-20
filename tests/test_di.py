"""DI container and config tests.

Config.from_repo_root produces correct paths. The container
wires repos that actually work against the filesystem. Protocol
conformance and usecase wiring are tested implicitly by the
usecase and CLI test suites.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bin.cli.config import Config


class TestConfig:
    def test_from_repo_root(self):
        config = Config.from_repo_root(Path("/repo"))
        assert config.repo_root == Path("/repo")
        assert config.workspace_root == Path("/repo/clients")
        assert config.skillsets_root == Path("/repo/skillsets")

    def test_frozen(self):
        config = Config.from_repo_root(Path("/repo"))
        with pytest.raises(AttributeError):
            config.workspace_root = Path("/other")  # type: ignore[misc]


class TestContainerUsable:
    """Repos from the container work against the temp workspace."""

    def test_round_trip_through_container(self, container):
        from .conftest import make_project

        container.projects.save(make_project())
        got = container.projects.get("holloway-group", "strat-1", "maps-1")
        assert got is not None
        assert got.slug == "maps-1"


class TestContainerWiring:
    """Verify DI wiring that cannot be caught by usecase-level tests."""

    def test_pack_nudger_receives_skillset_bc_dirs(self, container):
        """BC discovery populates the nudger's skillset-to-directory mapping."""
        # At least one BC module has SKILLSETS → mapping should be non-empty
        assert container.pack_nudger._skillset_bc_dirs
