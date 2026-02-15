"""Domain entities for consulting practice accounting operations.

Entities carry identity and scoping context so that repository
save(entity) calls are self-contained. Skillsets are first-class
entities discovered from manifests at runtime, not hardcoded enums.

Domain exceptions live in practice.exceptions.
Deliverable content entities live in practice.content.
PipelineStage lives in practice.discovery.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel

from practice.discovery import PipelineStage


# ---------------------------------------------------------------------------
# Skillset entities (discovered from skillsets/*.md manifests)
# ---------------------------------------------------------------------------


class Skillset(BaseModel):
    """A consulting product line. Discovered from skillsets/*.md."""

    name: str
    display_name: str
    description: str
    pipeline: list[PipelineStage]
    slug_pattern: str


# ---------------------------------------------------------------------------
# Practice entities
# ---------------------------------------------------------------------------


class ProjectStatus(str, Enum):
    """Lifecycle phase of a consulting project.

    The lifecycle is linear:
    planning → elaboration → implementation → review → closed.
    Each label describes the project's phase, not the operator's activity.
    """

    PLANNING = "planning"
    ELABORATION = "elaboration"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    CLOSED = "closed"

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
