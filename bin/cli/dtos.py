"""Request and response DTOs for accounting usecases.

DTOs are the contract between the application layer (CLI) and the
usecases. Each usecase has a FooRequest and FooResponse pair.
These are pure data structures with no behaviour.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from practice.entities import Confidence, ProjectStatus

if TYPE_CHECKING:
    from practice.entities import DecisionEntry, Engagement, Project, ResearchTopic


# ---------------------------------------------------------------------------
# Shared sub-DTOs
# ---------------------------------------------------------------------------


class ProjectInfo(BaseModel):
    """Project summary returned by list and get queries."""

    slug: str
    engagement: str
    skillset: str
    status: str
    created: date
    notes: str

    @classmethod
    def from_entity(cls, p: Project) -> ProjectInfo:
        return cls(
            slug=p.slug,
            engagement=p.engagement,
            skillset=p.skillset,
            status=p.status.value,
            created=p.created,
            notes=p.notes,
        )


class DecisionInfo(BaseModel):
    """Decision entry returned by list queries."""

    id: str
    date: date
    title: str
    fields: dict[str, str]

    @classmethod
    def from_entity(cls, d: DecisionEntry) -> DecisionInfo:
        return cls(id=d.id, date=d.date, title=d.title, fields=d.fields)


class ResearchTopicInfo(BaseModel):
    """Research topic returned by list queries."""

    filename: str
    topic: str
    date: date
    confidence: str

    @classmethod
    def from_entity(cls, t: ResearchTopic) -> ResearchTopicInfo:
        return cls(
            filename=t.filename,
            topic=t.topic,
            date=t.date,
            confidence=t.confidence.value,
        )


class EngagementInfo(BaseModel):
    """Engagement summary returned by list and get queries."""

    slug: str
    client: str
    status: str
    allowed_sources: list[str]
    created: date
    notes: str

    @classmethod
    def from_entity(cls, e: Engagement) -> EngagementInfo:
        return cls(
            slug=e.slug,
            client=e.client,
            status=e.status.value,
            allowed_sources=e.allowed_sources,
            created=e.created,
            notes=e.notes,
        )


class StageProgress(BaseModel):
    """Progress for one pipeline stage."""

    order: int
    skill: str
    description: str
    completed: bool


# ---------------------------------------------------------------------------
# 1. InitializeWorkspace
# ---------------------------------------------------------------------------


class InitializeWorkspaceRequest(BaseModel):
    """Create a new client workspace with empty registries."""

    client: str = Field(description="Client slug.")


class InitializeWorkspaceResponse(BaseModel):
    client: str


# ---------------------------------------------------------------------------
# 2. RegisterProject
# ---------------------------------------------------------------------------


class RegisterProjectRequest(BaseModel):
    """Register a new project, its decision log, and engagement entry."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    slug: str = Field(description="Project slug (e.g. maps-1).")
    skillset: str = Field(description="Skillset name (must match a manifest).")
    scope: str = Field(description="Project scope description.")
    notes: str = Field(default="", description="Additional notes.")


class RegisterProjectResponse(BaseModel):
    client: str
    engagement: str
    slug: str
    skillset: str


# ---------------------------------------------------------------------------
# 3. UpdateProjectStatus
# ---------------------------------------------------------------------------


class UpdateProjectStatusRequest(BaseModel):
    """Transition a project to the next lifecycle status."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    project_slug: str = Field(
        description="Project slug.",
        json_schema_extra={"cli_name": "project"},
    )
    status: str = Field(
        description="New status.",
        json_schema_extra={"choices": ProjectStatus},
    )


class UpdateProjectStatusResponse(BaseModel):
    client: str
    project_slug: str
    status: str


# ---------------------------------------------------------------------------
# 4. RecordDecision
# ---------------------------------------------------------------------------


class RecordDecisionRequest(BaseModel):
    """Record a timestamped decision against a project."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    project_slug: str = Field(
        description="Project slug.",
        json_schema_extra={"cli_name": "project"},
    )
    title: str = Field(description="Decision title.")
    fields: dict[str, str] = Field(
        default_factory=dict,
        description="Key=Value pair (repeatable).",
        json_schema_extra={"cli_name": "field"},
    )


class RecordDecisionResponse(BaseModel):
    client: str
    project_slug: str
    decision_id: str
    title: str


# ---------------------------------------------------------------------------
# 5. AddEngagementEntry
# ---------------------------------------------------------------------------


class AddEngagementEntryRequest(BaseModel):
    """Add a timestamped entry to the client engagement log."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    title: str = Field(description="Entry title.")
    fields: dict[str, str] = Field(
        default_factory=dict,
        description="Key=Value pair (repeatable).",
        json_schema_extra={"cli_name": "field"},
    )


class AddEngagementEntryResponse(BaseModel):
    client: str
    entry_id: str
    title: str


# ---------------------------------------------------------------------------
# 6. RegisterResearchTopic
# ---------------------------------------------------------------------------


class RegisterResearchTopicRequest(BaseModel):
    """Register a research topic in the client manifest."""

    client: str = Field(description="Client slug.")
    topic: str = Field(description="Topic name.")
    filename: str = Field(description="Research file name.")
    confidence: str = Field(
        description="Confidence level.",
        json_schema_extra={"choices": Confidence},
    )


class RegisterResearchTopicResponse(BaseModel):
    client: str
    filename: str
    topic: str


# ---------------------------------------------------------------------------
# 7. ListProjects
# ---------------------------------------------------------------------------


class ListProjectsRequest(BaseModel):
    """List projects for a client engagement, with optional filters."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    skillset: str | None = Field(default=None, description="Filter by skillset.")
    status: str | None = Field(
        default=None,
        description="Filter by status.",
        json_schema_extra={"choices": ProjectStatus},
    )


class ListProjectsResponse(BaseModel):
    client: str
    projects: list[ProjectInfo]


# ---------------------------------------------------------------------------
# 8. GetProject
# ---------------------------------------------------------------------------


class GetProjectRequest(BaseModel):
    """Retrieve a single project by client, engagement, and slug."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    slug: str = Field(description="Project slug.")


class GetProjectResponse(BaseModel):
    client: str
    slug: str
    project: ProjectInfo


# ---------------------------------------------------------------------------
# 9. GetProjectProgress
# ---------------------------------------------------------------------------


class GetProjectProgressRequest(BaseModel):
    """Show pipeline progress for a project."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    project_slug: str = Field(
        description="Project slug.",
        json_schema_extra={"cli_name": "project"},
    )


class GetProjectProgressResponse(BaseModel):
    client: str
    project_slug: str
    skillset: str
    stages: list[StageProgress]
    current_stage: str | None
    next_prerequisite: str | None


# ---------------------------------------------------------------------------
# 10. ListDecisions
# ---------------------------------------------------------------------------


class ListDecisionsRequest(BaseModel):
    """List all decisions recorded for a project."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    project_slug: str = Field(
        description="Project slug.",
        json_schema_extra={"cli_name": "project"},
    )


class ListDecisionsResponse(BaseModel):
    client: str
    project_slug: str
    decisions: list[DecisionInfo]


# ---------------------------------------------------------------------------
# 11. ListResearchTopics
# ---------------------------------------------------------------------------


class ListResearchTopicsRequest(BaseModel):
    """List all research topics for a client."""

    client: str = Field(description="Client slug.")


class ListResearchTopicsResponse(BaseModel):
    client: str
    topics: list[ResearchTopicInfo]


# ---------------------------------------------------------------------------
# 12. CreateEngagement
# ---------------------------------------------------------------------------


class CreateEngagementRequest(BaseModel):
    """Create a new engagement for a client."""

    client: str = Field(description="Client slug.")
    slug: str = Field(description="Engagement slug.")
    notes: str = Field(default="", description="Additional notes.")


class CreateEngagementResponse(BaseModel):
    client: str
    slug: str
    status: str


# ---------------------------------------------------------------------------
# 13. GetEngagement
# ---------------------------------------------------------------------------


class GetEngagementRequest(BaseModel):
    """Retrieve a single engagement by client and slug."""

    client: str = Field(description="Client slug.")
    slug: str = Field(description="Engagement slug.")


class GetEngagementResponse(BaseModel):
    client: str
    slug: str
    engagement: EngagementInfo


# ---------------------------------------------------------------------------
# 14. ListEngagements
# ---------------------------------------------------------------------------


class ListEngagementsRequest(BaseModel):
    """List all engagements for a client."""

    client: str = Field(description="Client slug.")


class ListEngagementsResponse(BaseModel):
    client: str
    engagements: list[EngagementInfo]


# ---------------------------------------------------------------------------
# 15. AddEngagementSource
# ---------------------------------------------------------------------------


class AddEngagementSourceRequest(BaseModel):
    """Add a skillset source to an engagement's allowlist."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    source: str = Field(description="Source slug to add.")


class AddEngagementSourceResponse(BaseModel):
    client: str
    engagement: str
    source: str
    allowed_sources: list[str]


# ---------------------------------------------------------------------------
# 16. RemoveEngagementSource
# ---------------------------------------------------------------------------


class RemoveEngagementSourceRequest(BaseModel):
    """Remove a skillset source from an engagement's allowlist."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")
    source: str = Field(description="Source slug to remove.")


class RemoveEngagementSourceResponse(BaseModel):
    client: str
    engagement: str
    source: str
    allowed_sources: list[str]


# ---------------------------------------------------------------------------
# 17. EngagementStatus
# ---------------------------------------------------------------------------


class EngagementStatusRequest(BaseModel):
    """Derive engagement state from gate artifacts."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")


class EngagementStatusResponse(BaseModel):
    dashboard: "EngagementDashboardInfo"
    nudges: list[str] = []


class EngagementDashboardInfo(BaseModel):
    """Flattened dashboard for CLI rendering."""

    engagement_slug: str
    status: str
    projects: list["ProjectPositionInfo"]


class ProjectPositionInfo(BaseModel):
    """Pipeline position for one project."""

    project_slug: str
    skillset: str
    current_stage: int
    total_stages: int
    completed_gates: list[str]
    next_gate: str | None


# ---------------------------------------------------------------------------
# 18. NextAction
# ---------------------------------------------------------------------------


class NextActionRequest(BaseModel):
    """Determine the recommended next skill execution."""

    client: str = Field(description="Client slug.")
    engagement: str = Field(description="Engagement slug.")


class NextActionResponse(BaseModel):
    skill: str | None
    project_slug: str | None
    reason: str
    nudges: list[str] = []


# ---------------------------------------------------------------------------
# RenderSite (cross-BC orchestration)
# ---------------------------------------------------------------------------


class RenderSiteRequest(BaseModel):
    """Render the deliverable site for a client."""

    client: str = Field(description="Client slug.")


class RenderSiteResponse(BaseModel):
    client: str
    site_path: str
    page_count: int


# ---------------------------------------------------------------------------
# Skillset (cross-BC, aggregates from all BCs)
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
# Source (cross-BC, lists installed sources)
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


# ---------------------------------------------------------------------------
# Profile — named collections of skillsets
# ---------------------------------------------------------------------------


class ProfileInfo(BaseModel):
    name: str
    display_name: str
    description: str
    skillsets: list[str]
    source: str


class ListProfilesRequest(BaseModel):
    """List all registered profiles."""


class ListProfilesResponse(BaseModel):
    profiles: list[ProfileInfo]


class ShowProfileRequest(BaseModel):
    """Show details of a registered profile."""

    name: str = Field(description="Profile name.")


class ShowProfileResponse(BaseModel):
    profile: ProfileInfo


# ---------------------------------------------------------------------------
# SkillPath — locate a skill directory by name
# ---------------------------------------------------------------------------


class SkillPathRequest(BaseModel):
    """Find the filesystem path to a skill by name."""

    name: str = Field(description="Skill name.")


class SkillPathResponse(BaseModel):
    path: str


# ---------------------------------------------------------------------------
# PackStatus — knowledge pack freshness inspection
# ---------------------------------------------------------------------------


class PackStatusRequest(BaseModel):
    """Show compilation freshness of a knowledge pack."""

    path: str = Field(description="Path to the pack root directory.")


class PackItemInfo(BaseModel):
    name: str
    is_composite: bool
    state: str


class PackStatusResponse(BaseModel):
    pack_root: str
    compilation_state: str
    deep_state: str
    items: list[PackItemInfo]
    children: list["PackStatusResponse"] = []


# ---------------------------------------------------------------------------
# WIP (cross-client work-in-progress)
# ---------------------------------------------------------------------------


class WipProjectInfo(BaseModel):
    """Pipeline position for one in-progress project."""

    client: str
    engagement: str
    project_slug: str
    skillset: str
    current_stage: int
    total_stages: int
    next_skill: str | None
    next_gate: str | None
    blocked: bool
    blocked_reason: str | None


class WipEngagementInfo(BaseModel):
    """One engagement with incomplete projects."""

    client: str
    engagement_slug: str
    status: str
    projects: list[WipProjectInfo]


class GetWipRequest(BaseModel):
    """Show all work in progress across clients."""

    client: str | None = Field(default=None, description="Filter to one client.")


class GetWipResponse(BaseModel):
    engagements: list[WipEngagementInfo]
    nudges: list[str] = []
