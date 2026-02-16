"""CLI command registration for the Wardley Mapping bounded context.

Registers the tour command group.
"""

from __future__ import annotations

from typing import Any

import click

from bin.cli.introspect import generate_command
from wardley_mapping.dtos import RegisterTourRequest


# ---------------------------------------------------------------------------
# Format callbacks
# ---------------------------------------------------------------------------


def _format_tour_register(resp: Any) -> None:
    click.echo(
        f"Registered tour '{resp.name}' with {resp.stop_count} stops "
        f"for '{resp.client}/{resp.project_slug}'"
    )


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def register_commands(cli: click.Group) -> None:
    """Register Wardley Mapping commands on the given CLI group."""

    @cli.group()
    def tour() -> None:
        """Manage presentation tours."""

    tour.add_command(
        generate_command(
            name="register",
            request_model=RegisterTourRequest,
            usecase_attr="register_tour_usecase",
            format_output=_format_tour_register,
        )
    )
