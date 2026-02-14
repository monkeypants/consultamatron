"""Tests for WardleyProjectPresenter.

Verifies content assembly from workspace files into ProjectContribution
entities without involving any rendering infrastructure.
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import pytest

from bin.cli.entities import Project, ProjectStatus, TourManifest, TourStop
from bin.cli.infrastructure.wardley_presenter import WardleyProjectPresenter

CLIENT = "test-corp"
SLUG = "maps-1"

MINIMAL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    "<circle cx='50' cy='50' r='40'/></svg>"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _write_owm_with_svg(owm_path: Path, svg_path: Path) -> None:
    """Write an OWM file and its SVG, ensuring SVG is newer."""
    _write(owm_path, "// placeholder owm")
    _write(svg_path, MINIMAL_SVG)
    # Backdate the OWM so SVG is considered fresh
    os.utime(owm_path, (0, 0))


def _make_project(**overrides) -> Project:
    defaults = dict(
        slug=SLUG,
        client=CLIENT,
        skillset="wardley-mapping",
        status=ProjectStatus.ELABORATION,
        created=date(2025, 6, 1),
    )
    return Project(**(defaults | overrides))


def _noop_script(tmp_path: Path) -> Path:
    """Create a no-op shell script for OWM rendering in tests."""
    script = tmp_path / "noop-owm.sh"
    script.write_text("#!/bin/sh\ntrue\n")
    script.chmod(0o755)
    return script


def _make_presenter(ws_root: Path) -> WardleyProjectPresenter:
    script = _noop_script(ws_root)
    return WardleyProjectPresenter(
        workspace_root=ws_root,
        ensure_owm_script=script,
    )


# ---------------------------------------------------------------------------
# Fully equipped workspace
# ---------------------------------------------------------------------------


@pytest.fixture
def full_workspace(tmp_path):
    """Workspace with all Wardley stages, atlas, and tour."""
    ws = tmp_path / CLIENT
    proj = ws / "projects" / SLUG

    # Brief
    _write(proj / "brief.agreed.md", "# Brief\n\nFreight operations scope.")

    # Needs
    _write(proj / "needs" / "needs.agreed.md", "# Needs\n\n- Track shipments")

    # Chain
    _write(
        proj / "chain" / "supply-chain.agreed.md",
        "# Supply Chain\n\nTracking depends on GPS.",
    )

    # Evolve
    _write_owm_with_svg(proj / "evolve" / "map.agreed.owm", proj / "evolve" / "map.svg")
    _write(
        proj / "evolve" / "assessments" / "gps.md",
        "# GPS\n\nCommodity provider.",
    )

    # Strategy
    _write_owm_with_svg(
        proj / "strategy" / "map.agreed.owm", proj / "strategy" / "map.svg"
    )
    _write(
        proj / "strategy" / "plays" / "01-outsource.md",
        "# Outsource GPS\n\nSwitch provider.",
    )

    # Decisions
    _write(proj / "decisions.md", "# Decisions\n\n## D-001\n\nProject created.")

    # Atlas
    for view in ("overview", "bottlenecks", "movement"):
        _write(proj / "atlas" / view / "map.svg", MINIMAL_SVG)
        _write(
            proj / "atlas" / view / "analysis.md",
            f"# {view.title()}\n\nAnalysis.",
        )

    # Tour opening + transitions
    tour_dir = proj / "presentations" / "investor"
    _write(
        tour_dir / "opening.md",
        "# Investor Briefing\n\nFirst paragraph.\n\nSecond paragraph description.",
    )
    _write(
        tour_dir / "transitions" / "01-trans.md",
        "# Transition\n\nFrom overview to bottlenecks.",
    )

    return tmp_path


@pytest.fixture
def full_tours():
    return [
        TourManifest(
            name="investor",
            client=CLIENT,
            project_slug=SLUG,
            title="Investor Briefing",
            stops=[
                TourStop(
                    order="1",
                    title="Overview",
                    atlas_source="atlas/overview/",
                ),
                TourStop(
                    order="2",
                    title="Bottlenecks",
                    atlas_source="atlas/bottlenecks/",
                ),
            ],
        )
    ]


class TestFullWorkspace:
    """Fully equipped Wardley project produces all three sections."""

    def test_has_three_sections(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        labels = [s.label for s in contrib.sections]
        assert labels == ["Presentations", "Atlas", "Analysis"]

    def test_hero_is_strategy(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        assert contrib.hero_figure is not None
        assert contrib.hero_figure.caption == "Strategy map"

    def test_presentations_section_has_tour(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        pres = contrib.sections[0]
        assert len(pres.tours) == 1
        assert pres.tours[0].title == "Investor Briefing"

    def test_tour_has_groups_and_stops(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        tour = contrib.sections[0].tours[0]
        assert len(tour.groups) == 2
        assert tour.groups[0].stops[0].title == "Overview"

    def test_tour_opening(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        tour = contrib.sections[0].tours[0]
        assert "First paragraph" in tour.opening_md

    def test_tour_description_from_second_paragraph(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        tour = contrib.sections[0].tours[0]
        assert "Second paragraph description" in tour.description

    def test_tour_transition(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        tour = contrib.sections[0].tours[0]
        assert "From overview to bottlenecks" in tour.groups[0].transition_md

    def test_atlas_has_categorized_groups(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        atlas = contrib.sections[1]
        group_labels = [g.label for g in atlas.groups]
        assert "Structural" in group_labels
        assert "Connectivity" in group_labels
        assert "Dynamic" in group_labels

    def test_analysis_has_all_pages(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        analysis = contrib.sections[2]
        slugs = [p.slug for p in analysis.pages]
        assert slugs == [
            "strategy",
            "map",
            "supply-chain",
            "needs",
            "brief",
            "decisions",
        ]

    def test_strategy_page_has_figure(self, full_workspace, full_tours):
        presenter = _make_presenter(full_workspace)
        contrib = presenter.present(_make_project(), full_tours)
        analysis = contrib.sections[2]
        strategy_page = analysis.pages[0]
        assert len(strategy_page.figures) == 1
        assert strategy_page.figures[0].caption == "Strategy map"


# ---------------------------------------------------------------------------
# Minimal workspace — just a brief
# ---------------------------------------------------------------------------


class TestMinimalWorkspace:
    """A project with only a brief gets an Analysis section with one page."""

    def test_single_analysis_section(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "projects" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nMinimal project.")

        presenter = _make_presenter(tmp_path)
        contrib = presenter.present(_make_project(), [])
        assert len(contrib.sections) == 1
        assert contrib.sections[0].label == "Analysis"
        assert len(contrib.sections[0].pages) == 1
        assert contrib.sections[0].pages[0].slug == "brief"

    def test_no_hero_without_maps(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "projects" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nMinimal.")

        presenter = _make_presenter(tmp_path)
        contrib = presenter.present(_make_project(), [])
        assert contrib.hero_figure is None


# ---------------------------------------------------------------------------
# Hero figure priority
# ---------------------------------------------------------------------------


class TestHeroPriority:
    """Strategy > evolve > landscape fallback for hero figure."""

    def test_evolve_fallback(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "projects" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nScope.")
        _write_owm_with_svg(
            proj / "evolve" / "map.agreed.owm", proj / "evolve" / "map.svg"
        )

        presenter = _make_presenter(tmp_path)
        contrib = presenter.present(_make_project(), [])
        assert contrib.hero_figure is not None
        assert contrib.hero_figure.caption == "Evolution map"

    def test_landscape_fallback(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "projects" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nScope.")
        _write(proj / "landscape.svg", MINIMAL_SVG)

        presenter = _make_presenter(tmp_path)
        contrib = presenter.present(_make_project(), [])
        assert contrib.hero_figure is not None
        assert "approximate" in contrib.hero_figure.caption


# ---------------------------------------------------------------------------
# Atlas categorization
# ---------------------------------------------------------------------------


class TestAtlasCategorization:
    def test_categories_assigned_correctly(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "projects" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nScope.")

        # Create views in different categories
        for view in ("overview", "bottlenecks", "movement", "sourcing"):
            _write(proj / "atlas" / view / "analysis.md", f"# {view}\n\nText.")
            _write(proj / "atlas" / view / "map.svg", MINIMAL_SVG)

        presenter = _make_presenter(tmp_path)
        contrib = presenter.present(_make_project(), [])

        atlas = next(s for s in contrib.sections if s.label == "Atlas")
        cat_map = {g.slug: [p.slug for p in g.pages] for g in atlas.groups}

        assert "overview" in cat_map.get("structural", [])
        assert "bottlenecks" in cat_map.get("connectivity", [])
        assert "movement" in cat_map.get("dynamic", [])
        assert "sourcing" in cat_map.get("strategic", [])


# ---------------------------------------------------------------------------
# Tour stop grouping
# ---------------------------------------------------------------------------


class TestTourStopGrouping:
    def test_sub_stops_grouped_with_parent(self, tmp_path):
        ws = tmp_path / CLIENT
        proj = ws / "projects" / SLUG
        _write(proj / "brief.agreed.md", "# Brief\n\nScope.")

        for view in ("overview", "risk", "bottlenecks"):
            _write(proj / "atlas" / view / "analysis.md", f"# {view}\n\nText.")
            _write(proj / "atlas" / view / "map.svg", MINIMAL_SVG)

        tour_dir = proj / "presentations" / "exec"
        _write(tour_dir / "opening.md", "# Exec\n\nOpening.")

        tours = [
            TourManifest(
                name="exec",
                client=CLIENT,
                project_slug=SLUG,
                title="Executive Tour",
                stops=[
                    TourStop(
                        order="1", title="Overview", atlas_source="atlas/overview/"
                    ),
                    TourStop(order="2", title="Risk Section", atlas_source=""),
                    TourStop(
                        order="2a", title="Risk Detail", atlas_source="atlas/risk/"
                    ),
                    TourStop(
                        order="2b",
                        title="Bottleneck Detail",
                        atlas_source="atlas/bottlenecks/",
                    ),
                    TourStop(
                        order="3", title="Summary", atlas_source="atlas/overview/"
                    ),
                ],
            )
        ]

        presenter = _make_presenter(tmp_path)
        contrib = presenter.present(_make_project(), tours)
        tour = contrib.sections[0].tours[0]

        assert len(tour.groups) == 3
        assert len(tour.groups[0].stops) == 1  # "1"
        assert len(tour.groups[1].stops) == 3  # "2", "2a", "2b"
        assert len(tour.groups[2].stops) == 1  # "3"

        # Sub-stops have h3 level
        assert tour.groups[1].stops[0].level == "h2"
        assert tour.groups[1].stops[1].level == "h3"

        # Header stop has is_header=True
        assert tour.groups[1].stops[0].is_header is True
