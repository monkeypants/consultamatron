"""Usecase implementations — re-exports from consulting.usecases
and wardley_mapping.usecases, plus site usecase that remains in bin/cli.
"""

from __future__ import annotations

from bin.cli.dtos import (
    ListSkillsetsRequest,
    ListSkillsetsResponse,
    ListSourcesRequest,
    ListSourcesResponse,
    RegisterProspectusRequest,
    RegisterProspectusResponse,
    RenderSiteRequest,
    RenderSiteResponse,
    ShowSkillsetRequest,
    ShowSkillsetResponse,
    ShowSourceRequest,
    ShowSourceResponse,
    SkillsetInfo,
    SkillsetStageInfo,
    SourceInfo,
    UpdateProspectusRequest,
    UpdateProspectusResponse,
)
from bin.cli.infrastructure.skillset_scaffold import SkillsetScaffold
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
from practice.exceptions import DuplicateError, NotFoundError
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
    "RegisterProspectusUseCase",
    "RegisterResearchTopicUseCase",
    "RegisterTourUseCase",
    "RenderSiteUseCase",
    "ShowSkillsetUseCase",
    "ShowSourceUseCase",
    "UpdateProjectStatusUseCase",
    "UpdateProspectusUseCase",
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
        is_implemented=s.is_implemented,
        problem_domain=s.problem_domain,
        deliverables=list(s.deliverables),
        value_proposition=s.value_proposition,
        classification=list(s.classification),
        evidence=list(s.evidence),
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


def _split_csv(value: str) -> list[str]:
    """Split a comma-separated string into a list, stripping whitespace."""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


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

        if request.implemented is not None:
            want_implemented = request.implemented.lower() == "true"
            all_skillsets = [
                s for s in all_skillsets if s.is_implemented == want_implemented
            ]

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


# ---------------------------------------------------------------------------
# Prospectus — register and update unimplemented skillsets
# ---------------------------------------------------------------------------


class RegisterProspectusUseCase:
    """Register a new skillset prospectus (unimplemented skillset)."""

    def __init__(
        self,
        skillsets: SkillsetRepository,
        scaffold: SkillsetScaffold,
    ) -> None:
        self._skillsets = skillsets
        self._scaffold = scaffold

    def execute(self, request: RegisterProspectusRequest) -> RegisterProspectusResponse:
        if self._skillsets.get(request.name) is not None:
            raise DuplicateError(f"Skillset already exists: {request.name}")
        init_path = self._scaffold.create(
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            slug_pattern=request.slug_pattern,
            problem_domain=request.problem_domain,
            value_proposition=request.value_proposition,
            deliverables=_split_csv(request.deliverables),
            classification=_split_csv(request.classification),
            evidence=_split_csv(request.evidence),
        )
        return RegisterProspectusResponse(
            name=request.name,
            init_path=str(init_path),
        )


class UpdateProspectusUseCase:
    """Update an existing skillset prospectus."""

    def __init__(
        self,
        skillsets: SkillsetRepository,
        scaffold: SkillsetScaffold,
    ) -> None:
        self._skillsets = skillsets
        self._scaffold = scaffold

    def execute(self, request: UpdateProspectusRequest) -> UpdateProspectusResponse:
        existing = self._skillsets.get(request.name)
        if existing is None:
            raise NotFoundError(f"Skillset not found: {request.name}")
        if existing.is_implemented:
            raise DuplicateError(
                f"Skillset {request.name!r} is implemented; "
                "update the BC module directly"
            )
        init_path = self._scaffold.update(
            name=request.name,
            display_name=request.display_name,
            description=request.description,
            slug_pattern=request.slug_pattern,
            problem_domain=request.problem_domain,
            value_proposition=request.value_proposition,
            deliverables=_split_csv(request.deliverables)
            if request.deliverables is not None
            else None,
            classification=_split_csv(request.classification)
            if request.classification is not None
            else None,
            evidence=_split_csv(request.evidence)
            if request.evidence is not None
            else None,
        )
        return UpdateProspectusResponse(
            name=request.name,
            init_path=str(init_path),
        )
