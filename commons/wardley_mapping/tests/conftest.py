"""Fixtures and builders for wardley_mapping tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from bin.cli.config import Config
from practice.entities import Project, ProjectStatus
from wardley_mapping.infrastructure import JsonTourManifestRepository
from wardley_mapping.types import TourManifest, TourStop

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

DEFAULT_CLIENT = "holloway-group"
DEFAULT_PROJECT = "maps-1"
DEFAULT_ENGAGEMENT = "strat-1"
DEFAULT_DATE = date(2025, 6, 1)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_config(tmp_path):
    """Config with real repo_root for BC discovery, temp workspace for isolation."""
    return Config(
        repo_root=_REPO_ROOT,
        workspace_root=tmp_path / "clients",
        skillsets_root=tmp_path / "skillsets",
    )


@pytest.fixture(params=["json"])
def tour_repo(request, tmp_config):
    if request.param == "json":
        return JsonTourManifestRepository(tmp_config.workspace_root)


# ---------------------------------------------------------------------------
# Entity builders
# ---------------------------------------------------------------------------


def make_tour_stop(**overrides) -> TourStop:
    defaults = dict(
        order="1",
        title="Overview",
        atlas_source="atlas/overview/",
    )
    return TourStop(**(defaults | overrides))


def make_tour(**overrides) -> TourManifest:
    defaults = dict(
        name="investor",
        client=DEFAULT_CLIENT,
        engagement=DEFAULT_ENGAGEMENT,
        project_slug=DEFAULT_PROJECT,
        title="Investor Tour",
        stops=[make_tour_stop()],
    )
    return TourManifest(**(defaults | overrides))


def make_project(**overrides) -> Project:
    defaults = dict(
        slug=DEFAULT_PROJECT,
        client=DEFAULT_CLIENT,
        engagement=DEFAULT_ENGAGEMENT,
        skillset="wardley-mapping",
        status=ProjectStatus.PLANNING,
        created=DEFAULT_DATE,
    )
    return Project(**(defaults | overrides))
