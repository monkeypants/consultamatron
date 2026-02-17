"""Discovery types shared across all bounded contexts.

A bounded context declares its pipeline through PipelineStage
entries. These types are the shared vocabulary that the engagement
lifecycle layer uses to discover and drive skillset pipelines.
"""

from __future__ import annotations

from pydantic import BaseModel


class PipelineStage(BaseModel):
    """One stage in a skillset's pipeline."""

    order: int
    skill: str
    prerequisite_gate: str
    produces_gate: str
    description: str
    consumes: list[str] = []
