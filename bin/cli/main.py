"""CLI entry point for consulting practice accounting operations.

Thin application shell: create CLI group, discover bounded context
commands, keep cross-BC commands (site). No business logic lives here.

Invocation: uv run practice <group> <command> [options]
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.dtos import (
    ListSkillsetsRequest,
    ListSourcesRequest,
    RenderSiteRequest,
    ShowSkillsetRequest,
    ShowSourceRequest,
)
from bin.cli.introspect import generate_command

import consulting.cli
import wardley_mapping.cli


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Consultamatron accounting operations."""
    ctx.obj = Container(Config.from_repo_root(Path.cwd()))


# -- Register bounded context commands -------------------------------------

consulting.cli.register_commands(cli)
wardley_mapping.cli.register_commands(cli)


# ---------------------------------------------------------------------------
# skillset (cross-BC, stays here)
# ---------------------------------------------------------------------------


@cli.group()
def skillset() -> None:
    """Browse registered skillsets."""


def _format_skillset_list(resp: Any) -> None:
    if not resp.skillsets:
        click.echo("No skillsets registered.")
        return
    for s in resp.skillsets:
        click.echo(f"  {s.name}  {s.display_name}  ({len(s.stages)} stages)")


def _format_skillset_show(resp: Any) -> None:
    s = resp.skillset
    click.echo(f"Name:        {s.name}")
    click.echo(f"Display:     {s.display_name}")
    click.echo(f"Description: {s.description}")
    click.echo(f"Slug:        {s.slug_pattern}")
    click.echo(f"Pipeline:    {len(s.stages)} stages")
    for st in s.stages:
        click.echo(f"  {st.order}. {st.description} ({st.skill})")


skillset.add_command(
    generate_command(
        name="list",
        request_model=ListSkillsetsRequest,
        usecase_attr="list_skillsets_usecase",
        format_output=_format_skillset_list,
    )
)
skillset.add_command(
    generate_command(
        name="show",
        request_model=ShowSkillsetRequest,
        usecase_attr="show_skillset_usecase",
        format_output=_format_skillset_show,
    )
)


# ---------------------------------------------------------------------------
# source (cross-BC, stays here)
# ---------------------------------------------------------------------------


@cli.group()
def source() -> None:
    """Browse installed skillset sources."""


def _format_source_list(resp: Any) -> None:
    if not resp.sources:
        click.echo("No sources installed.")
        return
    for s in resp.sources:
        click.echo(f"  {s.slug}  {s.source_type}  ({len(s.skillset_names)} skillsets)")


def _format_source_show(resp: Any) -> None:
    s = resp.source
    click.echo(f"Slug:      {s.slug}")
    click.echo(f"Type:      {s.source_type}")
    click.echo(f"Skillsets: {', '.join(s.skillset_names)}")


source.add_command(
    generate_command(
        name="list",
        request_model=ListSourcesRequest,
        usecase_attr="list_sources_usecase",
        format_output=_format_source_list,
    )
)
source.add_command(
    generate_command(
        name="show",
        request_model=ShowSourceRequest,
        usecase_attr="show_source_usecase",
        format_output=_format_source_show,
    )
)


# ---------------------------------------------------------------------------
# site (cross-BC, stays here)
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
    )
)


if __name__ == "__main__":
    cli()
