"""Wardley Mapping site rendering tests.

Tests WM-specific site output: project index, presentations, atlas,
analysis pages, and content.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.dtos import RenderSiteRequest
from bin.cli.dtos import (
    CreateEngagementRequest,
    InitializeWorkspaceRequest,
    RegisterProjectRequest,
)
from wardley_mapping.dtos import RegisterTourRequest
from wardley_mapping.types import TourStop

CLIENT = "acme-corp"

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

MINIMAL_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
    "<circle cx='50' cy='50' r='40'/></svg>"
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _build_wardley_workspace(ws: Path) -> None:
    """Build a fully-equipped Wardley project workspace."""
    proj = ws / "engagements" / "strat-1" / "maps-1"

    _write(proj / "brief.agreed.md", "# Project Brief\n\nScope: freight operations.")
    _write(
        proj / "needs" / "needs.agreed.md",
        "# User Needs\n\n- Track shipments\n- Manage fleet",
    )
    _write(
        proj / "chain" / "supply-chain.agreed.md",
        "# Supply Chain\n\nTracking depends on GPS, Fleet depends on Dispatch.",
    )
    _write(proj / "evolve" / "map.agreed.owm", "// placeholder owm")
    _write(proj / "evolve" / "map.svg", MINIMAL_SVG)
    _write(
        proj / "evolve" / "assessments" / "gps.md",
        "# GPS Assessment\n\nCommodity. Multiple providers.",
    )
    _write(proj / "strategy" / "map.agreed.owm", "// placeholder owm")
    _write(proj / "strategy" / "map.svg", MINIMAL_SVG)
    _write(
        proj / "strategy" / "plays" / "01-outsource-gps.md",
        "# Outsource GPS\n\nSwitch to commodity provider.",
    )
    _write(proj / "decisions.md", "# Decisions\n\n## D-001: Project created\n\nInit.")

    for view_name in ("overview", "bottlenecks", "movement", "layers", "risk"):
        view_dir = proj / "atlas" / view_name
        _write(view_dir / "map.svg", MINIMAL_SVG)
        _write(
            view_dir / "analysis.md",
            f"# {view_name.title()} Analysis\n\nAnalysis for {view_name}.",
        )

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
    _write(proj / "landscape.svg", MINIMAL_SVG)


def _build_research(ws: Path) -> None:
    _write(
        ws / "resources" / "index.md",
        "# Research Synthesis\n\nAcme Corp is a freight logistics company.",
    )
    _write(
        ws / "resources" / "market-position.md",
        "# Market Position\n\nLeading provider in AU freight.",
    )


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory):
    """Render a site with a WM project only."""
    tmp_path = tmp_path_factory.mktemp("wm-site")
    config = Config(
        repo_root=_REPO_ROOT,
        workspace_root=tmp_path / "clients",
        skillsets_root=tmp_path / "skillsets",
    )
    container = Container(config)

    container.initialize_workspace_usecase.execute(
        InitializeWorkspaceRequest(client=CLIENT)
    )
    container.create_engagement_usecase.execute(
        CreateEngagementRequest(client=CLIENT, slug="strat-1")
    )

    ws = config.workspace_root / CLIENT
    _build_research(ws)
    _build_wardley_workspace(ws)

    container.register_project_usecase.execute(
        RegisterProjectRequest(
            client=CLIENT,
            engagement="strat-1",
            slug="maps-1",
            skillset="wardley-mapping",
            scope="Freight operations",
        )
    )

    container.register_tour_usecase.execute(
        RegisterTourRequest(
            client=CLIENT,
            engagement="strat-1",
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

    resp = container.render_site_usecase.execute(RenderSiteRequest(client=CLIENT))
    return Path(resp.site_path)


class TestWardleySiteStructure:
    def test_project_index(self, rendered_site):
        assert (rendered_site / "maps-1" / "index.html").is_file()

    def test_presentations_index(self, rendered_site):
        assert (rendered_site / "maps-1" / "presentations" / "index.html").is_file()

    def test_tour_rendered(self, rendered_site):
        assert (rendered_site / "maps-1" / "presentations" / "investor.html").is_file()

    def test_atlas_index(self, rendered_site):
        assert (rendered_site / "maps-1" / "atlas" / "index.html").is_file()

    def test_atlas_views(self, rendered_site):
        for view in ("overview", "bottlenecks", "movement", "layers", "risk"):
            path = rendered_site / "maps-1" / "atlas" / f"{view}.html"
            assert path.is_file(), f"Missing atlas/{view}.html"

    def test_analysis_pages(self, rendered_site):
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


class TestWardleyContentPresence:
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

    def test_supply_chain_content(self, rendered_site):
        html = (rendered_site / "maps-1" / "analysis" / "supply-chain.html").read_text()
        assert "GPS" in html
