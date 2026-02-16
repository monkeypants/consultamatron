"""Usecase implementations for consulting practice accounting.

Each usecase has an execute(request) -> response method satisfying
the UseCase protocol. Repository dependencies are injected via
constructor.
"""

from __future__ import annotations

from consulting.dtos import (
    AddEngagementEntryRequest,
    AddEngagementEntryResponse,
    AddEngagementSourceRequest,
    AddEngagementSourceResponse,
    CreateEngagementRequest,
    CreateEngagementResponse,
    DecisionInfo,
    EngagementInfo,
    GetEngagementRequest,
    GetEngagementResponse,
    GetProjectProgressRequest,
    GetProjectProgressResponse,
    GetProjectRequest,
    GetProjectResponse,
    InitializeWorkspaceRequest,
    InitializeWorkspaceResponse,
    ListDecisionsRequest,
    ListDecisionsResponse,
    ListEngagementsRequest,
    ListEngagementsResponse,
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
    RemoveEngagementSourceRequest,
    RemoveEngagementSourceResponse,
    ResearchTopicInfo,
    StageProgress,
    UpdateProjectStatusRequest,
    UpdateProjectStatusResponse,
)
from consulting.entities import DecisionEntry, EngagementEntry
from consulting.repositories import (
    DecisionRepository,
    EngagementLogRepository,
    EngagementRepository,
    ProjectRepository,
    ResearchTopicRepository,
    SkillsetRepository,
)
from practice.entities import (
    Confidence,
    Engagement,
    EngagementStatus,
    Project,
    ProjectStatus,
    ResearchTopic,
)
from practice.exceptions import DuplicateError, InvalidTransitionError, NotFoundError
from practice.repositories import Clock, IdGenerator, SourceRepository


# ---------------------------------------------------------------------------
# Write usecases
# ---------------------------------------------------------------------------


class InitializeWorkspaceUseCase:
    """Coordinate workspace bootstrapping across registries.

    Rejects duplicate clients. Seeds a "Client onboarded" engagement
    entry via the engagement repository.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        engagement_log: EngagementLogRepository,
        research: ResearchTopicRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._engagement_log = engagement_log
        self._research = research
        self._clock = clock
        self._id_gen = id_gen

    def execute(
        self, request: InitializeWorkspaceRequest
    ) -> InitializeWorkspaceResponse:
        if self._projects.client_exists(request.client):
            raise DuplicateError(f"Client workspace already exists: {request.client}")
        self._engagement_log.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                engagement="",
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title="Client onboarded",
                fields={},
            )
        )
        return InitializeWorkspaceResponse(client=request.client)


class RegisterProjectUseCase:
    """Coordinate project creation across three repositories.

    Validates the skillset exists and the slug is unique, then creates
    the project, seeds the decision log with a "Project created" entry
    using the scope as its field set, and records an engagement entry.
    All three writes must succeed together.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        decisions: DecisionRepository,
        engagement_log: EngagementLogRepository,
        skillsets: SkillsetRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._decisions = decisions
        self._engagement_log = engagement_log
        self._skillsets = skillsets
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: RegisterProjectRequest) -> RegisterProjectResponse:
        if self._skillsets.get(request.skillset) is None:
            raise NotFoundError(f"Unknown skillset: {request.skillset}")
        if (
            self._projects.get(request.client, request.engagement, request.slug)
            is not None
        ):
            raise DuplicateError(
                f"Project already exists: {request.client}/{request.slug}"
            )

        today = self._clock.today()
        self._projects.save(
            Project(
                slug=request.slug,
                client=request.client,
                engagement=request.engagement,
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
                engagement=request.engagement,
                project_slug=request.slug,
                date=today,
                timestamp=self._clock.now(),
                title="Project created",
                fields=fields,
            )
        )
        self._engagement_log.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                engagement=request.engagement,
                date=today,
                timestamp=self._clock.now(),
                title=f"Project registered: {request.slug}",
                fields=fields,
            )
        )

        return RegisterProjectResponse(
            client=request.client,
            engagement=request.engagement,
            slug=request.slug,
            skillset=request.skillset,
        )


class UpdateProjectStatusUseCase:
    """Enforce linear status transitions.

    Validates that the requested status is the next step in the
    lifecycle sequence; rejects skipped or backward transitions.
    """

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(
        self, request: UpdateProjectStatusRequest
    ) -> UpdateProjectStatusResponse:
        project = self._projects.get(
            request.client, request.engagement, request.project_slug
        )
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
    """Validate project existence then persist a decision entry.

    Generates a unique ID and delegates timestamp to the clock.
    """

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
        if (
            self._projects.get(request.client, request.engagement, request.project_slug)
            is None
        ):
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        entry_id = self._id_gen.new_id()
        self._decisions.save(
            DecisionEntry(
                id=entry_id,
                client=request.client,
                engagement=request.engagement,
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
            title=request.title,
        )


class AddEngagementEntryUseCase:
    """Validate client existence then persist an engagement entry.

    Generates a unique ID and delegates timestamp to the clock.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        engagement_log: EngagementLogRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._engagement_log = engagement_log
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: AddEngagementEntryRequest) -> AddEngagementEntryResponse:
        if not self._projects.client_exists(request.client):
            raise NotFoundError(f"Client not found: {request.client}")

        entry_id = self._id_gen.new_id()
        self._engagement_log.save(
            EngagementEntry(
                id=entry_id,
                client=request.client,
                engagement=request.engagement,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title=request.title,
                fields=request.fields,
            )
        )

        return AddEngagementEntryResponse(
            client=request.client,
            entry_id=entry_id,
            title=request.title,
        )


class RegisterResearchTopicUseCase:
    """Validate filename uniqueness then persist a research topic.

    Converts the confidence string to the Confidence enum.
    """

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
            topic=request.topic,
        )


# ---------------------------------------------------------------------------
# Read usecases
# ---------------------------------------------------------------------------


class ListProjectsUseCase:
    """Query with optional skillset and status filters.

    Converts the status string to ProjectStatus enum when present.
    """

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, request: ListProjectsRequest) -> ListProjectsResponse:
        status = ProjectStatus(request.status) if request.status else None
        projects = self._projects.list_filtered(
            request.client,
            request.engagement,
            skillset=request.skillset,
            status=status,
        )
        return ListProjectsResponse(
            client=request.client,
            projects=[ProjectInfo.from_entity(p) for p in projects],
        )


class GetProjectUseCase:
    """Look up a single project by client and slug."""

    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    def execute(self, request: GetProjectRequest) -> GetProjectResponse:
        project = self._projects.get(request.client, request.engagement, request.slug)
        if project is None:
            raise NotFoundError(f"Project not found: {request.client}/{request.slug}")
        return GetProjectResponse(
            client=request.client,
            slug=request.slug,
            project=ProjectInfo.from_entity(project),
        )


class GetProjectProgressUseCase:
    """Join decision titles against pipeline stage descriptions.

    Relies on string equality between DecisionEntry.title and
    PipelineStage.description — a fragile but intentional coupling
    documented in the conformance tests.
    """

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
        project = self._projects.get(
            request.client, request.engagement, request.project_slug
        )
        if project is None:
            raise NotFoundError(
                f"Project not found: {request.client}/{request.project_slug}"
            )

        skillset = self._skillsets.get(project.skillset)
        if skillset is None:
            raise NotFoundError(f"Skillset not found: {project.skillset}")

        decisions = self._decisions.list_all(
            request.client, request.engagement, request.project_slug
        )
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
    """Retrieve and sort decisions by timestamp.

    Returns the complete chronological log with no filtering.
    """

    def __init__(self, decisions: DecisionRepository) -> None:
        self._decisions = decisions

    def execute(self, request: ListDecisionsRequest) -> ListDecisionsResponse:
        decisions = self._decisions.list_all(
            request.client, request.engagement, request.project_slug
        )
        decisions.sort(key=lambda d: d.timestamp)
        return ListDecisionsResponse(
            client=request.client,
            project_slug=request.project_slug,
            decisions=[DecisionInfo.from_entity(d) for d in decisions],
        )


class ListResearchTopicsUseCase:
    """Retrieve all research topics for a client with no filtering."""

    def __init__(self, research: ResearchTopicRepository) -> None:
        self._research = research

    def execute(self, request: ListResearchTopicsRequest) -> ListResearchTopicsResponse:
        topics = self._research.list_all(request.client)
        return ListResearchTopicsResponse(
            client=request.client,
            topics=[ResearchTopicInfo.from_entity(t) for t in topics],
        )


# ---------------------------------------------------------------------------
# Engagement usecases
# ---------------------------------------------------------------------------


class CreateEngagementUseCase:
    """Create a new engagement with commons as the default source.

    Validates the client workspace exists and the slug is unique.
    Seeds the allowlist with "commons" and logs an engagement entry.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        engagements: EngagementRepository,
        engagement_log: EngagementLogRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._engagements = engagements
        self._engagement_log = engagement_log
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: CreateEngagementRequest) -> CreateEngagementResponse:
        if not self._projects.client_exists(request.client):
            raise NotFoundError(f"Client not found: {request.client}")
        if self._engagements.get(request.client, request.slug) is not None:
            raise DuplicateError(
                f"Engagement already exists: {request.client}/{request.slug}"
            )

        engagement = Engagement(
            slug=request.slug,
            client=request.client,
            status=EngagementStatus.PLANNING,
            allowed_sources=["commons"],
            created=self._clock.today(),
            notes=request.notes,
        )
        self._engagements.save(engagement)
        self._engagement_log.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                engagement=request.slug,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title="Engagement created",
                fields={},
            )
        )

        return CreateEngagementResponse(
            client=request.client,
            slug=request.slug,
            status=engagement.status.value,
        )


class GetEngagementUseCase:
    """Look up a single engagement by client and slug."""

    def __init__(self, engagements: EngagementRepository) -> None:
        self._engagements = engagements

    def execute(self, request: GetEngagementRequest) -> GetEngagementResponse:
        engagement = self._engagements.get(request.client, request.slug)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.slug}"
            )
        return GetEngagementResponse(
            client=request.client,
            slug=request.slug,
            engagement=EngagementInfo.from_entity(engagement),
        )


class ListEngagementsUseCase:
    """List all engagements for a client."""

    def __init__(self, engagements: EngagementRepository) -> None:
        self._engagements = engagements

    def execute(self, request: ListEngagementsRequest) -> ListEngagementsResponse:
        engagements = self._engagements.list_all(request.client)
        return ListEngagementsResponse(
            client=request.client,
            engagements=[EngagementInfo.from_entity(e) for e in engagements],
        )


class AddEngagementSourceUseCase:
    """Add a source to an engagement's allowlist.

    Validates the engagement exists, the source is installed, and the
    source is not already in the list.
    """

    def __init__(
        self,
        engagements: EngagementRepository,
        engagement_log: EngagementLogRepository,
        sources: SourceRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._engagements = engagements
        self._engagement_log = engagement_log
        self._sources = sources
        self._clock = clock
        self._id_gen = id_gen

    def execute(
        self, request: AddEngagementSourceRequest
    ) -> AddEngagementSourceResponse:
        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )
        if self._sources.get(request.source) is None:
            raise NotFoundError(f"Source not found: {request.source}")
        if request.source in engagement.allowed_sources:
            raise DuplicateError(f"Source already allowed: {request.source}")

        new_sources = engagement.allowed_sources + [request.source]
        self._engagements.save(
            engagement.model_copy(update={"allowed_sources": new_sources})
        )
        self._engagement_log.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                engagement=request.engagement,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title=f"Source added: {request.source}",
                fields={},
            )
        )

        return AddEngagementSourceResponse(
            client=request.client,
            engagement=request.engagement,
            source=request.source,
            allowed_sources=new_sources,
        )


class RemoveEngagementSourceUseCase:
    """Remove a source from an engagement's allowlist.

    Rejects removing "commons" (always required). Validates no projects
    in the engagement use skillsets from the source being removed.
    """

    def __init__(
        self,
        engagements: EngagementRepository,
        engagement_log: EngagementLogRepository,
        projects: ProjectRepository,
        sources: SourceRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._engagements = engagements
        self._engagement_log = engagement_log
        self._projects = projects
        self._sources = sources
        self._clock = clock
        self._id_gen = id_gen

    def execute(
        self, request: RemoveEngagementSourceRequest
    ) -> RemoveEngagementSourceResponse:
        if request.source == "commons":
            raise InvalidTransitionError("Cannot remove commons source")

        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )
        if request.source not in engagement.allowed_sources:
            raise NotFoundError(f"Source not in allowlist: {request.source}")

        # Check no projects use skillsets from this source
        projects = self._projects.list_filtered(request.client, request.engagement)
        for project in projects:
            if self._sources.skillset_source(project.skillset) == request.source:
                raise InvalidTransitionError(
                    f"Cannot remove source '{request.source}': "
                    f"project '{project.slug}' uses skillset '{project.skillset}' from it"
                )

        new_sources = [s for s in engagement.allowed_sources if s != request.source]
        self._engagements.save(
            engagement.model_copy(update={"allowed_sources": new_sources})
        )
        self._engagement_log.save(
            EngagementEntry(
                id=self._id_gen.new_id(),
                client=request.client,
                engagement=request.engagement,
                date=self._clock.today(),
                timestamp=self._clock.now(),
                title=f"Source removed: {request.source}",
                fields={},
            )
        )

        return RemoveEngagementSourceResponse(
            client=request.client,
            engagement=request.engagement,
            source=request.source,
            allowed_sources=new_sources,
        )
