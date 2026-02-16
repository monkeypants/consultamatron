"""CLI command registration for the consulting bounded context.

Registers project, decision, engagement, and research command groups.
"""

from __future__ import annotations

from typing import Any

import click

from bin.cli.introspect import generate_command
from consulting.dtos import (
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
    UpdateProjectStatusRequest,
)


# ---------------------------------------------------------------------------
# Format callbacks
# ---------------------------------------------------------------------------


def _format_init_workspace(resp: Any) -> None:
    click.echo(f"Initialized workspace for '{resp.client}'")


def _format_register_project(resp: Any) -> None:
    click.echo(
        f"Registered project '{resp.slug}' ({resp.skillset}) for '{resp.client}'"
    )


def _format_update_status(resp: Any) -> None:
    click.echo(f"Updated '{resp.project_slug}' status to '{resp.status}'")


def _format_list_projects(resp: Any) -> None:
    if not resp.projects:
        click.echo("No projects found.")
        return
    for p in resp.projects:
        click.echo(f"  {p.slug}  {p.skillset}  {p.status}  {p.created}")


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


def _format_decision_record(resp: Any) -> None:
    click.echo(
        f"Recorded decision '{resp.title}' for "
        f"'{resp.client}/{resp.project_slug}' ({resp.decision_id})"
    )


def _format_decision_list(resp: Any) -> None:
    if not resp.decisions:
        click.echo("No decisions recorded.")
        return
    for d in resp.decisions:
        click.echo(f"  {d.date}  {d.title}")
        for k, v in d.fields.items():
            click.echo(f"           {k}: {v}")


def _format_engagement_add(resp: Any) -> None:
    click.echo(
        f"Added engagement entry '{resp.title}' for '{resp.client}' ({resp.entry_id})"
    )


def _format_research_add(resp: Any) -> None:
    click.echo(
        f"Registered topic '{resp.topic}' as '{resp.filename}' for '{resp.client}'"
    )


def _format_research_list(resp: Any) -> None:
    if not resp.topics:
        click.echo("No research topics found.")
        return
    for t in resp.topics:
        click.echo(f"  {t.filename}  {t.topic}  {t.confidence}  {t.date}")


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_commands(cli: click.Group) -> None:
    """Register consulting commands on the given CLI group."""

    # -- project -----------------------------------------------------------

    @cli.group()
    def project() -> None:
        """Manage consulting projects."""

    project.add_command(
        generate_command(
            name="init",
            request_model=InitializeWorkspaceRequest,
            usecase_attr="initialize_workspace_usecase",
            format_output=_format_init_workspace,
        )
    )
    project.add_command(
        generate_command(
            name="register",
            request_model=RegisterProjectRequest,
            usecase_attr="register_project_usecase",
            format_output=_format_register_project,
        )
    )
    project.add_command(
        generate_command(
            name="update-status",
            request_model=UpdateProjectStatusRequest,
            usecase_attr="update_project_status_usecase",
            format_output=_format_update_status,
        )
    )
    project.add_command(
        generate_command(
            name="list",
            request_model=ListProjectsRequest,
            usecase_attr="list_projects_usecase",
            format_output=_format_list_projects,
        )
    )
    project.add_command(
        generate_command(
            name="get",
            request_model=GetProjectRequest,
            usecase_attr="get_project_usecase",
            format_output=_format_get_project,
        )
    )
    project.add_command(
        generate_command(
            name="progress",
            request_model=GetProjectProgressRequest,
            usecase_attr="get_project_progress_usecase",
            format_output=_format_project_progress,
        )
    )

    # -- decision ----------------------------------------------------------

    @cli.group()
    def decision() -> None:
        """Manage project decisions."""

    decision.add_command(
        generate_command(
            name="record",
            request_model=RecordDecisionRequest,
            usecase_attr="record_decision_usecase",
            format_output=_format_decision_record,
        )
    )
    decision.add_command(
        generate_command(
            name="list",
            request_model=ListDecisionsRequest,
            usecase_attr="list_decisions_usecase",
            format_output=_format_decision_list,
        )
    )

    # -- engagement --------------------------------------------------------

    @cli.group()
    def engagement() -> None:
        """Manage client engagement history."""

    engagement.add_command(
        generate_command(
            name="add",
            request_model=AddEngagementEntryRequest,
            usecase_attr="add_engagement_entry_usecase",
            format_output=_format_engagement_add,
        )
    )

    # -- research ----------------------------------------------------------

    @cli.group()
    def research() -> None:
        """Manage research topics."""

    research.add_command(
        generate_command(
            name="add",
            request_model=RegisterResearchTopicRequest,
            usecase_attr="register_research_topic_usecase",
            format_output=_format_research_add,
        )
    )
    research.add_command(
        generate_command(
            name="list",
            request_model=ListResearchTopicsRequest,
            usecase_attr="list_research_topics_usecase",
            format_output=_format_research_list,
        )
    )
