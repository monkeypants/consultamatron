"""Repository protocols for consulting practice accounting operations.

Each protocol defines the contract between usecases and persistence.
Implementations may use markdown files, SQLite, or any other backing
store. Usecases depend on these protocols, never on implementations.

Follows the same conventions as bingo-frog bounded contexts:
- Entities carry identity and scoping; save(entity) is self-contained
- Mutable entities get full CRUD (get, list, save, delete)
- Immutable entities get create + read only (save is create-only)
- Specialized query methods serve specific usecase needs
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from pathlib import Path
from typing import Protocol, runtime_checkable

from bin.cli.entities import (
    DecisionEntry,
    EngagementEntry,
    Project,
    ProjectContribution,
    ProjectStatus,
    ResearchTopic,
    Skillset,
    TourManifest,
)


# ---------------------------------------------------------------------------
# Skillset — read-only, discovered from manifests
# ---------------------------------------------------------------------------


@runtime_checkable
class SkillsetRepository(Protocol):
    """Read-only repository for skillset manifests.

    Skillsets are reference data discovered from skillsets/*.md at
    runtime. They are never created, updated, or deleted through
    the accounting CLI.
    """

    def get(self, name: str) -> Skillset | None:
        """Retrieve a skillset by name."""
        ...

    def list_all(self) -> list[Skillset]:
        """List all known skillsets."""
        ...


# ---------------------------------------------------------------------------
# Project — mutable CRUD, slug is identity within client
# ---------------------------------------------------------------------------


@runtime_checkable
class ProjectRepository(Protocol):
    """Repository for consulting projects.

    Projects are mutable — status transitions, notes updates.
    The slug is the natural key, scoped to a client.
    """

    # -----------------------------------------------------------------
    # Standard CRUD
    # -----------------------------------------------------------------

    def get(self, client: str, slug: str) -> Project | None:
        """Retrieve a project by client and slug."""
        ...

    def list_all(self, client: str) -> list[Project]:
        """List all projects for a client."""
        ...

    def list_filtered(
        self,
        client: str,
        skillset: str | None = None,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        """List projects with optional filters."""
        ...

    def save(self, project: Project) -> None:
        """Save a project (create or update)."""
        ...

    def delete(self, client: str, slug: str) -> bool:
        """Delete a project by client and slug. Returns True if deleted."""
        ...

    # -----------------------------------------------------------------
    # Specialized queries
    # -----------------------------------------------------------------

    def client_exists(self, client: str) -> bool:
        """Check whether a client workspace has been initialised."""
        ...


# ---------------------------------------------------------------------------
# Decision — immutable, append-only log per project
# ---------------------------------------------------------------------------


@runtime_checkable
class DecisionRepository(Protocol):
    """Repository for project decision entries.

    Decisions are immutable — created once, never updated or deleted.
    Analogous to bingo-frog's TransactionRepository.
    """

    # -----------------------------------------------------------------
    # Standard methods (no update, no delete)
    # -----------------------------------------------------------------

    def get(self, client: str, project_slug: str, id: str) -> DecisionEntry | None:
        """Retrieve a decision entry by ID."""
        ...

    def list_all(self, client: str, project_slug: str) -> list[DecisionEntry]:
        """List all decisions for a project in chronological order."""
        ...

    def list_filtered(
        self,
        client: str,
        project_slug: str,
        title: str | None = None,
    ) -> list[DecisionEntry]:
        """List decisions with optional filters.

        The title filter supports GetProjectProgress, which matches
        decision titles against pipeline stage descriptions.
        """
        ...

    def save(self, entry: DecisionEntry) -> None:
        """Save a new decision entry (create only — no updates)."""
        ...


# ---------------------------------------------------------------------------
# Engagement — immutable, append-only log per client
# ---------------------------------------------------------------------------


@runtime_checkable
class EngagementRepository(Protocol):
    """Repository for client engagement log entries.

    Engagement entries are immutable — created once, never updated
    or deleted. Analogous to bingo-frog's AuditLogRepository.
    """

    # -----------------------------------------------------------------
    # Standard methods (no update, no delete)
    # -----------------------------------------------------------------

    def get(self, client: str, id: str) -> EngagementEntry | None:
        """Retrieve an engagement entry by ID."""
        ...

    def list_all(self, client: str) -> list[EngagementEntry]:
        """List all engagement entries for a client in chronological order."""
        ...

    def save(self, entry: EngagementEntry) -> None:
        """Save a new engagement entry (create only — no updates)."""
        ...


# ---------------------------------------------------------------------------
# Research topic — mutable CRUD, filename is identity within client
# ---------------------------------------------------------------------------


@runtime_checkable
class ResearchTopicRepository(Protocol):
    """Repository for research topics in the client's manifest.

    Research topics are mutable — confidence can be revised as
    understanding improves. The filename is the natural key,
    scoped to a client.
    """

    # -----------------------------------------------------------------
    # Standard CRUD
    # -----------------------------------------------------------------

    def get(self, client: str, filename: str) -> ResearchTopic | None:
        """Retrieve a research topic by client and filename."""
        ...

    def list_all(self, client: str) -> list[ResearchTopic]:
        """List all research topics for a client."""
        ...

    def save(self, topic: ResearchTopic) -> None:
        """Save a research topic (create or update)."""
        ...

    def exists(self, client: str, filename: str) -> bool:
        """Check whether a research topic exists for this filename."""
        ...


# ---------------------------------------------------------------------------
# Tour manifest — replace semantics, name is identity within project
# ---------------------------------------------------------------------------


@runtime_checkable
class TourManifestRepository(Protocol):
    """Repository for audience tour manifests.

    Tour manifests use replace semantics — each save overwrites
    the entire manifest. The name is the natural key, scoped to
    a client and project.
    """

    def get(
        self, client: str, project_slug: str, tour_name: str
    ) -> TourManifest | None:
        """Retrieve a tour manifest by client, project, and name."""
        ...

    def list_all(self, client: str, project_slug: str) -> list[TourManifest]:
        """List all tour manifests for a project."""
        ...

    def save(self, manifest: TourManifest) -> None:
        """Save a tour manifest (creates or replaces)."""
        ...


# ---------------------------------------------------------------------------
# Project presenter — assembles workspace artifacts into deliverable content
# ---------------------------------------------------------------------------


@runtime_checkable
class ProjectPresenter(Protocol):
    """Assembles a project's workspace artifacts into structured content.

    Reads workspace files (markdown, SVGs, manifests) for a specific
    skillset and produces a ProjectContribution that any renderer can
    consume without knowing the skillset.
    """

    def present(
        self,
        project: Project,
        tours: list[TourManifest],
    ) -> ProjectContribution: ...


# ---------------------------------------------------------------------------
# Site renderer — infrastructure port for HTML generation
# ---------------------------------------------------------------------------


@runtime_checkable
class SiteRenderer(Protocol):
    """Infrastructure port for generating static HTML sites.

    Receives pre-assembled ProjectContribution entities from the usecase.
    The renderer handles content transformation (markdown→HTML, SVG
    embedding, templates) and file I/O, but does not decide what to
    present — that decision belongs to ProjectPresenters.
    """

    def render(
        self,
        client: str,
        contributions: list[ProjectContribution],
        research_topics: list[ResearchTopic],
    ) -> Path:
        """Render a static site for a client. Returns the output directory."""
        ...


# ---------------------------------------------------------------------------
# Infrastructure services — clock and identity generation
# ---------------------------------------------------------------------------


@runtime_checkable
class Clock(Protocol):
    """Wall-clock abstraction for timestamping domain events.

    Provides both date (for display) and datetime (for ordering).
    The timezone is available for consumers that need temporal context.
    """

    def today(self) -> date:
        """Return the current date in the configured timezone."""
        ...

    def now(self) -> datetime:
        """Return the current timezone-aware datetime."""
        ...

    def tz(self) -> tzinfo:
        """Return the configured timezone."""
        ...


@runtime_checkable
class IdGenerator(Protocol):
    """Identity generation for new domain entities."""

    def new_id(self) -> str:
        """Return a new unique identifier."""
        ...
