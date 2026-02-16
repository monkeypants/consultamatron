"""Usecase implementations — re-exports from consulting.usecases
and wardley_mapping.usecases, plus site usecase that remains in bin/cli.
"""

from __future__ import annotations

from bin.cli.dtos import (
    ListSkillsetsRequest,
    ListSkillsetsResponse,
    ListSourcesRequest,
    ListSourcesResponse,
    RenderSiteRequest,
    RenderSiteResponse,
    ShowSkillsetRequest,
    ShowSkillsetResponse,
    ShowSourceRequest,
    ShowSourceResponse,
    SkillsetInfo,
    SkillsetStageInfo,
    SourceInfo,
)
from consulting.repositories import (
    EngagementRepository,
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
from practice.entities import Skillset, SkillsetSource
from practice.exceptions import NotFoundError
from practice.repositories import ProjectPresenter, SiteRenderer, SourceRepository
from wardley_mapping.usecases import RegisterTourUseCase

__all__ = [
    "AddEngagementEntryUseCase",
    "GetProjectProgressUseCase",
    "GetProjectUseCase",
    "InitializeWorkspaceUseCase",
    "ListDecisionsUseCase",
    "ListProjectsUseCase",
    "ListSkillsetsUseCase",
    "ListSourcesUseCase",
    "ListResearchTopicsUseCase",
    "RecordDecisionUseCase",
    "RegisterProjectUseCase",
    "RegisterResearchTopicUseCase",
    "RegisterTourUseCase",
    "RenderSiteUseCase",
    "ShowSkillsetUseCase",
    "ShowSourceUseCase",
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
    """List registered skillsets, optionally filtered by engagement sources."""

    def __init__(
        self,
        skillsets: SkillsetRepository,
        engagements: EngagementRepository | None = None,
        sources: SourceRepository | None = None,
    ) -> None:
        self._skillsets = skillsets
        self._engagements = engagements
        self._sources = sources

    def execute(self, request: ListSkillsetsRequest) -> ListSkillsetsResponse:
        all_skillsets = self._skillsets.list_all()

        if (
            request.client
            and request.engagement
            and self._engagements
            and self._sources
        ):
            engagement = self._engagements.get(request.client, request.engagement)
            if engagement is None:
                raise NotFoundError(
                    f"Engagement not found: {request.client}/{request.engagement}"
                )
            allowed_names: set[str] = set()
            for source_slug in engagement.allowed_sources:
                src = self._sources.get(source_slug)
                if src:
                    allowed_names.update(src.skillset_names)
            all_skillsets = [s for s in all_skillsets if s.name in allowed_names]

        return ListSkillsetsResponse(
            skillsets=[_skillset_to_info(s) for s in all_skillsets],
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


# ---------------------------------------------------------------------------
# Source — stays here (cross-BC, lists installed sources)
# ---------------------------------------------------------------------------


def _source_to_info(s: SkillsetSource) -> SourceInfo:
    return SourceInfo(
        slug=s.slug,
        source_type=s.source_type.value,
        skillset_names=s.skillset_names,
    )


class ListSourcesUseCase:
    """List all installed skillset sources."""

    def __init__(self, sources: SourceRepository) -> None:
        self._sources = sources

    def execute(self, request: ListSourcesRequest) -> ListSourcesResponse:
        return ListSourcesResponse(
            sources=[_source_to_info(s) for s in self._sources.list_all()],
        )


class ShowSourceUseCase:
    """Show details of an installed source by slug."""

    def __init__(self, sources: SourceRepository) -> None:
        self._sources = sources

    def execute(self, request: ShowSourceRequest) -> ShowSourceResponse:
        source = self._sources.get(request.slug)
        if source is None:
            raise NotFoundError(f"Source not found: {request.slug}")
        return ShowSourceResponse(source=_source_to_info(source))
