"""Dependency injection container.

Single responsibility: know which implementations to use and configure
them with the right paths. Consumers depend on protocol types, never
on implementations directly.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from bin.cli.config import Config
from bin.cli.infrastructure.code_skillset_repository import CodeSkillsetRepository
from practice.bc_discovery import discover_all_bc_modules
from bin.cli.infrastructure.filesystem_profile_repository import (
    FilesystemProfileRepository,
)
from bin.cli.infrastructure.filesystem_freshness_inspector import (
    FilesystemFreshnessInspector,
)
from bin.cli.infrastructure.filesystem_knowledge_pack_repository import (
    FilesystemKnowledgePackRepository,
)
from bin.cli.infrastructure.filesystem_skill_manifest_repository import (
    FilesystemSkillManifestRepository,
)
from bin.cli.infrastructure.pack_nudger import FilesystemPackNudger
from bin.cli.infrastructure.filesystem_gate_inspector import FilesystemGateInspector
from bin.cli.infrastructure.filesystem_source_repository import (
    FilesystemSourceRepository,
)
from bin.cli.infrastructure.skillset_scaffold import SkillsetScaffold
from bin.cli.infrastructure.jinja_renderer import JinjaSiteRenderer
from bin.cli.infrastructure.json_repos import (
    JsonDecisionRepository,
    JsonEngagementEntityRepository,
    JsonEngagementLogRepository,
    JsonProjectRepository,
    JsonResearchTopicRepository,
)
from bin.cli.usecases import (
    ListProfilesUseCase,
    ListSkillsetsUseCase,
    ListSourcesUseCase,
    PackStatusUseCase,
    RegisterProspectusUseCase,
    RenderSiteUseCase,
    ShowProfileUseCase,
    ShowSkillsetUseCase,
    ShowSourceUseCase,
    SkillPathUseCase,
    UpdateProspectusUseCase,
)
from consulting.repositories import (
    DecisionRepository,
    EngagementLogRepository,
    EngagementRepository,
    ProjectRepository,
    ResearchTopicRepository,
    SkillsetRepository,
)
from consulting.usecases import (
    AddEngagementEntryUseCase,
    AddEngagementSourceUseCase,
    CreateEngagementUseCase,
    GetEngagementStatusUseCase,
    GetEngagementUseCase,
    GetNextActionUseCase,
    GetProjectProgressUseCase,
    GetProjectUseCase,
    GetWipStatusUseCase,
    InitializeWorkspaceUseCase,
    ListDecisionsUseCase,
    ListEngagementsUseCase,
    ListProjectsUseCase,
    ListResearchTopicsUseCase,
    RecordDecisionUseCase,
    RegisterProjectUseCase,
    RegisterResearchTopicUseCase,
    RemoveEngagementSourceUseCase,
    UpdateProjectStatusUseCase,
)
from practice.repositories import (
    Clock,
    FreshnessInspector,
    GateInspector,
    IdGenerator,
    KnowledgePackRepository,
    PackNudger,
    ProfileRepository,
    ProjectPresenter,
    SiteRenderer,
    SkillManifestRepository,
    SourceRepository,
)


# ---------------------------------------------------------------------------
# Infrastructure service implementations
# ---------------------------------------------------------------------------


class WallClock:
    """Production clock — real time anchored to UTC."""

    _tz = timezone.utc

    def today(self) -> date:
        return datetime.now(self._tz).date()

    def now(self) -> datetime:
        return datetime.now(self._tz)

    def tz(self) -> timezone:
        return self._tz


class UuidGenerator:
    """Production identity generator — returns a random UUID."""

    def new_id(self) -> str:
        return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Container
# ---------------------------------------------------------------------------


class Container:
    """Wires repository implementations and usecases.

    Usage:
        config = Config.from_repo_root(Path("."))
        c = Container(config)
        resp = c.register_project_usecase.execute(req)
    """

    def __init__(self, config: Config) -> None:
        self.config = config

        # -- Infrastructure services ----------------------------------------
        self.clock: Clock = WallClock()
        self.id_gen: IdGenerator = UuidGenerator()

        # -- Repositories --------------------------------------------------
        self.skillsets: SkillsetRepository = CodeSkillsetRepository(
            config.repo_root,
        )
        self.projects: ProjectRepository = JsonProjectRepository(
            config.workspace_root,
        )
        self.decisions: DecisionRepository = JsonDecisionRepository(
            config.workspace_root,
        )
        self.engagement_log: EngagementLogRepository = JsonEngagementLogRepository(
            config.workspace_root,
        )
        self.research: ResearchTopicRepository = JsonResearchTopicRepository(
            config.workspace_root,
        )
        self.engagement_entities: EngagementRepository = JsonEngagementEntityRepository(
            config.workspace_root
        )
        self.sources: SourceRepository = FilesystemSourceRepository(
            config.repo_root, self.skillsets
        )
        self.profiles: ProfileRepository = FilesystemProfileRepository(
            config.repo_root, self.sources
        )
        self.freshness_inspector: FreshnessInspector = FilesystemFreshnessInspector()
        self.gate_inspector: GateInspector = FilesystemGateInspector(
            config.workspace_root,
        )
        self.site_renderer: SiteRenderer = JinjaSiteRenderer(
            workspace_root=config.workspace_root,
            repo_root=config.repo_root,
        )
        self.skill_manifests: SkillManifestRepository = (
            FilesystemSkillManifestRepository(config.repo_root)
        )
        self.knowledge_packs: KnowledgePackRepository = (
            FilesystemKnowledgePackRepository(config.repo_root)
        )

        # -- BC discovery (presenters + service hooks) -------------------------
        self.presenters: dict[str, ProjectPresenter] = {}
        skillset_bc_dirs: dict[str, Path] = {}
        for mod in discover_all_bc_modules(config.repo_root):
            for skillset in getattr(mod, "SKILLSETS", []):
                skillset_bc_dirs[skillset.name] = Path(mod.__file__).resolve().parent
            factory = getattr(mod, "PRESENTER_FACTORY", None)
            if factory is not None:
                entries = factory if isinstance(factory, list) else [factory]
                for skillset_name, create_fn in entries:
                    self.presenters[skillset_name] = create_fn(
                        config.workspace_root, config.repo_root
                    )
            register = getattr(mod, "register_services", None)
            if register is not None:
                register(self)

        self.pack_nudger: PackNudger = FilesystemPackNudger(
            config.repo_root,
            self.freshness_inspector,
            skillset_bc_dirs,
            knowledge_packs=self.knowledge_packs,
        )

        # -- Write usecases ------------------------------------------------
        self.initialize_workspace_usecase = InitializeWorkspaceUseCase(
            projects=self.projects,
            engagement_log=self.engagement_log,
            research=self.research,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.register_project_usecase = RegisterProjectUseCase(
            projects=self.projects,
            decisions=self.decisions,
            engagement_log=self.engagement_log,
            engagements=self.engagement_entities,
            skillsets=self.skillsets,
            sources=self.sources,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.update_project_status_usecase = UpdateProjectStatusUseCase(
            projects=self.projects,
        )
        self.record_decision_usecase = RecordDecisionUseCase(
            projects=self.projects,
            decisions=self.decisions,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.add_engagement_entry_usecase = AddEngagementEntryUseCase(
            projects=self.projects,
            engagement_log=self.engagement_log,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.register_research_topic_usecase = RegisterResearchTopicUseCase(
            projects=self.projects,
            research=self.research,
            clock=self.clock,
        )
        self.create_engagement_usecase = CreateEngagementUseCase(
            projects=self.projects,
            engagements=self.engagement_entities,
            engagement_log=self.engagement_log,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.add_engagement_source_usecase = AddEngagementSourceUseCase(
            engagements=self.engagement_entities,
            engagement_log=self.engagement_log,
            sources=self.sources,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.remove_engagement_source_usecase = RemoveEngagementSourceUseCase(
            engagements=self.engagement_entities,
            engagement_log=self.engagement_log,
            projects=self.projects,
            sources=self.sources,
            clock=self.clock,
            id_gen=self.id_gen,
        )

        # -- Read usecases -------------------------------------------------
        self.list_projects_usecase = ListProjectsUseCase(
            projects=self.projects,
        )
        self.get_project_usecase = GetProjectUseCase(
            projects=self.projects,
        )
        self.get_project_progress_usecase = GetProjectProgressUseCase(
            projects=self.projects,
            decisions=self.decisions,
            skillsets=self.skillsets,
            pack_nudger=self.pack_nudger,
        )
        self.list_decisions_usecase = ListDecisionsUseCase(
            decisions=self.decisions,
        )
        self.list_research_topics_usecase = ListResearchTopicsUseCase(
            research=self.research,
        )
        self.get_engagement_usecase = GetEngagementUseCase(
            engagements=self.engagement_entities,
        )
        self.list_engagements_usecase = ListEngagementsUseCase(
            engagements=self.engagement_entities,
        )
        self.list_skillsets_usecase = ListSkillsetsUseCase(
            skillsets=self.skillsets,
            engagements=self.engagement_entities,
            sources=self.sources,
        )
        self.show_skillset_usecase = ShowSkillsetUseCase(
            skillsets=self.skillsets,
        )
        self.list_sources_usecase = ListSourcesUseCase(
            sources=self.sources,
        )
        self.show_source_usecase = ShowSourceUseCase(
            sources=self.sources,
        )
        self.list_profiles_usecase = ListProfilesUseCase(
            profiles=self.profiles,
        )
        self.show_profile_usecase = ShowProfileUseCase(
            profiles=self.profiles,
        )
        self.skill_path_usecase = SkillPathUseCase(
            repo_root=config.repo_root,
        )
        self.render_site_usecase = RenderSiteUseCase(
            projects=self.projects,
            research=self.research,
            renderer=self.site_renderer,
            presenters=self.presenters,
        )

        # -- Engagement protocol usecases ----------------------------------
        self.get_engagement_status_usecase = GetEngagementStatusUseCase(
            engagements=self.engagement_entities,
            projects=self.projects,
            skillsets=self.skillsets,
            gate_inspector=self.gate_inspector,
            pack_nudger=self.pack_nudger,
        )
        self.get_next_action_usecase = GetNextActionUseCase(
            engagements=self.engagement_entities,
            projects=self.projects,
            skillsets=self.skillsets,
            gate_inspector=self.gate_inspector,
            pack_nudger=self.pack_nudger,
        )
        self.get_wip_status_usecase = GetWipStatusUseCase(
            projects=self.projects,
            engagements=self.engagement_entities,
            skillsets=self.skillsets,
            gate_inspector=self.gate_inspector,
            pack_nudger=self.pack_nudger,
        )

        # -- Prospectus usecases -------------------------------------------
        self.scaffold = SkillsetScaffold(config.repo_root)
        self.register_prospectus_usecase = RegisterProspectusUseCase(
            skillsets=self.skillsets,
            scaffold=self.scaffold,
        )
        self.update_prospectus_usecase = UpdateProspectusUseCase(
            skillsets=self.skillsets,
            scaffold=self.scaffold,
        )
        self.pack_status_usecase = PackStatusUseCase(
            inspector=self.freshness_inspector,
        )
