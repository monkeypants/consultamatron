"""Usecase implementations — re-exports from consulting.usecases
and wardley_mapping.usecases, plus site usecase that remains in bin/cli.
"""

from __future__ import annotations

from bin.cli.dtos import (
    ListSkillsetsRequest,
    ListSkillsetsResponse,
    RenderSiteRequest,
    RenderSiteResponse,
    ShowSkillsetRequest,
    ShowSkillsetResponse,
    SkillsetInfo,
    SkillsetStageInfo,
)
from consulting.repositories import (
    ProjectRepository,
    ResearchTopicRepository,
    SkillsetRepository,
)
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
from practice.entities import Skillset
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
    "ListSkillsetsUseCase",
    "ListResearchTopicsUseCase",
    "RecordDecisionUseCase",
    "RegisterProjectUseCase",
    "RegisterResearchTopicUseCase",
    "RegisterTourUseCase",
    "RenderSiteUseCase",
    "ShowSkillsetUseCase",
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


# ---------------------------------------------------------------------------
# Skillset — stays here (cross-BC, aggregates from all BCs)
# ---------------------------------------------------------------------------


def _skillset_to_info(s: Skillset) -> SkillsetInfo:
    return SkillsetInfo(
        name=s.name,
        display_name=s.display_name,
        description=s.description,
        slug_pattern=s.slug_pattern,
        stages=[
            SkillsetStageInfo(
                order=st.order,
                skill=st.skill,
                description=st.description,
                prerequisite_gate=st.prerequisite_gate,
                produces_gate=st.produces_gate,
            )
            for st in s.pipeline
        ],
    )


class ListSkillsetsUseCase:
    """List all registered skillsets."""

    def __init__(self, skillsets: SkillsetRepository) -> None:
        self._skillsets = skillsets

    def execute(self, request: ListSkillsetsRequest) -> ListSkillsetsResponse:
        return ListSkillsetsResponse(
            skillsets=[_skillset_to_info(s) for s in self._skillsets.list_all()],
        )


class ShowSkillsetUseCase:
    """Show details of a registered skillset by name."""

    def __init__(self, skillsets: SkillsetRepository) -> None:
        self._skillsets = skillsets

    def execute(self, request: ShowSkillsetRequest) -> ShowSkillsetResponse:
        skillset = self._skillsets.get(request.name)
        if skillset is None:
            raise NotFoundError(f"Skillset not found: {request.name}")
        return ShowSkillsetResponse(skillset=_skillset_to_info(skillset))
