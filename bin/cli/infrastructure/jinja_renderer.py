"""Jinja2 + Markdown site renderer implementation.

Infrastructure implementation of the SiteRenderer protocol. Takes
structured entity data from the usecase and workspace prose files,
produces a static HTML site using Jinja2 templates and the Python
markdown library.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

from bin.cli.content import Figure, ProjectContribution, ProjectSection, TourPageContent
from bin.cli.entities import ResearchTopic


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

    # -- Public interface --------------------------------------------------

    def render(
        self,
        client: str,
        contributions: list[ProjectContribution],
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

        for contrib in contributions:
            site_proj_dir = site / contrib.slug
            site_proj_dir.mkdir(parents=True, exist_ok=True)

            print(f"\nProject: {contrib.slug}")
            self._render_project_from_contribution(
                contrib, site_proj_dir, org_name, env
            )

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

    # -- Contribution-based rendering --------------------------------------

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
