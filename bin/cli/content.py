"""Deliverable content entities.

Structure of what gets delivered to the client, independent of
rendering format.  Assembled by ProjectPresenters from workspace
files, consumed by SiteRenderers to produce output.
"""

from __future__ import annotations

from pydantic import BaseModel


class Figure(BaseModel):
    """A visual artifact (SVG content) with optional caption."""

    caption: str
    svg_content: str


class ContentPage(BaseModel):
    """A single page of prose content with optional figures."""

    title: str
    slug: str
    body_md: str
    figures: list[Figure] = []


class PageGroup(BaseModel):
    """A labeled collection of pages (e.g. atlas category)."""

    label: str
    slug: str
    pages: list[ContentPage]


class TourStopContent(BaseModel):
    """One assembled tour stop with figures and analysis."""

    title: str
    level: str
    is_header: bool
    figures: list[Figure]
    analysis_md: str


class TourGroupContent(BaseModel):
    """A group of related stops plus transition prose."""

    stops: list[TourStopContent]
    transition_md: str


class TourPageContent(BaseModel):
    """A complete tour presentation, assembled from workspace files."""

    title: str
    slug: str
    description: str
    opening_md: str
    groups: list[TourGroupContent]


class ProjectSection(BaseModel):
    """A major section within a project."""

    label: str
    slug: str
    description: str = ""
    pages: list[ContentPage] = []
    groups: list[PageGroup] = []
    tours: list[TourPageContent] = []


class ProjectContribution(BaseModel):
    """Everything a project contributes to the client deliverable.

    Assembled by a ProjectPresenter from workspace files. Contains
    enough structure for any renderer to produce output without
    knowing the skillset.
    """

    slug: str
    title: str
    skillset: str
    status: str
    hero_figure: Figure | None = None
    overview_md: str
    sections: list[ProjectSection] = []
