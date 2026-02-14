"""CLI entry point for consulting practice accounting operations.

Thin application shell: parse arguments, compose a request DTO,
execute the usecase, format the response. No business logic lives here.

Invocation: uv run consultamatron <group> <command> [options]
"""

from __future__ import annotations

import json
from pathlib import Path

import click

from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.usecases import TRequest, TResponse, UseCase
from bin.cli.dtos import (
    AddEngagementEntryRequest,
    GetProjectProgressRequest,
    GetProjectRequest,
    InitializeWorkspaceRequest,
    ListDecisionsRequest,
    ListProjectsRequest,
    ListResearchTopicsRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
    RegisterResearchTopicRequest,
    RegisterTourRequest,
    RenderSiteRequest,
    TourStopInput,
    UpdateProjectStatusRequest,
)


def _parse_fields(raw: tuple[str, ...]) -> dict[str, str]:
    """Parse Key=Value pairs from repeatable --field options."""
    fields: dict[str, str] = {}
    for item in raw:
        key, sep, value = item.partition("=")
        if not sep:
            raise click.BadParameter(f"Field must be Key=Value, got: {item}")
        fields[key] = value
    return fields


def _run(usecase: UseCase[TRequest, TResponse], request: TRequest) -> TResponse:
    """Execute a usecase, converting ValueError to a clean CLI error.

    The TypeVars are unbound at module scope, but mypy/pyright infer the
    concrete types at each call site.  If this stops being sufficient
    (e.g. the function grows overloads), replace with an explicit Generic
    wrapper class.
    """
    try:
        return usecase.execute(request)
    except ValueError as e:
        raise click.ClickException(str(e))


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Consultamatron accounting operations."""
    ctx.obj = Container(Config.from_repo_root(Path.cwd()))


# ---------------------------------------------------------------------------
# project
# ---------------------------------------------------------------------------


@cli.group()
def project() -> None:
    """Manage consulting projects."""


@project.command("init")
@click.option("--client", required=True, help="Client slug.")
@click.pass_obj
def project_init(di: Container, client: str) -> None:
    """Initialize a new client workspace.

    Creates empty project registry, engagement log, and research
    manifest. Logs a "Client onboarded" engagement entry.
    """
    req = InitializeWorkspaceRequest(client=client)
    resp = _run(di.initialize_workspace_usecase, req)
    click.echo(f"Initialized workspace for '{resp.client}'")


@project.command("register")
@click.option("--client", required=True, help="Client slug.")
@click.option("--slug", required=True, help="Project slug (e.g. maps-1).")
@click.option(
    "--skillset",
    required=True,
    help="Skillset name (must match a manifest).",
)
@click.option("--scope", required=True, help="Project scope description.")
@click.option("--notes", default="", help="Additional notes.")
@click.pass_obj
def project_register(
    di: Container,
    client: str,
    slug: str,
    skillset: str,
    scope: str,
    notes: str,
) -> None:
    """Register a new project for a client.

    Adds the project to the registry, creates its decision log with a
    "Project created" entry, and logs an engagement entry.
    """
    req = RegisterProjectRequest(
        client=client,
        slug=slug,
        skillset=skillset,
        scope=scope,
        notes=notes,
    )
    resp = _run(di.register_project_usecase, req)
    click.echo(
        f"Registered project '{resp.slug}' ({resp.skillset}) for '{resp.client}'"
    )


@project.command("update-status")
@click.option("--client", required=True, help="Client slug.")
@click.option("--project", "project_slug", required=True, help="Project slug.")
@click.option(
    "--status",
    required=True,
    type=click.Choice(["planned", "active", "complete", "reviewed"]),
    help="New status.",
)
@click.pass_obj
def project_update_status(
    di: Container, client: str, project_slug: str, status: str
) -> None:
    """Update a project's status.

    Validates the transition follows planned -> active -> complete ->
    reviewed. No skipping, no reversal.
    """
    req = UpdateProjectStatusRequest(
        client=client, project_slug=project_slug, status=status
    )
    resp = _run(di.update_project_status_usecase, req)
    click.echo(f"Updated '{resp.project_slug}' status to '{resp.status}'")


@project.command("list")
@click.option("--client", required=True, help="Client slug.")
@click.option("--skillset", default=None, help="Filter by skillset.")
@click.option(
    "--status",
    default=None,
    type=click.Choice(["planned", "active", "complete", "reviewed"]),
    help="Filter by status.",
)
@click.pass_obj
def project_list(
    di: Container,
    client: str,
    skillset: str | None,
    status: str | None,
) -> None:
    """List projects for a client."""
    req = ListProjectsRequest(client=client, skillset=skillset, status=status)
    resp = _run(di.list_projects_usecase, req)
    if not resp.projects:
        click.echo("No projects found.")
        return
    for p in resp.projects:
        click.echo(f"  {p.slug}  {p.skillset}  {p.status}  {p.created}")


@project.command("get")
@click.option("--client", required=True, help="Client slug.")
@click.option("--slug", required=True, help="Project slug.")
@click.pass_obj
def project_get(di: Container, client: str, slug: str) -> None:
    """Get details for a specific project."""
    req = GetProjectRequest(client=client, slug=slug)
    resp = _run(di.get_project_usecase, req)
    if resp.project is None:
        raise click.ClickException(f"Project '{slug}' not found.")
    p = resp.project
    click.echo(f"Slug:     {p.slug}")
    click.echo(f"Skillset: {p.skillset}")
    click.echo(f"Status:   {p.status}")
    click.echo(f"Created:  {p.created}")
    if p.notes:
        click.echo(f"Notes:    {p.notes}")


@project.command("progress")
@click.option("--client", required=True, help="Client slug.")
@click.option("--project", "project_slug", required=True, help="Project slug.")
@click.pass_obj
def project_progress(di: Container, client: str, project_slug: str) -> None:
    """Show pipeline progress for a project.

    Loads the skillset definition, matches decision log entries against
    pipeline stages, and reports completed stages, current stage, and
    next prerequisite.
    """
    req = GetProjectProgressRequest(client=client, project_slug=project_slug)
    resp = _run(di.get_project_progress_usecase, req)
    if not resp.stages:
        click.echo("No pipeline stages found.")
        return
    for s in resp.stages:
        mark = "x" if s.completed else " "
        click.echo(f"  [{mark}] {s.order}. {s.description} ({s.skill})")
    if resp.current_stage:
        click.echo(f"\nCurrent: {resp.current_stage}")
    if resp.next_prerequisite:
        click.echo(f"Next gate: {resp.next_prerequisite}")


# ---------------------------------------------------------------------------
# decision
# ---------------------------------------------------------------------------


@cli.group()
def decision() -> None:
    """Manage project decisions."""


@decision.command("record")
@click.option("--client", required=True, help="Client slug.")
@click.option("--project", "project_slug", required=True, help="Project slug.")
@click.option("--title", required=True, help="Decision title.")
@click.option("--field", multiple=True, help="Key=Value pair (repeatable).")
@click.pass_obj
def decision_record(
    di: Container,
    client: str,
    project_slug: str,
    title: str,
    field: tuple[str, ...],
) -> None:
    """Record a decision for a project.

    Appends a timestamped decision entry to the project's decision log.
    Fields are key=value pairs specific to the decision.
    """
    req = RecordDecisionRequest(
        client=client,
        project_slug=project_slug,
        title=title,
        fields=_parse_fields(field),
    )
    resp = _run(di.record_decision_usecase, req)
    click.echo(
        f"Recorded decision '{title}' for "
        f"'{resp.client}/{resp.project_slug}' ({resp.decision_id})"
    )


@decision.command("list")
@click.option("--client", required=True, help="Client slug.")
@click.option("--project", "project_slug", required=True, help="Project slug.")
@click.pass_obj
def decision_list(di: Container, client: str, project_slug: str) -> None:
    """List decisions for a project in chronological order."""
    req = ListDecisionsRequest(client=client, project_slug=project_slug)
    resp = _run(di.list_decisions_usecase, req)
    if not resp.decisions:
        click.echo("No decisions recorded.")
        return
    for d in resp.decisions:
        click.echo(f"  {d.date}  {d.title}")
        for k, v in d.fields.items():
            click.echo(f"           {k}: {v}")


# ---------------------------------------------------------------------------
# engagement
# ---------------------------------------------------------------------------


@cli.group()
def engagement() -> None:
    """Manage client engagement history."""


@engagement.command("add")
@click.option("--client", required=True, help="Client slug.")
@click.option("--title", required=True, help="Entry title.")
@click.option("--field", multiple=True, help="Key=Value pair (repeatable).")
@click.pass_obj
def engagement_add(
    di: Container, client: str, title: str, field: tuple[str, ...]
) -> None:
    """Add an entry to the engagement log.

    Appends a timestamped entry to the client's engagement history.
    """
    req = AddEngagementEntryRequest(
        client=client, title=title, fields=_parse_fields(field)
    )
    resp = _run(di.add_engagement_entry_usecase, req)
    click.echo(
        f"Added engagement entry '{title}' for '{resp.client}' ({resp.entry_id})"
    )


# ---------------------------------------------------------------------------
# research
# ---------------------------------------------------------------------------


@cli.group()
def research() -> None:
    """Manage research topics."""


@research.command("add")
@click.option("--client", required=True, help="Client slug.")
@click.option("--topic", required=True, help="Topic name.")
@click.option("--filename", required=True, help="Research file name.")
@click.option(
    "--confidence",
    required=True,
    type=click.Choice(["High", "Medium-High", "Medium", "Low"]),
    help="Confidence level.",
)
@click.pass_obj
def research_add(
    di: Container,
    client: str,
    topic: str,
    filename: str,
    confidence: str,
) -> None:
    """Register a research topic in the client manifest.

    Fails if the filename already exists in the manifest.
    """
    req = RegisterResearchTopicRequest(
        client=client,
        topic=topic,
        filename=filename,
        confidence=confidence,
    )
    resp = _run(di.register_research_topic_usecase, req)
    click.echo(f"Registered topic '{topic}' as '{resp.filename}' for '{resp.client}'")


@research.command("list")
@click.option("--client", required=True, help="Client slug.")
@click.pass_obj
def research_list(di: Container, client: str) -> None:
    """List research topics for a client."""
    req = ListResearchTopicsRequest(client=client)
    resp = _run(di.list_research_topics_usecase, req)
    if not resp.topics:
        click.echo("No research topics found.")
        return
    for t in resp.topics:
        click.echo(f"  {t.filename}  {t.topic}  {t.confidence}  {t.date}")


# ---------------------------------------------------------------------------
# tour
# ---------------------------------------------------------------------------


@cli.group()
def tour() -> None:
    """Manage presentation tours."""


@tour.command("register")
@click.option("--client", required=True, help="Client slug.")
@click.option("--project", "project_slug", required=True, help="Project slug.")
@click.option("--name", required=True, help="Tour name (e.g. investor).")
@click.option("--title", required=True, help="Tour display title.")
@click.option("--stops", required=True, help="JSON array of tour stops.")
@click.pass_obj
def tour_register(
    di: Container,
    client: str,
    project_slug: str,
    name: str,
    title: str,
    stops: str,
) -> None:
    """Register or replace a tour manifest.

    Replaces the entire manifest for the named tour. Each stop must
    have order, title, and atlas_source fields.
    """
    try:
        stops_data = json.loads(stops)
    except json.JSONDecodeError as e:
        raise click.BadParameter(f"Invalid JSON for --stops: {e}") from e
    req = RegisterTourRequest(
        client=client,
        project_slug=project_slug,
        name=name,
        title=title,
        stops=[TourStopInput(**s) for s in stops_data],
    )
    resp = _run(di.register_tour_usecase, req)
    click.echo(
        f"Registered tour '{resp.name}' with {resp.stop_count} stops "
        f"for '{resp.client}/{resp.project_slug}'"
    )


# ---------------------------------------------------------------------------
# site
# ---------------------------------------------------------------------------


@cli.group()
def site() -> None:
    """Site generation."""


@site.command("render")
@click.argument("client")
@click.pass_obj
def site_render(di: Container, client: str) -> None:
    """Render a static HTML site for a client workspace.

    Gathers structured data from the project registry, tour manifests,
    and research manifest, then delegates to the site renderer.
    """
    req = RenderSiteRequest(client=client)
    resp = _run(di.render_site_usecase, req)
    click.echo(f"Open: {resp.site_path}/index.html")
    click.echo(f"({resp.page_count} pages)")


if __name__ == "__main__":
    cli()
