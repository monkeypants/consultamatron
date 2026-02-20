"""Infrastructure service protocols shared across bounded contexts.

These protocols define the ports that the practice layer requires.
Implementations are injected by the application layer.
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from pathlib import Path
from typing import Protocol, runtime_checkable

from practice.content import ProjectContribution
from practice.entities import (
    DecisionEntry,
    Engagement,
    EngagementEntry,
    KnowledgePack,
    PackFreshness,
    Profile,
    Project,
    ProjectStatus,
    ResearchTopic,
    SkillManifest,
    Skillset,
    SkillsetSource,
)


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
    ) -> ProjectContribution: ...


@runtime_checkable
class SourceRepository(Protocol):
    """Read-only repository for skillset sources.

    Sources represent where skillsets come from — commons, partnerships,
    or personal.  The repository tracks which skillsets belong
    to which source, enabling engagement-level access control.
    """

    def get(self, slug: str) -> SkillsetSource | None:
        """Retrieve a source by slug."""
        ...

    def list_all(self) -> list[SkillsetSource]:
        """List all installed sources."""
        ...

    def skillset_source(self, skillset_name: str) -> str | None:
        """Return the source slug that provides a given skillset, or None."""
        ...


@runtime_checkable
class SiteRenderer(Protocol):
    """Infrastructure port for generating static HTML sites.

    Receives pre-assembled ProjectContribution entities from the usecase.
    The renderer handles content transformation (markdown->HTML, SVG
    embedding, templates) and file I/O, but does not decide what to
    present -- that decision belongs to ProjectPresenters.
    """

    def render(
        self,
        client: str,
        contributions: list[ProjectContribution],
        research_topics: list[ResearchTopic],
    ) -> Path:
        """Render a static site for a client. Returns the output directory."""
        ...


@runtime_checkable
class ProfileRepository(Protocol):
    """Read-only repository for named skillset profiles."""

    def get(self, name: str) -> tuple[Profile, str] | None:
        """Retrieve a profile by name, returning (profile, source_slug) or None."""
        ...

    def list_all(self) -> list[tuple[Profile, str]]:
        """List all profiles as (profile, source_slug) tuples."""
        ...


@runtime_checkable
class GateInspector(Protocol):
    """Driven port: check gate artifact existence.

    The engagement protocol use cases need to know whether a gate
    artifact exists without knowing the storage mechanism. This port
    abstracts file existence into a testable contract.
    """

    def exists(
        self, client: str, engagement: str, project: str, gate_path: str
    ) -> bool:
        """Return True if the gate artifact exists."""
        ...


@runtime_checkable
class FreshnessInspector(Protocol):
    """Assess compilation freshness of a knowledge pack."""

    def assess(self, pack_root: Path) -> PackFreshness:
        """Return freshness tree rooted at pack_root.

        Recursively inspects nested packs. Each node in the returned
        tree has shallow compilation_state for its own level and
        children for nested packs. Use deep_state for the transitive
        rollup.
        """
        ...


@runtime_checkable
class PackNudger(Protocol):
    """Check design-time packs for freshness and return nudges.

    Usecases call this to discover dirty or corrupt knowledge packs
    that are contextually relevant to the current operation. The
    nudges are informational strings appended to response DTOs.
    """

    def check(self, skillset_names: list[str] | None = None) -> list[str]:
        """Return nudge strings for non-clean design-time packs.

        When skillset_names is provided, check only packs related to
        those skillsets. When None, check all design-time packs.
        """
        ...


@runtime_checkable
class SkillsetKnowledge(Protocol):
    """Read typed knowledge items from a skillset's docs pack.

    Each skillset has one docs/ knowledge pack containing items
    identified by type (pantheon, patterns, principles, anti-patterns).
    The port abstracts the storage mechanism — filesystem, API, or
    test double.
    """

    def read_item(self, skillset_name: str, item_type: str) -> str | None:
        """Return the body content of a typed item, or None if absent."""
        ...


@runtime_checkable
class ItemCompiler(Protocol):
    """Generate a _bytecode/ summary for a single pack item."""

    def compile(self, item_path: Path, pack_root: Path) -> str:
        """Read item content, return summary text for _bytecode/ mirror."""
        ...


@runtime_checkable
class SkillManifestRepository(Protocol):
    """Read-only repository for parsed SKILL.md manifests."""

    def get(self, name: str) -> SkillManifest | None:
        """Retrieve a skill manifest by name."""
        ...

    def list_all(self) -> list[SkillManifest]:
        """List all discovered skill manifests."""
        ...


# ---------------------------------------------------------------------------
# Domain repository protocols (engagement accounting)
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


@runtime_checkable
class KnowledgePackRepository(Protocol):
    """Read-only repository for knowledge pack manifests."""

    def get(self, name: str) -> KnowledgePack | None:
        """Retrieve a knowledge pack by name."""
        ...

    def list_all(self) -> list[KnowledgePack]:
        """List all discovered knowledge packs."""
        ...

    def packs_with_paths(self) -> list[tuple[KnowledgePack, Path]]:
        """Return (pack, pack_root) pairs for all discovered packs."""
        ...


@runtime_checkable
class EngagementRepository(Protocol):
    """Repository for consulting engagement entities.

    Engagements are mutable — status transitions, source list changes.
    The slug is the natural key, scoped to a client.
    """

    def get(self, client: str, slug: str) -> Engagement | None:
        """Retrieve an engagement by client and slug."""
        ...

    def list_all(self, client: str) -> list[Engagement]:
        """List all engagements for a client."""
        ...

    def save(self, engagement: Engagement) -> None:
        """Save an engagement (create or update)."""
        ...


@runtime_checkable
class ProjectRepository(Protocol):
    """Repository for consulting projects.

    Projects are mutable — status transitions, notes updates.
    The slug is the natural key, scoped to a client and engagement.
    """

    def get(self, client: str, engagement: str, slug: str) -> Project | None:
        """Retrieve a project by client, engagement, and slug."""
        ...

    def list_all(self, client: str) -> list[Project]:
        """List all projects for a client across all engagements."""
        ...

    def list_filtered(
        self,
        client: str,
        engagement: str,
        skillset: str | None = None,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        """List projects within an engagement with optional filters."""
        ...

    def save(self, project: Project) -> None:
        """Save a project (create or update)."""
        ...

    def delete(self, client: str, engagement: str, slug: str) -> bool:
        """Delete a project. Returns True if deleted."""
        ...

    def client_exists(self, client: str) -> bool:
        """Check whether a client workspace has been initialised."""
        ...

    def list_clients(self) -> list[str]:
        """List all client slugs that have workspaces."""
        ...


@runtime_checkable
class DecisionRepository(Protocol):
    """Repository for project decision entries.

    Decisions are immutable — created once, never updated or deleted.
    """

    def get(
        self, client: str, engagement: str, project_slug: str, id: str
    ) -> DecisionEntry | None:
        """Retrieve a decision entry by ID."""
        ...

    def list_all(
        self, client: str, engagement: str, project_slug: str
    ) -> list[DecisionEntry]:
        """List all decisions for a project in chronological order."""
        ...

    def list_filtered(
        self,
        client: str,
        engagement: str,
        project_slug: str,
        title: str | None = None,
    ) -> list[DecisionEntry]:
        """List decisions with optional filters."""
        ...

    def save(self, entry: DecisionEntry) -> None:
        """Save a new decision entry (create only — no updates)."""
        ...


@runtime_checkable
class EngagementLogRepository(Protocol):
    """Repository for client engagement log entries.

    Engagement entries are immutable — created once, never updated
    or deleted.
    """

    def get(self, client: str, id: str) -> EngagementEntry | None:
        """Retrieve an engagement entry by ID."""
        ...

    def list_all(self, client: str) -> list[EngagementEntry]:
        """List all engagement entries for a client in chronological order."""
        ...

    def save(self, entry: EngagementEntry) -> None:
        """Save a new engagement entry (create only — no updates)."""
        ...


@runtime_checkable
class ResearchTopicRepository(Protocol):
    """Repository for research topics in the client's manifest.

    Research topics are mutable — confidence can be revised as
    understanding improves. The filename is the natural key,
    scoped to a client.
    """

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
