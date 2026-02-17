"""Wardley Mapping bounded context."""

from __future__ import annotations

from practice.discovery import PipelineStage
from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from wardley_mapping.infrastructure import JsonTourManifestRepository
    from wardley_mapping.presenter import WardleyProjectPresenter

    return WardleyProjectPresenter(
        workspace_root=workspace_root,
        ensure_owm_script=repo_root / "bin" / "ensure-owm.sh",
        tours=JsonTourManifestRepository(workspace_root),
    )


PRESENTER_FACTORY = ("wardley-mapping", _create_presenter)


def register_services(container) -> None:
    """Register WM-specific services on the DI container."""
    from wardley_mapping.infrastructure import JsonTourManifestRepository
    from wardley_mapping.usecases import RegisterTourUseCase

    container.tours = JsonTourManifestRepository(container.config.workspace_root)
    container.register_tour_usecase = RegisterTourUseCase(
        projects=container.projects,
        tours=container.tours,
    )


SKILLSETS: list[Skillset] = [
    Skillset(
        name="wardley-mapping",
        display_name="Wardley Mapping",
        description=(
            "Strategic mapping methodology that positions components by"
            " visibility to the user and evolutionary maturity. Produces"
            " OWM map files suitable for strategic decision-making."
        ),
        slug_pattern="maps-{n}",
        pipeline=[
            PipelineStage(
                order=1,
                skill="wm-research",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Stage 1: Project brief agreed",
                consumes=["topics", "confidence"],
            ),
            PipelineStage(
                order=2,
                skill="wm-needs",
                prerequisite_gate="brief.agreed.md",
                produces_gate="needs/needs.agreed.md",
                description="Stage 2: User needs agreed",
                consumes=["scope", "context"],
            ),
            PipelineStage(
                order=3,
                skill="wm-chain",
                prerequisite_gate="needs/needs.agreed.md",
                produces_gate="chain/supply-chain.agreed.md",
                description="Stage 3: Supply chain agreed",
                consumes=["users", "needs"],
            ),
            PipelineStage(
                order=4,
                skill="wm-evolve",
                prerequisite_gate="chain/supply-chain.agreed.md",
                produces_gate="evolve/map.agreed.owm",
                description="Stage 4: Evolution map agreed",
                consumes=["components", "dependencies"],
            ),
            PipelineStage(
                order=5,
                skill="wm-strategy",
                prerequisite_gate="evolve/map.agreed.owm",
                produces_gate="strategy/map.agreed.owm",
                description="Stage 5: Strategy map agreed",
                consumes=["components", "evolution"],
            ),
        ],
    ),
]
