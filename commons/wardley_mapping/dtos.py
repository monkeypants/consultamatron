"""Request and response DTOs for Wardley Mapping usecases."""

from __future__ import annotations

from pydantic import BaseModel, Field

from wardley_mapping.types import TourStop


class RegisterTourRequest(BaseModel):
    """Register or replace a presentation tour for a project."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    project_slug: str = Field(
        description="Project slug.",
        json_schema_extra={"cli_name": "project"},
    )
    name: str = Field(description="Tour name (e.g. investor).")
    title: str = Field(description="Tour display title.")
    stops: list[TourStop] = Field(description="JSON array of tour stops.")


class RegisterTourResponse(BaseModel):
    client: str
    project_slug: str
    name: str
    stop_count: int
