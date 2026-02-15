"""Lifecycle entities for consulting practice accounting.

Shared domain entities (Project, ProjectStatus, Confidence,
ResearchTopic, Skillset) live in practice.entities — they appear
in protocol signatures that cross bounded context boundaries.

This module holds lifecycle-only entities that will move to the
consulting bounded context in a future PR.

Domain exceptions live in practice.exceptions.
Deliverable content entities live in practice.content.
PipelineStage lives in practice.discovery.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


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
