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
from bin.cli.dtos import RenderSiteRequest
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
