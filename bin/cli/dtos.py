"""Request and response DTOs — re-exports from consulting.dtos
plus tour and site DTOs that remain in bin/cli.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from bin.cli.wm_types import TourStop
from consulting.dtos import (
    AddEngagementEntryRequest,
    AddEngagementEntryResponse,
    DecisionInfo,
    GetProjectProgressRequest,
    GetProjectProgressResponse,
    GetProjectRequest,
    GetProjectResponse,
    InitializeWorkspaceRequest,
    InitializeWorkspaceResponse,
    ListDecisionsRequest,
    ListDecisionsResponse,
    ListProjectsRequest,
    ListProjectsResponse,
    ListResearchTopicsRequest,
    ListResearchTopicsResponse,
    ProjectInfo,
    RecordDecisionRequest,
    RecordDecisionResponse,
    RegisterProjectRequest,
    RegisterProjectResponse,
    RegisterResearchTopicRequest,
    RegisterResearchTopicResponse,
    ResearchTopicInfo,
    StageProgress,
    UpdateProjectStatusRequest,
    UpdateProjectStatusResponse,
)

__all__ = [
    "AddEngagementEntryRequest",
    "AddEngagementEntryResponse",
    "DecisionInfo",
    "GetProjectProgressRequest",
    "GetProjectProgressResponse",
    "GetProjectRequest",
    "GetProjectResponse",
    "InitializeWorkspaceRequest",
    "InitializeWorkspaceResponse",
    "ListDecisionsRequest",
    "ListDecisionsResponse",
    "ListProjectsRequest",
    "ListProjectsResponse",
    "ListResearchTopicsRequest",
    "ListResearchTopicsResponse",
    "ProjectInfo",
    "RecordDecisionRequest",
    "RecordDecisionResponse",
    "RegisterProjectRequest",
    "RegisterProjectResponse",
    "RegisterResearchTopicRequest",
    "RegisterResearchTopicResponse",
    "RegisterTourRequest",
    "RegisterTourResponse",
    "RenderSiteRequest",
    "RenderSiteResponse",
    "ResearchTopicInfo",
    "StageProgress",
    "UpdateProjectStatusRequest",
    "UpdateProjectStatusResponse",
]


# ---------------------------------------------------------------------------
# RegisterTour — stays here until wardley_mapping BC is extracted
# ---------------------------------------------------------------------------


class RegisterTourRequest(BaseModel):
    """Register or replace a presentation tour for a project."""

    client: str = Field(description="Client slug.")
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


# ---------------------------------------------------------------------------
# RenderSite — stays here (cross-BC orchestration)
# ---------------------------------------------------------------------------


class RenderSiteRequest(BaseModel):
    """Render the deliverable site for a client."""

    client: str = Field(description="Client slug.")


class RenderSiteResponse(BaseModel):
    client: str
    site_path: str
    page_count: int
