"""Business Model Canvas bounded context."""

from __future__ import annotations

from practice.discovery import PipelineStage
from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from business_model_canvas.presenter import BmcProjectPresenter

    return BmcProjectPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("business-model-canvas", _create_presenter)

SKILLSETS: list[Skillset] = [
    Skillset(
        name="business-model-canvas",
        display_name="Business Model Canvas",
        description=(
            "Structured analysis of an organisation's business model across"
            " nine building blocks. Produces evidence-linked canvas documents"
            " grounded in research."
        ),
        slug_pattern="canvas-{n}",
        pipeline=[
            PipelineStage(
                order=1,
                skill="bmc-research",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Stage 1: Project brief agreed",
                consumes=["topics", "confidence"],
            ),
            PipelineStage(
                order=2,
                skill="bmc-segments",
                prerequisite_gate="brief.agreed.md",
                produces_gate="segments/segments.agreed.md",
                description="Stage 2: Customer segments agreed",
                consumes=["scope", "context"],
            ),
            PipelineStage(
                order=3,
                skill="bmc-canvas",
                prerequisite_gate="segments/segments.agreed.md",
                produces_gate="canvas.agreed.md",
                description="Stage 3: Business Model Canvas agreed",
                consumes=["segments", "value_propositions"],
            ),
        ],
    ),
]
