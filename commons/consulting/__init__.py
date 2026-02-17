"""Consulting bounded context — engagement lifecycle."""

from __future__ import annotations

from practice.discovery import PipelineStage
from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from consulting.presenter import ConsultingProjectPresenter

    return ConsultingProjectPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("consulting", _create_presenter)

SKILLSETS: list[Skillset] = [
    Skillset(
        name="consulting",
        display_name="Consulting",
        description=(
            "Core engagement lifecycle: research the organisation, plan"
            " engagements, execute skillset projects, and review outcomes."
        ),
        slug_pattern="consult-{n}",
        classification=["lifecycle", "engagement-management"],
        pipeline=[
            PipelineStage(
                order=1,
                skill="org-research",
                prerequisite_gate="",
                produces_gate="resources/index.md",
                description="Stage 1: Organisation research complete",
            ),
            PipelineStage(
                order=2,
                skill="engage",
                prerequisite_gate="resources/index.md",
                produces_gate="engagements/index.json",
                description="Stage 2: Engagement planned",
                consumes=["topics", "confidence"],
            ),
            PipelineStage(
                order=3,
                skill="review",
                prerequisite_gate="engagements/index.json",
                produces_gate="review/review.agreed.md",
                description="Stage 3: Post-implementation review agreed",
                consumes=["projects", "decisions"],
            ),
        ],
    ),
]
