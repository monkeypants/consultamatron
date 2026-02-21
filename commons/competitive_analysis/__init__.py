"""Competitive Analysis bounded context."""

from practice.entities import Pipeline


def _create_presenter(workspace_root, repo_root):
    from competitive_analysis.presenter import CompetitiveAnalysisPresenter

    return CompetitiveAnalysisPresenter(workspace_root=workspace_root)


PRESENTER_FACTORY = ("competitive-analysis", _create_presenter)

PIPELINES: list[Pipeline] = [
    Pipeline(
        name="competitive-analysis",
        display_name="Competitive Analysis",
        description="Market positioning methodology.",
        slug_pattern="comp-{n}",
    ),
]
