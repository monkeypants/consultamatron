"""Shared site rendering structural tests.

Verifies structural properties that apply regardless of which
skillsets are present: site directory, stylesheet, client pages,
research sub-reports, and content basics.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from .conftest import _HAS_BC_PACKAGES
from bin.cli.dtos import RenderSiteRequest
from bin.cli.infrastructure.code_skillset_repository import CodeSkillsetRepository
from bin.cli.dtos import (
    CreateEngagementRequest,
    InitializeWorkspaceRequest,
    RegisterProjectRequest,
)

CLIENT = "acme-corp"

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _build_research(ws: Path) -> None:
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


@pytest.fixture(scope="module")
def rendered_site(tmp_path_factory):
    """Build a minimal workspace and render the site."""
    if not _HAS_BC_PACKAGES:
        pytest.skip("No BC packages installed")
    tmp_path = tmp_path_factory.mktemp("site")
    config = Config(
        repo_root=_REPO_ROOT,
        workspace_root=tmp_path / "clients",
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

    # Register one project per implemented skillset with a minimal brief
    repo = CodeSkillsetRepository(_REPO_ROOT)
    for skillset in repo.list_all():
        if not skillset.is_implemented:
            continue
        slug = skillset.slug_pattern.replace("{n}", "1")
        proj_dir = ws / "engagements" / "strat-1" / slug
        _write(proj_dir / "brief.agreed.md", f"# Brief\n\nMinimal {skillset.name}.")
        container.register_project_usecase.execute(
            RegisterProjectRequest(
                client=CLIENT,
                engagement="strat-1",
                slug=slug,
                skillset=skillset.name,
                scope=f"Test {skillset.name}",
            )
        )

    resp = container.render_site_usecase.execute(RenderSiteRequest(client=CLIENT))
    return Path(resp.site_path)


class TestSiteStructure:
    """Shared structural properties of the rendered site."""

    def test_site_directory_exists(self, rendered_site):
        assert rendered_site.is_dir()

    def test_style_css_exists(self, rendered_site):
        assert (rendered_site / "style.css").is_file()

    def test_client_pages_exist(self, rendered_site):
        for page in (
            "index.html",
            "projects.html",
            "resources.html",
        ):
            assert (rendered_site / page).is_file(), f"Missing {page}"

    def test_research_sub_reports(self, rendered_site):
        for topic in ("market-position", "technology"):
            path = rendered_site / "resources" / f"{topic}.html"
            assert path.is_file(), f"Missing research/{topic}.html"


class TestContentPresence:
    """Shared content assertions."""

    def test_org_name_on_home(self, rendered_site):
        html = (rendered_site / "index.html").read_text()
        assert "acme-corp" in html

    def test_research_synthesis_content(self, rendered_site):
        html = (rendered_site / "resources.html").read_text()
        assert "freight logistics" in html


class TestPageCount:
    def test_minimum_page_count(self, rendered_site):
        pages = list(rendered_site.rglob("*.html"))
        # Client: 4 + Research: 2 + at least 1 project index per BC
        assert len(pages) >= 8, f"Only {len(pages)} pages rendered"
