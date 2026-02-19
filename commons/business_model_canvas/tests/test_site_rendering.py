"""Business Model Canvas site rendering tests.

Tests BMC-specific site output: project index and analysis pages.
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

CLIENT = "acme-corp"

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _build_bmc_workspace(ws: Path) -> None:
    """Build a BMC project workspace."""
    proj = ws / "engagements" / "strat-1" / "bmc-1"

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
    _write(
        ws / "resources" / "index.md",
        "# Research Synthesis\n\nAcme Corp is a freight logistics company.",
    )


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory):
    """Render a site with a BMC project only."""
    tmp_path = tmp_path_factory.mktemp("bmc-site")
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
    _build_bmc_workspace(ws)

    container.register_project_usecase.execute(
        RegisterProjectRequest(
            client=CLIENT,
            engagement="strat-1",
            slug="bmc-1",
            skillset="business-model-canvas",
            scope="Business model analysis",
        )
    )

    resp = container.render_site_usecase.execute(RenderSiteRequest(client=CLIENT))
    return Path(resp.site_path)


class TestBmcSiteStructure:
    def test_project_index(self, rendered_site):
        assert (rendered_site / "bmc-1" / "index.html").is_file()

    def test_analysis_pages(self, rendered_site):
        bmc = rendered_site / "bmc-1" / "analysis"
        for page in ("canvas.html", "segments.html", "brief.html", "decisions.html"):
            assert (bmc / page).is_file(), f"Missing bmc-1/analysis/{page}"


class TestBmcContentPresence:
    def test_canvas_content(self, rendered_site):
        html = (rendered_site / "bmc-1" / "analysis" / "canvas.html").read_text()
        assert "Value Propositions" in html
