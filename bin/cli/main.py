"""CLI entry point for consulting practice accounting operations.

Thin application shell: create CLI group, discover bounded context
commands, keep cross-BC commands (site). No business logic lives here.

Invocation: uv run practice <group> <command> [options]
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import click

from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.dtos import (
    ListProfilesRequest,
    ListSkillsetsRequest,
    ListSourcesRequest,
    PackStatusRequest,
    RegisterProspectusRequest,
    RenderSiteRequest,
    ShowProfileRequest,
    ShowSkillsetRequest,
    ShowSourceRequest,
    SkillPathRequest,
    UpdateProspectusRequest,
)
from bin.cli.introspect import generate_command
from practice.bc_discovery import discover_all_bc_modules

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Consultamatron accounting operations."""
    ctx.obj = Container(Config.from_repo_root(Path.cwd()))


# -- Register bounded context commands -------------------------------------

for _mod in discover_all_bc_modules(_REPO_ROOT):
    try:
        _cli_mod = importlib.import_module(f"{_mod.__name__}.cli")
    except (ImportError, ModuleNotFoundError):
        continue
    if hasattr(_cli_mod, "register_commands"):
        _cli_mod.register_commands(cli)


# ---------------------------------------------------------------------------
# skillset (cross-BC, stays here)
# ---------------------------------------------------------------------------


@cli.group()
def skillset() -> None:
    """Browse and manage registered skillsets."""


def _format_skillset_list(resp: Any) -> None:
    if not resp.skillsets:
        click.echo("No skillsets registered.")
        return
    for s in resp.skillsets:
        status = "implemented" if s.is_implemented else "prospectus"
        click.echo(f"  {s.name}  {s.display_name}  ({len(s.stages)} stages, {status})")


def _format_skillset_show(resp: Any) -> None:
    s = resp.skillset
    status = "implemented" if s.is_implemented else "prospectus"
    click.echo(f"Name:        {s.name}")
    click.echo(f"Display:     {s.display_name}")
    click.echo(f"Description: {s.description}")
    click.echo(f"Slug:        {s.slug_pattern}")
    click.echo(f"Status:      {status}")
    if s.problem_domain:
        click.echo(f"Domain:      {s.problem_domain}")
    if s.value_proposition:
        click.echo(f"Value:       {s.value_proposition}")
    if s.deliverables:
        click.echo(f"Deliverables: {', '.join(s.deliverables)}")
    if s.classification:
        click.echo(f"Tags:        {', '.join(s.classification)}")
    if s.evidence:
        click.echo(f"Evidence:    {', '.join(s.evidence)}")
    click.echo(f"Pipeline:    {len(s.stages)} stages")
    for st in s.stages:
        click.echo(f"  {st.order}. {st.description} ({st.skill})")


def _format_prospectus_register(resp: Any) -> None:
    click.echo(f"Registered prospectus: {resp.name}")
    click.echo(f"Created: {resp.init_path}")


def _format_prospectus_update(resp: Any) -> None:
    click.echo(f"Updated prospectus: {resp.name}")


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
skillset.add_command(
    generate_command(
        name="add",
        request_model=RegisterProspectusRequest,
        usecase_attr="register_prospectus_usecase",
        format_output=_format_prospectus_register,
    )
)
skillset.add_command(
    generate_command(
        name="update",
        request_model=UpdateProspectusRequest,
        usecase_attr="update_prospectus_usecase",
        format_output=_format_prospectus_update,
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
# profile (cross-BC, stays here)
# ---------------------------------------------------------------------------


@cli.group()
def profile() -> None:
    """Browse registered profiles."""


def _format_profile_list(resp: Any) -> None:
    if not resp.profiles:
        click.echo("No profiles registered.")
        return
    for p in resp.profiles:
        click.echo(
            f"  {p.name}  {p.display_name}  ({len(p.skillsets)} skillsets, {p.source})"
        )


def _format_profile_show(resp: Any) -> None:
    p = resp.profile
    click.echo(f"Name:        {p.name}")
    click.echo(f"Display:     {p.display_name}")
    click.echo(f"Description: {p.description}")
    click.echo(f"Source:      {p.source}")
    click.echo(f"Skillsets:   {', '.join(p.skillsets)}")


profile.add_command(
    generate_command(
        name="list",
        request_model=ListProfilesRequest,
        usecase_attr="list_profiles_usecase",
        format_output=_format_profile_list,
    )
)
profile.add_command(
    generate_command(
        name="show",
        request_model=ShowProfileRequest,
        usecase_attr="show_profile_usecase",
        format_output=_format_profile_show,
    )
)


# ---------------------------------------------------------------------------
# skill (cross-BC, stays here)
# ---------------------------------------------------------------------------


@cli.group()
def skill() -> None:
    """Skill operations."""


def _format_skill_path(resp: Any) -> None:
    click.echo(resp.path)


skill.add_command(
    generate_command(
        name="path",
        request_model=SkillPathRequest,
        usecase_attr="skill_path_usecase",
        format_output=_format_skill_path,
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


# ---------------------------------------------------------------------------
# pack (cross-BC, stays here)
# ---------------------------------------------------------------------------

_STATE_COLOURS = {
    "clean": "green",
    "dirty": "yellow",
    "absent": "cyan",
    "corrupt": "red",
}


def _format_pack_status(resp: Any, indent: int = 0) -> None:
    prefix = "  " * indent
    colour = _STATE_COLOURS.get(resp.deep_state, "white")
    click.echo(f"{prefix}{resp.pack_root}")
    click.echo(
        f"{prefix}  state: {click.style(resp.deep_state, fg=colour)}"
        f"  (shallow: {resp.compilation_state})"
    )
    for item in resp.items:
        kind = "pack" if item.is_composite else "item"
        item_colour = _STATE_COLOURS.get(item.state, "white")
        click.echo(
            f"{prefix}  {click.style(item.state, fg=item_colour):>10s}  "
            f"{item.name} ({kind})"
        )
    for child in resp.children:
        _format_pack_status(child, indent + 1)


@cli.group()
def pack() -> None:
    """Knowledge pack operations."""


pack.add_command(
    generate_command(
        name="status",
        request_model=PackStatusRequest,
        usecase_attr="pack_status_usecase",
        format_output=_format_pack_status,
    )
)


if __name__ == "__main__":
    cli()
