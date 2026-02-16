"""Wardley Mapping usecase implementations."""

from __future__ import annotations

from practice.exceptions import NotFoundError
from wardley_mapping.dtos import RegisterTourRequest, RegisterTourResponse
from wardley_mapping.types import ProjectLookup, TourManifest, TourManifestRepository


class RegisterTourUseCase:
    """Validate project existence then persist a tour manifest.

    Replaces any existing tour with the same name (upsert semantics).
    """

    def __init__(
        self,
        projects: ProjectLookup,
        tours: TourManifestRepository,
    ) -> None:
        self._projects = projects
        self._tours = tours

    def execute(self, request: RegisterTourRequest) -> RegisterTourResponse:
        if (
            self._projects.get(request.client, request.engagement, request.project_slug)
            is None
        ):
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        self._tours.save(
            TourManifest(
                name=request.name,
                client=request.client,
                engagement=request.engagement,
                project_slug=request.project_slug,
                title=request.title,
                stops=request.stops,
            )
        )

        return RegisterTourResponse(
            client=request.client,
            project_slug=request.project_slug,
            name=request.name,
            stop_count=len(request.stops),
        )
