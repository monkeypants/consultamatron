"""Six Simple Rules Complexity Audit bounded context."""

from practice.discovery import PipelineStage
from practice.entities import Skillset

SKILLSETS: list[Skillset] = [
    Skillset(
        name="six-simple-rules-complexity-audit",
        display_name="Six Simple Rules Complexity Audit",
        description=(
            "Organisational complexity audit using Yves Morieux's Six Simple"
            " Rules framework. Diagnoses complexity root causes rule by rule,"
            " aggregates findings, and synthesises actionable recommendations."
        ),
        slug_pattern="audit-{n}",
        pipeline=[
            PipelineStage(
                order=1,
                skill="ca-research",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Stage 1: Audit brief agreed",
            ),
            PipelineStage(
                order=2,
                skill="ca-diagnose-understanding",
                prerequisite_gate="brief.agreed.md",
                produces_gate="diagnostics/rule1-understanding.agreed.md",
                description="Stage 2: Rule 1 diagnostic agreed",
            ),
            PipelineStage(
                order=3,
                skill="ca-diagnose-integrators",
                prerequisite_gate="diagnostics/rule1-understanding.agreed.md",
                produces_gate="diagnostics/rule2-integrators.agreed.md",
                description="Stage 3: Rule 2 diagnostic agreed",
            ),
            PipelineStage(
                order=4,
                skill="ca-diagnose-power",
                prerequisite_gate="diagnostics/rule2-integrators.agreed.md",
                produces_gate="diagnostics/rule3-power.agreed.md",
                description="Stage 4: Rule 3 diagnostic agreed",
            ),
            PipelineStage(
                order=5,
                skill="ca-diagnose-future",
                prerequisite_gate="diagnostics/rule3-power.agreed.md",
                produces_gate="diagnostics/rule4-future.agreed.md",
                description="Stage 5: Rule 4 diagnostic agreed",
            ),
            PipelineStage(
                order=6,
                skill="ca-diagnose-reciprocity",
                prerequisite_gate="diagnostics/rule4-future.agreed.md",
                produces_gate="diagnostics/rule5-reciprocity.agreed.md",
                description="Stage 6: Rule 5 diagnostic agreed",
            ),
            PipelineStage(
                order=7,
                skill="ca-diagnose-rewards",
                prerequisite_gate="diagnostics/rule5-reciprocity.agreed.md",
                produces_gate="diagnostics/rule6-rewards.agreed.md",
                description="Stage 7: Rule 6 diagnostic agreed",
            ),
            PipelineStage(
                order=8,
                skill="ca-aggregate",
                prerequisite_gate="diagnostics/rule6-rewards.agreed.md",
                produces_gate="diagnostics.agreed.md",
                description="Stage 8: Diagnostics aggregated and agreed",
            ),
            PipelineStage(
                order=9,
                skill="ca-synthesise",
                prerequisite_gate="diagnostics.agreed.md",
                produces_gate="audit.agreed.md",
                description="Stage 9: Audit report agreed",
            ),
        ],
    ),
]
