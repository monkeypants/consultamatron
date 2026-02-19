"""Wardley Mapping domain types.

Types specific to the Wardley Mapping skillset that do not belong in
the generic practice layer.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel


class TourStop(BaseModel):
    """One stop in a curated presentation tour."""

    order: str
    title: str
    atlas_source: str
    map_file: str = "map.svg"
    analysis_file: str = "analysis.md"


class TourManifest(BaseModel):
    """A complete tour definition for a specific audience."""

    name: str
    client: str
    engagement: str
    project_slug: str
    title: str
    stops: list[TourStop]


@runtime_checkable
class TourManifestRepository(Protocol):
    """Repository for audience tour manifests.

    Tour manifests use replace semantics — each save overwrites
    the entire manifest. The name is the natural key, scoped to
    a client, engagement, and project.
    """

    def get(
        self,
        client: str,
        engagement: str,
        project_slug: str,
        tour_name: str,
    ) -> TourManifest | None:
        """Retrieve a tour manifest."""
        ...

    def list_all(
        self, client: str, engagement: str, project_slug: str
    ) -> list[TourManifest]:
        """List all tour manifests for a project."""
        ...

    def save(self, manifest: TourManifest) -> None:
        """Save a tour manifest (creates or replaces)."""
        ...


@runtime_checkable
class ProjectLookup(Protocol):
    """Minimal project existence check.

    ProjectRepository already satisfies this shape, so DI passes it
    through with no adapter.
    """

    def get(self, client: str, engagement: str, slug: str) -> object | None:
        """Return something truthy if the project exists, None otherwise."""
        ...
