"""CLI entry point for consulting practice accounting operations.

Thin application shell: parse arguments, compose a request DTO,
execute the usecase, format the response. No business logic lives here.

Invocation: uv run consultamatron <group> <command> [options]
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from bin.cli.config import Config
from bin.cli.di import Container
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
    UpdateProjectStatusRequest,
)
from bin.cli.introspect import generate_command
from bin.cli.usecases import (
    AddEngagementEntryUseCase,
    GetProjectProgressUseCase,
    GetProjectUseCase,
    InitializeWorkspaceUseCase,
    ListDecisionsUseCase,
    ListProjectsUseCase,
    ListResearchTopicsUseCase,
    RecordDecisionUseCase,
    RegisterProjectUseCase,
    RegisterResearchTopicUseCase,
    RegisterTourUseCase,
    RenderSiteUseCase,
    UpdateProjectStatusUseCase,
)


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


def _format_init_workspace(resp: Any) -> None:
    click.echo(f"Initialized workspace for '{resp.client}'")


project.add_command(
    generate_command(
        name="init",
        request_model=InitializeWorkspaceRequest,
        usecase_attr="initialize_workspace_usecase",
        format_output=_format_init_workspace,
        help_text=InitializeWorkspaceUseCase.__doc__,
    )
)


def _format_register_project(resp: Any) -> None:
    click.echo(
        f"Registered project '{resp.slug}' ({resp.skillset}) for '{resp.client}'"
    )


project.add_command(
    generate_command(
        name="register",
        request_model=RegisterProjectRequest,
        usecase_attr="register_project_usecase",
        format_output=_format_register_project,
        help_text=RegisterProjectUseCase.__doc__,
    )
)


def _format_update_status(resp: Any) -> None:
    click.echo(f"Updated '{resp.project_slug}' status to '{resp.status}'")


project.add_command(
    generate_command(
        name="update-status",
        request_model=UpdateProjectStatusRequest,
        usecase_attr="update_project_status_usecase",
        format_output=_format_update_status,
        help_text=UpdateProjectStatusUseCase.__doc__,
    )
)


def _format_list_projects(resp: Any) -> None:
    if not resp.projects:
        click.echo("No projects found.")
        return
    for p in resp.projects:
        click.echo(f"  {p.slug}  {p.skillset}  {p.status}  {p.created}")


project.add_command(
    generate_command(
        name="list",
        request_model=ListProjectsRequest,
        usecase_attr="list_projects_usecase",
        format_output=_format_list_projects,
        help_text=ListProjectsUseCase.__doc__,
    )
)


def _format_get_project(resp: Any) -> None:
    if resp.project is None:
        raise click.ClickException(f"Project '{resp.slug}' not found.")
    p = resp.project
    click.echo(f"Slug:     {p.slug}")
    click.echo(f"Skillset: {p.skillset}")
    click.echo(f"Status:   {p.status}")
    click.echo(f"Created:  {p.created}")
    if p.notes:
        click.echo(f"Notes:    {p.notes}")


project.add_command(
    generate_command(
        name="get",
        request_model=GetProjectRequest,
        usecase_attr="get_project_usecase",
        format_output=_format_get_project,
        help_text=GetProjectUseCase.__doc__,
    )
)


def _format_project_progress(resp: Any) -> None:
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


project.add_command(
    generate_command(
        name="progress",
        request_model=GetProjectProgressRequest,
        usecase_attr="get_project_progress_usecase",
        format_output=_format_project_progress,
        help_text=GetProjectProgressUseCase.__doc__,
    )
)


# ---------------------------------------------------------------------------
# decision
# ---------------------------------------------------------------------------


@cli.group()
def decision() -> None:
    """Manage project decisions."""


def _format_decision_record(resp: Any) -> None:
    click.echo(
        f"Recorded decision '{resp.title}' for "
        f"'{resp.client}/{resp.project_slug}' ({resp.decision_id})"
    )


decision.add_command(
    generate_command(
        name="record",
        request_model=RecordDecisionRequest,
        usecase_attr="record_decision_usecase",
        format_output=_format_decision_record,
        help_text=RecordDecisionUseCase.__doc__,
    )
)


def _format_decision_list(resp: Any) -> None:
    if not resp.decisions:
        click.echo("No decisions recorded.")
        return
    for d in resp.decisions:
        click.echo(f"  {d.date}  {d.title}")
        for k, v in d.fields.items():
            click.echo(f"           {k}: {v}")


decision.add_command(
    generate_command(
        name="list",
        request_model=ListDecisionsRequest,
        usecase_attr="list_decisions_usecase",
        format_output=_format_decision_list,
        help_text=ListDecisionsUseCase.__doc__,
    )
)


# ---------------------------------------------------------------------------
# engagement
# ---------------------------------------------------------------------------


@cli.group()
def engagement() -> None:
    """Manage client engagement history."""


def _format_engagement_add(resp: Any) -> None:
    click.echo(
        f"Added engagement entry '{resp.title}' for '{resp.client}' ({resp.entry_id})"
    )


engagement.add_command(
    generate_command(
        name="add",
        request_model=AddEngagementEntryRequest,
        usecase_attr="add_engagement_entry_usecase",
        format_output=_format_engagement_add,
        help_text=AddEngagementEntryUseCase.__doc__,
    )
)


# ---------------------------------------------------------------------------
# research
# ---------------------------------------------------------------------------


@cli.group()
def research() -> None:
    """Manage research topics."""


def _format_research_add(resp: Any) -> None:
    click.echo(
        f"Registered topic '{resp.topic}' as '{resp.filename}' for '{resp.client}'"
    )


research.add_command(
    generate_command(
        name="add",
        request_model=RegisterResearchTopicRequest,
        usecase_attr="register_research_topic_usecase",
        format_output=_format_research_add,
        help_text=RegisterResearchTopicUseCase.__doc__,
    )
)


def _format_research_list(resp: Any) -> None:
    if not resp.topics:
        click.echo("No research topics found.")
        return
    for t in resp.topics:
        click.echo(f"  {t.filename}  {t.topic}  {t.confidence}  {t.date}")


research.add_command(
    generate_command(
        name="list",
        request_model=ListResearchTopicsRequest,
        usecase_attr="list_research_topics_usecase",
        format_output=_format_research_list,
        help_text=ListResearchTopicsUseCase.__doc__,
    )
)


# ---------------------------------------------------------------------------
# tour
# ---------------------------------------------------------------------------


@cli.group()
def tour() -> None:
    """Manage presentation tours."""


def _format_tour_register(resp: Any) -> None:
    click.echo(
        f"Registered tour '{resp.name}' with {resp.stop_count} stops "
        f"for '{resp.client}/{resp.project_slug}'"
    )


tour.add_command(
    generate_command(
        name="register",
        request_model=RegisterTourRequest,
        usecase_attr="register_tour_usecase",
        format_output=_format_tour_register,
        help_text=RegisterTourUseCase.__doc__,
    )
)


# ---------------------------------------------------------------------------
# site
# ---------------------------------------------------------------------------


@cli.group()
def site() -> None:
    """Site generation."""


def _format_site_render(resp: Any) -> None:
    click.echo(f"Open: {resp.site_path}/index.html")
    click.echo(f"({resp.page_count} pages)")


site.add_command(
    generate_command(
        name="render",
        request_model=RenderSiteRequest,
        usecase_attr="render_site_usecase",
        format_output=_format_site_render,
        help_text=RenderSiteUseCase.__doc__,
    )
)


if __name__ == "__main__":
    cli()
