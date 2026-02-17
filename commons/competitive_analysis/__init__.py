"""Competitive Analysis bounded context."""

from practice.entities import Skillset


def _create_presenter(workspace_root, repo_root):
    from competitive_analysis.presenter import CompetitiveAnalysisPresenter

    return CompetitiveAnalysisPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("competitive-analysis", _create_presenter)

SKILLSETS: list[Skillset] = [
    Skillset(
        name="competitive-analysis",
        display_name="Competitive Analysis",
        description="Market positioning methodology.",
        slug_pattern="comp-{n}",
        problem_domain="Market positioning",
        value_proposition="Know your rivals.",
        deliverables=["Competitor landscape report", "Market gap analysis"],
        classification=["strategy", "market-analysis"],
        evidence=["Porter's Five Forces"],
    ),
]
