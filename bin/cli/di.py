"""Dependency injection container.

Single responsibility: know which implementations to use and configure
them with the right paths. Consumers depend on protocol types, never
on implementations directly.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from bin.cli.config import Config
from bin.cli.infrastructure.code_skillset_repository import CodeSkillsetRepository
from bin.cli.infrastructure.composite_skillset_repository import (
    CompositeSkillsetRepository,
)
from bin.cli.infrastructure.filesystem_source_repository import (
    FilesystemSourceRepository,
)
from bin.cli.infrastructure.skillset_scaffold import SkillsetScaffold
from business_model_canvas.presenter import BmcProjectPresenter
from bin.cli.infrastructure.jinja_renderer import JinjaSiteRenderer
from bin.cli.infrastructure.json_repos import (
    JsonDecisionRepository,
    JsonEngagementEntityRepository,
    JsonEngagementLogRepository,
    JsonProjectRepository,
    JsonResearchTopicRepository,
    JsonTourManifestRepository,
)
from bin.cli.usecases import (
    ListSkillsetsUseCase,
    ListSourcesUseCase,
    RegisterProspectusUseCase,
    RenderSiteUseCase,
    ShowSkillsetUseCase,
    ShowSourceUseCase,
    UpdateProspectusUseCase,
)
from wardley_mapping.presenter import WardleyProjectPresenter
from wardley_mapping.types import TourManifestRepository
from wardley_mapping.usecases import RegisterTourUseCase
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
    GetEngagementUseCase,
    GetProjectProgressUseCase,
    GetProjectUseCase,
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
    IdGenerator,
    ProjectPresenter,
    SiteRenderer,
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
        # -- Infrastructure services ----------------------------------------
        self.clock: Clock = WallClock()
        self.id_gen: IdGenerator = UuidGenerator()

        # -- Repositories --------------------------------------------------
        _commons_skillsets = CodeSkillsetRepository(
            config.repo_root,
        )
        self.skillsets: SkillsetRepository = CompositeSkillsetRepository(
            _commons_skillsets, config.repo_root
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
        self.tours: TourManifestRepository = JsonTourManifestRepository(
            config.workspace_root,
        )
        self.engagement_entities: EngagementRepository = JsonEngagementEntityRepository(
            config.workspace_root
        )
        self.sources: SourceRepository = FilesystemSourceRepository(
            config.repo_root, _commons_skillsets
        )
        self.site_renderer: SiteRenderer = JinjaSiteRenderer(
            workspace_root=config.workspace_root,
            repo_root=config.repo_root,
        )

        # -- Project presenters ------------------------------------------------
        self.presenters: dict[str, ProjectPresenter] = {
            "wardley-mapping": WardleyProjectPresenter(
                workspace_root=config.workspace_root,
                ensure_owm_script=config.repo_root / "bin" / "ensure-owm.sh",
                tours=self.tours,
            ),
            "business-model-canvas": BmcProjectPresenter(
                workspace_root=config.workspace_root,
            ),
        }

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
        self.register_tour_usecase = RegisterTourUseCase(
            projects=self.projects,
            tours=self.tours,
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
        self.render_site_usecase = RenderSiteUseCase(
            projects=self.projects,
            research=self.research,
            renderer=self.site_renderer,
            presenters=self.presenters,
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
