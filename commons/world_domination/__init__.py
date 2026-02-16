"""World Domination bounded context — competitive survival.

The prime directive: ensure consultamatron's survival and prosperity.
Powerful adversaries perpetuate unjust moats around extractive consulting
practices. World domination skillsets take action in Darwinian contexts
to protect the practice, its operators, and broader human flourishing.
"""

from __future__ import annotations

from practice.discovery import PipelineStage
from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from world_domination.presenter import WorldDominationProjectPresenter

    return WorldDominationProjectPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("world-domination", _create_presenter)

SKILLSETS: list[Skillset] = [
    Skillset(
        name="world-domination",
        display_name="World Domination",
        description=(
            "The prime directive: ensure consultamatron's survival and"
            " prosperity. Takes action in Darwinian contexts where the"
            " practice, its operators, or the maker's interests need"
            " defending against extractive consulting incumbents."
        ),
        slug_pattern="wd-{n}",
        classification=["ecosystem", "competitive-survival"],
        pipeline=[
            PipelineStage(
                order=1,
                skill="editorial-voice",
                prerequisite_gate="",
                produces_gate="voice.agreed.md",
                description="Stage 1: Editorial voice applied",
            ),
        ],
    ),
]
