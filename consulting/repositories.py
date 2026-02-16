"""Repository protocols for consulting practice accounting operations.

Each protocol defines the contract between usecases and persistence.
Implementations may use markdown files, SQLite, or any other backing
store. Usecases depend on these protocols, never on implementations.

Follows the same conventions as bingo-frog bounded contexts:
- Entities carry identity and scoping; save(entity) is self-contained
- Mutable entities get full CRUD (get, list, save, delete)
- Immutable entities get create + read only (save is create-only)
- Specialized query methods serve specific usecase needs

Infrastructure service protocols (Clock, IdGenerator) and presentation
protocols (ProjectPresenter, SiteRenderer) live in practice.repositories.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from consulting.entities import DecisionEntry, EngagementEntry
from practice.entities import Project, ProjectStatus, ResearchTopic, Skillset


# ---------------------------------------------------------------------------
# Skillset — read-only, discovered from manifests
# ---------------------------------------------------------------------------


@runtime_checkable
class SkillsetRepository(Protocol):
    """Read-only repository for skillset manifests.

    Skillsets are reference data declared in bounded context modules
    at import time. They are never created, updated, or deleted through
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
