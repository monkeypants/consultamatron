"""Domain entities for consulting practice accounting operations.

Entities carry identity and scoping context so that repository
save(entity) calls are self-contained. Skillsets are first-class
entities discovered from manifests at runtime, not hardcoded enums.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Domain exceptions
# ---------------------------------------------------------------------------


class DomainError(Exception):
    """Base for all domain-level errors raised by usecases."""


class NotFoundError(DomainError):
    """A required entity does not exist."""


class DuplicateError(DomainError):
    """An entity with the same identity already exists."""


class InvalidTransitionError(DomainError):
    """A requested state transition violates domain rules."""


# ---------------------------------------------------------------------------
# Skillset entities (discovered from skillsets/*.md manifests)
# ---------------------------------------------------------------------------


class PipelineStage(BaseModel):
    """One stage in a skillset's pipeline."""

    order: int
    skill: str
    prerequisite_gate: str
    produces_gate: str
    description: str


class Skillset(BaseModel):
    """A consulting product line. Discovered from skillsets/*.md."""

    name: str
    display_name: str
    description: str
    pipeline: list[PipelineStage]
    slug_pattern: str
    atlas_skills: list[str] = []
    tour_skills: list[str] = []


# ---------------------------------------------------------------------------
# Practice entities
# ---------------------------------------------------------------------------


class ProjectStatus(str, Enum):
    """Lifecycle phase of a consulting project.

    The lifecycle is linear: planned → active → complete → reviewed.
    This is the envelope the work lives in, not the work graph itself.
    """

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETE = "complete"
    REVIEWED = "reviewed"

    def next(self) -> ProjectStatus | None:
        """Return the next lifecycle phase, or None if terminal."""
        members = list(ProjectStatus)
        idx = members.index(self)
        return members[idx + 1] if idx + 1 < len(members) else None


class Confidence(str, Enum):
    HIGH = "High"
    MEDIUM_HIGH = "Medium-High"
    MEDIUM = "Medium"
    LOW = "Low"


class Project(BaseModel):
    """A single consulting project within a client engagement."""

    slug: str
    client: str
    skillset: str
    status: ProjectStatus
    created: date
    notes: str = ""


class DecisionEntry(BaseModel):
    """A timestamped decision recorded during a project.

    Immutable — created once, never updated or deleted.
    The date field is for human display; timestamp is for ordering.
    """

    id: str
    client: str
    project_slug: str
    date: date
    timestamp: datetime
    title: str
    fields: dict[str, str]


class EngagementEntry(BaseModel):
    """A timestamped entry in the client engagement log.

    Immutable — created once, never updated or deleted.
    The date field is for human display; timestamp is for ordering.
    """

    id: str
    client: str
    date: date
    timestamp: datetime
    title: str
    fields: dict[str, str]


class ResearchTopic(BaseModel):
    """A completed research topic in the client's research manifest."""

    filename: str
    client: str
    topic: str
    date: date
    confidence: Confidence


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
    project_slug: str
    title: str
    stops: list[TourStop]


# ---------------------------------------------------------------------------
# Deliverable content entities — structure of what gets delivered,
# independent of rendering format.
# ---------------------------------------------------------------------------


class Figure(BaseModel):
    """A visual artifact (SVG content) with optional caption."""

    caption: str
    svg_content: str


class ContentPage(BaseModel):
    """A single page of prose content with optional figures."""

    title: str
    slug: str
    body_md: str
    figures: list[Figure] = []


class PageGroup(BaseModel):
    """A labeled collection of pages (e.g. atlas category)."""

    label: str
    slug: str
    pages: list[ContentPage]


class TourStopContent(BaseModel):
    """One assembled tour stop with figures and analysis."""

    title: str
    level: str
    is_header: bool
    figures: list[Figure]
    analysis_md: str


class TourGroupContent(BaseModel):
    """A group of related stops plus transition prose."""

    stops: list[TourStopContent]
    transition_md: str


class TourPageContent(BaseModel):
    """A complete tour presentation, assembled from workspace files."""

    title: str
    slug: str
    description: str
    opening_md: str
    groups: list[TourGroupContent]


class ProjectSection(BaseModel):
    """A major section within a project."""

    label: str
    slug: str
    description: str = ""
    pages: list[ContentPage] = []
    groups: list[PageGroup] = []
    tours: list[TourPageContent] = []


class ProjectContribution(BaseModel):
    """Everything a project contributes to the client deliverable.

    Assembled by a ProjectPresenter from workspace files. Contains
    enough structure for any renderer to produce output without
    knowing the skillset.
    """

    slug: str
    title: str
    skillset: str
    status: str
    hero_figure: Figure | None = None
    overview_md: str
    sections: list[ProjectSection] = []
