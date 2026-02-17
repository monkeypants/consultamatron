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

from pydantic import BaseModel, Field

from practice.discovery import PipelineStage


# ---------------------------------------------------------------------------
# Skillset (discovery vocabulary — every BC declares these)
# ---------------------------------------------------------------------------


class Skillset(BaseModel):
    """A consulting product line declared in bounded context modules.

    A Skillset with a populated pipeline is implemented — projects can
    be created and driven through the pipeline. A Skillset with an empty
    pipeline is a prospectus — it describes a methodology that is not yet
    operational.
    """

    name: str
    display_name: str
    description: str
    pipeline: list[PipelineStage] = []
    slug_pattern: str
    problem_domain: str = ""
    deliverables: list[str] = []
    value_proposition: str = ""
    classification: list[str] = []
    evidence: list[str] = []

    @property
    def is_implemented(self) -> bool:
        """True when the pipeline has at least one stage."""
        return len(self.pipeline) > 0


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
    engagement: str
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


# ---------------------------------------------------------------------------
# Engagement (unit of contracted work with a client)
# ---------------------------------------------------------------------------


class EngagementStatus(str, Enum):
    """Lifecycle phase of a consulting engagement.

    The lifecycle is linear:
    planning → active → review → closed.
    """

    PLANNING = "planning"
    ACTIVE = "active"
    REVIEW = "review"
    CLOSED = "closed"

    def next(self) -> EngagementStatus | None:
        """Return the next lifecycle phase, or None if terminal."""
        members = list(EngagementStatus)
        idx = members.index(self)
        return members[idx + 1] if idx + 1 < len(members) else None


class Engagement(BaseModel):
    """A unit of contracted work with a client.

    Engagements scope which skillset sources are permitted and
    contain projects. Research stays client-scoped.
    """

    slug: str
    client: str
    status: EngagementStatus
    allowed_sources: list[str] = Field(default_factory=lambda: ["commons", "personal"])
    created: date
    notes: str = ""


# ---------------------------------------------------------------------------
# SkillsetSource (provenance of skillset definitions)
# ---------------------------------------------------------------------------


class SourceType(str, Enum):
    """Where a skillset comes from."""

    COMMONS = "commons"
    PERSONAL = "personal"
    PARTNERSHIP = "partnership"


class SkillsetSource(BaseModel):
    """A source of skillset definitions."""

    slug: str
    source_type: SourceType
    skillset_names: list[str]


# ---------------------------------------------------------------------------
# Profile (named collection of skillsets for an activity type)
# ---------------------------------------------------------------------------


class Profile(BaseModel):
    """A named collection of skillsets for a type of activity."""

    name: str
    display_name: str
    description: str
    skillsets: list[str]


# ---------------------------------------------------------------------------
# Engagement protocol value objects (computed, no identity, no persistence)
# ---------------------------------------------------------------------------


class ProjectPipelinePosition(BaseModel):
    """Derived position of one project within its skillset pipeline."""

    project_slug: str
    skillset: str
    current_stage: int
    total_stages: int
    completed_gates: list[str]
    next_gate: str | None


class EngagementDashboard(BaseModel):
    """Aggregate engagement state derived from gate artifacts."""

    engagement_slug: str
    status: str
    projects: list[ProjectPipelinePosition]


class NextAction(BaseModel):
    """Recommended next skill execution within an engagement."""

    skill: str
    project_slug: str
    reason: str
    prerequisite_exists: bool
