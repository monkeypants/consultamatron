"""Wardley Mapping bounded context."""

from practice.discovery import PipelineStage
from practice.entities import Skillset

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
            ),
            PipelineStage(
                order=2,
                skill="wm-needs",
                prerequisite_gate="brief.agreed.md",
                produces_gate="needs/needs.agreed.md",
                description="Stage 2: User needs agreed",
            ),
            PipelineStage(
                order=3,
                skill="wm-chain",
                prerequisite_gate="needs/needs.agreed.md",
                produces_gate="chain/supply-chain.agreed.md",
                description="Stage 3: Supply chain agreed",
            ),
            PipelineStage(
                order=4,
                skill="wm-evolve",
                prerequisite_gate="chain/supply-chain.agreed.md",
                produces_gate="evolve/map.agreed.owm",
                description="Stage 4: Evolution map agreed",
            ),
            PipelineStage(
                order=5,
                skill="wm-strategy",
                prerequisite_gate="evolve/map.agreed.owm",
                produces_gate="strategy/map.agreed.owm",
                description="Stage 5: Strategy map agreed",
            ),
        ],
    ),
]
