"""Wardley Mapping project presenter.

Assembles workspace artifacts for a Wardley Mapping project into a
ProjectContribution that any renderer can consume without knowing
the skillset internals.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from practice.content import (
    ContentPage,
    Figure,
    NarrativeGroup,
    NarrativePage,
    NarrativeStop,
    PageGroup,
    ProjectContribution,
    ProjectSection,
)
from practice.entities import Project
from wardley_mapping.types import TourManifest, TourManifestRepository


def _atlas_category(name: str) -> str:
    """Classify an atlas view into a category."""
    if name in ("overview", "layers", "teams", "flows"):
        return "structural"
    if (
        name.startswith("need-")
        or name.startswith("anchor-")
        or name in ("bottlenecks", "shared-components")
    ):
        return "connectivity"
    if name.startswith("play-") or name in (
        "sourcing",
        "evolution-mismatch",
        "pipelines",
    ):
        return "strategic"
    if name in ("movement", "inertia", "forces", "risk", "doctrine"):
        return "dynamic"
    return "strategic"


def _title_case(slug: str) -> str:
    """Convert a slug like 'shared-components' to 'Shared Components'."""
    return " ".join(w.capitalize() for w in slug.split("-"))


def _read_md(path: Path) -> str:
    """Read a markdown file and return its text, or empty string."""
    if path.is_file():
        return path.read_text()
    return ""


def _read_svg(path: Path) -> str:
    """Read an SVG file and return its content, or empty string."""
    if path.is_file():
        return path.read_text()
    return ""


def _extract_second_paragraph(text: str) -> str:
    """Extract the second paragraph from markdown text."""
    paragraphs: list[str] = []
    current: list[str] = []
    for line in text.split("\n"):
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        elif not line.startswith("#"):
            current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs[1] if len(paragraphs) > 1 else ""


class WardleyProjectPresenter:
    """Assembles Wardley Mapping workspace artifacts into structured content."""

    def __init__(
        self,
        workspace_root: Path,
        ensure_owm_script: Path,
        tours: TourManifestRepository,
    ) -> None:
        self._ws_root = workspace_root
        self._ensure_owm = ensure_owm_script
        self._tours = tours

    def present(
        self,
        project: Project,
    ) -> ProjectContribution:
        proj_dir = (
            self._ws_root
            / project.client
            / "engagements"
            / project.engagement
            / project.slug
        )

        self._ensure_owm_svgs(proj_dir)

        tours = self._tours.list_all(project.client, project.engagement, project.slug)

        has_brief = (proj_dir / "brief.agreed.md").is_file()
        has_needs = (proj_dir / "needs" / "needs.agreed.md").is_file()
        has_chain = (proj_dir / "chain" / "supply-chain.agreed.md").is_file()
        has_evolve = (proj_dir / "evolve" / "map.agreed.owm").is_file()
        has_strategy = (proj_dir / "strategy" / "map.agreed.owm").is_file()
        has_atlas = (proj_dir / "atlas").is_dir()
        has_presentations = bool(tours)
        has_decisions = (proj_dir / "decisions.md").is_file()
        has_analysis = any(
            [has_brief, has_needs, has_chain, has_evolve, has_strategy, has_decisions]
        )

        sections: list[ProjectSection] = []

        if has_presentations:
            sections.append(self._build_presentations_section(proj_dir, tours))

        if has_atlas:
            sections.append(self._build_atlas_section(proj_dir))

        if has_analysis:
            sections.append(
                self._build_analysis_section(
                    proj_dir,
                    has_brief,
                    has_needs,
                    has_chain,
                    has_evolve,
                    has_strategy,
                    has_decisions,
                )
            )

        hero = self._select_hero(proj_dir, has_strategy, has_evolve)

        return ProjectContribution(
            slug=project.slug,
            title=project.slug,
            skillset=project.skillset,
            status=project.status.value,
            hero_figure=hero,
            overview_md="",
            sections=sections,
        )

    # -- OWM rendering -----------------------------------------------------

    def _ensure_owm_svgs(self, project_dir: Path) -> None:
        """Shell out to ensure-owm.sh for all OWM files in the project."""
        for owm in project_dir.rglob("*.owm"):
            svg = owm.with_suffix(".svg")
            if not svg.exists() or owm.stat().st_mtime > svg.stat().st_mtime:
                print(f"    Rendering {owm} -> SVG")
                subprocess.run([str(self._ensure_owm), str(owm)], capture_output=True)

    # -- Hero figure selection ---------------------------------------------

    def _select_hero(
        self, proj_dir: Path, has_strategy: bool, has_evolve: bool
    ) -> Figure | None:
        if has_strategy and (proj_dir / "strategy" / "map.svg").is_file():
            return Figure(
                caption="Strategy map",
                svg_content=_read_svg(proj_dir / "strategy" / "map.svg"),
            )
        if has_evolve and (proj_dir / "evolve" / "map.svg").is_file():
            return Figure(
                caption="Evolution map",
                svg_content=_read_svg(proj_dir / "evolve" / "map.svg"),
            )
        if (proj_dir / "landscape.svg").is_file():
            return Figure(
                caption="Landscape sketch (approximate)",
                svg_content=_read_svg(proj_dir / "landscape.svg"),
            )
        return None

    # -- Presentations section ---------------------------------------------

    def _build_presentations_section(
        self, proj_dir: Path, tours: list[TourManifest]
    ) -> ProjectSection:
        narrative_pages: list[NarrativePage] = []
        for manifest in tours:
            tour_dir = proj_dir / "presentations" / manifest.name
            narrative_pages.append(self._assemble_tour(proj_dir, tour_dir, manifest))

        return ProjectSection(
            label="Presentations",
            slug="presentations",
            description=("Curated tours of the strategy map for different audiences"),
            narratives=narrative_pages,
        )

    def _assemble_tour(
        self,
        proj_dir: Path,
        tour_dir: Path,
        manifest: TourManifest,
    ) -> NarrativePage:
        if not manifest.stops:
            return NarrativePage(
                title=manifest.title,
                slug=manifest.name,
                description="",
                opening_md="",
                groups=[],
            )

        # Group stops by base order (strip trailing letters)
        raw_groups: list[dict] = []
        current_base = None
        current_stops: list = []
        for stop in manifest.stops:
            base = re.sub(r"[a-z]+$", "", stop.order)
            if base != current_base:
                if current_stops:
                    raw_groups.append({"base": current_base, "stops": current_stops})
                current_base = base
                current_stops = [stop]
            else:
                current_stops.append(stop)
        if current_stops:
            raw_groups.append({"base": current_base, "stops": current_stops})

        # Transition files
        trans_dir = tour_dir / "transitions"
        trans_files = sorted(trans_dir.glob("*.md")) if trans_dir.is_dir() else []

        # Opening
        opening_md = _read_md(tour_dir / "opening.md")

        # Description from opening
        description = _extract_second_paragraph(opening_md) if opening_md else ""

        # Build groups
        groups: list[NarrativeGroup] = []
        for gi, group in enumerate(raw_groups):
            stops: list[NarrativeStop] = []
            for stop in group["stops"]:
                has_suffix = bool(re.search(r"[a-z]$", stop.order))
                level = "h3" if has_suffix else "h2"

                if not stop.atlas_source:
                    stops.append(
                        NarrativeStop(
                            title=stop.title,
                            level=level,
                            is_header=True,
                            figures=[],
                            analysis_md="",
                        )
                    )
                    continue

                atlas_path = proj_dir / stop.atlas_source.rstrip("/")
                figures = self._collect_stop_figures(atlas_path, stop.map_file)
                analysis_md = _read_md(atlas_path / stop.analysis_file)

                stops.append(
                    NarrativeStop(
                        title=stop.title,
                        level=level,
                        is_header=False,
                        figures=figures,
                        analysis_md=analysis_md,
                    )
                )

            transition_md = ""
            if gi < len(trans_files) and trans_files[gi].is_file():
                transition_md = trans_files[gi].read_text()

            groups.append(NarrativeGroup(stops=stops, transition_md=transition_md))

        return NarrativePage(
            title=manifest.title,
            slug=manifest.name,
            description=description,
            opening_md=opening_md,
            groups=groups,
        )

    def _collect_stop_figures(self, atlas_path: Path, map_file: str) -> list[Figure]:
        svg_path = atlas_path / map_file
        if svg_path.is_file():
            return [Figure(caption="", svg_content=_read_svg(svg_path))]

        # Fallback: first SVG in directory
        for svg_file in sorted(atlas_path.glob("*.svg")):
            return [Figure(caption="", svg_content=_read_svg(svg_file))]

        return []

    # -- Atlas section -----------------------------------------------------

    def _build_atlas_section(self, proj_dir: Path) -> ProjectSection:
        atlas_dir = proj_dir / "atlas"

        views: list[str] = []
        for view_dir in sorted(atlas_dir.iterdir()):
            if not view_dir.is_dir():
                continue
            if not (view_dir / "analysis.md").is_file():
                continue
            views.append(view_dir.name)

        # Build category groups
        cat_order = ["structural", "connectivity", "strategic", "dynamic"]
        cat_labels = {
            "structural": "Structural",
            "connectivity": "Connectivity",
            "strategic": "Strategic",
            "dynamic": "Dynamic",
        }
        cat_pages: dict[str, list[ContentPage]] = {c: [] for c in cat_order}

        for v in views:
            view_dir = atlas_dir / v
            figures = self._collect_atlas_figures(view_dir)
            analysis_md = _read_md(view_dir / "analysis.md")

            page = ContentPage(
                title=_title_case(v),
                slug=v,
                body_md=analysis_md,
                figures=figures,
            )
            cat = _atlas_category(v)
            cat_pages[cat].append(page)

        groups: list[PageGroup] = []
        for cat_name in cat_order:
            if cat_pages[cat_name]:
                groups.append(
                    PageGroup(
                        label=cat_labels[cat_name],
                        slug=cat_name,
                        pages=cat_pages[cat_name],
                    )
                )

        return ProjectSection(
            label="Atlas",
            slug="atlas",
            description=(
                "Analytical views derived from the comprehensive strategy map"
            ),
            groups=groups,
        )

    def _collect_atlas_figures(self, view_dir: Path) -> list[Figure]:
        svgs = sorted(view_dir.glob("*.svg"))
        if len(svgs) > 1:
            return [
                Figure(caption=_title_case(svg.stem), svg_content=_read_svg(svg))
                for svg in svgs
            ]
        if (view_dir / "map.svg").is_file():
            return [Figure(caption="", svg_content=_read_svg(view_dir / "map.svg"))]
        if svgs:
            return [Figure(caption="", svg_content=_read_svg(svgs[0]))]
        return []

    # -- Analysis section --------------------------------------------------

    def _build_analysis_section(
        self,
        proj_dir: Path,
        has_brief: bool,
        has_needs: bool,
        has_chain: bool,
        has_evolve: bool,
        has_strategy: bool,
        has_decisions: bool,
    ) -> ProjectSection:
        pages: list[ContentPage] = []

        if has_strategy:
            pages.append(self._build_strategy_page(proj_dir / "strategy"))
        if has_evolve:
            pages.append(self._build_evolve_page(proj_dir / "evolve"))
        if has_chain:
            pages.append(
                ContentPage(
                    title="Supply Chain",
                    slug="supply-chain",
                    body_md=_read_md(proj_dir / "chain" / "supply-chain.agreed.md"),
                )
            )
        if has_needs:
            pages.append(
                ContentPage(
                    title="User Needs",
                    slug="needs",
                    body_md=_read_md(proj_dir / "needs" / "needs.agreed.md"),
                )
            )
        if has_brief:
            pages.append(
                ContentPage(
                    title="Project Brief",
                    slug="brief",
                    body_md=_read_md(proj_dir / "brief.agreed.md"),
                )
            )
        if has_decisions:
            pages.append(
                ContentPage(
                    title="Decisions",
                    slug="decisions",
                    body_md=_read_md(proj_dir / "decisions.md"),
                )
            )

        return ProjectSection(
            label="Analysis",
            slug="analysis",
            description="Pipeline stages from brief through strategy",
            pages=pages,
        )

    def _build_strategy_page(self, strategy_dir: Path) -> ContentPage:
        figures: list[Figure] = []
        svg_path = strategy_dir / "map.svg"
        if svg_path.is_file():
            figures.append(
                Figure(caption="Strategy map", svg_content=_read_svg(svg_path))
            )

        body_parts: list[str] = []
        plays_dir = strategy_dir / "plays"
        if plays_dir.is_dir():
            for f in sorted(plays_dir.glob("*.md")):
                body_parts.append(f.read_text())

        return ContentPage(
            title="Strategy",
            slug="strategy",
            body_md="\n\n---\n\n".join(body_parts),
            figures=figures,
        )

    def _build_evolve_page(self, evolve_dir: Path) -> ContentPage:
        figures: list[Figure] = []
        svg_path = evolve_dir / "map.svg"
        if svg_path.is_file():
            figures.append(
                Figure(caption="Evolution map", svg_content=_read_svg(svg_path))
            )

        body_parts: list[str] = []
        assessments_dir = evolve_dir / "assessments"
        if assessments_dir.is_dir():
            for f in sorted(assessments_dir.glob("*.md")):
                body_parts.append(f.read_text())

        return ContentPage(
            title="Evolution Map",
            slug="map",
            body_md="\n\n---\n\n".join(body_parts),
            figures=figures,
        )
