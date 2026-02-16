"""Usecase implementations — re-exports from consulting.usecases
and wardley_mapping.usecases, plus site usecase that remains in bin/cli.
"""

from __future__ import annotations

from bin.cli.dtos import RenderSiteRequest, RenderSiteResponse
from consulting.repositories import ProjectRepository, ResearchTopicRepository
from consulting.usecases import (
    AddEngagementEntryUseCase,
    GetProjectProgressUseCase,
    GetProjectUseCase,
    InitializeWorkspaceUseCase,
    ListDecisionsUseCase,
    ListProjectsUseCase,
    ListResearchTopicsUseCase,
    RecordDecisionUseCase,
    RegisterProjectUseCase,
    RegisterResearchTopicUseCase,
    UpdateProjectStatusUseCase,
)
from practice.exceptions import NotFoundError
from practice.repositories import ProjectPresenter, SiteRenderer
from wardley_mapping.usecases import RegisterTourUseCase

__all__ = [
    "AddEngagementEntryUseCase",
    "GetProjectProgressUseCase",
    "GetProjectUseCase",
    "InitializeWorkspaceUseCase",
    "ListDecisionsUseCase",
    "ListProjectsUseCase",
    "ListResearchTopicsUseCase",
    "RecordDecisionUseCase",
    "RegisterProjectUseCase",
    "RegisterResearchTopicUseCase",
    "RegisterTourUseCase",
    "RenderSiteUseCase",
    "UpdateProjectStatusUseCase",
]


# ---------------------------------------------------------------------------
# RenderSite — stays here (cross-BC orchestration)
# ---------------------------------------------------------------------------


class RenderSiteUseCase:
    """Coordinate site rendering across project presenters.

    Iterates all projects, dispatches to the presenter matching each
    project's skillset, collects contributions, and delegates to the
    SiteRenderer. Skips projects with unknown skillsets.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        research: ResearchTopicRepository,
        renderer: SiteRenderer,
        presenters: dict[str, ProjectPresenter],
    ) -> None:
        self._projects = projects
        self._research = research
        self._renderer = renderer
        self._presenters = presenters

    def execute(self, request: RenderSiteRequest) -> RenderSiteResponse:
        if not self._projects.client_exists(request.client):
            raise NotFoundError(f"Client not found: {request.client}")

        projects = self._projects.list_all(request.client)
        research_topics = self._research.list_all(request.client)

        contributions = []
        for project in projects:
            presenter = self._presenters.get(project.skillset)
            if presenter is None:
                print(f"    Unknown skillset '{project.skillset}', skipping")
                continue
            contributions.append(presenter.present(project))

        site_path = self._renderer.render(
            client=request.client,
            contributions=contributions,
            research_topics=research_topics,
        )

        page_count = len(list(site_path.rglob("*.html")))

        return RenderSiteResponse(
            client=request.client,
            site_path=str(site_path),
            page_count=page_count,
        )
