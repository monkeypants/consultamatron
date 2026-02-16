"""Request and response DTOs — re-exports from consulting.dtos
and wardley_mapping.dtos, plus site DTOs that remain in bin/cli.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

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
from wardley_mapping.dtos import RegisterTourRequest, RegisterTourResponse

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
# RenderSite — stays here (cross-BC orchestration)
# ---------------------------------------------------------------------------


class RenderSiteRequest(BaseModel):
    """Render the deliverable site for a client."""

    client: str = Field(description="Client slug.")


class RenderSiteResponse(BaseModel):
    client: str
    site_path: str
    page_count: int
