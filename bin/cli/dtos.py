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
    "RegisterProspectusRequest",
    "RegisterProspectusResponse",
    "RegisterResearchTopicRequest",
    "RegisterResearchTopicResponse",
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
    "SourceInfo",
    "ListSourcesRequest",
    "ListSourcesResponse",
    "ShowSourceRequest",
    "ShowSourceResponse",
    "UpdateProspectusRequest",
    "UpdateProspectusResponse",
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
    is_implemented: bool
    problem_domain: str
    deliverables: list[str]
    value_proposition: str
    classification: list[str]
    evidence: list[str]
    stages: list[SkillsetStageInfo]


class ListSkillsetsRequest(BaseModel):
    """List registered skillsets, optionally filtered by engagement."""

    client: str | None = Field(default=None, description="Client slug.")
    engagement: str | None = Field(default=None, description="Engagement slug.")

    implemented: str | None = Field(
        default=None,
        description="Filter by implementation status: 'true', 'false', or omit for all.",
    )


class ListSkillsetsResponse(BaseModel):
    skillsets: list[SkillsetInfo]


class ShowSkillsetRequest(BaseModel):
    """Show details of a registered skillset."""

    name: str = Field(description="Skillset name.")


class ShowSkillsetResponse(BaseModel):
    skillset: SkillsetInfo


# ---------------------------------------------------------------------------
# Source — stays here (cross-BC, lists installed sources)
# ---------------------------------------------------------------------------


class SourceInfo(BaseModel):
    slug: str
    source_type: str
    skillset_names: list[str]


class ListSourcesRequest(BaseModel):
    """List all installed skillset sources."""


class ListSourcesResponse(BaseModel):
    sources: list[SourceInfo]


class ShowSourceRequest(BaseModel):
    """Show details of an installed source."""

    slug: str = Field(description="Source slug.")


class ShowSourceResponse(BaseModel):
    source: SourceInfo


# ---------------------------------------------------------------------------
# Prospectus — register and update unimplemented skillsets
# ---------------------------------------------------------------------------


class RegisterProspectusRequest(BaseModel):
    """Register a new skillset prospectus."""

    name: str = Field(description="Skillset name (kebab-case).")
    display_name: str = Field(description="Human-readable display name.")
    description: str = Field(description="Short description of the methodology.")
    slug_pattern: str = Field(description="Project slug pattern with {n} placeholder.")
    problem_domain: str = Field(default="", description="Problem domain.")
    value_proposition: str = Field(default="", description="Value proposition.")
    deliverables: str = Field(
        default="",
        description="Comma-separated list of deliverables.",
    )
    classification: str = Field(
        default="",
        description="Comma-separated classification tags.",
    )
    evidence: str = Field(
        default="",
        description="Comma-separated evidence references.",
    )


class RegisterProspectusResponse(BaseModel):
    name: str
    init_path: str


class UpdateProspectusRequest(BaseModel):
    """Update an existing skillset prospectus."""

    name: str = Field(description="Skillset name to update.")
    display_name: str | None = Field(default=None, description="New display name.")
    description: str | None = Field(default=None, description="New description.")
    slug_pattern: str | None = Field(default=None, description="New slug pattern.")
    problem_domain: str | None = Field(default=None, description="New problem domain.")
    value_proposition: str | None = Field(
        default=None, description="New value proposition."
    )
    deliverables: str | None = Field(
        default=None,
        description="Comma-separated list of deliverables (replaces existing).",
    )
    classification: str | None = Field(
        default=None,
        description="Comma-separated classification tags (replaces existing).",
    )
    evidence: str | None = Field(
        default=None,
        description="Comma-separated evidence references (replaces existing).",
    )


class UpdateProspectusResponse(BaseModel):
    name: str
    init_path: str
