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
    "ListSkillsetsRequest",
    "ListSkillsetsResponse",
    "RenderSiteRequest",
    "RenderSiteResponse",
    "ShowSkillsetRequest",
    "ShowSkillsetResponse",
    "SkillsetInfo",
    "SkillsetStageInfo",
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


# ---------------------------------------------------------------------------
# Skillset — stays here (cross-BC, aggregates from all BCs)
# ---------------------------------------------------------------------------


class SkillsetStageInfo(BaseModel):
    order: int
    skill: str
    description: str
    prerequisite_gate: str
    produces_gate: str


class SkillsetInfo(BaseModel):
    name: str
    display_name: str
    description: str
    slug_pattern: str
    stages: list[SkillsetStageInfo]


class ListSkillsetsRequest(BaseModel):
    """List all registered skillsets."""


class ListSkillsetsResponse(BaseModel):
    skillsets: list[SkillsetInfo]


class ShowSkillsetRequest(BaseModel):
    """Show details of a registered skillset."""

    name: str = Field(description="Skillset name.")


class ShowSkillsetResponse(BaseModel):
    skillset: SkillsetInfo
