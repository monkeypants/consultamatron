"""Usecase implementations for consulting practice accounting.

Each usecase has an execute(request) -> response method satisfying
the UseCase protocol. Repository dependencies are injected via
constructor.
"""

from __future__ import annotations

from pathlib import Path

from bin.cli.dtos import (
    AddEngagementEntryRequest,
    AddEngagementEntryResponse,
    AddEngagementSourceRequest,
    AddEngagementSourceResponse,
    CreateEngagementRequest,
    CreateEngagementResponse,
    DecisionInfo,
    EngagementDashboardInfo,
    EngagementInfo,
    EngagementStatusRequest,
    EngagementStatusResponse,
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
    ListPantheonRequest,
    ListPantheonResponse,
    ListProfilesRequest,
    ListProfilesResponse,
    ListProjectsRequest,
    ListProjectsResponse,
    ListResearchTopicsRequest,
    ListResearchTopicsResponse,
    ListSkillsetsRequest,
    ListSkillsetsResponse,
    ListSourcesRequest,
    ListSourcesResponse,
    LuminarySummary,
    NextActionRequest,
    NextActionResponse,
    GetWipRequest,
    GetWipResponse,
    PackItemInfo,
    PackStatusRequest,
    PackStatusResponse,
    WipEngagementInfo,
    WipProjectInfo,
    ProfileInfo,
    ProjectInfo,
    ProjectPositionInfo,
    RecordDecisionRequest,
    RecordDecisionResponse,
    RegisterProjectRequest,
    RegisterProjectResponse,
    RegisterProspectusRequest,
    RegisterProspectusResponse,
    RegisterResearchTopicRequest,
    RegisterResearchTopicResponse,
    RemoveEngagementSourceRequest,
    RemoveEngagementSourceResponse,
    RenderSiteRequest,
    RenderSiteResponse,
    ResearchTopicInfo,
    ShowProfileRequest,
    ShowProfileResponse,
    ShowSkillsetRequest,
    ShowSkillsetResponse,
    ShowSourceRequest,
    ShowSourceResponse,
    SkillPathRequest,
    SkillPathResponse,
    SkillsetInfo,
    SkillsetStageInfo,
    SourceInfo,
    StageProgress,
    UpdateProjectStatusRequest,
    UpdateProjectStatusResponse,
    UpdateProspectusRequest,
    UpdateProspectusResponse,
    AggregateNeedsBriefRequest,
    AggregateNeedsBriefResponse,
    FlushObservationsRequest,
    FlushObservationsResponse,
    ObservationNeedInfo,
    RoutingDestinationInfo,
)
from bin.cli.infrastructure.skillset_scaffold import SkillsetScaffold
from practice.entities import (
    Confidence,
    DecisionEntry,
    Engagement,
    EngagementEntry,
    EngagementStatus,
    Observation,
    ObservationNeed,
    PackFreshness,
    Pipeline,
    Profile,
    Project,
    ProjectStatus,
    ResearchTopic,
    RoutingDestination,
    SkillsetSource,
)
from practice.exceptions import DuplicateError, InvalidTransitionError, NotFoundError
from practice.repositories import (
    Clock,
    DecisionRepository,
    EngagementLogRepository,
    EngagementRepository,
    FreshnessInspector,
    GateInspector,
    IdGenerator,
    NeedsReader,
    ObservationWriter,
    PackNudger,
    PendingObservationStore,
    ProfileRepository,
    ProjectPresenter,
    ProjectRepository,
    ResearchTopicRepository,
    SiteRenderer,
    SkillsetKnowledge,
    SkillsetRepository,
    SourceRepository,
)
from practice.routing import build_routing_allow_list


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

    Validates the engagement exists and is in PLANNING or ACTIVE status,
    the skillset exists, the skillset's source is in the engagement's
    allowed_sources, and the slug is unique.  Then creates the project,
    seeds the decision log with a "Project created" entry using the scope
    as its field set, and records an engagement entry.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        decisions: DecisionRepository,
        engagement_log: EngagementLogRepository,
        engagements: EngagementRepository,
        skillsets: SkillsetRepository,
        sources: SourceRepository,
        clock: Clock,
        id_gen: IdGenerator,
    ) -> None:
        self._projects = projects
        self._decisions = decisions
        self._engagement_log = engagement_log
        self._engagements = engagements
        self._skillsets = skillsets
        self._sources = sources
        self._clock = clock
        self._id_gen = id_gen

    def execute(self, request: RegisterProjectRequest) -> RegisterProjectResponse:
        # Validate engagement
        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )
        if engagement.status not in (
            EngagementStatus.PLANNING,
            EngagementStatus.ACTIVE,
        ):
            raise InvalidTransitionError(
                f"Engagement '{request.engagement}' is {engagement.status.value}, "
                f"must be planning or active to add projects"
            )

        # Validate skillset and source allowlist
        if self._skillsets.get(request.skillset) is None:
            raise NotFoundError(f"Unknown skillset: {request.skillset}")
        source_slug = self._sources.skillset_source(request.skillset)
        if source_slug is not None and source_slug not in engagement.allowed_sources:
            raise InvalidTransitionError(
                f"Source '{source_slug}' for skillset '{request.skillset}' "
                f"is not in engagement's allowed sources"
            )

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
        pack_nudger: PackNudger | None = None,
    ) -> None:
        self._projects = projects
        self._decisions = decisions
        self._skillsets = skillsets
        self._pack_nudger = pack_nudger

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

        for stage in sorted(skillset.stages, key=lambda s: s.order):
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
    """Create a new engagement with commons and personal as default sources.

    Validates the client workspace exists and the slug is unique.
    Seeds the allowlist with "commons" and "personal", then logs an
    engagement entry.
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
            allowed_sources=["commons", "personal"],
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
        if request.source in ("commons", "personal"):
            raise InvalidTransitionError(f"Cannot remove {request.source} source")

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


# ---------------------------------------------------------------------------
# Engagement protocol usecases
# ---------------------------------------------------------------------------


class GetEngagementStatusUseCase:
    """Derive engagement state from gate artifacts on disk."""

    def __init__(
        self,
        engagements: EngagementRepository,
        projects: ProjectRepository,
        skillsets: SkillsetRepository,
        gate_inspector: GateInspector,
        pack_nudger: PackNudger | None = None,
    ) -> None:
        self._engagements = engagements
        self._projects = projects
        self._skillsets = skillsets
        self._gate_inspector = gate_inspector
        self._pack_nudger = pack_nudger

    def execute(self, request: EngagementStatusRequest) -> EngagementStatusResponse:
        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )

        projects = self._projects.list_filtered(request.client, request.engagement)
        positions: list[ProjectPositionInfo] = []

        for project in projects:
            skillset = self._skillsets.get(project.skillset)
            if skillset is None or not skillset.is_implemented:
                continue

            stages = sorted(skillset.stages, key=lambda s: s.order)
            completed_gates: list[str] = []
            next_gate: str | None = None
            current_stage = len(stages) + 1  # past the end = all complete

            for i, stage in enumerate(stages):
                if self._gate_inspector.exists(
                    request.client,
                    request.engagement,
                    project.slug,
                    stage.produces_gate,
                ):
                    completed_gates.append(stage.produces_gate)
                elif next_gate is None:
                    next_gate = stage.produces_gate
                    current_stage = i + 1

            positions.append(
                ProjectPositionInfo(
                    project_slug=project.slug,
                    skillset=project.skillset,
                    current_stage=current_stage,
                    total_stages=len(stages),
                    completed_gates=completed_gates,
                    next_gate=next_gate,
                )
            )

        skillset_names = [p.skillset for p in positions]
        nudges = self._pack_nudger.check(skillset_names) if self._pack_nudger else []

        return EngagementStatusResponse(
            dashboard=EngagementDashboardInfo(
                engagement_slug=request.engagement,
                status=engagement.status.value,
                projects=positions,
            ),
            nudges=nudges,
        )


class GetNextActionUseCase:
    """Determine the recommended next skill execution."""

    def __init__(
        self,
        engagements: EngagementRepository,
        projects: ProjectRepository,
        skillsets: SkillsetRepository,
        gate_inspector: GateInspector,
        pack_nudger: PackNudger | None = None,
    ) -> None:
        self._engagements = engagements
        self._projects = projects
        self._skillsets = skillsets
        self._gate_inspector = gate_inspector
        self._pack_nudger = pack_nudger

    def execute(self, request: NextActionRequest) -> NextActionResponse:
        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )

        projects = self._projects.list_filtered(request.client, request.engagement)
        projects.sort(key=lambda p: p.created)
        skillset_names = [p.skillset for p in projects]
        nudges = self._pack_nudger.check(skillset_names) if self._pack_nudger else []

        for project in projects:
            skillset = self._skillsets.get(project.skillset)
            if skillset is None or not skillset.is_implemented:
                continue

            stages = sorted(skillset.stages, key=lambda s: s.order)
            for stage in stages:
                gate_exists = self._gate_inspector.exists(
                    request.client,
                    request.engagement,
                    project.slug,
                    stage.produces_gate,
                )
                if gate_exists:
                    continue

                # Found first incomplete stage
                if stage.prerequisite_gate:
                    prereq_exists = self._gate_inspector.exists(
                        request.client,
                        request.engagement,
                        project.slug,
                        stage.prerequisite_gate,
                    )
                else:
                    prereq_exists = True

                if not prereq_exists:
                    return NextActionResponse(
                        skill=None,
                        project_slug=project.slug,
                        reason=(
                            f"Blocked: prerequisite {stage.prerequisite_gate} "
                            f"missing for {project.slug}"
                        ),
                        nudges=nudges,
                    )

                return NextActionResponse(
                    skill=stage.skill,
                    project_slug=project.slug,
                    reason=(
                        f"Run {stage.skill} for {project.slug}"
                        + (
                            f" (prerequisite {stage.prerequisite_gate} exists)"
                            if stage.prerequisite_gate
                            else ""
                        )
                    ),
                    nudges=nudges,
                )

        return NextActionResponse(
            skill=None,
            project_slug=None,
            reason="All projects complete — run review",
            nudges=nudges,
        )


# ---------------------------------------------------------------------------
# RenderSite (cross-BC orchestration)
# ---------------------------------------------------------------------------


class RenderSiteUseCase:
    """Coordinate site rendering across project presenters."""

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
# Skillset (cross-BC, aggregates from all BCs)
# ---------------------------------------------------------------------------


def _skillset_to_info(s: Pipeline) -> SkillsetInfo:
    return SkillsetInfo(
        name=s.name,
        display_name=s.display_name,
        description=s.description,
        slug_pattern=s.slug_pattern,
        is_implemented=s.is_implemented,
        problem_domain="",
        deliverables=[],
        value_proposition="",
        classification=[],
        evidence=[],
        stages=[
            SkillsetStageInfo(
                order=st.order,
                skill=st.skill,
                description=st.description,
                prerequisite_gate=st.prerequisite_gate,
                produces_gate=st.produces_gate,
            )
            for st in s.stages
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
# Source (cross-BC, lists installed sources)
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


# ---------------------------------------------------------------------------
# Profile — named collections of skillsets
# ---------------------------------------------------------------------------


def _profile_to_info(profile: Profile, source: str) -> ProfileInfo:
    return ProfileInfo(
        name=profile.name,
        display_name=profile.display_name,
        description=profile.description,
        skillsets=list(profile.skillsets),
        source=source,
    )


class ListProfilesUseCase:
    """List all registered profiles."""

    def __init__(self, profiles: ProfileRepository) -> None:
        self._profiles = profiles

    def execute(self, request: ListProfilesRequest) -> ListProfilesResponse:
        return ListProfilesResponse(
            profiles=[_profile_to_info(p, s) for p, s in self._profiles.list_all()],
        )


class ShowProfileUseCase:
    """Show details of a registered profile by name."""

    def __init__(self, profiles: ProfileRepository) -> None:
        self._profiles = profiles

    def execute(self, request: ShowProfileRequest) -> ShowProfileResponse:
        result = self._profiles.get(request.name)
        if result is None:
            raise NotFoundError(f"Profile not found: {request.name}")
        profile, source = result
        return ShowProfileResponse(profile=_profile_to_info(profile, source))


# ---------------------------------------------------------------------------
# SkillPath — locate a skill directory by name
# ---------------------------------------------------------------------------


class SkillPathUseCase:
    """Find the filesystem path to a skill by name."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root

    def execute(self, request: SkillPathRequest) -> SkillPathResponse:
        for container in ("commons", "personal", "partnerships"):
            container_dir = self._repo_root / container
            if not container_dir.is_dir():
                continue
            for skill_md in container_dir.rglob(f"{request.name}/SKILL.md"):
                return SkillPathResponse(path=str(skill_md.parent))

        raise NotFoundError(f"Skill not found: {request.name}")


# ---------------------------------------------------------------------------
# PackStatus — knowledge pack freshness inspection
# ---------------------------------------------------------------------------


def _freshness_to_response(freshness: PackFreshness) -> PackStatusResponse:
    """Convert a PackFreshness tree into a PackStatusResponse tree."""
    return PackStatusResponse(
        pack_root=freshness.pack_root,
        compilation_state=freshness.compilation_state.value,
        deep_state=freshness.deep_state.value,
        items=[
            PackItemInfo(
                name=item.name,
                is_composite=item.is_composite,
                state=item.state,
            )
            for item in freshness.items
        ],
        children=[_freshness_to_response(c) for c in freshness.children],
    )


class PackStatusUseCase:
    """Show compilation freshness of a knowledge pack."""

    def __init__(self, inspector: FreshnessInspector) -> None:
        self._inspector = inspector

    def execute(self, request: PackStatusRequest) -> PackStatusResponse:
        root = Path(request.path).resolve()
        if not (root / "index.md").is_file():
            raise NotFoundError(f"No pack manifest at: {root}/index.md")
        freshness = self._inspector.assess(root)
        return _freshness_to_response(freshness)


class GetWipStatusUseCase:
    """Scan all clients for in-progress work.

    Walks every client workspace, finds non-closed engagements with
    non-closed projects, checks pipeline gate existence, and returns
    only projects that have incomplete pipelines.
    """

    def __init__(
        self,
        projects: ProjectRepository,
        engagements: EngagementRepository,
        skillsets: SkillsetRepository,
        gate_inspector: GateInspector,
        pack_nudger: PackNudger | None = None,
    ) -> None:
        self._projects = projects
        self._engagements = engagements
        self._skillsets = skillsets
        self._gate_inspector = gate_inspector
        self._pack_nudger = pack_nudger

    def execute(self, request: GetWipRequest) -> GetWipResponse:
        if request.client is not None:
            clients = [request.client]
        else:
            clients = self._projects.list_clients()

        result_engagements: list[WipEngagementInfo] = []
        skillset_names: list[str] = []

        for client in clients:
            engagements = self._engagements.list_all(client)
            for eng in engagements:
                if eng.status == EngagementStatus.CLOSED:
                    continue

                projects = self._projects.list_filtered(client, eng.slug)
                wip_projects: list[WipProjectInfo] = []

                for project in projects:
                    if project.status == ProjectStatus.CLOSED:
                        continue

                    skillset = self._skillsets.get(project.skillset)
                    if skillset is None or not skillset.is_implemented:
                        continue

                    skillset_names.append(project.skillset)
                    stages = sorted(skillset.stages, key=lambda s: s.order)

                    completed_count = 0
                    next_skill: str | None = None
                    next_gate: str | None = None
                    blocked = False
                    blocked_reason: str | None = None

                    for stage in stages:
                        gate_exists = self._gate_inspector.exists(
                            client,
                            eng.slug,
                            project.slug,
                            stage.produces_gate,
                        )
                        if gate_exists:
                            completed_count += 1
                            continue

                        if next_skill is None:
                            next_skill = stage.skill
                            next_gate = stage.produces_gate
                            if stage.prerequisite_gate:
                                prereq_exists = self._gate_inspector.exists(
                                    client,
                                    eng.slug,
                                    project.slug,
                                    stage.prerequisite_gate,
                                )
                                if not prereq_exists:
                                    blocked = True
                                    blocked_reason = f"prerequisite {stage.prerequisite_gate} missing"

                    if completed_count == len(stages):
                        continue

                    wip_projects.append(
                        WipProjectInfo(
                            client=client,
                            engagement=eng.slug,
                            project_slug=project.slug,
                            skillset=project.skillset,
                            current_stage=completed_count + 1,
                            total_stages=len(stages),
                            next_skill=next_skill,
                            next_gate=next_gate,
                            blocked=blocked,
                            blocked_reason=blocked_reason,
                        )
                    )

                if wip_projects:
                    result_engagements.append(
                        WipEngagementInfo(
                            client=client,
                            engagement_slug=eng.slug,
                            status=eng.status.value,
                            projects=wip_projects,
                        )
                    )

        nudges = self._pack_nudger.check(skillset_names) if self._pack_nudger else []

        return GetWipResponse(
            engagements=result_engagements,
            nudges=nudges,
        )


# ---------------------------------------------------------------------------
# Pantheon (cross-skillset luminary aggregation)
# ---------------------------------------------------------------------------


def _parse_pantheon(content: str) -> list[tuple[str, str]]:
    """Split pantheon markdown into (name, summary) pairs.

    Each luminary is a ``## Name`` section. Text before the first
    heading is skipped. Empty sections are skipped.
    """
    results: list[tuple[str, str]] = []
    sections = content.split("## ")
    for section in sections[1:]:  # skip preamble before first ##
        lines = section.strip().splitlines()
        if not lines:
            continue
        name = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        if not body:
            continue
        results.append((name, body))
    return results


class ListPantheonUseCase:
    """Aggregate luminaries from skillset knowledge packs."""

    def __init__(self, knowledge: SkillsetKnowledge) -> None:
        self._knowledge = knowledge

    def execute(self, request: ListPantheonRequest) -> ListPantheonResponse:
        luminaries: list[LuminarySummary] = []
        for skillset_name in request.skillset_names:
            content = self._knowledge.read_item(skillset_name, "pantheon")
            if content is None:
                continue
            for name, summary in _parse_pantheon(content):
                luminaries.append(
                    LuminarySummary(
                        name=name,
                        skillset=skillset_name,
                        summary=summary,
                    )
                )
        return ListPantheonResponse(luminaries=luminaries)


# ---------------------------------------------------------------------------
# Observation routing usecases
# ---------------------------------------------------------------------------


def _need_to_info(n: ObservationNeed) -> ObservationNeedInfo:
    return ObservationNeedInfo(
        slug=n.slug,
        owner_type=n.owner_type,
        owner_ref=n.owner_ref,
        level=n.level,
        need=n.need,
        rationale=n.rationale,
        lifecycle_moment=n.lifecycle_moment,
        served=n.served,
    )


class AggregateNeedsBriefUseCase:
    """Aggregate observation needs for an engagement context.

    Builds the routing allow list, gathers type- and instance-level
    needs for each eligible destination, and returns a structured brief.
    """

    def __init__(
        self,
        engagements: EngagementRepository,
        projects: ProjectRepository,
        sources: SourceRepository,
        needs_reader: NeedsReader,
        pack_nudger: PackNudger,
        workspace_root: Path,
    ) -> None:
        self._engagements = engagements
        self._projects = projects
        self._sources = sources
        self._needs_reader = needs_reader
        self._pack_nudger = pack_nudger
        self._workspace_root = workspace_root

    def execute(
        self, request: AggregateNeedsBriefRequest
    ) -> AggregateNeedsBriefResponse:
        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )

        projects = self._projects.list_filtered(request.client, request.engagement)

        # Resolve sources from engagement config
        resolved_sources = []
        for source_slug in engagement.allowed_sources:
            src = self._sources.get(source_slug)
            if src:
                resolved_sources.append(src)

        allow_list = build_routing_allow_list(
            client=request.client,
            engagement=engagement,
            projects=projects,
            sources=resolved_sources,
        )

        # Gather needs for each eligible destination
        needs: list[ObservationNeed] = []
        seen_types: set[str] = set()
        for dest in allow_list.destinations:
            # Type-level needs (once per owner_type)
            if dest.owner_type not in seen_types:
                seen_types.add(dest.owner_type)
                needs.extend(self._needs_reader.type_level_needs(dest.owner_type))
            # Instance-level needs
            needs.extend(
                self._needs_reader.instance_needs(dest.owner_type, dest.owner_ref)
            )

        nudges = self._pack_nudger.check()

        pending_dir = (
            self._workspace_root
            / request.client
            / "engagements"
            / request.engagement
            / ".observations-pending"
        )

        return AggregateNeedsBriefResponse(
            needs=[_need_to_info(n) for n in needs],
            destinations=[
                RoutingDestinationInfo(owner_type=d.owner_type, owner_ref=d.owner_ref)
                for d in allow_list.destinations
            ],
            pending_dir=str(pending_dir),
            inflection=request.inflection,
            nudges=nudges,
        )


class FlushObservationsUseCase:
    """Flush pending observations to routed destinations.

    Reads pending observation files, resolves need_refs to
    destinations via the needs aggregation, filters through the
    allow list, writes via ObservationWriter, and cleans up.
    """

    def __init__(
        self,
        engagements: EngagementRepository,
        projects: ProjectRepository,
        sources: SourceRepository,
        needs_reader: NeedsReader,
        observation_writer: ObservationWriter,
        pending_store: PendingObservationStore,
        workspace_root: Path,
    ) -> None:
        self._engagements = engagements
        self._projects = projects
        self._sources = sources
        self._needs_reader = needs_reader
        self._writer = observation_writer
        self._pending_store = pending_store
        self._workspace_root = workspace_root

    def execute(self, request: FlushObservationsRequest) -> FlushObservationsResponse:
        engagement = self._engagements.get(request.client, request.engagement)
        if engagement is None:
            raise NotFoundError(
                f"Engagement not found: {request.client}/{request.engagement}"
            )

        projects = self._projects.list_filtered(request.client, request.engagement)

        resolved_sources = []
        for source_slug in engagement.allowed_sources:
            src = self._sources.get(source_slug)
            if src:
                resolved_sources.append(src)

        allow_list = build_routing_allow_list(
            client=request.client,
            engagement=engagement,
            projects=projects,
            sources=resolved_sources,
        )
        allowed_set = {(d.owner_type, d.owner_ref) for d in allow_list.destinations}

        # Build need_slug → destinations mapping
        need_to_dests: dict[str, list[RoutingDestination]] = {}
        seen_types: set[str] = set()
        for dest in allow_list.destinations:
            if dest.owner_type not in seen_types:
                seen_types.add(dest.owner_type)
                for need in self._needs_reader.type_level_needs(dest.owner_type):
                    need_to_dests.setdefault(need.slug, []).append(dest)
            for need in self._needs_reader.instance_needs(
                dest.owner_type, dest.owner_ref
            ):
                need_to_dests.setdefault(need.slug, []).append(dest)

        pending = self._pending_store.read_pending(request.client, request.engagement)

        routed = 0
        rejected = 0
        flushed = 0

        for obs in pending:
            # Resolve need_refs → destinations
            resolved_dests: dict[tuple[str, str], RoutingDestination] = {}
            for ref in obs.need_refs:
                for dest in need_to_dests.get(ref, []):
                    key = (dest.owner_type, dest.owner_ref)
                    if key in allowed_set:
                        resolved_dests[key] = dest

            if resolved_dests:
                obs_with_dests = Observation(
                    slug=obs.slug,
                    source_inflection=obs.source_inflection,
                    need_refs=obs.need_refs,
                    content=obs.content,
                    destinations=list(resolved_dests.values()),
                )
                self._writer.write(obs_with_dests)
                routed += len(resolved_dests)
            flushed += 1

        if pending:
            self._pending_store.clear_pending(request.client, request.engagement)

        return FlushObservationsResponse(
            routed=routed, rejected=rejected, flushed=flushed
        )
