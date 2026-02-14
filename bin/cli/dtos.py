"""Request and response DTOs for accounting usecases.

DTOs are the contract between the application layer (CLI) and the
usecases. Each usecase has a FooRequest and FooResponse pair.
These are pure data structures with no behaviour.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel

from bin.cli.entities import TourStop

if TYPE_CHECKING:
    from bin.cli.entities import DecisionEntry, Project, ResearchTopic


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
    client: str


class InitializeWorkspaceResponse(BaseModel):
    client: str


# ---------------------------------------------------------------------------
# 2. RegisterProject
# ---------------------------------------------------------------------------


class RegisterProjectRequest(BaseModel):
    client: str
    slug: str
    skillset: str
    scope: str
    notes: str = ""


class RegisterProjectResponse(BaseModel):
    client: str
    slug: str
    skillset: str


# ---------------------------------------------------------------------------
# 3. UpdateProjectStatus
# ---------------------------------------------------------------------------


class UpdateProjectStatusRequest(BaseModel):
    client: str
    project_slug: str
    status: str


class UpdateProjectStatusResponse(BaseModel):
    client: str
    project_slug: str
    status: str


# ---------------------------------------------------------------------------
# 4. RecordDecision
# ---------------------------------------------------------------------------


class RecordDecisionRequest(BaseModel):
    client: str
    project_slug: str
    title: str
    fields: dict[str, str]


class RecordDecisionResponse(BaseModel):
    client: str
    project_slug: str
    decision_id: str


# ---------------------------------------------------------------------------
# 5. AddEngagementEntry
# ---------------------------------------------------------------------------


class AddEngagementEntryRequest(BaseModel):
    client: str
    title: str
    fields: dict[str, str] = {}


class AddEngagementEntryResponse(BaseModel):
    client: str
    entry_id: str


# ---------------------------------------------------------------------------
# 6. RegisterResearchTopic
# ---------------------------------------------------------------------------


class RegisterResearchTopicRequest(BaseModel):
    client: str
    topic: str
    filename: str
    confidence: str


class RegisterResearchTopicResponse(BaseModel):
    client: str
    filename: str


# ---------------------------------------------------------------------------
# 7. RegisterTour
# ---------------------------------------------------------------------------


class RegisterTourRequest(BaseModel):
    client: str
    project_slug: str
    name: str
    title: str
    stops: list[TourStop]


class RegisterTourResponse(BaseModel):
    client: str
    project_slug: str
    name: str
    stop_count: int


# ---------------------------------------------------------------------------
# 8. ListProjects
# ---------------------------------------------------------------------------


class ListProjectsRequest(BaseModel):
    client: str
    skillset: str | None = None
    status: str | None = None


class ListProjectsResponse(BaseModel):
    client: str
    projects: list[ProjectInfo]


# ---------------------------------------------------------------------------
# 9. GetProject
# ---------------------------------------------------------------------------


class GetProjectRequest(BaseModel):
    client: str
    slug: str


class GetProjectResponse(BaseModel):
    client: str
    project: ProjectInfo | None


# ---------------------------------------------------------------------------
# 10. GetProjectProgress
# ---------------------------------------------------------------------------


class GetProjectProgressRequest(BaseModel):
    client: str
    project_slug: str


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
    client: str
    project_slug: str


class ListDecisionsResponse(BaseModel):
    client: str
    project_slug: str
    decisions: list[DecisionInfo]


# ---------------------------------------------------------------------------
# 12. ListResearchTopics
# ---------------------------------------------------------------------------


class ListResearchTopicsRequest(BaseModel):
    client: str


class ListResearchTopicsResponse(BaseModel):
    client: str
    topics: list[ResearchTopicInfo]


# ---------------------------------------------------------------------------
# 13. RenderSite
# ---------------------------------------------------------------------------


class RenderSiteRequest(BaseModel):
    client: str


class RenderSiteResponse(BaseModel):
    client: str
    site_path: str
    page_count: int
