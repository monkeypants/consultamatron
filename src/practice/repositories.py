"""Infrastructure service protocols shared across bounded contexts.

These protocols define the ports that the practice layer requires.
Implementations are injected by the application layer.
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from pathlib import Path
from typing import Protocol, runtime_checkable

from practice.content import ProjectContribution
from practice.entities import Profile, Project, ResearchTopic, SkillsetSource


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
