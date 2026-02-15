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

from bin.cli.content import Figure, NarrativePage, ProjectContribution, ProjectSection
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


def _build_project_nav(active, depth, sections):
    """Build project-level nav items with depth-aware paths."""
    prefix = "../" if depth == 1 else ""
    items = [
        {
            "label": "Overview",
            "url": f"{prefix}index.html",
            "active": active == "index",
        },
    ]
    for section in sections:
        items.append(
            {
                "label": section.label,
                "url": f"{prefix}{section.slug}/index.html",
                "active": active == section.slug,
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

        sections = contrib.sections

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

        for section in sections:
            if section.narratives:
                self._render_section_narratives(
                    env,
                    section,
                    site_dir,
                    org_name,
                    project_name,
                    sections,
                    project_breadcrumb,
                )
            elif section.groups:
                self._render_section_groups(
                    env,
                    section,
                    site_dir,
                    org_name,
                    project_name,
                    sections,
                    project_breadcrumb,
                )
            else:
                self._render_section_pages(
                    env,
                    section,
                    site_dir,
                    org_name,
                    project_name,
                    sections,
                    project_breadcrumb,
                )

        # Project index
        content = ""
        if contrib.hero_figure:
            content += self._figure_to_html(contrib.hero_figure)

        if contrib.overview_md:
            content += _md_to_html(contrib.overview_md)

        if sections:
            content += '<ul class="section-list">'
            for section in sections:
                content += (
                    f'<li><a href="{section.slug}/index.html">{section.label}</a>'
                    f'<span class="desc">{section.description}</span></li>'
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
            nav=_build_project_nav("index", 0, sections),
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
        sections,
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
            nav=_build_project_nav(section.slug, 1, sections),
            toc=section_toc(),
            content=Markup(""),
        )
        print(f"    {section.slug}/index.html")

        shared = dict(
            org_name=org_name,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb(section.label, 1),
            nav=_build_project_nav(section.slug, 1, sections),
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

    def _render_section_narratives(
        self,
        env,
        section: ProjectSection,
        site_dir,
        org_name,
        project_name,
        sections,
        project_breadcrumb,
    ) -> None:
        """Render a section with narrative pages."""
        section_dir = Path(site_dir) / section.slug
        section_dir.mkdir(parents=True, exist_ok=True)

        narrative_infos = [
            {
                "name": t.slug,
                "url": f"{t.slug}.html",
                "title": t.title,
                "description": t.description,
            }
            for t in section.narratives
        ]

        def narratives_toc(active_name=None):
            return [
                {
                    "label": t["title"],
                    "url": t["url"],
                    "active": t["name"] == active_name,
                }
                for t in narrative_infos
            ]

        # Section index
        _render_page(
            env,
            "presentations_index.html",
            section_dir / "index.html",
            title=f"{section.label} — {project_name} — {org_name}",
            org_name=org_name,
            heading=section.label,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb(section.label, 1),
            nav=_build_project_nav(section.slug, 1, sections),
            toc=None,
            tours=narrative_infos,
        )
        print(f"    {section.slug}/index.html")

        for narrative in section.narratives:
            self._render_narrative_page(
                env,
                narrative,
                section_dir / f"{narrative.slug}.html",
                org_name,
                project_name,
                _build_project_nav(section.slug, 1, sections),
                project_breadcrumb(section.label, 1),
                narratives_toc(narrative.slug),
            )

    def _render_narrative_page(
        self,
        env,
        narrative: NarrativePage,
        output_file,
        org_name,
        project_name,
        nav,
        breadcrumb,
        toc,
    ) -> None:
        """Render a single narrative page."""
        opening_html = _md_to_html(narrative.opening_md) if narrative.opening_md else ""

        template_groups = []
        for group in narrative.groups:
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
            "narrative.html",
            output_file,
            title=f"{narrative.title} — {project_name} — {org_name}",
            org_name=org_name,
            heading=narrative.title,
            css_path="../../style.css",
            breadcrumb=breadcrumb,
            nav=nav,
            toc=toc,
            opening_html=Markup(opening_html),
            groups=template_groups,
        )
        print(f"    {Path(output_file).parent.name}/{narrative.slug}.html")

    def _render_section_groups(
        self,
        env,
        section: ProjectSection,
        site_dir,
        org_name,
        project_name,
        sections,
        project_breadcrumb,
    ) -> None:
        """Render a section with categorized groups."""
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

        def groups_toc(active_slug=None):
            return [
                {
                    "label": p.title,
                    "url": f"{p.slug}.html",
                    "active": p.slug == active_slug,
                }
                for p in all_pages
            ]

        # Groups index
        _render_page(
            env,
            "groups_index.html",
            section_dir / "index.html",
            title=f"{section.label} — {project_name} — {org_name}",
            org_name=org_name,
            heading=section.label,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb(section.label, 1),
            nav=_build_project_nav(section.slug, 1, sections),
            toc=None,
            categories=categories,
        )
        print(f"    {section.slug}/index.html")

        shared = dict(
            org_name=org_name,
            css_path="../../style.css",
            breadcrumb=project_breadcrumb(section.label, 1),
            nav=_build_project_nav(section.slug, 1, sections),
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
                toc=groups_toc(page.slug),
                content=Markup(content),
                **shared,
            )
            print(f"    {section.slug}/{page.slug}.html")
