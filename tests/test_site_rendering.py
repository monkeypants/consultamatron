"""Snapshot regression tests for site rendering.

Creates a synthetic workspace with Wardley and BMC projects, renders
via the God Class, and asserts structural properties. Not brittle
pixel-matching — just enough to catch regressions during refactoring.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.dtos import (
    InitializeWorkspaceRequest,
    RegisterProjectRequest,
    RegisterTourRequest,
    RenderSiteRequest,
)
from bin.cli.wm_types import TourStop

from .conftest import seed_all_skillsets

CLIENT = "acme-corp"


# ---------------------------------------------------------------------------
# Workspace builder helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


MINIMAL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    "<circle cx='50' cy='50' r='40'/></svg>"
)


def _build_wardley_workspace(ws: Path) -> None:
    """Build a fully-equipped Wardley project workspace."""
    proj = ws / "projects" / "maps-1"

    # Brief
    _write(proj / "brief.agreed.md", "# Project Brief\n\nScope: freight operations.")

    # Needs
    _write(
        proj / "needs" / "needs.agreed.md",
        "# User Needs\n\n- Track shipments\n- Manage fleet",
    )

    # Chain
    _write(
        proj / "chain" / "supply-chain.agreed.md",
        "# Supply Chain\n\nTracking depends on GPS, Fleet depends on Dispatch.",
    )

    # Evolve
    _write(proj / "evolve" / "map.agreed.owm", "// placeholder owm")
    _write(proj / "evolve" / "map.svg", MINIMAL_SVG)
    _write(
        proj / "evolve" / "assessments" / "gps.md",
        "# GPS Assessment\n\nCommodity. Multiple providers.",
    )

    # Strategy
    _write(proj / "strategy" / "map.agreed.owm", "// placeholder owm")
    _write(proj / "strategy" / "map.svg", MINIMAL_SVG)
    _write(
        proj / "strategy" / "plays" / "01-outsource-gps.md",
        "# Outsource GPS\n\nSwitch to commodity provider.",
    )

    # Decisions
    _write(proj / "decisions.md", "# Decisions\n\n## D-001: Project created\n\nInit.")

    # Atlas views
    for view_name in ("overview", "bottlenecks", "movement", "layers", "risk"):
        view_dir = proj / "atlas" / view_name
        _write(view_dir / "map.svg", MINIMAL_SVG)
        _write(
            view_dir / "analysis.md",
            f"# {view_name.title()} Analysis\n\nAnalysis for {view_name}.",
        )

    # Tour: investor
    tour_dir = proj / "presentations" / "investor"
    _write(
        tour_dir / "opening.md",
        "# Investor Briefing\n\nThis is the opening paragraph.\n\n"
        "This is the second paragraph with a description.",
    )
    _write(
        tour_dir / "transitions" / "01-after-overview.md",
        "# Transition\n\nMoving from overview to detail.",
    )

    # Landscape sketch (fallback hero)
    _write(proj / "landscape.svg", MINIMAL_SVG)


def _build_bmc_workspace(ws: Path) -> None:
    """Build a BMC project workspace."""
    proj = ws / "projects" / "bmc-1"

    _write(proj / "brief.agreed.md", "# BMC Brief\n\nBusiness model analysis.")
    _write(
        proj / "segments" / "segments.agreed.md",
        "# Customer Segments\n\n- Enterprise\n- SMB",
    )
    _write(
        proj / "canvas.agreed.md",
        "# Business Model Canvas\n\n## Value Propositions\n\nFreight visibility.",
    )
    _write(proj / "decisions.md", "# Decisions\n\n## D-001: Project created\n\nInit.")


def _build_research(ws: Path) -> None:
    """Build research files."""
    _write(
        ws / "resources" / "index.md",
        "# Research Synthesis\n\nAcme Corp is a freight logistics company.",
    )
    _write(
        ws / "resources" / "market-position.md",
        "# Market Position\n\nLeading provider in AU freight.",
    )
    _write(
        ws / "resources" / "technology.md",
        "# Technology Landscape\n\nLegacy TMS with modern API layer.",
    )


def _build_engagement(ws: Path) -> None:
    """Build engagement log."""
    _write(
        ws / "engagement.md",
        "# Engagement Log — Acme Corp\n\n## 2025-06-01: Client onboarded\n\nKickoff.",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory):
    """Build a synthetic workspace and render the site. Returns the site path."""
    tmp_path = tmp_path_factory.mktemp("site")
    config = Config(
        repo_root=Path(__file__).resolve().parent.parent,
        workspace_root=tmp_path / "clients",
        skillsets_root=tmp_path / "skillsets",
    )
    seed_all_skillsets(config.skillsets_root)
    container = Container(config)

    # Initialize workspace
    container.initialize_workspace_usecase.execute(
        InitializeWorkspaceRequest(client=CLIENT)
    )

    ws = config.workspace_root / CLIENT

    # Build filesystem content
    _build_research(ws)
    _build_engagement(ws)
    _build_wardley_workspace(ws)
    _build_bmc_workspace(ws)

    # Register projects via usecase
    container.register_project_usecase.execute(
        RegisterProjectRequest(
            client=CLIENT,
            slug="maps-1",
            skillset="wardley-mapping",
            scope="Freight operations",
        )
    )
    container.register_project_usecase.execute(
        RegisterProjectRequest(
            client=CLIENT,
            slug="bmc-1",
            skillset="business-model-canvas",
            scope="Business model analysis",
        )
    )

    # Register investor tour
    container.register_tour_usecase.execute(
        RegisterTourRequest(
            client=CLIENT,
            project_slug="maps-1",
            name="investor",
            title="Investor Briefing: Strategic Position",
            stops=[
                TourStop(
                    order="1",
                    title="Strategic Overview",
                    atlas_source="atlas/overview/",
                ),
                TourStop(
                    order="2",
                    title="Competitive Moats",
                    atlas_source="atlas/bottlenecks/",
                ),
                TourStop(
                    order="2a",
                    title="Risk Profile",
                    atlas_source="atlas/risk/",
                ),
                TourStop(
                    order="3",
                    title="Evolution Programme",
                    atlas_source="atlas/movement/",
                ),
            ],
        )
    )

    # Render
    resp = container.render_site_usecase.execute(RenderSiteRequest(client=CLIENT))
    return Path(resp.site_path)


# ---------------------------------------------------------------------------
# Structural assertions
# ---------------------------------------------------------------------------


class TestSiteStructure:
    """Verify the rendered site has the expected structure."""

    def test_site_directory_exists(self, rendered_site):
        assert rendered_site.is_dir()

    def test_style_css_exists(self, rendered_site):
        assert (rendered_site / "style.css").is_file()

    def test_client_pages_exist(self, rendered_site):
        for page in (
            "index.html",
            "projects.html",
            "resources.html",
            "engagement.html",
        ):
            assert (rendered_site / page).is_file(), f"Missing {page}"

    def test_research_sub_reports(self, rendered_site):
        for topic in ("market-position", "technology"):
            path = rendered_site / "resources" / f"{topic}.html"
            assert path.is_file(), f"Missing research/{topic}.html"

    def test_wardley_project_index(self, rendered_site):
        assert (rendered_site / "maps-1" / "index.html").is_file()

    def test_wardley_presentations_index(self, rendered_site):
        assert (rendered_site / "maps-1" / "presentations" / "index.html").is_file()

    def test_wardley_tour_rendered(self, rendered_site):
        assert (rendered_site / "maps-1" / "presentations" / "investor.html").is_file()

    def test_wardley_atlas_index(self, rendered_site):
        assert (rendered_site / "maps-1" / "atlas" / "index.html").is_file()

    def test_wardley_atlas_views(self, rendered_site):
        for view in ("overview", "bottlenecks", "movement", "layers", "risk"):
            path = rendered_site / "maps-1" / "atlas" / f"{view}.html"
            assert path.is_file(), f"Missing atlas/{view}.html"

    def test_wardley_analysis_pages(self, rendered_site):
        analysis = rendered_site / "maps-1" / "analysis"
        for page in (
            "index.html",
            "strategy.html",
            "map.html",
            "supply-chain.html",
            "needs.html",
            "brief.html",
            "decisions.html",
        ):
            assert (analysis / page).is_file(), f"Missing analysis/{page}"

    def test_bmc_project_index(self, rendered_site):
        assert (rendered_site / "bmc-1" / "index.html").is_file()

    def test_bmc_pages(self, rendered_site):
        bmc = rendered_site / "bmc-1" / "analysis"
        for page in ("canvas.html", "segments.html", "brief.html", "decisions.html"):
            assert (bmc / page).is_file(), f"Missing bmc-1/analysis/{page}"


class TestContentPresence:
    """Verify key content strings appear in rendered pages."""

    def test_org_name_on_home(self, rendered_site):
        html = (rendered_site / "index.html").read_text()
        assert "Acme Corp" in html

    def test_research_synthesis_content(self, rendered_site):
        html = (rendered_site / "resources.html").read_text()
        assert "freight logistics" in html

    def test_tour_opening(self, rendered_site):
        html = (
            rendered_site / "maps-1" / "presentations" / "investor.html"
        ).read_text()
        assert "opening paragraph" in html

    def test_tour_stop_titles(self, rendered_site):
        html = (
            rendered_site / "maps-1" / "presentations" / "investor.html"
        ).read_text()
        assert "Strategic Overview" in html
        assert "Competitive Moats" in html

    def test_atlas_overview_content(self, rendered_site):
        html = (rendered_site / "maps-1" / "atlas" / "overview.html").read_text()
        assert "Analysis for overview" in html

    def test_strategy_has_svg(self, rendered_site):
        html = (rendered_site / "maps-1" / "analysis" / "strategy.html").read_text()
        assert "<svg" in html

    def test_bmc_canvas_content(self, rendered_site):
        html = (rendered_site / "bmc-1" / "analysis" / "canvas.html").read_text()
        assert "Value Propositions" in html

    def test_supply_chain_content(self, rendered_site):
        html = (rendered_site / "maps-1" / "analysis" / "supply-chain.html").read_text()
        assert "GPS" in html


class TestPageCount:
    """Verify total page count is reasonable."""

    def test_minimum_page_count(self, rendered_site):
        pages = list(rendered_site.rglob("*.html"))
        # Client: 4 (home, projects, resources, engagement)
        # Research: 2 (market-position, technology)
        # Wardley: 1 index + 1 pres index + 1 tour + 1 atlas index
        #          + 5 atlas views + 7 analysis = 16
        # BMC: 1 index + 4 pages = 5
        # Total minimum: ~27
        assert len(pages) >= 25, f"Only {len(pages)} pages rendered"
