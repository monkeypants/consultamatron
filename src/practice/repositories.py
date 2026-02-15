"""Infrastructure service protocols shared across bounded contexts.

These protocols define the ports that the practice layer requires.
Implementations are injected by the application layer.
"""

from __future__ import annotations

from datetime import date, datetime, tzinfo
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from practice.content import ProjectContribution

if TYPE_CHECKING:
    # TODO(#47): Move to consulting.entities when bounded contexts land.
    from bin.cli.entities import Project, ResearchTopic


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
        project: "Project",
    ) -> ProjectContribution: ...


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
        research_topics: list["ResearchTopic"],
    ) -> Path:
        """Render a static site for a client. Returns the output directory."""
        ...
