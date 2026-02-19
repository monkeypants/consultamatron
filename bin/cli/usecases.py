"""Usecase implementations — re-exports from consulting.usecases
and wardley_mapping.usecases, plus site usecase that remains in bin/cli.
"""

from __future__ import annotations

from pathlib import Path

from bin.cli.dtos import (
    AggregateNeedsBriefRequest,
    AggregateNeedsBriefResponse,
    ListProfilesRequest,
    ListProfilesResponse,
    ListSkillsetsRequest,
    ListSkillsetsResponse,
    ListSourcesRequest,
    ListSourcesResponse,
    ObservationNeedInfo,
    PackItemInfo,
    PackStatusRequest,
    PackStatusResponse,
    ProfileInfo,
    RegisterProspectusRequest,
    RegisterProspectusResponse,
    RenderSiteRequest,
    RenderSiteResponse,
    RouteObservationsRequest,
    RouteObservationsResponse,
    RoutingDestinationInfo,
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
from practice.entities import (
    Observation,
    ObservationNeed,
    PackFreshness,
    Profile,
    RoutingDestination,
    Skillset,
    SkillsetSource,
)
from practice.exceptions import DuplicateError, NotFoundError
from practice.repositories import (
    FreshnessInspector,
    NeedsReader,
    ObservationWriter,
    PackNudger,
    ProfileRepository,
    ProjectPresenter,
    SiteRenderer,
    SourceRepository,
)
from practice.routing import build_routing_allow_list

__all__ = [
    "AddEngagementEntryUseCase",
    "AggregateNeedsBriefUseCase",
    "RouteObservationsUseCase",
    "GetProjectProgressUseCase",
    "GetProjectUseCase",
    "InitializeWorkspaceUseCase",
    "ListDecisionsUseCase",
    "ListProfilesUseCase",
    "ListProjectsUseCase",
    "ListSkillsetsUseCase",
    "ListSourcesUseCase",
    "PackStatusUseCase",
    "ListResearchTopicsUseCase",
    "RecordDecisionUseCase",
    "RegisterProjectUseCase",
    "RegisterProspectusUseCase",
    "RegisterResearchTopicUseCase",
    "RenderSiteUseCase",
    "ShowProfileUseCase",
    "ShowSkillsetUseCase",
    "ShowSourceUseCase",
    "SkillPathUseCase",
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


# ---------------------------------------------------------------------------
# Observation routing — needs aggregation
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
    ) -> None:
        self._engagements = engagements
        self._projects = projects
        self._sources = sources
        self._needs_reader = needs_reader
        self._pack_nudger = pack_nudger

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

        return AggregateNeedsBriefResponse(
            needs=[_need_to_info(n) for n in needs],
            destinations=[
                RoutingDestinationInfo(owner_type=d.owner_type, owner_ref=d.owner_ref)
                for d in allow_list.destinations
            ],
            nudges=nudges,
        )


class RouteObservationsUseCase:
    """Route observations to their declared destinations.

    Rebuilds the allow list, filters each observation's destinations
    against it, writes eligible observations via ObservationWriter,
    and counts routed vs rejected.
    """

    def __init__(
        self,
        engagements: EngagementRepository,
        projects: ProjectRepository,
        sources: SourceRepository,
        observation_writer: ObservationWriter,
    ) -> None:
        self._engagements = engagements
        self._projects = projects
        self._sources = sources
        self._writer = observation_writer

    def execute(self, request: RouteObservationsRequest) -> RouteObservationsResponse:
        import json

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

        raw_observations = json.loads(request.observations)
        routed = 0
        rejected = 0

        for raw in raw_observations:
            eligible = []
            ineligible_count = 0
            for dest_data in raw.get("destinations", []):
                key = (dest_data["owner_type"], dest_data["owner_ref"])
                if key in allowed_set:
                    eligible.append(
                        RoutingDestination(
                            owner_type=dest_data["owner_type"],
                            owner_ref=dest_data["owner_ref"],
                        )
                    )
                else:
                    ineligible_count += 1

            rejected += ineligible_count

            if eligible:
                obs = Observation(
                    slug=raw["slug"],
                    source_inflection=raw["source_inflection"],
                    need_refs=raw.get("need_refs", []),
                    content=raw.get("content", ""),
                    destinations=eligible,
                )
                self._writer.write(obs)
                routed += len(eligible)

        return RouteObservationsResponse(routed=routed, rejected=rejected)
