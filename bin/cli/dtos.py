"""Request and response DTOs for accounting usecases.

DTOs are the contract between the application layer (CLI) and the
usecases. Each usecase has a FooRequest and FooResponse pair.
These are pure data structures with no behaviour.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from bin.cli.wm_types import TourStop
from practice.entities import Confidence, ProjectStatus

if TYPE_CHECKING:
    from bin.cli.entities import DecisionEntry
    from practice.entities import Project, ResearchTopic


# ---------------------------------------------------------------------------
# Shared sub-DTOs
# ---------------------------------------------------------------------------


class ProjectInfo(BaseModel):
    """Project summary returned by list and get queries."""

    slug: str
    skillset: str
    status: str
    created: date
    notes: str

    @classmethod
    def from_entity(cls, p: Project) -> ProjectInfo:
        return cls(
            slug=p.slug,
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
    """Register a new project, its decision log, and engagement entry.

    Creates the project in the registry, seeds a "Project created"
    decision, and logs an engagement entry.
    """

    client: str = Field(description="Client slug.")
    slug: str = Field(description="Project slug (e.g. maps-1).")
    skillset: str = Field(description="Skillset name (must match a manifest).")
    scope: str = Field(description="Project scope description.")
    notes: str = Field(default="", description="Additional notes.")


class RegisterProjectResponse(BaseModel):
    client: str
    slug: str
    skillset: str


# ---------------------------------------------------------------------------
# 3. UpdateProjectStatus
# ---------------------------------------------------------------------------


class UpdateProjectStatusRequest(BaseModel):
    """Transition a project to the next lifecycle status."""

    client: str = Field(description="Client slug.")
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
# 7. RegisterTour
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
# 8. ListProjects
# ---------------------------------------------------------------------------


class ListProjectsRequest(BaseModel):
    """List projects for a client, with optional filters."""

    client: str = Field(description="Client slug.")
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
# 9. GetProject
# ---------------------------------------------------------------------------


class GetProjectRequest(BaseModel):
    """Retrieve a single project by client and slug."""

    client: str = Field(description="Client slug.")
    slug: str = Field(description="Project slug.")


class GetProjectResponse(BaseModel):
    client: str
    slug: str
    project: ProjectInfo | None


# ---------------------------------------------------------------------------
# 10. GetProjectProgress
# ---------------------------------------------------------------------------


class GetProjectProgressRequest(BaseModel):
    """Show pipeline progress for a project."""

    client: str = Field(description="Client slug.")
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
# 11. ListDecisions
# ---------------------------------------------------------------------------


class ListDecisionsRequest(BaseModel):
    """List all decisions recorded for a project."""

    client: str = Field(description="Client slug.")
    project_slug: str = Field(
        description="Project slug.",
        json_schema_extra={"cli_name": "project"},
    )


class ListDecisionsResponse(BaseModel):
    client: str
    project_slug: str
    decisions: list[DecisionInfo]


# ---------------------------------------------------------------------------
# 12. ListResearchTopics
# ---------------------------------------------------------------------------


class ListResearchTopicsRequest(BaseModel):
    """List all research topics for a client."""

    client: str = Field(description="Client slug.")


class ListResearchTopicsResponse(BaseModel):
    client: str
    topics: list[ResearchTopicInfo]


# ---------------------------------------------------------------------------
# 13. RenderSite
# ---------------------------------------------------------------------------


class RenderSiteRequest(BaseModel):
    """Render the deliverable site for a client."""

    client: str = Field(description="Client slug.")


class RenderSiteResponse(BaseModel):
    client: str
    site_path: str
    page_count: int
