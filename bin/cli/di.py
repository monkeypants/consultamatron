"""Dependency injection container.

Single responsibility: know which implementations to use and configure
them with the right paths. Consumers depend on protocol types, never
on implementations directly.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from bin.cli.config import Config
from bin.cli.infrastructure.bmc_presenter import BmcProjectPresenter
from bin.cli.infrastructure.jinja_renderer import JinjaSiteRenderer
from bin.cli.infrastructure.json_repos import (
    JsonDecisionRepository,
    JsonEngagementRepository,
    JsonProjectRepository,
    JsonResearchTopicRepository,
    JsonSkillsetRepository,
    JsonTourManifestRepository,
)
from bin.cli.infrastructure.wardley_presenter import WardleyProjectPresenter
from practice.repositories import Clock, IdGenerator, ProjectPresenter, SiteRenderer
from bin.cli.repositories import (
    DecisionRepository,
    EngagementRepository,
    ProjectRepository,
    ResearchTopicRepository,
    SkillsetRepository,
)
from bin.cli.wm_types import TourManifestRepository
from bin.cli.usecases import (
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
    RegisterTourUseCase,
    RenderSiteUseCase,
    UpdateProjectStatusUseCase,
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
        self.skillsets: SkillsetRepository = JsonSkillsetRepository(
            config.skillsets_root,
        )
        self.projects: ProjectRepository = JsonProjectRepository(
            config.workspace_root,
        )
        self.decisions: DecisionRepository = JsonDecisionRepository(
            config.workspace_root,
        )
        self.engagement: EngagementRepository = JsonEngagementRepository(
            config.workspace_root,
        )
        self.research: ResearchTopicRepository = JsonResearchTopicRepository(
            config.workspace_root,
        )
        self.tours: TourManifestRepository = JsonTourManifestRepository(
            config.workspace_root,
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
            engagement=self.engagement,
            research=self.research,
            clock=self.clock,
            id_gen=self.id_gen,
        )
        self.register_project_usecase = RegisterProjectUseCase(
            projects=self.projects,
            decisions=self.decisions,
            engagement=self.engagement,
            skillsets=self.skillsets,
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
            engagement=self.engagement,
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
        self.render_site_usecase = RenderSiteUseCase(
            projects=self.projects,
            research=self.research,
            renderer=self.site_renderer,
            presenters=self.presenters,
        )
