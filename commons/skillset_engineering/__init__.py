"""Skillset Engineering bounded context.

Meta-skillsets for creating new consulting products and refining
existing ones. Operates on the practice infrastructure itself —
the skillsets, pipelines, skill files, semantic bytecode, and
conformance tests that comprise a consulting methodology.
"""

from __future__ import annotations

from practice.discovery import PipelineStage
from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from skillset_engineering.presenter import SkillsetEngineeringPresenter

    return SkillsetEngineeringPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = [
    ("new-skillset", _create_presenter),
    ("refine-skillset", _create_presenter),
]

SKILLSETS: list[Skillset] = [
    Skillset(
        name="new-skillset",
        display_name="New Skillset",
        description=(
            "Meta-methodology for creating new consulting skillsets."
            " Guides the operator from initial brief through domain research,"
            " pipeline design, and full implementation — producing a BC package"
            " that passes all conformance tests, with skill files, bash wrappers,"
            " and hierarchical semantic bytecode references for token-efficient"
            " agent operation."
        ),
        slug_pattern="skillset-{n}",
        problem_domain="Practice engineering",
        value_proposition=(
            "Systematise the creation of new consulting products so they"
            " are consistent, discoverable, and conformance-tested from"
            " the moment they ship."
        ),
        deliverables=[
            "Skillset prospectus or implemented BC package",
            "Skill files with methodology guides",
            "Bash script wrappers for CLI operations",
            "Semantic bytecode reference hierarchy",
            "Presenter and test infrastructure",
        ],
        classification=["meta", "practice-engineering"],
        evidence=[
            "Consultamatron conformance test suite",
            "Existing WM and BMC skillset implementations",
        ],
        pipeline=[
            PipelineStage(
                order=1,
                skill="ns-brief",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Stage 1: Skillset brief agreed",
                consumes=["topics", "confidence"],
            ),
            PipelineStage(
                order=2,
                skill="ns-research",
                prerequisite_gate="brief.agreed.md",
                produces_gate="research/synthesis.agreed.md",
                description="Stage 2: Domain research synthesised",
                consumes=["scope", "problem_domain"],
            ),
            PipelineStage(
                order=3,
                skill="ns-design",
                prerequisite_gate="research/synthesis.agreed.md",
                produces_gate="design/design.agreed.md",
                description="Stage 3: Pipeline design agreed",
                consumes=["methodology", "patterns"],
            ),
            PipelineStage(
                order=4,
                skill="ns-implement",
                prerequisite_gate="design/design.agreed.md",
                produces_gate="implementation.agreed.md",
                description="Stage 4: Implementation complete",
                consumes=["pipeline", "skills", "gates"],
            ),
        ],
    ),
    Skillset(
        name="refine-skillset",
        display_name="Refine Skillset",
        description=(
            "Iterative quality improvement for existing skillsets."
            " Assesses a skillset against quality criteria derived from"
            " usage feedback, conformance results, and domain evolution,"
            " then plans and executes targeted improvements. Each cycle"
            " monotonically improves quality — more tokens spent on"
            " refinement yields higher-quality methodology, regardless"
            " of evidence volume."
        ),
        slug_pattern="refine-{n}",
        problem_domain="Practice engineering",
        value_proposition=(
            "Continuously improve consulting methodologies through"
            " structured assessment and iteration, ensuring skillsets"
            " stay sharp as domains evolve and usage patterns reveal"
            " weaknesses."
        ),
        deliverables=[
            "Quality assessment report",
            "Improvement plan with prioritised changes",
            "Updated skillset artifacts",
        ],
        classification=["meta", "practice-engineering"],
        evidence=[
            "Consultamatron conformance test suite",
            "Feedback from skillset usage",
        ],
        pipeline=[
            PipelineStage(
                order=1,
                skill="rs-assess",
                prerequisite_gate="resources/index.md",
                produces_gate="assessment.agreed.md",
                description="Stage 1: Quality assessment agreed",
                consumes=["topics", "confidence"],
            ),
            PipelineStage(
                order=2,
                skill="rs-plan",
                prerequisite_gate="assessment.agreed.md",
                produces_gate="plan.agreed.md",
                description="Stage 2: Improvement plan agreed",
                consumes=["quality_scores", "issues"],
            ),
            PipelineStage(
                order=3,
                skill="rs-iterate",
                prerequisite_gate="plan.agreed.md",
                produces_gate="iteration.agreed.md",
                description="Stage 3: Iteration complete",
                consumes=["changes", "acceptance_criteria"],
            ),
        ],
    ),
]
