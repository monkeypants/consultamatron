"""Jinja2 + Markdown site renderer implementation.

Infrastructure implementation of the SiteRenderer protocol. Takes
structured entity data from the usecase and workspace prose files,
produces a static HTML site using Jinja2 templates and the Python
markdown library.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

from bin.cli.entities import (
    Figure,
    Project,
    ProjectContribution,
    ProjectSection,
    ResearchTopic,
    TourManifest,
    TourPageContent,
)


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def _preprocess_trees(text):
    """Fence box-drawing character runs in code blocks."""
    box_chars = re.compile(r"[├│└─┌┐┬┤┼┘┴]")
    lines = text.split("\n")
    out = []
    in_fence = False
    in_tree = False
    for line in lines:
        if line.startswith("```"):
            if in_tree:
                out.append("```")
                in_tree = False
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        if box_chars.search(line):
            if not in_tree:
                out.append("```")
                in_tree = True
            out.append(line)
        else:
            if in_tree:
                out.append("```")
                in_tree = False
            out.append(line)
    if in_tree:
        out.append("```")
    return "\n".join(out)


def _preprocess_kv(text):
    """Insert blank line before **Label**: lines that follow non-blank lines."""
    lines = text.split("\n")
    out = []
    kv_re = re.compile(r"^\*\*[^*]+\*\*:")
    for i, line in enumerate(lines):
        if kv_re.match(line) and i > 0 and lines[i - 1].strip():
            out.append("")
        out.append(line)
    return "\n".join(out)


def _preprocess_lists(text):
    """Insert blank line before the first list item after a paragraph."""
    lines = text.split("\n")
    out = []
    list_re = re.compile(r"^(\s*[-*+]|\s*\d+\.) ")
    in_list = False
    for i, line in enumerate(lines):
        is_list_item = bool(list_re.match(line))
        is_continuation = not is_list_item and line.startswith("  ") and line.strip()
        if is_list_item:
            if not in_list and i > 0 and lines[i - 1].strip():
                out.append("")
            in_list = True
        elif is_continuation and in_list:
            pass
        elif not line.strip() and in_list:
            pass
        else:
            in_list = False
        out.append(line)
    return "\n".join(out)


def _md_to_html(text):
    """Preprocess and convert markdown to HTML, stripping the first H1."""
    text = _preprocess_kv(text)
    text = _preprocess_lists(text)
    text = _preprocess_trees(text)
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    html = re.sub(r"<h1[^>]*>.*?</h1>", "", html, count=1, flags=re.DOTALL)
    return html.strip()


# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------


def _embed_svg(svg_path, caption=""):
    """Read an SVG file and return <figure> HTML."""
    p = Path(svg_path)
    if not p.is_file():
        return ""
    svg_content = p.read_text()
    svg_content = svg_content.replace(
        "<svg ", '<svg style="max-width:100%;height:auto" ', 1
    )
    parts = ["<figure>", svg_content]
    if caption:
        parts.append(f"<figcaption>{caption}</figcaption>")
    parts.append("</figure>")
    return "\n".join(parts)


def _read_md(path):
    """Read a markdown file and return its text, or empty string."""
    p = Path(path)
    if p.is_file():
        return p.read_text()
    return ""


def _extract_h1(text):
    """Extract the first H1 text from markdown."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _title_case(slug):
    """Convert a slug like 'shared-components' to 'Shared Components'."""
    return " ".join(w.capitalize() for w in slug.split("-"))


def _extract_second_paragraph(text):
    """Extract the second paragraph from markdown text."""
    paragraphs = []
    current = []
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


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------


def _build_breadcrumb(*crumbs):
    """Build breadcrumb list. Last crumb has no url."""
    result = []
    for i, crumb in enumerate(crumbs):
        if i == len(crumbs) - 1:
            result.append({"label": crumb[0]})
        else:
            result.append({"label": crumb[0], "url": crumb[1]})
    return result


def _build_client_nav(active, has_engagement=True):
    """Build client-level nav items."""
    items = [
        {"label": "Home", "url": "index.html", "active": active == "index"},
        {"label": "Projects", "url": "projects.html", "active": active == "projects"},
        {"label": "Research", "url": "resources.html", "active": active == "resources"},
    ]
    if has_engagement:
        items.append(
            {
                "label": "History",
                "url": "engagement.html",
                "active": active == "engagement",
            }
        )
    return items


def _build_project_nav(active, depth, has_presentations, has_atlas, has_analysis):
    """Build project-level nav items with depth-aware paths."""
    prefix = "../" if depth == 1 else ""
    items = [
        {
            "label": "Overview",
            "url": f"{prefix}index.html",
            "active": active == "index",
        },
    ]
    if has_presentations:
        items.append(
            {
                "label": "Presentations",
                "url": f"{prefix}presentations/index.html",
                "active": active == "presentations",
            }
        )
    if has_atlas:
        items.append(
            {
                "label": "Atlas",
                "url": f"{prefix}atlas/index.html",
                "active": active == "atlas",
            }
        )
    if has_analysis:
        items.append(
            {
                "label": "Analysis",
                "url": f"{prefix}analysis/index.html",
                "active": active == "analysis",
            }
        )
    return items


def _atlas_category(name):
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


# ---------------------------------------------------------------------------
# Render helper
# ---------------------------------------------------------------------------


def _render_page(env, template_name, output_path, **ctx):
    """Render a template to a file."""
    tmpl = env.get_template(template_name)
    html = tmpl.render(**ctx)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html)


# ---------------------------------------------------------------------------
# JinjaSiteRenderer
# ---------------------------------------------------------------------------


class JinjaSiteRenderer:
    """Jinja2 + Markdown implementation of SiteRenderer.

    Constructed with workspace and repo paths. The render() method
    receives structured data from the usecase and reads prose content
    directly from the workspace filesystem.
    """

    def __init__(self, workspace_root: Path, repo_root: Path) -> None:
        self._ws_root = workspace_root
        self._template_dir = repo_root / "bin" / "templates"
        self._css_file = repo_root / "bin" / "site.css"
        self._ensure_owm = repo_root / "bin" / "ensure-owm.sh"

    # -- Public interface --------------------------------------------------

    def render(
        self,
        client: str,
        projects: list[Project],
        tours: dict[str, list[TourManifest]],
        research_topics: list[ResearchTopic],
    ) -> Path:
        ws = self._ws_root / client
        site = ws / "site"

        env = Environment(
            loader=FileSystemLoader(str(self._template_dir)),
            autoescape=False,
        )

        org_name = self._extract_org_name(ws, client)

        if site.exists():
            shutil.rmtree(site)
        site.mkdir(parents=True)
        (site / "resources").mkdir()
        shutil.copy(self._css_file, site / "style.css")

        print(f"Workspace: {ws} ({org_name})")
        print("Generating client pages...")

        self._render_client_pages(ws, site, env, org_name, research_topics)

        for project in projects:
            proj_dir = ws / "projects" / project.slug
            site_proj_dir = site / project.slug
            site_proj_dir.mkdir(parents=True, exist_ok=True)

            project_tours = tours.get(project.slug, [])

            print(f"\nProject: {project.slug}")

            if project.skillset == "wardley-mapping":
                self._render_wardley_project(
                    proj_dir, site_proj_dir, org_name, env, project_tours
                )
            elif project.skillset == "business-model-canvas":
                self._render_bmc_project(proj_dir, site_proj_dir, org_name, env)
            else:
                print(f"    Unknown skillset '{project.skillset}', skipping")

        print(f"\nSite generated: {site}/")
        return site

    # -- Internal helpers --------------------------------------------------

    def _extract_org_name(self, ws, client):
        """Derive display name from engagement.md or fall back to slug."""
        eng_path = ws / "engagement.md"
        if eng_path.is_file():
            for line in eng_path.read_text().split("\n"):
                m = re.search(r"^#.*—\s*(.+)$", line)
                if m:
                    return m.group(1).strip()
        return client

    def _ensure_owm_svgs(self, project_dir):
        """Shell out to ensure-owm.sh for all OWM files in the project."""
        for owm in Path(project_dir).rglob("*.owm"):
            svg = owm.with_suffix(".svg")
            if not svg.exists() or owm.stat().st_mtime > svg.stat().st_mtime:
                print(f"    Rendering {owm} -> SVG")
                subprocess.run([str(self._ensure_owm), str(owm)], capture_output=True)

    # -- Client pages ------------------------------------------------------

    def _render_client_pages(self, ws, site, env, org_name, research_topics):
        ws = Path(ws)
        site = Path(site)
        has_engagement = (ws / "engagement.md").is_file()

        # Home page
        content_parts = []
        engagement_text = _read_md(ws / "engagement.md")
        if engagement_text:
            content_parts.append(_md_to_html(engagement_text))

        _render_page(
            env,
            "base.html",
            site / "index.html",
            title="Home",
            org_name=org_name,
            heading=org_name,
            css_path="style.css",
            breadcrumb=[],
            nav=_build_client_nav("index", has_engagement),
            toc=None,
            content=Markup("\n".join(content_parts)),
        )

        # Projects page
        projects_md = _read_md(ws / "projects" / "index.md")
        project_dirs = (
            sorted(
                p.name
                for p in (ws / "projects").iterdir()
                if p.is_dir() and p.name != "site"
            )
            if (ws / "projects").is_dir()
            else []
        )

        projects_html = _md_to_html(projects_md) if projects_md else ""

        for pname in project_dirs:
            projects_html = projects_html.replace(
                f">{pname}<", f'><a href="{pname}/index.html">{pname}</a><'
            )
            projects_html = re.sub(
                rf"(<h[23]>)({re.escape(pname)})(:.+?)(</h[23]>)",
                rf'\1<a href="{pname}/index.html">\2\3</a>\4',
                projects_html,
            )

        _render_page(
            env,
            "base.html",
            site / "projects.html",
            title=f"Projects — {org_name}",
            org_name=org_name,
            heading="Projects",
            css_path="style.css",
            breadcrumb=_build_breadcrumb((org_name, "index.html"), ("Projects",)),
            nav=_build_client_nav("projects", has_engagement),
            toc=None,
            content=Markup(projects_html),
        )

        # Research pages — use structured topics for TOC, fall back to
        # filesystem scan if no topics registered
        if research_topics:
            research_files = []
            for rt in research_topics:
                rf = ws / "resources" / rt.filename
                if rf.is_file():
                    research_files.append((rf, rt.topic))
        else:
            research_files = [
                (p, _extract_h1(p.read_text()) or _title_case(p.stem))
                for p in sorted((ws / "resources").glob("*.md"))
                if p.name != "index.md"
            ]

        research_toc_entries = [
            {"label": "Synthesis", "url": "resources.html", "active": False}
        ]
        for rf, title in research_files:
            slug = rf.stem
            research_toc_entries.append(
                {"label": title, "url": f"resources/{slug}.html", "active": False}
            )

        # Synthesis page
        synth_toc = [
            dict(e, active=(e["label"] == "Synthesis")) for e in research_toc_entries
        ]
        synth_md = _read_md(ws / "resources" / "index.md")
        _render_page(
            env,
            "base.html",
            site / "resources.html",
            title=f"Research — {org_name}",
            org_name=org_name,
            heading="Research",
            css_path="style.css",
            breadcrumb=_build_breadcrumb((org_name, "index.html"), ("Research",)),
            nav=_build_client_nav("resources", has_engagement),
            toc=synth_toc,
            content=Markup(_md_to_html(synth_md)),
        )
        print("  resources.html")

        # Sub-report pages
        for rf, title in research_files:
            slug = rf.stem
            sub_toc = []
            for e in research_toc_entries:
                entry = dict(e)
                entry["active"] = entry["label"] == title
                if not entry["url"].startswith("resources/"):
                    entry["url"] = f"../{entry['url']}"
                else:
                    entry["url"] = entry["url"].replace("resources/", "")
                sub_toc.append(entry)

            sub_nav = [
                {**item, "url": f"../{item['url']}"}
                for item in _build_client_nav("resources", has_engagement)
            ]

            _render_page(
                env,
                "base.html",
                site / "resources" / f"{slug}.html",
                title=f"{title} — {org_name}",
                org_name=org_name,
                heading=title,
                css_path="../style.css",
                breadcrumb=_build_breadcrumb(
                    (org_name, "../index.html"),
                    ("Research", "../resources.html"),
                    (title,),
                ),
                nav=sub_nav,
                toc=sub_toc,
                content=Markup(_md_to_html(rf.read_text())),
            )
            print(f"  resources/{slug}.html")

        # Engagement page
        if has_engagement:
            eng_md = _read_md(ws / "engagement.md")
            _render_page(
                env,
                "base.html",
                site / "engagement.html",
                title=f"History — {org_name}",
                org_name=org_name,
                heading="Engagement History",
                css_path="style.css",
                breadcrumb=_build_breadcrumb((org_name, "index.html"), ("History",)),
                nav=_build_client_nav("engagement", has_engagement),
                toc=None,
                content=Markup(_md_to_html(eng_md)),
            )
            print("  engagement.html")

    # -- Wardley project ---------------------------------------------------

    def _render_wardley_project(
        self, project_dir, site_dir, org_name, env, project_tours
    ):
        project_dir = Path(project_dir)
        site_dir = Path(site_dir)
        project_name = project_dir.name

        self._ensure_owm_svgs(project_dir)

        has_brief = (project_dir / "brief.agreed.md").is_file()
        has_needs = (project_dir / "needs" / "needs.agreed.md").is_file()
        has_chain = (project_dir / "chain" / "supply-chain.agreed.md").is_file()
        has_evolve = (project_dir / "evolve" / "map.agreed.owm").is_file()
        has_strategy = (project_dir / "strategy" / "map.agreed.owm").is_file()
        has_atlas = (project_dir / "atlas").is_dir()
        has_presentations = bool(project_tours)
        has_decisions = (project_dir / "decisions.md").is_file()
        has_analysis = any(
            [has_brief, has_needs, has_chain, has_evolve, has_strategy, has_decisions]
        )

        print(
            f"    Stages: brief={has_brief} needs={has_needs} chain={has_chain} "
            f"evolve={has_evolve} strategy={has_strategy}"
        )
        print(f"    Extras: atlas={has_atlas} presentations={has_presentations}")

        # Legacy flat mode
        if not has_atlas and not has_presentations:
            self._render_wardley_legacy(
                project_dir,
                site_dir,
                org_name,
                project_name,
                env,
                has_brief,
                has_needs,
                has_chain,
                has_evolve,
                has_strategy,
                has_decisions,
            )
            return

        # Three-tier IA
        nav_args = dict(
            has_presentations=has_presentations,
            has_atlas=has_atlas,
            has_analysis=has_analysis,
        )

        def project_breadcrumb(section_label=None, depth=0):
            if depth == 0:
                return _build_breadcrumb(
                    (org_name, "../index.html"),
                    (project_name,),
                )
            crumbs = [
                (org_name, "../../index.html"),
                (project_name, "../index.html"),
            ]
            if section_label:
                crumbs.append((section_label,))
            return _build_breadcrumb(*crumbs)

        # Presentations
        if has_presentations:
            site_dir.joinpath("presentations").mkdir(parents=True, exist_ok=True)

            tour_infos = []
            for manifest in project_tours:
                tour_dir = project_dir / "presentations" / manifest.name
                desc = ""
                opening_path = tour_dir / "opening.md"
                if opening_path.is_file():
                    desc = _extract_second_paragraph(opening_path.read_text())

                tour_infos.append(
                    {
                        "name": manifest.name,
                        "url": f"{manifest.name}.html",
                        "title": manifest.title,
                        "description": desc,
                    }
                )

            def presentations_toc(active_name=None):
                toc = []
                for t in tour_infos:
                    toc.append(
                        {
                            "label": t["title"],
                            "url": t["url"],
                            "active": t["name"] == active_name,
                        }
                    )
                return toc

            _render_page(
                env,
                "presentations_index.html",
                site_dir / "presentations" / "index.html",
                title=f"Presentations — {project_name} — {org_name}",
                org_name=org_name,
                heading="Presentations",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Presentations", 1),
                nav=_build_project_nav("presentations", 1, **nav_args),
                toc=None,
                tours=tour_infos,
            )
            print("    presentations/index.html")

            for manifest in project_tours:
                tour_dir = project_dir / "presentations" / manifest.name
                self._render_tour_page(
                    env,
                    tour_dir,
                    manifest,
                    site_dir / "presentations" / f"{manifest.name}.html",
                    project_dir,
                    org_name,
                    project_name,
                    _build_project_nav("presentations", 1, **nav_args),
                    project_breadcrumb("Presentations", 1),
                    presentations_toc(manifest.name),
                )

        # Atlas
        if has_atlas:
            site_dir.joinpath("atlas").mkdir(parents=True, exist_ok=True)

            views = []
            for view_dir in sorted((project_dir / "atlas").iterdir()):
                if not view_dir.is_dir():
                    continue
                if not (view_dir / "analysis.md").is_file():
                    continue
                views.append(view_dir.name)

            categories = [
                {"name": "structural", "label": "Structural", "views": []},
                {"name": "connectivity", "label": "Connectivity", "views": []},
                {"name": "strategic", "label": "Strategic", "views": []},
                {"name": "dynamic", "label": "Dynamic", "views": []},
            ]
            cat_map = {c["name"]: c for c in categories}
            for v in views:
                cat = _atlas_category(v)
                cat_map[cat]["views"].append(
                    {"name": _title_case(v), "url": f"{v}.html"}
                )

            def atlas_toc(active_name=None):
                toc = []
                for v in views:
                    toc.append(
                        {
                            "label": _title_case(v),
                            "url": f"{v}.html",
                            "active": v == active_name,
                        }
                    )
                return toc

            _render_page(
                env,
                "atlas_index.html",
                site_dir / "atlas" / "index.html",
                title=f"Atlas — {project_name} — {org_name}",
                org_name=org_name,
                heading="Atlas",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Atlas", 1),
                nav=_build_project_nav("atlas", 1, **nav_args),
                toc=None,
                categories=categories,
            )
            print("    atlas/index.html")

            for v in views:
                view_dir = project_dir / "atlas" / v
                self._render_atlas_view_page(
                    env,
                    view_dir,
                    v,
                    site_dir / "atlas" / f"{v}.html",
                    org_name,
                    project_name,
                    _build_project_nav("atlas", 1, **nav_args),
                    project_breadcrumb("Atlas", 1),
                    atlas_toc(v),
                )

        # Analysis
        if has_analysis:
            self._render_analysis_pages(
                env,
                project_dir,
                site_dir,
                org_name,
                project_name,
                nav_args,
                project_breadcrumb,
                has_brief,
                has_needs,
                has_chain,
                has_evolve,
                has_strategy,
                has_decisions,
            )

        # Project index
        content = ""
        if has_strategy and (project_dir / "strategy" / "map.svg").is_file():
            content += _embed_svg(project_dir / "strategy" / "map.svg", "Strategy map")
        elif has_evolve and (project_dir / "evolve" / "map.svg").is_file():
            content += _embed_svg(project_dir / "evolve" / "map.svg", "Evolution map")
        elif (project_dir / "landscape.svg").is_file():
            content += _embed_svg(
                project_dir / "landscape.svg", "Landscape sketch (approximate)"
            )

        content += '<ul class="section-list">'
        if has_presentations:
            content += (
                '<li><a href="presentations/index.html">Presentations</a>'
                '<span class="desc">Curated tours of the strategy map for '
                "different audiences</span></li>"
            )
        if has_atlas:
            content += (
                '<li><a href="atlas/index.html">Atlas</a>'
                '<span class="desc">Analytical views derived from the '
                "comprehensive strategy map</span></li>"
            )
        if has_analysis:
            content += (
                '<li><a href="analysis/index.html">Analysis</a>'
                '<span class="desc">Pipeline stages from brief through '
                "strategy</span></li>"
            )
        content += "</ul>"

        _render_page(
            env,
            "base.html",
            site_dir / "index.html",
            title=f"Overview — {project_name} — {org_name}",
            org_name=org_name,
            heading="Overview",
            css_path="../style.css",
            breadcrumb=_build_breadcrumb(
                (org_name, "../index.html"),
                (project_name,),
            ),
            nav=_build_project_nav("index", 0, **nav_args),
            toc=None,
            content=Markup(content),
        )
        print("    index.html")

    def _render_analysis_pages(
        self,
        env,
        project_dir,
        site_dir,
        org_name,
        project_name,
        nav_args,
        project_breadcrumb,
        has_brief,
        has_needs,
        has_chain,
        has_evolve,
        has_strategy,
        has_decisions,
    ):
        """Render all analysis sub-pages."""
        site_dir.joinpath("analysis").mkdir(parents=True, exist_ok=True)

        analysis_items = []
        if has_strategy:
            analysis_items.append(("Strategy", "strategy"))
        if has_evolve:
            analysis_items.append(("Evolution Map", "map"))
        if has_chain:
            analysis_items.append(("Supply Chain", "supply-chain"))
        if has_needs:
            analysis_items.append(("User Needs", "needs"))
        if has_brief:
            analysis_items.append(("Project Brief", "brief"))
        if has_decisions:
            analysis_items.append(("Decisions", "decisions"))

        def analysis_toc(active_slug=None):
            return [
                {"label": label, "url": f"{slug}.html", "active": slug == active_slug}
                for label, slug in analysis_items
            ]

        # Analysis index
        _render_page(
            env,
            "base.html",
            site_dir / "analysis" / "index.html",
            title=f"Analysis — {project_name} — {org_name}",
            org_name=org_name,
            heading="Analysis",
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Analysis", 1),
            nav=_build_project_nav("analysis", 1, **nav_args),
            toc=analysis_toc(),
            content=Markup(""),
        )
        print("    analysis/index.html")

        shared = dict(
            org_name=org_name,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Analysis", 1),
            nav=_build_project_nav("analysis", 1, **nav_args),
        )

        if has_strategy:
            content = ""
            svg_path = project_dir / "strategy" / "map.svg"
            if svg_path.is_file():
                content += _embed_svg(svg_path, "Strategy map")
            plays_dir = project_dir / "strategy" / "plays"
            if plays_dir.is_dir():
                for f in sorted(plays_dir.glob("*.md")):
                    content += _md_to_html(f.read_text()) + "<hr>"
            _render_page(
                env,
                "base.html",
                site_dir / "analysis" / "strategy.html",
                title=f"Strategy — {project_name} — {org_name}",
                heading="Strategy",
                toc=analysis_toc("strategy"),
                content=Markup(content),
                **shared,
            )
            print("    analysis/strategy.html")

        if has_evolve:
            content = ""
            svg_path = project_dir / "evolve" / "map.svg"
            if svg_path.is_file():
                content += _embed_svg(svg_path, "Evolution map")
            assessments_dir = project_dir / "evolve" / "assessments"
            if assessments_dir.is_dir():
                for f in sorted(assessments_dir.glob("*.md")):
                    content += _md_to_html(f.read_text()) + "<hr>"
            _render_page(
                env,
                "base.html",
                site_dir / "analysis" / "map.html",
                title=f"Evolution Map — {project_name} — {org_name}",
                heading="Evolution Map",
                toc=analysis_toc("map"),
                content=Markup(content),
                **shared,
            )
            print("    analysis/map.html")

        if has_chain:
            content = _md_to_html(
                _read_md(project_dir / "chain" / "supply-chain.agreed.md")
            )
            _render_page(
                env,
                "base.html",
                site_dir / "analysis" / "supply-chain.html",
                title=f"Supply Chain — {project_name} — {org_name}",
                heading="Supply Chain",
                toc=analysis_toc("supply-chain"),
                content=Markup(content),
                **shared,
            )
            print("    analysis/supply-chain.html")

        if has_needs:
            content = _md_to_html(_read_md(project_dir / "needs" / "needs.agreed.md"))
            _render_page(
                env,
                "base.html",
                site_dir / "analysis" / "needs.html",
                title=f"User Needs — {project_name} — {org_name}",
                heading="User Needs",
                toc=analysis_toc("needs"),
                content=Markup(content),
                **shared,
            )
            print("    analysis/needs.html")

        if has_brief:
            content = _md_to_html(_read_md(project_dir / "brief.agreed.md"))
            _render_page(
                env,
                "base.html",
                site_dir / "analysis" / "brief.html",
                title=f"Project Brief — {project_name} — {org_name}",
                heading="Project Brief",
                toc=analysis_toc("brief"),
                content=Markup(content),
                **shared,
            )
            print("    analysis/brief.html")

        if has_decisions:
            content = _md_to_html(_read_md(project_dir / "decisions.md"))
            _render_page(
                env,
                "base.html",
                site_dir / "analysis" / "decisions.html",
                title=f"Decisions — {project_name} — {org_name}",
                heading="Decisions",
                toc=analysis_toc("decisions"),
                content=Markup(content),
                **shared,
            )
            print("    analysis/decisions.html")

    # -- Legacy flat Wardley -----------------------------------------------

    def _render_wardley_legacy(
        self,
        project_dir,
        site_dir,
        org_name,
        project_name,
        env,
        has_brief,
        has_needs,
        has_chain,
        has_evolve,
        has_strategy,
        has_decisions,
    ):
        project_dir = Path(project_dir)
        site_dir = Path(site_dir)

        def legacy_nav(active):
            items = [
                {"label": "Overview", "url": "index.html", "active": active == "index"}
            ]
            if has_strategy:
                items.append(
                    {
                        "label": "Strategy",
                        "url": "strategy.html",
                        "active": active == "strategy",
                    }
                )
            if has_evolve:
                items.append(
                    {"label": "Map", "url": "map.html", "active": active == "map"}
                )
            if has_chain:
                items.append(
                    {
                        "label": "Supply Chain",
                        "url": "supply-chain.html",
                        "active": active == "supply-chain",
                    }
                )
            if has_needs:
                items.append(
                    {"label": "Needs", "url": "needs.html", "active": active == "needs"}
                )
            if has_brief:
                items.append(
                    {"label": "Brief", "url": "brief.html", "active": active == "brief"}
                )
            if has_decisions:
                items.append(
                    {
                        "label": "Decisions",
                        "url": "decisions.html",
                        "active": active == "decisions",
                    }
                )
            return items

        bc = _build_breadcrumb((org_name, "../index.html"), (project_name,))

        # Index
        content = ""
        if has_strategy and (project_dir / "strategy" / "map.svg").is_file():
            content += _embed_svg(project_dir / "strategy" / "map.svg", "Strategy map")
        elif has_evolve and (project_dir / "evolve" / "map.svg").is_file():
            content += _embed_svg(project_dir / "evolve" / "map.svg", "Evolution map")
        elif (project_dir / "landscape.svg").is_file():
            content += _embed_svg(
                project_dir / "landscape.svg", "Landscape sketch (approximate)"
            )

        _render_page(
            env,
            "base.html",
            site_dir / "index.html",
            title=f"Overview — {project_name} — {org_name}",
            org_name=org_name,
            heading="Overview",
            css_path="../style.css",
            breadcrumb=bc,
            nav=legacy_nav("index"),
            toc=None,
            content=Markup(content),
        )
        print("    index.html")

        if has_brief:
            _render_page(
                env,
                "base.html",
                site_dir / "brief.html",
                title=f"Project Brief — {project_name} — {org_name}",
                org_name=org_name,
                heading="Project Brief",
                css_path="../style.css",
                breadcrumb=bc,
                nav=legacy_nav("brief"),
                toc=None,
                content=Markup(_md_to_html(_read_md(project_dir / "brief.agreed.md"))),
            )
            print("    brief.html")

        if has_decisions:
            _render_page(
                env,
                "base.html",
                site_dir / "decisions.html",
                title=f"Decisions — {project_name} — {org_name}",
                org_name=org_name,
                heading="Decisions",
                css_path="../style.css",
                breadcrumb=bc,
                nav=legacy_nav("decisions"),
                toc=None,
                content=Markup(_md_to_html(_read_md(project_dir / "decisions.md"))),
            )
            print("    decisions.html")

        if has_needs:
            _render_page(
                env,
                "base.html",
                site_dir / "needs.html",
                title=f"User Needs — {project_name} — {org_name}",
                org_name=org_name,
                heading="User Needs",
                css_path="../style.css",
                breadcrumb=bc,
                nav=legacy_nav("needs"),
                toc=None,
                content=Markup(
                    _md_to_html(_read_md(project_dir / "needs" / "needs.agreed.md"))
                ),
            )
            print("    needs.html")

        if has_chain:
            _render_page(
                env,
                "base.html",
                site_dir / "supply-chain.html",
                title=f"Supply Chain — {project_name} — {org_name}",
                org_name=org_name,
                heading="Supply Chain",
                css_path="../style.css",
                breadcrumb=bc,
                nav=legacy_nav("supply-chain"),
                toc=None,
                content=Markup(
                    _md_to_html(
                        _read_md(project_dir / "chain" / "supply-chain.agreed.md")
                    )
                ),
            )
            print("    supply-chain.html")

        if has_evolve:
            content = ""
            if (project_dir / "evolve" / "map.svg").is_file():
                content += _embed_svg(
                    project_dir / "evolve" / "map.svg", "Evolution map"
                )
            assessments = project_dir / "evolve" / "assessments"
            if assessments.is_dir():
                for f in sorted(assessments.glob("*.md")):
                    content += _md_to_html(f.read_text()) + "<hr>"
            _render_page(
                env,
                "base.html",
                site_dir / "map.html",
                title=f"Evolution Map — {project_name} — {org_name}",
                org_name=org_name,
                heading="Evolution Map",
                css_path="../style.css",
                breadcrumb=bc,
                nav=legacy_nav("map"),
                toc=None,
                content=Markup(content),
            )
            print("    map.html")

        if has_strategy:
            content = ""
            if (project_dir / "strategy" / "map.svg").is_file():
                content += _embed_svg(
                    project_dir / "strategy" / "map.svg", "Strategy map"
                )
            plays_dir = project_dir / "strategy" / "plays"
            if plays_dir.is_dir():
                for f in sorted(plays_dir.glob("*.md")):
                    content += _md_to_html(f.read_text()) + "<hr>"
            _render_page(
                env,
                "base.html",
                site_dir / "strategy.html",
                title=f"Strategy — {project_name} — {org_name}",
                org_name=org_name,
                heading="Strategy",
                css_path="../style.css",
                breadcrumb=bc,
                nav=legacy_nav("strategy"),
                toc=None,
                content=Markup(content),
            )
            print("    strategy.html")

    # -- Tour page ---------------------------------------------------------

    def _render_tour_page(
        self,
        env,
        tour_dir,
        manifest,
        output_file,
        project_dir,
        org_name,
        project_name,
        nav,
        breadcrumb,
        toc,
    ):
        """Render a single tour page from a TourManifest entity."""
        if not manifest.stops:
            return

        # Group stops by base order (strip trailing letters)
        groups = []
        current_base = None
        current_stops = []
        for stop in manifest.stops:
            base = re.sub(r"[a-z]+$", "", stop.order)
            if base != current_base:
                if current_stops:
                    groups.append({"base": current_base, "stops": current_stops})
                current_base = base
                current_stops = [stop]
            else:
                current_stops.append(stop)
        if current_stops:
            groups.append({"base": current_base, "stops": current_stops})

        # Collect transition files
        trans_dir = tour_dir / "transitions"
        trans_files = sorted(trans_dir.glob("*.md")) if trans_dir.is_dir() else []

        # Opening
        opening_html = ""
        opening_path = tour_dir / "opening.md"
        if opening_path.is_file():
            opening_html = _md_to_html(opening_path.read_text())

        # Build group data for template
        template_groups = []
        for gi, group in enumerate(groups):
            rendered_rows = []
            for stop in group["stops"]:
                has_suffix = bool(re.search(r"[a-z]$", stop.order))
                level = "h3" if has_suffix else "h2"

                if not stop.atlas_source:
                    rendered_rows.append(
                        {
                            "level": level,
                            "title": stop.title,
                            "is_header": True,
                            "svgs_html": "",
                            "analysis_html": "",
                        }
                    )
                    continue

                atlas_path = project_dir / stop.atlas_source.rstrip("/")

                # Embed SVGs
                svgs_html = ""
                svg_path = atlas_path / stop.map_file
                if svg_path.is_file():
                    svgs_html += _embed_svg(svg_path, "")
                else:
                    # Fallback: look for any SVG
                    for svg_file in sorted(atlas_path.glob("*.svg")):
                        svgs_html += _embed_svg(svg_file, "")
                        break

                # Analysis
                analysis_html = ""
                analysis_path = atlas_path / stop.analysis_file
                if analysis_path.is_file():
                    analysis_html = _md_to_html(analysis_path.read_text())

                rendered_rows.append(
                    {
                        "level": level,
                        "title": stop.title,
                        "is_header": False,
                        "svgs_html": Markup(svgs_html),
                        "analysis_html": Markup(analysis_html),
                    }
                )

            # Transition after this group
            transition_html = ""
            if gi < len(trans_files):
                trans_file = trans_files[gi]
                if trans_file.is_file():
                    transition_html = _md_to_html(trans_file.read_text())

            template_groups.append(
                {
                    "rows": rendered_rows,
                    "transition_html": Markup(transition_html),
                }
            )

        _render_page(
            env,
            "tour.html",
            output_file,
            title=f"{manifest.title} — {project_name} — {org_name}",
            org_name=org_name,
            heading=manifest.title,
            css_path="../../style.css",
            breadcrumb=breadcrumb,
            nav=nav,
            toc=toc,
            opening_html=Markup(opening_html),
            groups=template_groups,
        )
        print(f"    presentations/{manifest.name}.html")

    # -- Atlas view page ---------------------------------------------------

    def _render_atlas_view_page(
        self,
        env,
        view_dir,
        view_name,
        output_file,
        org_name,
        project_name,
        nav,
        breadcrumb,
        toc,
    ):
        view_dir = Path(view_dir)
        title = _title_case(view_name)

        svgs = sorted(view_dir.glob("*.svg"))
        content = ""

        if len(svgs) > 1:
            for svg in svgs:
                caption = _title_case(svg.stem)
                content += _embed_svg(svg, caption)
        elif (view_dir / "map.svg").is_file():
            content += _embed_svg(view_dir / "map.svg", "")
        elif svgs:
            content += _embed_svg(svgs[0], "")

        analysis_path = view_dir / "analysis.md"
        if analysis_path.is_file():
            content += _md_to_html(analysis_path.read_text())

        _render_page(
            env,
            "base.html",
            output_file,
            title=f"{title} — {project_name} — {org_name}",
            org_name=org_name,
            heading=title,
            css_path="../../style.css",
            breadcrumb=breadcrumb,
            nav=nav,
            toc=toc,
            content=Markup(content),
        )
        print(f"    atlas/{view_name}.html")

    # -- BMC project -------------------------------------------------------

    def _render_bmc_project(self, project_dir, site_dir, org_name, env):
        project_dir = Path(project_dir)
        site_dir = Path(site_dir)
        project_name = project_dir.name

        has_brief = (project_dir / "brief.agreed.md").is_file()
        has_segments = (project_dir / "segments" / "segments.agreed.md").is_file()
        has_canvas = (project_dir / "canvas.agreed.md").is_file()
        has_decisions = (project_dir / "decisions.md").is_file()

        print(
            f"    Stages: brief={has_brief} segments={has_segments} canvas={has_canvas}"
        )

        def bmc_nav(active):
            items = [
                {"label": "Overview", "url": "index.html", "active": active == "index"}
            ]
            if has_canvas:
                items.append(
                    {
                        "label": "Canvas",
                        "url": "canvas.html",
                        "active": active == "canvas",
                    }
                )
            if has_segments:
                items.append(
                    {
                        "label": "Segments",
                        "url": "segments.html",
                        "active": active == "segments",
                    }
                )
            if has_brief:
                items.append(
                    {
                        "label": "Brief",
                        "url": "brief.html",
                        "active": active == "brief",
                    }
                )
            if has_decisions:
                items.append(
                    {
                        "label": "Decisions",
                        "url": "decisions.html",
                        "active": active == "decisions",
                    }
                )
            return items

        bc = _build_breadcrumb((org_name, "../index.html"), (project_name,))

        # Index
        content = ""
        if has_canvas:
            content = _md_to_html(_read_md(project_dir / "canvas.agreed.md"))
        _render_page(
            env,
            "base.html",
            site_dir / "index.html",
            title=f"Overview — {project_name} — {org_name}",
            org_name=org_name,
            heading="Overview",
            css_path="../style.css",
            breadcrumb=bc,
            nav=bmc_nav("index"),
            toc=None,
            content=Markup(content),
        )
        print("    index.html")

        if has_canvas:
            _render_page(
                env,
                "base.html",
                site_dir / "canvas.html",
                title=f"Business Model Canvas — {project_name} — {org_name}",
                org_name=org_name,
                heading="Business Model Canvas",
                css_path="../style.css",
                breadcrumb=bc,
                nav=bmc_nav("canvas"),
                toc=None,
                content=Markup(_md_to_html(_read_md(project_dir / "canvas.agreed.md"))),
            )
            print("    canvas.html")

        if has_segments:
            _render_page(
                env,
                "base.html",
                site_dir / "segments.html",
                title=f"Customer Segments — {project_name} — {org_name}",
                org_name=org_name,
                heading="Customer Segments",
                css_path="../style.css",
                breadcrumb=bc,
                nav=bmc_nav("segments"),
                toc=None,
                content=Markup(
                    _md_to_html(
                        _read_md(project_dir / "segments" / "segments.agreed.md")
                    )
                ),
            )
            print("    segments.html")

        if has_brief:
            _render_page(
                env,
                "base.html",
                site_dir / "brief.html",
                title=f"Project Brief — {project_name} — {org_name}",
                org_name=org_name,
                heading="Project Brief",
                css_path="../style.css",
                breadcrumb=bc,
                nav=bmc_nav("brief"),
                toc=None,
                content=Markup(_md_to_html(_read_md(project_dir / "brief.agreed.md"))),
            )
            print("    brief.html")

        if has_decisions:
            _render_page(
                env,
                "base.html",
                site_dir / "decisions.html",
                title=f"Decisions — {project_name} — {org_name}",
                org_name=org_name,
                heading="Decisions",
                css_path="../style.css",
                breadcrumb=bc,
                nav=bmc_nav("decisions"),
                toc=None,
                content=Markup(_md_to_html(_read_md(project_dir / "decisions.md"))),
            )
            print("    decisions.html")

    # -- Contribution-based rendering (new path) --------------------------

    def _figure_to_html(self, figure: Figure) -> str:
        """Convert a Figure entity to <figure> HTML."""
        svg = figure.svg_content.replace(
            "<svg ", '<svg style="max-width:100%;height:auto" ', 1
        )
        parts = ["<figure>", svg]
        if figure.caption:
            parts.append(f"<figcaption>{figure.caption}</figcaption>")
        parts.append("</figure>")
        return "\n".join(parts)

    def _render_project_from_contribution(
        self,
        contrib: ProjectContribution,
        site_dir,
        org_name: str,
        env,
    ) -> None:
        """Render a project from a ProjectContribution entity."""
        site_dir = Path(site_dir)
        project_name = contrib.slug

        has_presentations = any(s.slug == "presentations" for s in contrib.sections)
        has_atlas = any(s.slug == "atlas" for s in contrib.sections)
        has_analysis = any(s.slug == "analysis" for s in contrib.sections)

        nav_args = dict(
            has_presentations=has_presentations,
            has_atlas=has_atlas,
            has_analysis=has_analysis,
        )

        def project_breadcrumb(section_label=None, depth=0):
            if depth == 0:
                return _build_breadcrumb(
                    (org_name, "../index.html"),
                    (project_name,),
                )
            crumbs = [
                (org_name, "../../index.html"),
                (project_name, "../index.html"),
            ]
            if section_label:
                crumbs.append((section_label,))
            return _build_breadcrumb(*crumbs)

        for section in contrib.sections:
            if section.tours:
                self._render_section_tours(
                    env,
                    section,
                    site_dir,
                    org_name,
                    project_name,
                    nav_args,
                    project_breadcrumb,
                )
            elif section.groups:
                self._render_section_groups(
                    env,
                    section,
                    site_dir,
                    org_name,
                    project_name,
                    nav_args,
                    project_breadcrumb,
                )
            else:
                self._render_section_pages(
                    env,
                    section,
                    site_dir,
                    org_name,
                    project_name,
                    nav_args,
                    project_breadcrumb,
                )

        # Project index
        content = ""
        if contrib.hero_figure:
            content += self._figure_to_html(contrib.hero_figure)

        if contrib.overview_md:
            content += _md_to_html(contrib.overview_md)

        section_descriptions = {
            "presentations": (
                "Curated tours of the strategy map for different audiences"
            ),
            "atlas": ("Analytical views derived from the comprehensive strategy map"),
            "analysis": "Pipeline stages from brief through strategy",
        }

        if any(s.slug in section_descriptions for s in contrib.sections):
            content += '<ul class="section-list">'
            for section in contrib.sections:
                desc = section.description or section_descriptions.get(section.slug, "")
                content += (
                    f'<li><a href="{section.slug}/index.html">{section.label}</a>'
                    f'<span class="desc">{desc}</span></li>'
                )
            content += "</ul>"

        _render_page(
            env,
            "base.html",
            site_dir / "index.html",
            title=f"Overview — {project_name} — {org_name}",
            org_name=org_name,
            heading="Overview",
            css_path="../style.css",
            breadcrumb=project_breadcrumb(depth=0),
            nav=_build_project_nav("index", 0, **nav_args),
            toc=None,
            content=Markup(content),
        )
        print("    index.html")

    def _render_section_pages(
        self,
        env,
        section: ProjectSection,
        site_dir,
        org_name,
        project_name,
        nav_args,
        project_breadcrumb,
    ) -> None:
        """Render a section with flat pages (e.g. Analysis)."""
        section_dir = Path(site_dir) / section.slug
        section_dir.mkdir(parents=True, exist_ok=True)

        def section_toc(active_slug=None):
            return [
                {
                    "label": p.title,
                    "url": f"{p.slug}.html",
                    "active": p.slug == active_slug,
                }
                for p in section.pages
            ]

        # Section index
        _render_page(
            env,
            "base.html",
            section_dir / "index.html",
            title=f"{section.label} — {project_name} — {org_name}",
            org_name=org_name,
            heading=section.label,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb(section.label, 1),
            nav=_build_project_nav(section.slug, 1, **nav_args),
            toc=section_toc(),
            content=Markup(""),
        )
        print(f"    {section.slug}/index.html")

        shared = dict(
            org_name=org_name,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb(section.label, 1),
            nav=_build_project_nav(section.slug, 1, **nav_args),
        )

        for page in section.pages:
            content = ""
            for fig in page.figures:
                content += self._figure_to_html(fig)
            content += _md_to_html(page.body_md)

            _render_page(
                env,
                "base.html",
                section_dir / f"{page.slug}.html",
                title=f"{page.title} — {project_name} — {org_name}",
                heading=page.title,
                toc=section_toc(page.slug),
                content=Markup(content),
                **shared,
            )
            print(f"    {section.slug}/{page.slug}.html")

    def _render_section_tours(
        self,
        env,
        section: ProjectSection,
        site_dir,
        org_name,
        project_name,
        nav_args,
        project_breadcrumb,
    ) -> None:
        """Render a Presentations section with tour pages."""
        section_dir = Path(site_dir) / section.slug
        section_dir.mkdir(parents=True, exist_ok=True)

        tour_infos = [
            {
                "name": t.slug,
                "url": f"{t.slug}.html",
                "title": t.title,
                "description": t.description,
            }
            for t in section.tours
        ]

        def presentations_toc(active_name=None):
            return [
                {
                    "label": t["title"],
                    "url": t["url"],
                    "active": t["name"] == active_name,
                }
                for t in tour_infos
            ]

        # Presentations index
        _render_page(
            env,
            "presentations_index.html",
            section_dir / "index.html",
            title=f"Presentations — {project_name} — {org_name}",
            org_name=org_name,
            heading="Presentations",
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Presentations", 1),
            nav=_build_project_nav("presentations", 1, **nav_args),
            toc=None,
            tours=tour_infos,
        )
        print("    presentations/index.html")

        for tour in section.tours:
            self._render_tour_from_content(
                env,
                tour,
                section_dir / f"{tour.slug}.html",
                org_name,
                project_name,
                _build_project_nav("presentations", 1, **nav_args),
                project_breadcrumb("Presentations", 1),
                presentations_toc(tour.slug),
            )

    def _render_tour_from_content(
        self,
        env,
        tour: TourPageContent,
        output_file,
        org_name,
        project_name,
        nav,
        breadcrumb,
        toc,
    ) -> None:
        """Render a single tour from TourPageContent."""
        opening_html = _md_to_html(tour.opening_md) if tour.opening_md else ""

        template_groups = []
        for group in tour.groups:
            rendered_rows = []
            for stop in group.stops:
                svgs_html = ""
                for fig in stop.figures:
                    svgs_html += self._figure_to_html(fig)

                analysis_html = ""
                if stop.analysis_md:
                    analysis_html = _md_to_html(stop.analysis_md)

                rendered_rows.append(
                    {
                        "level": stop.level,
                        "title": stop.title,
                        "is_header": stop.is_header,
                        "svgs_html": Markup(svgs_html),
                        "analysis_html": Markup(analysis_html),
                    }
                )

            transition_html = ""
            if group.transition_md:
                transition_html = _md_to_html(group.transition_md)

            template_groups.append(
                {
                    "rows": rendered_rows,
                    "transition_html": Markup(transition_html),
                }
            )

        _render_page(
            env,
            "tour.html",
            output_file,
            title=f"{tour.title} — {project_name} — {org_name}",
            org_name=org_name,
            heading=tour.title,
            css_path="../../style.css",
            breadcrumb=breadcrumb,
            nav=nav,
            toc=toc,
            opening_html=Markup(opening_html),
            groups=template_groups,
        )
        print(f"    presentations/{tour.slug}.html")

    def _render_section_groups(
        self,
        env,
        section: ProjectSection,
        site_dir,
        org_name,
        project_name,
        nav_args,
        project_breadcrumb,
    ) -> None:
        """Render an Atlas section with categorized groups."""
        section_dir = Path(site_dir) / section.slug
        section_dir.mkdir(parents=True, exist_ok=True)

        # Flatten all pages for TOC
        all_pages = [p for g in section.groups for p in g.pages]

        categories = [
            {
                "name": g.slug,
                "label": g.label,
                "views": [{"name": p.title, "url": f"{p.slug}.html"} for p in g.pages],
            }
            for g in section.groups
        ]

        def atlas_toc(active_slug=None):
            return [
                {
                    "label": p.title,
                    "url": f"{p.slug}.html",
                    "active": p.slug == active_slug,
                }
                for p in all_pages
            ]

        # Atlas index
        _render_page(
            env,
            "atlas_index.html",
            section_dir / "index.html",
            title=f"Atlas — {project_name} — {org_name}",
            org_name=org_name,
            heading="Atlas",
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Atlas", 1),
            nav=_build_project_nav("atlas", 1, **nav_args),
            toc=None,
            categories=categories,
        )
        print("    atlas/index.html")

        shared = dict(
            org_name=org_name,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Atlas", 1),
            nav=_build_project_nav("atlas", 1, **nav_args),
        )

        for page in all_pages:
            content = ""
            for fig in page.figures:
                content += self._figure_to_html(fig)
            content += _md_to_html(page.body_md)

            _render_page(
                env,
                "base.html",
                section_dir / f"{page.slug}.html",
                title=f"{page.title} — {project_name} — {org_name}",
                heading=page.title,
                toc=atlas_toc(page.slug),
                content=Markup(content),
                **shared,
            )
            print(f"    atlas/{page.slug}.html")
