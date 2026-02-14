"""Domain entities for consulting practice accounting operations.

Entities carry identity and scoping context so that repository
save(entity) calls are self-contained. Skillsets are first-class
entities discovered from manifests at runtime, not hardcoded enums.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel


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
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETE = "complete"
    REVIEWED = "reviewed"


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
    """

    id: str
    client: str
    project_slug: str
    date: date
    title: str
    fields: dict[str, str]


class EngagementEntry(BaseModel):
    """A timestamped entry in the client engagement log.

    Immutable — created once, never updated or deleted.
    """

    id: str
    client: str
    date: date
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
