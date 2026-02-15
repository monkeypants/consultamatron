"""Usecase implementations for consulting practice accounting.

Each usecase has an execute(request) -> response method satisfying
the UseCase protocol. Repository dependencies are injected via
constructor.
"""

from __future__ import annotations

from typing import Protocol, TypeVar

from bin.cli.dtos import (
    AddEngagementEntryRequest,
    AddEngagementEntryResponse,
    DecisionInfo,
    GetProjectProgressRequest,
    GetProjectProgressResponse,
    GetProjectRequest,
    GetProjectResponse,
    InitializeWorkspaceRequest,
    InitializeWorkspaceResponse,
    ListDecisionsRequest,
    ListDecisionsResponse,
    ListProjectsRequest,
    ListProjectsResponse,
    ListResearchTopicsRequest,
    ListResearchTopicsResponse,
    ProjectInfo,
    RecordDecisionRequest,
    RecordDecisionResponse,
    RegisterProjectRequest,
    RegisterProjectResponse,
    RegisterResearchTopicRequest,
    RegisterResearchTopicResponse,
    RegisterTourRequest,
    RegisterTourResponse,
    RenderSiteRequest,
    RenderSiteResponse,
    ResearchTopicInfo,
    StageProgress,
    UpdateProjectStatusRequest,
    UpdateProjectStatusResponse,
)
from bin.cli.entities import (
    Confidence,
    DecisionEntry,
    EngagementEntry,
    Project,
    ProjectStatus,
    ResearchTopic,
    TourManifest,
)
from bin.cli.exceptions import DuplicateError, InvalidTransitionError, NotFoundError
from bin.cli.repositories import (
    Clock,
    DecisionRepository,
    EngagementRepository,
    IdGenerator,
    ProjectPresenter,
    ProjectRepository,
    ResearchTopicRepository,
    SiteRenderer,
    SkillsetRepository,
    TourManifestRepository,
)

TRequest = TypeVar("TRequest", contravariant=True)
TResponse = TypeVar("TResponse", covariant=True)


class UseCase(Protocol[TRequest, TResponse]):
    """Contract: every usecase takes a typed request, returns a typed response."""

    def execute(self, request: TRequest) -> TResponse: ...


# ---------------------------------------------------------------------------
# Write usecases
# ---------------------------------------------------------------------------


class InitializeWorkspaceUseCase:
    """Create a new client workspace with empty registries."""

    def __init__(
        self,
        projects: ProjectRepository,
        engagement: EngagementRepository,
        research: ResearchTopicRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._engagement = engagement
        self._research = research
        self._clock = clock
        self._id_gen = id_gen

    def execute(
        self, request: InitializeWorkspaceRequest
    ) -> InitializeWorkspaceResponse:
        if self._projects.client_exists(request.client):
            raise DuplicateError(f"Client workspace already exists: {request.client}")
        self._engagement.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title="Client onboarded",
                fields={},
            )
        )
        return InitializeWorkspaceResponse(client=request.client)


class RegisterProjectUseCase:
    """Register a new project, its decision log, and engagement entry."""

    def __init__(
        self,
        projects: ProjectRepository,
        decisions: DecisionRepository,
        engagement: EngagementRepository,
        skillsets: SkillsetRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._decisions = decisions
        self._engagement = engagement
        self._skillsets = skillsets
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: RegisterProjectRequest) -> RegisterProjectResponse:
        if self._skillsets.get(request.skillset) is None:
            raise NotFoundError(f"Unknown skillset: {request.skillset}")
        if self._projects.get(request.client, request.slug) is not None:
            raise DuplicateError(
                f"Project already exists: {request.client}/{request.slug}"
            )

        today = self._clock.today()
        self._projects.save(
            Project(
                slug=request.slug,
                client=request.client,
                skillset=request.skillset,
                status=ProjectStatus.PLANNING,
                created=today,
                notes=request.notes,
            )
        )

        fields = {"Skillset": request.skillset, "Scope": request.scope}
        self._decisions.save(
            DecisionEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                project_slug=request.slug,
                date=today,
                timestamp=self._clock.now(),
                title="Project created",
                fields=fields,
            )
        )
        self._engagement.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                date=today,
                timestamp=self._clock.now(),
                title=f"Project registered: {request.slug}",
                fields=fields,
            )
        )

        return RegisterProjectResponse(
            client=request.client,
            slug=request.slug,
            skillset=request.skillset,
        )


class UpdateProjectStatusUseCase:
    """Transition a project's status with validation."""

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(
        self, request: UpdateProjectStatusRequest
    ) -> UpdateProjectStatusResponse:
        project = self._projects.get(request.client, request.project_slug)
        if project is None:
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        new_status = ProjectStatus(request.status)
        if new_status != project.status.next():
            raise InvalidTransitionError(
                f"Invalid transition: {project.status.value} -> {new_status.value}"
            )

        self._projects.save(project.model_copy(update={"status": new_status}))

        return UpdateProjectStatusResponse(
            client=request.client,
            project_slug=request.project_slug,
            status=new_status.value,
        )


class RecordDecisionUseCase:
    """Append a timestamped decision to a project's log."""

    def __init__(
        self,
        projects: ProjectRepository,
        decisions: DecisionRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._decisions = decisions
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: RecordDecisionRequest) -> RecordDecisionResponse:
        if self._projects.get(request.client, request.project_slug) is None:
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        entry_id = self._id_gen.new_id()
        self._decisions.save(
            DecisionEntry(
                id=entry_id,
                client=request.client,
                project_slug=request.project_slug,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title=request.title,
                fields=request.fields,
            )
        )

        return RecordDecisionResponse(
            client=request.client,
            project_slug=request.project_slug,
            decision_id=entry_id,
        )


class AddEngagementEntryUseCase:
    """Append a timestamped entry to the engagement log."""

    def __init__(
        self,
        projects: ProjectRepository,
        engagement: EngagementRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._engagement = engagement
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: AddEngagementEntryRequest) -> AddEngagementEntryResponse:
        if not self._projects.client_exists(request.client):
            raise NotFoundError(f"Client not found: {request.client}")

        entry_id = self._id_gen.new_id()
        self._engagement.save(
            EngagementEntry(
                id=entry_id,
                client=request.client,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title=request.title,
                fields=request.fields,
            )
        )

        return AddEngagementEntryResponse(
            client=request.client,
            entry_id=entry_id,
        )


class RegisterResearchTopicUseCase:
    """Register a research topic in the client manifest."""

    def __init__(
        self,
        projects: ProjectRepository,
        research: ResearchTopicRepository,
        clock: Clock,
    ) -> None:
        self._projects = projects
        self._research = research
        self._clock = clock

    def execute(
        self, request: RegisterResearchTopicRequest
    ) -> RegisterResearchTopicResponse:
        if self._research.exists(request.client, request.filename):
            raise DuplicateError(f"Research topic already exists: {request.filename}")

        self._research.save(
            ResearchTopic(
                filename=request.filename,
                client=request.client,
                topic=request.topic,
                date=self._clock.today(),
                confidence=Confidence(request.confidence),
            )
        )

        return RegisterResearchTopicResponse(
            client=request.client,
            filename=request.filename,
        )


class RegisterTourUseCase:
    """Register or replace a tour manifest."""

    def __init__(
        self,
        projects: ProjectRepository,
        tours: TourManifestRepository,
    ) -> None:
        self._projects = projects
        self._tours = tours

    def execute(self, request: RegisterTourRequest) -> RegisterTourResponse:
        if self._projects.get(request.client, request.project_slug) is None:
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        self._tours.save(
            TourManifest(
                name=request.name,
                client=request.client,
                project_slug=request.project_slug,
                title=request.title,
                stops=request.stops,
            )
        )

        return RegisterTourResponse(
            client=request.client,
            project_slug=request.project_slug,
            name=request.name,
            stop_count=len(request.stops),
        )


# ---------------------------------------------------------------------------
# Read usecases
# ---------------------------------------------------------------------------


class ListProjectsUseCase:
    """Query projects with optional filters."""

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, request: ListProjectsRequest) -> ListProjectsResponse:
        status = ProjectStatus(request.status) if request.status else None
        projects = self._projects.list_filtered(
            request.client,
            skillset=request.skillset,
            status=status,
        )
        return ListProjectsResponse(
            client=request.client,
            projects=[ProjectInfo.from_entity(p) for p in projects],
        )


class GetProjectUseCase:
    """Retrieve a single project by slug."""

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, request: GetProjectRequest) -> GetProjectResponse:
        project = self._projects.get(request.client, request.slug)
        if project is None:
            return GetProjectResponse(client=request.client, project=None)
        return GetProjectResponse(
            client=request.client,
            project=ProjectInfo.from_entity(project),
        )


class GetProjectProgressUseCase:
    """Match decision log against skillset pipeline to report progress."""

    def __init__(
        self,
        projects: ProjectRepository,
        decisions: DecisionRepository,
        skillsets: SkillsetRepository,
    ) -> None:
        self._projects = projects
        self._decisions = decisions
        self._skillsets = skillsets

    def execute(self, request: GetProjectProgressRequest) -> GetProjectProgressResponse:
        project = self._projects.get(request.client, request.project_slug)
        if project is None:
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        skillset = self._skillsets.get(project.skillset)
        if skillset is None:
            raise NotFoundError(f"Skillset not found: {project.skillset}")

        decisions = self._decisions.list_all(request.client, request.project_slug)
        decision_titles = {d.title for d in decisions}

        stages: list[StageProgress] = []
        current_stage: str | None = None
        next_prerequisite: str | None = None

        for stage in sorted(skillset.pipeline, key=lambda s: s.order):
            completed = stage.description in decision_titles
            stages.append(
                StageProgress(
                    order=stage.order,
                    skill=stage.skill,
                    description=stage.description,
                    completed=completed,
                )
            )
            if not completed and current_stage is None:
                current_stage = stage.skill
                next_prerequisite = stage.prerequisite_gate

        return GetProjectProgressResponse(
            client=request.client,
            project_slug=request.project_slug,
            skillset=project.skillset,
            stages=stages,
            current_stage=current_stage,
            next_prerequisite=next_prerequisite,
        )


class ListDecisionsUseCase:
    """List all decisions for a project in chronological order."""

    def __init__(self, decisions: DecisionRepository) -> None:
        self._decisions = decisions

    def execute(self, request: ListDecisionsRequest) -> ListDecisionsResponse:
        decisions = self._decisions.list_all(request.client, request.project_slug)
        decisions.sort(key=lambda d: d.timestamp)
        return ListDecisionsResponse(
            client=request.client,
            project_slug=request.project_slug,
            decisions=[DecisionInfo.from_entity(d) for d in decisions],
        )


class ListResearchTopicsUseCase:
    """List all research topics for a client."""

    def __init__(self, research: ResearchTopicRepository) -> None:
        self._research = research

    def execute(self, request: ListResearchTopicsRequest) -> ListResearchTopicsResponse:
        topics = self._research.list_all(request.client)
        return ListResearchTopicsResponse(
            client=request.client,
            topics=[ResearchTopicInfo.from_entity(t) for t in topics],
        )


class RenderSiteUseCase:
    """Gather structured data, assemble contributions, and render."""

    def __init__(
        self,
        projects: ProjectRepository,
        tours: TourManifestRepository,
        research: ResearchTopicRepository,
        renderer: SiteRenderer,
        presenters: dict[str, ProjectPresenter],
    ) -> None:
        self._projects = projects
        self._tours = tours
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
            project_tours = self._tours.list_all(request.client, project.slug)
            contributions.append(presenter.present(project, project_tours))

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
