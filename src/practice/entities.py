"""Shared domain entities referenced by practice-layer protocols.

Entities that appear in protocol signatures in this package are shared
vocabulary across all bounded contexts. They live here — not in any
single BC — so that dependency direction flows downward.

Lifecycle-only entities (DecisionEntry, EngagementEntry) belong in
their bounded context, not here.
"""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel

from practice.discovery import PipelineStage


# ---------------------------------------------------------------------------
# Skillset (discovery vocabulary — every BC declares these)
# ---------------------------------------------------------------------------


class Skillset(BaseModel):
    """A consulting product line. Discovered from skillsets/*.md."""

    name: str
    display_name: str
    description: str
    pipeline: list[PipelineStage]
    slug_pattern: str


# ---------------------------------------------------------------------------
# Project (shared — appears in ProjectPresenter.present() signature)
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


# ---------------------------------------------------------------------------
# ResearchTopic (shared — appears in SiteRenderer.render() signature)
# ---------------------------------------------------------------------------


class ResearchTopic(BaseModel):
    """A completed research topic in the client's research manifest."""

    filename: str
    client: str
    topic: str
    date: date
    confidence: Confidence
