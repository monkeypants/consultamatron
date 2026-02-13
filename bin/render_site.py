#!/usr/bin/env python3
"""
Render a static HTML site from a Consultamatron client workspace.

Replaces the bash renderers (render-site.sh, render-wardley.sh,
render-bmc.sh, site-helpers.sh) with a single Python script using
Jinja2 templates and the markdown library.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup


# ── Markdown helpers ─────────────────────────────────────────────────


def preprocess_trees(text):
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


def preprocess_kv(text):
    """Insert blank line before **Label**: lines that follow non-blank lines."""
    lines = text.split("\n")
    out = []
    kv_re = re.compile(r"^\*\*[^*]+\*\*:")
    for i, line in enumerate(lines):
        if kv_re.match(line) and i > 0 and lines[i - 1].strip():
            out.append("")
        out.append(line)
    return "\n".join(out)


def preprocess_lists(text):
    """Insert blank line before the first list item after a paragraph.

    The Python markdown library (unlike pandoc) requires a blank line
    between a paragraph and a list for the list to be recognised.
    Only insert before the *first* item in a run — not between items
    or after continuation lines, which would create a loose list.
    """
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
            pass  # still in the list
        elif not line.strip() and in_list:
            pass  # blank line inside list context, don't reset yet
        else:
            in_list = False
        out.append(line)
    return "\n".join(out)


def md_to_html(text):
    """Preprocess and convert markdown to HTML, stripping the first H1."""
    text = preprocess_kv(text)
    text = preprocess_lists(text)
    text = preprocess_trees(text)
    html = markdown.markdown(text, extensions=["tables", "fenced_code"])
    # Strip first h1
    html = re.sub(r"<h1[^>]*>.*?</h1>", "", html, count=1, flags=re.DOTALL)
    return html.strip()


def embed_svg(svg_path, caption=""):
    """Read an SVG file and return <figure> HTML."""
    p = Path(svg_path)
    if not p.is_file():
        return ""
    svg_content = p.read_text()
    # Make SVG responsive
    svg_content = svg_content.replace(
        "<svg ", '<svg style="max-width:100%;height:auto" ', 1
    )
    parts = ["<figure>", svg_content]
    if caption:
        parts.append(f"<figcaption>{caption}</figcaption>")
    parts.append("</figure>")
    return "\n".join(parts)


def ensure_owm_svgs(project_dir):
    """Shell out to ensure-owm.sh for all OWM files in the project."""
    script = Path(__file__).parent / "ensure-owm.sh"
    for owm in Path(project_dir).rglob("*.owm"):
        svg = owm.with_suffix(".svg")
        if not svg.exists() or owm.stat().st_mtime > svg.stat().st_mtime:
            print(f"    Rendering {owm} -> SVG")
            subprocess.run([str(script), str(owm)], capture_output=True)


def read_md(path):
    """Read a markdown file and return its text, or empty string."""
    p = Path(path)
    if p.is_file():
        return p.read_text()
    return ""


def extract_h1(text):
    """Extract the first H1 text from markdown."""
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def title_case(slug):
    """Convert a slug like 'shared-components' to 'Shared Components'."""
    return " ".join(w.capitalize() for w in slug.split("-"))


# ── Manifest parsing ─────────────────────────────────────────────────


def parse_manifest(manifest_path):
    """Parse a tour manifest.md and return normalized row dicts.

    Each row: {order, title, atlas_dir, map_files}
    atlas_dir is relative to project (e.g. 'atlas/overview/')
    map_files is a list of SVG filenames, or empty for defaults.
    """
    text = read_md(manifest_path)
    if not text:
        return []

    rows = []
    header_seen = False
    for line in text.split("\n"):
        if not line.startswith("|"):
            continue
        # Skip separator rows
        if re.match(r"^\|[-| ]+\|$", line.strip()):
            continue

        cols = [c.strip() for c in line.split("|")]
        # Remove empty first and last from leading/trailing pipes
        if cols and cols[0] == "":
            cols = cols[1:]
        if cols and cols[-1] == "":
            cols = cols[:-1]

        # Detect header row (no atlas/ reference)
        if not header_seen and not any("atlas/" in c for c in cols):
            header_seen = True
            continue

        if not cols:
            continue

        order = cols[0].strip()

        # Find atlas column
        atlas_col = -1
        for i in range(1, len(cols)):
            if cols[i].strip().startswith("atlas/"):
                atlas_col = i
                break

        atlas_dir = ""
        title = ""
        map_files = []

        if atlas_col >= 0:
            atlas_dir = cols[atlas_col].strip().rstrip("/") + "/"

        n = len(cols)

        if n >= 5 and atlas_col == 2:
            # Format A: order|title|atlas|map|analysis (5 cols)
            title = cols[1].strip()
            mf = cols[3].strip()
            if ".svg" in mf:
                map_files = [f.strip() for f in mf.split(",")]
        elif n == 4 and atlas_col == 2:
            # Format B: order|slug|atlas|label (4 cols, atlas=col 2)
            title = cols[3].strip()
        elif n == 4 and atlas_col == 1:
            # Format C: order|atlas|slug|title (4 cols, atlas=col 1)
            title = cols[3].strip()
        elif atlas_col < 0:
            # Header row (no atlas source) - title from col 1
            title = cols[1].strip() if n > 1 else order
        else:
            title = cols[1].strip() if n > 1 else order

        rows.append(
            {
                "order": order,
                "title": title,
                "atlas_dir": atlas_dir,
                "map_files": map_files,
            }
        )

    return rows


def atlas_category(name):
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


# ── Navigation builders ──────────────────────────────────────────────


def build_breadcrumb(*crumbs):
    """Build breadcrumb list. Each crumb is (label, url) or (label,). Last has no url."""
    result = []
    for i, crumb in enumerate(crumbs):
        if i == len(crumbs) - 1:
            result.append({"label": crumb[0]})
        else:
            result.append({"label": crumb[0], "url": crumb[1]})
    return result


def build_client_nav(active, has_engagement=True):
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


def build_project_nav(active, depth, has_presentations, has_atlas, has_analysis):
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


# ── Page rendering helpers ───────────────────────────────────────────


def render_page(env, template_name, output_path, **ctx):
    """Render a template to a file."""
    tmpl = env.get_template(template_name)
    html = tmpl.render(**ctx)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html)


# ── Client-level pages ───────────────────────────────────────────────


def render_client_pages(ws, site, env, org_name):
    """Generate all client-level pages."""
    has_engagement = Path(ws, "engagement.md").is_file()

    # ── Home page ────────────────────────────────────────────────────
    content_parts = []
    engagement_text = read_md(Path(ws, "engagement.md"))
    if engagement_text:
        content_parts.append(md_to_html(engagement_text))

    render_page(
        env,
        "base.html",
        Path(site, "index.html"),
        title="Home",
        org_name=org_name,
        heading=org_name,
        css_path="style.css",
        breadcrumb=[],
        nav=build_client_nav("index", has_engagement),
        toc=None,
        content=Markup("\n".join(content_parts)),
    )

    # ── Projects page ────────────────────────────────────────────────
    projects_md = read_md(Path(ws, "projects", "index.md"))
    # Collect project dirs for linking
    project_dirs = (
        sorted(
            p.name
            for p in Path(ws, "projects").iterdir()
            if p.is_dir() and p.name != "site"
        )
        if Path(ws, "projects").is_dir()
        else []
    )

    projects_html = md_to_html(projects_md) if projects_md else ""

    # Inject links to project sub-sites where slugs appear in the text
    for pname in project_dirs:
        # Link the slug in table cells: >slug<
        projects_html = projects_html.replace(
            f">{pname}<", f'><a href="{pname}/index.html">{pname}</a><'
        )
        # Link the slug at the start of headings: >slug: Title</h2>
        projects_html = re.sub(
            rf"(<h[23]>)({re.escape(pname)})(:.+?)(</h[23]>)",
            rf'\1<a href="{pname}/index.html">\2\3</a>\4',
            projects_html,
        )

    render_page(
        env,
        "base.html",
        Path(site, "projects.html"),
        title=f"Projects — {org_name}",
        org_name=org_name,
        heading="Projects",
        css_path="style.css",
        breadcrumb=build_breadcrumb((org_name, "index.html"), ("Projects",)),
        nav=build_client_nav("projects", has_engagement),
        toc=None,
        content=Markup(projects_html),
    )

    # ── Research pages ───────────────────────────────────────────────
    research_files = sorted(
        p for p in Path(ws, "resources").glob("*.md") if p.name != "index.md"
    )

    # Build research TOC entries
    research_toc_entries = [
        {"label": "Synthesis", "url": "resources.html", "active": False}
    ]
    for rf in research_files:
        slug = rf.stem
        title = extract_h1(rf.read_text()) or title_case(slug)
        research_toc_entries.append(
            {
                "label": title,
                "url": f"resources/{slug}.html",
                "active": False,
            }
        )

    # Synthesis page
    synth_toc = [
        dict(e, active=(e["label"] == "Synthesis")) for e in research_toc_entries
    ]
    synth_md = read_md(Path(ws, "resources", "index.md"))
    render_page(
        env,
        "base.html",
        Path(site, "resources.html"),
        title=f"Research — {org_name}",
        org_name=org_name,
        heading="Research",
        css_path="style.css",
        breadcrumb=build_breadcrumb((org_name, "index.html"), ("Research",)),
        nav=build_client_nav("resources", has_engagement),
        toc=synth_toc,
        content=Markup(md_to_html(synth_md)),
    )
    print("  resources.html")

    # Sub-report pages
    for rf in research_files:
        slug = rf.stem
        title = extract_h1(rf.read_text()) or title_case(slug)
        sub_toc = []
        for e in research_toc_entries:
            entry = dict(e)
            entry["active"] = entry["label"] == title
            if not entry["url"].startswith("resources/"):
                entry["url"] = f"../{entry['url']}"
            else:
                entry["url"] = entry["url"].replace("resources/", "")
            sub_toc.append(entry)

        # Build nav with ../ prefix
        sub_nav = [
            {**item, "url": f"../{item['url']}"}
            for item in build_client_nav("resources", has_engagement)
        ]

        render_page(
            env,
            "base.html",
            Path(site, "resources", f"{slug}.html"),
            title=f"{title} — {org_name}",
            org_name=org_name,
            heading=title,
            css_path="../style.css",
            breadcrumb=build_breadcrumb(
                (org_name, "../index.html"),
                ("Research", "../resources.html"),
                (title,),
            ),
            nav=sub_nav,
            toc=sub_toc,
            content=Markup(md_to_html(rf.read_text())),
        )
        print(f"  resources/{slug}.html")

    # ── Engagement page ──────────────────────────────────────────────
    if has_engagement:
        eng_md = read_md(Path(ws, "engagement.md"))
        render_page(
            env,
            "base.html",
            Path(site, "engagement.html"),
            title=f"History — {org_name}",
            org_name=org_name,
            heading="Engagement History",
            css_path="style.css",
            breadcrumb=build_breadcrumb((org_name, "index.html"), ("History",)),
            nav=build_client_nav("engagement", has_engagement),
            toc=None,
            content=Markup(md_to_html(eng_md)),
        )
        print("  engagement.html")

    return project_dirs


# ── Wardley project renderer ─────────────────────────────────────────


def render_wardley_project(project, site_dir, org_name, env):
    """Render a Wardley Mapping project."""
    project = Path(project)
    site_dir = Path(site_dir)
    project_name = project.name

    # Ensure OWM SVGs
    ensure_owm_svgs(project)

    # Detect stages
    has_brief = (project / "brief.agreed.md").is_file()
    has_needs = (project / "needs" / "needs.agreed.md").is_file()
    has_chain = (project / "chain" / "supply-chain.agreed.md").is_file()
    has_evolve = (project / "evolve" / "map.agreed.owm").is_file()
    has_strategy = (project / "strategy" / "map.agreed.owm").is_file()
    has_atlas = (project / "atlas").is_dir()
    has_presentations = (project / "presentations").is_dir()
    has_decisions = (project / "decisions.md").is_file()
    has_analysis = any(
        [has_brief, has_needs, has_chain, has_evolve, has_strategy, has_decisions]
    )

    print(
        f"    Stages: brief={has_brief} needs={has_needs} chain={has_chain} "
        f"evolve={has_evolve} strategy={has_strategy}"
    )
    print(f"    Extras: atlas={has_atlas} presentations={has_presentations}")

    # ── Legacy flat mode ─────────────────────────────────────────────
    if not has_atlas and not has_presentations:
        _render_wardley_legacy(
            project,
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

    # ── Three-tier IA ────────────────────────────────────────────────
    nav_args = dict(
        has_presentations=has_presentations,
        has_atlas=has_atlas,
        has_analysis=has_analysis,
    )

    def project_breadcrumb(section_label=None, depth=0):
        if depth == 0:
            return build_breadcrumb(
                (org_name, "../index.html"),
                (project_name,),
            )
        crumbs = [
            (org_name, "../../index.html"),
            (project_name, "../index.html"),
        ]
        if section_label:
            crumbs.append((section_label,))
        return build_breadcrumb(*crumbs)

    # ── Presentations ────────────────────────────────────────────────
    if has_presentations:
        site_dir.joinpath("presentations").mkdir(parents=True, exist_ok=True)

        # Collect tour info
        tours = []
        for tour_dir in sorted(Path(project, "presentations").iterdir()):
            if not tour_dir.is_dir():
                continue
            manifest_path = tour_dir / "manifest.md"
            if not manifest_path.is_file():
                continue
            tour_name = tour_dir.name
            manifest_text = manifest_path.read_text()
            tour_title = extract_h1(manifest_text) or title_case(tour_name)

            # Description from opening.md second paragraph
            desc = ""
            opening_path = tour_dir / "opening.md"
            if opening_path.is_file():
                desc = _extract_second_paragraph(opening_path.read_text())

            tours.append(
                {
                    "name": tour_name,
                    "url": f"{tour_name}.html",
                    "title": tour_title,
                    "description": desc,
                }
            )

        # Presentations TOC for sibling navigation
        def presentations_toc(active_name=None):
            toc = []
            for t in tours:
                toc.append(
                    {
                        "label": t["title"],
                        "url": t["url"],
                        "active": t["name"] == active_name,
                    }
                )
            return toc

        # Presentations index
        render_page(
            env,
            "presentations_index.html",
            site_dir / "presentations" / "index.html",
            title=f"Presentations — {project_name} — {org_name}",
            org_name=org_name,
            heading="Presentations",
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Presentations", 1),
            nav=build_project_nav("presentations", 1, **nav_args),
            toc=None,
            tours=tours,
        )
        print("    presentations/index.html")

        # Individual tour pages
        for tour in tours:
            tour_dir = project / "presentations" / tour["name"]
            _render_tour_page(
                env,
                tour_dir,
                tour["name"],
                tour["title"],
                site_dir / "presentations" / f"{tour['name']}.html",
                project,
                org_name,
                project_name,
                build_project_nav("presentations", 1, **nav_args),
                project_breadcrumb("Presentations", 1),
                presentations_toc(tour["name"]),
            )

    # ── Atlas ────────────────────────────────────────────────────────
    if has_atlas:
        site_dir.joinpath("atlas").mkdir(parents=True, exist_ok=True)

        # Collect views with analysis.md
        views = []
        for view_dir in sorted(Path(project, "atlas").iterdir()):
            if not view_dir.is_dir():
                continue
            if not (view_dir / "analysis.md").is_file():
                continue
            views.append(view_dir.name)

        # Categorize
        categories = [
            {"name": "structural", "label": "Structural", "views": []},
            {"name": "connectivity", "label": "Connectivity", "views": []},
            {"name": "strategic", "label": "Strategic", "views": []},
            {"name": "dynamic", "label": "Dynamic", "views": []},
        ]
        cat_map = {c["name"]: c for c in categories}
        for v in views:
            cat = atlas_category(v)
            cat_map[cat]["views"].append({"name": title_case(v), "url": f"{v}.html"})

        # Atlas TOC for sibling navigation
        def atlas_toc(active_name=None):
            toc = []
            for v in views:
                toc.append(
                    {
                        "label": title_case(v),
                        "url": f"{v}.html",
                        "active": v == active_name,
                    }
                )
            return toc

        # Atlas index
        render_page(
            env,
            "atlas_index.html",
            site_dir / "atlas" / "index.html",
            title=f"Atlas — {project_name} — {org_name}",
            org_name=org_name,
            heading="Atlas",
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Atlas", 1),
            nav=build_project_nav("atlas", 1, **nav_args),
            toc=None,
            categories=categories,
        )
        print("    atlas/index.html")

        # Individual view pages
        for v in views:
            view_dir = project / "atlas" / v
            _render_atlas_view_page(
                env,
                view_dir,
                v,
                site_dir / "atlas" / f"{v}.html",
                org_name,
                project_name,
                build_project_nav("atlas", 1, **nav_args),
                project_breadcrumb("Atlas", 1),
                atlas_toc(v),
            )

    # ── Analysis ─────────────────────────────────────────────────────
    if has_analysis:
        site_dir.joinpath("analysis").mkdir(parents=True, exist_ok=True)

        # Build analysis TOC
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
        render_page(
            env,
            "base.html",
            site_dir / "analysis" / "index.html",
            title=f"Analysis — {project_name} — {org_name}",
            org_name=org_name,
            heading="Analysis",
            css_path="../../style.css",
            breadcrumb=project_breadcrumb("Analysis", 1),
            nav=build_project_nav("analysis", 1, **nav_args),
            toc=analysis_toc(),
            content=Markup(""),
        )
        print("    analysis/index.html")

        # Strategy
        if has_strategy:
            content = ""
            svg_path = project / "strategy" / "map.svg"
            if svg_path.is_file():
                content += embed_svg(svg_path, "Strategy map")
            plays_dir = project / "strategy" / "plays"
            if plays_dir.is_dir():
                for f in sorted(plays_dir.glob("*.md")):
                    content += md_to_html(f.read_text()) + "<hr>"
            render_page(
                env,
                "base.html",
                site_dir / "analysis" / "strategy.html",
                title=f"Strategy — {project_name} — {org_name}",
                org_name=org_name,
                heading="Strategy",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Analysis", 1),
                nav=build_project_nav("analysis", 1, **nav_args),
                toc=analysis_toc("strategy"),
                content=Markup(content),
            )
            print("    analysis/strategy.html")

        # Evolution Map
        if has_evolve:
            content = ""
            svg_path = project / "evolve" / "map.svg"
            if svg_path.is_file():
                content += embed_svg(svg_path, "Evolution map")
            assessments_dir = project / "evolve" / "assessments"
            if assessments_dir.is_dir():
                for f in sorted(assessments_dir.glob("*.md")):
                    content += md_to_html(f.read_text()) + "<hr>"
            render_page(
                env,
                "base.html",
                site_dir / "analysis" / "map.html",
                title=f"Evolution Map — {project_name} — {org_name}",
                org_name=org_name,
                heading="Evolution Map",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Analysis", 1),
                nav=build_project_nav("analysis", 1, **nav_args),
                toc=analysis_toc("map"),
                content=Markup(content),
            )
            print("    analysis/map.html")

        # Supply Chain
        if has_chain:
            content = md_to_html(read_md(project / "chain" / "supply-chain.agreed.md"))
            render_page(
                env,
                "base.html",
                site_dir / "analysis" / "supply-chain.html",
                title=f"Supply Chain — {project_name} — {org_name}",
                org_name=org_name,
                heading="Supply Chain",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Analysis", 1),
                nav=build_project_nav("analysis", 1, **nav_args),
                toc=analysis_toc("supply-chain"),
                content=Markup(content),
            )
            print("    analysis/supply-chain.html")

        # User Needs
        if has_needs:
            content = md_to_html(read_md(project / "needs" / "needs.agreed.md"))
            render_page(
                env,
                "base.html",
                site_dir / "analysis" / "needs.html",
                title=f"User Needs — {project_name} — {org_name}",
                org_name=org_name,
                heading="User Needs",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Analysis", 1),
                nav=build_project_nav("analysis", 1, **nav_args),
                toc=analysis_toc("needs"),
                content=Markup(content),
            )
            print("    analysis/needs.html")

        # Brief
        if has_brief:
            content = md_to_html(read_md(project / "brief.agreed.md"))
            render_page(
                env,
                "base.html",
                site_dir / "analysis" / "brief.html",
                title=f"Project Brief — {project_name} — {org_name}",
                org_name=org_name,
                heading="Project Brief",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Analysis", 1),
                nav=build_project_nav("analysis", 1, **nav_args),
                toc=analysis_toc("brief"),
                content=Markup(content),
            )
            print("    analysis/brief.html")

        # Decisions
        if has_decisions:
            content = md_to_html(read_md(project / "decisions.md"))
            render_page(
                env,
                "base.html",
                site_dir / "analysis" / "decisions.html",
                title=f"Decisions — {project_name} — {org_name}",
                org_name=org_name,
                heading="Decisions",
                css_path="../../style.css",
                breadcrumb=project_breadcrumb("Analysis", 1),
                nav=build_project_nav("analysis", 1, **nav_args),
                toc=analysis_toc("decisions"),
                content=Markup(content),
            )
            print("    analysis/decisions.html")

    # ── Project index ────────────────────────────────────────────────
    content = ""
    # Hero map
    if has_strategy and (project / "strategy" / "map.svg").is_file():
        content += embed_svg(project / "strategy" / "map.svg", "Strategy map")
    elif has_evolve and (project / "evolve" / "map.svg").is_file():
        content += embed_svg(project / "evolve" / "map.svg", "Evolution map")
    elif (project / "landscape.svg").is_file():
        content += embed_svg(
            project / "landscape.svg", "Landscape sketch (approximate)"
        )

    # Section routing
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

    render_page(
        env,
        "base.html",
        site_dir / "index.html",
        title=f"Overview — {project_name} — {org_name}",
        org_name=org_name,
        heading="Overview",
        css_path="../style.css",
        breadcrumb=build_breadcrumb(
            (org_name, "../index.html"),
            (project_name,),
        ),
        nav=build_project_nav("index", 0, **nav_args),
        toc=None,
        content=Markup(content),
    )
    print("    index.html")


def _render_wardley_legacy(
    project,
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
    """Render a Wardley project in legacy flat mode (no atlas/presentations)."""
    project = Path(project)
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
            items.append({"label": "Map", "url": "map.html", "active": active == "map"})
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

    bc = build_breadcrumb((org_name, "../index.html"), (project_name,))

    # Index
    content = ""
    if has_strategy and (project / "strategy" / "map.svg").is_file():
        content += embed_svg(project / "strategy" / "map.svg", "Strategy map")
    elif has_evolve and (project / "evolve" / "map.svg").is_file():
        content += embed_svg(project / "evolve" / "map.svg", "Evolution map")
    elif (project / "landscape.svg").is_file():
        content += embed_svg(
            project / "landscape.svg", "Landscape sketch (approximate)"
        )

    render_page(
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
        render_page(
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
            content=Markup(md_to_html(read_md(project / "brief.agreed.md"))),
        )
        print("    brief.html")

    if has_decisions:
        render_page(
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
            content=Markup(md_to_html(read_md(project / "decisions.md"))),
        )
        print("    decisions.html")

    if has_needs:
        render_page(
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
            content=Markup(md_to_html(read_md(project / "needs" / "needs.agreed.md"))),
        )
        print("    needs.html")

    if has_chain:
        render_page(
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
                md_to_html(read_md(project / "chain" / "supply-chain.agreed.md"))
            ),
        )
        print("    supply-chain.html")

    if has_evolve:
        content = ""
        if (project / "evolve" / "map.svg").is_file():
            content += embed_svg(project / "evolve" / "map.svg", "Evolution map")
        assessments = project / "evolve" / "assessments"
        if assessments.is_dir():
            for f in sorted(assessments.glob("*.md")):
                content += md_to_html(f.read_text()) + "<hr>"
        render_page(
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
        if (project / "strategy" / "map.svg").is_file():
            content += embed_svg(project / "strategy" / "map.svg", "Strategy map")
        plays_dir = project / "strategy" / "plays"
        if plays_dir.is_dir():
            for f in sorted(plays_dir.glob("*.md")):
                content += md_to_html(f.read_text()) + "<hr>"
        render_page(
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


def _extract_second_paragraph(text):
    """Extract the second paragraph from markdown text (for tour descriptions)."""
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


def _render_tour_page(
    env,
    tour_dir,
    tour_name,
    page_title,
    output_file,
    project,
    org_name,
    project_name,
    nav,
    breadcrumb,
    toc,
):
    """Render a single tour page."""
    manifest_path = tour_dir / "manifest.md"
    rows = parse_manifest(manifest_path)
    if not rows:
        return

    # Group rows by base order (strip trailing letters)
    groups = []
    current_base = None
    current_rows = []
    for row in rows:
        base = re.sub(r"[a-z]+$", "", row["order"])
        if base != current_base:
            if current_rows:
                groups.append({"base": current_base, "rows": current_rows})
            current_base = base
            current_rows = [row]
        else:
            current_rows.append(row)
    if current_rows:
        groups.append({"base": current_base, "rows": current_rows})

    # Collect transition files
    trans_dir = tour_dir / "transitions"
    trans_files = sorted(trans_dir.glob("*.md")) if trans_dir.is_dir() else []

    # Build opening HTML
    opening_html = ""
    opening_path = tour_dir / "opening.md"
    if opening_path.is_file():
        opening_html = md_to_html(opening_path.read_text())

    # Build group data for template
    template_groups = []
    for gi, group in enumerate(groups):
        rendered_rows = []
        for row in group["rows"]:
            has_suffix = bool(re.search(r"[a-z]$", row["order"]))
            level = "h3" if has_suffix else "h2"

            if not row["atlas_dir"]:
                # Header row — just a title
                rendered_rows.append(
                    {
                        "level": level,
                        "title": row["title"],
                        "is_header": True,
                        "svgs_html": "",
                        "analysis_html": "",
                    }
                )
                continue

            atlas_path = project / row["atlas_dir"]

            # Embed SVGs
            svgs_html = ""
            if row["map_files"]:
                for svg_name in row["map_files"]:
                    svg_path = atlas_path / svg_name
                    if svg_path.is_file():
                        svgs_html += embed_svg(svg_path, "")
                    else:
                        # Try with .svg extension
                        svg_try = atlas_path / (Path(svg_name).stem + ".svg")
                        if svg_try.is_file():
                            svgs_html += embed_svg(svg_try, "")
            else:
                # Default: look for map.svg
                default_svg = atlas_path / "map.svg"
                if default_svg.is_file():
                    svgs_html += embed_svg(default_svg, "")
                else:
                    # Single non-standard SVG
                    for svg_file in sorted(atlas_path.glob("*.svg")):
                        svgs_html += embed_svg(svg_file, "")
                        break

            # Analysis
            analysis_html = ""
            analysis_path = atlas_path / "analysis.md"
            if analysis_path.is_file():
                analysis_html = md_to_html(analysis_path.read_text())

            rendered_rows.append(
                {
                    "level": level,
                    "title": row["title"],
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
                transition_html = md_to_html(trans_file.read_text())

        template_groups.append(
            {
                "rows": rendered_rows,
                "transition_html": Markup(transition_html),
            }
        )

    render_page(
        env,
        "tour.html",
        output_file,
        title=f"{page_title} — {project_name} — {org_name}",
        org_name=org_name,
        heading=page_title,
        css_path="../../style.css",
        breadcrumb=breadcrumb,
        nav=nav,
        toc=toc,
        opening_html=Markup(opening_html),
        groups=template_groups,
    )
    print(f"    presentations/{tour_name}.html")


def _render_atlas_view_page(
    env, view_dir, view_name, output_file, org_name, project_name, nav, breadcrumb, toc
):
    """Render a single atlas view page."""
    view_dir = Path(view_dir)
    title = title_case(view_name)

    # Collect SVGs
    svgs = sorted(view_dir.glob("*.svg"))
    content = ""

    if len(svgs) > 1:
        for svg in svgs:
            caption = title_case(svg.stem)
            content += embed_svg(svg, caption)
    elif (view_dir / "map.svg").is_file():
        content += embed_svg(view_dir / "map.svg", "")
    elif svgs:
        content += embed_svg(svgs[0], "")

    # Analysis
    analysis_path = view_dir / "analysis.md"
    if analysis_path.is_file():
        content += md_to_html(analysis_path.read_text())

    render_page(
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


# ── BMC project renderer ─────────────────────────────────────────────


def render_bmc_project(project, site_dir, org_name, env):
    """Render a Business Model Canvas project."""
    project = Path(project)
    site_dir = Path(site_dir)
    project_name = project.name

    has_brief = (project / "brief.agreed.md").is_file()
    has_segments = (project / "segments" / "segments.agreed.md").is_file()
    has_canvas = (project / "canvas.agreed.md").is_file()
    has_decisions = (project / "decisions.md").is_file()

    print(f"    Stages: brief={has_brief} segments={has_segments} canvas={has_canvas}")

    def bmc_nav(active):
        items = [
            {"label": "Overview", "url": "index.html", "active": active == "index"}
        ]
        if has_canvas:
            items.append(
                {"label": "Canvas", "url": "canvas.html", "active": active == "canvas"}
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

    bc = build_breadcrumb((org_name, "../index.html"), (project_name,))

    # Index — show canvas content if available
    content = ""
    if has_canvas:
        content = md_to_html(read_md(project / "canvas.agreed.md"))
    render_page(
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
        render_page(
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
            content=Markup(md_to_html(read_md(project / "canvas.agreed.md"))),
        )
        print("    canvas.html")

    if has_segments:
        render_page(
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
                md_to_html(read_md(project / "segments" / "segments.agreed.md"))
            ),
        )
        print("    segments.html")

    if has_brief:
        render_page(
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
            content=Markup(md_to_html(read_md(project / "brief.agreed.md"))),
        )
        print("    brief.html")

    if has_decisions:
        render_page(
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
            content=Markup(md_to_html(read_md(project / "decisions.md"))),
        )
        print("    decisions.html")


# ── Skillset detection ───────────────────────────────────────────────


def detect_skillset(proj_name, proj_dir):
    """Detect the skillset of a project."""
    proj_dir = Path(proj_dir)
    if re.match(r"^(maps|map|wardley)-", proj_name):
        return "wardley"
    if re.match(r"^(canvas|bmc)-", proj_name):
        return "bmc"
    # Fallback: check artifacts
    if (
        (proj_dir / "needs").is_dir()
        or (proj_dir / "chain").is_dir()
        or (proj_dir / "evolve").is_dir()
    ):
        return "wardley"
    if (
        (proj_dir / "segments").is_dir()
        or (proj_dir / "canvas.md").is_file()
        or (proj_dir / "canvas.agreed.md").is_file()
    ):
        return "bmc"
    return None


# ── Main ─────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print("Usage: render_site.py <workspace-path>", file=sys.stderr)
        sys.exit(1)

    ws = Path(sys.argv[1]).resolve()
    if not ws.is_dir():
        print(f"Error: workspace directory not found: {ws}", file=sys.stderr)
        sys.exit(1)
    if not (ws / "resources" / "index.md").is_file():
        print(
            "Error: no resources/index.md in workspace. Run org-research first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Extract org name
    org_name = ""
    eng_path = ws / "engagement.md"
    if eng_path.is_file():
        for line in eng_path.read_text().split("\n"):
            m = re.search(r"^#.*—\s*(.+)$", line)
            if m:
                org_name = m.group(1).strip()
                break
    if not org_name:
        org_name = ws.name

    site = ws / "site"

    # Set up Jinja2
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=False,
    )

    # Phase 1: Build site directory
    if site.exists():
        shutil.rmtree(site)
    site.mkdir(parents=True)
    (site / "resources").mkdir()
    shutil.copy(Path(__file__).parent / "site.css", site / "style.css")

    print(f"Workspace: {ws} ({org_name})")
    print("Generating client pages...")

    # Phase 2: Client-level pages
    project_dirs = render_client_pages(str(ws), str(site), env, org_name)

    # Phase 3: Project pages
    for proj_name in project_dirs:
        proj_dir = ws / "projects" / proj_name
        site_proj_dir = site / proj_name

        print(f"\nProject: {proj_name}")

        skillset = detect_skillset(proj_name, proj_dir)
        site_proj_dir.mkdir(parents=True, exist_ok=True)

        if skillset == "wardley":
            render_wardley_project(str(proj_dir), str(site_proj_dir), org_name, env)
        elif skillset == "bmc":
            render_bmc_project(str(proj_dir), str(site_proj_dir), org_name, env)
        else:
            print(f"    Unknown skillset for {proj_name}, skipping")

    print(f"\nSite generated: {site}/")
    print(f"Open: {site}/index.html")


if __name__ == "__main__":
    main()
