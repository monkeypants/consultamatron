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
    AddEngagementEntryRequest,
    AddEngagementSourceRequest,
    CreateEngagementRequest,
    EngagementStatusRequest,
    GetEngagementRequest,
    GetProjectProgressRequest,
    GetProjectRequest,
    InitializeWorkspaceRequest,
    ListDecisionsRequest,
    ListEngagementsRequest,
    ListProfilesRequest,
    ListProjectsRequest,
    ListResearchTopicsRequest,
    ListSkillsetsRequest,
    ListSourcesRequest,
    GetWipRequest,
    ListPantheonRequest,
    NextActionRequest,
    PackStatusRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
    RegisterProspectusRequest,
    RegisterResearchTopicRequest,
    RemoveEngagementSourceRequest,
    RenderSiteRequest,
    ShowProfileRequest,
    ShowSkillsetRequest,
    ShowSourceRequest,
    SkillPathRequest,
    UpdateProjectStatusRequest,
    UpdateProspectusRequest,
    AggregateNeedsBriefRequest,
    FlushObservationsRequest,
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
# project
# ---------------------------------------------------------------------------


@cli.group()
def project() -> None:
    """Manage consulting projects."""


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


# ---------------------------------------------------------------------------
# engagement
# ---------------------------------------------------------------------------


@cli.group()
def engagement() -> None:
    """Manage client engagement history."""


def _format_engagement_status(resp: Any) -> None:
    d = resp.dashboard
    click.echo(f"{d.engagement_slug} ({d.status})")
    if not d.projects:
        click.echo("  No projects.")
        return
    click.echo()
    for p in d.projects:
        completed = len(p.completed_gates)
        label = f"stage {p.current_stage}/{p.total_stages}"
        click.echo(f"  {p.project_slug} ({p.skillset}): {label}")
        if completed == p.total_stages:
            click.echo("    All stages complete.")
        elif p.next_gate:
            click.echo(f"    Next gate: {p.next_gate}")


def _format_next_action(resp: Any) -> None:
    click.echo(resp.reason)


def _format_engagement_add(resp: Any) -> None:
    click.echo(
        f"Added engagement entry '{resp.title}' for '{resp.client}' ({resp.entry_id})"
    )


def _format_engagement_create(resp: Any) -> None:
    click.echo(
        f"Created engagement '{resp.slug}' for '{resp.client}' (status: {resp.status})"
    )


def _format_engagement_get(resp: Any) -> None:
    e = resp.engagement
    click.echo(f"Slug:     {e.slug}")
    click.echo(f"Client:   {e.client}")
    click.echo(f"Status:   {e.status}")
    click.echo(f"Sources:  {', '.join(e.allowed_sources)}")
    click.echo(f"Created:  {e.created}")
    if e.notes:
        click.echo(f"Notes:    {e.notes}")


def _format_engagement_list(resp: Any) -> None:
    if not resp.engagements:
        click.echo("No engagements found.")
        return
    for e in resp.engagements:
        click.echo(
            f"  {e.slug}  {e.status}  {', '.join(e.allowed_sources)}  {e.created}"
        )


def _format_engagement_add_source(resp: Any) -> None:
    click.echo(
        f"Added source '{resp.source}' to engagement '{resp.client}/{resp.engagement}'"
    )
    click.echo(f"Allowed sources: {', '.join(resp.allowed_sources)}")


def _format_engagement_remove_source(resp: Any) -> None:
    click.echo(
        f"Removed source '{resp.source}' from engagement "
        f"'{resp.client}/{resp.engagement}'"
    )
    click.echo(f"Allowed sources: {', '.join(resp.allowed_sources)}")


engagement.add_command(
    generate_command(
        name="status",
        request_model=EngagementStatusRequest,
        usecase_attr="get_engagement_status_usecase",
        format_output=_format_engagement_status,
    )
)
engagement.add_command(
    generate_command(
        name="next",
        request_model=NextActionRequest,
        usecase_attr="get_next_action_usecase",
        format_output=_format_next_action,
    )
)
engagement.add_command(
    generate_command(
        name="create",
        request_model=CreateEngagementRequest,
        usecase_attr="create_engagement_usecase",
        format_output=_format_engagement_create,
    )
)
engagement.add_command(
    generate_command(
        name="get",
        request_model=GetEngagementRequest,
        usecase_attr="get_engagement_usecase",
        format_output=_format_engagement_get,
    )
)
engagement.add_command(
    generate_command(
        name="list",
        request_model=ListEngagementsRequest,
        usecase_attr="list_engagements_usecase",
        format_output=_format_engagement_list,
    )
)
engagement.add_command(
    generate_command(
        name="add",
        request_model=AddEngagementEntryRequest,
        usecase_attr="add_engagement_entry_usecase",
        format_output=_format_engagement_add,
    )
)
engagement.add_command(
    generate_command(
        name="add-source",
        request_model=AddEngagementSourceRequest,
        usecase_attr="add_engagement_source_usecase",
        format_output=_format_engagement_add_source,
    )
)
engagement.add_command(
    generate_command(
        name="remove-source",
        request_model=RemoveEngagementSourceRequest,
        usecase_attr="remove_engagement_source_usecase",
        format_output=_format_engagement_remove_source,
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


def _format_research_list(resp: Any) -> None:
    if not resp.topics:
        click.echo("No research topics found.")
        return
    for t in resp.topics:
        click.echo(f"  {t.filename}  {t.topic}  {t.confidence}  {t.date}")


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
        total_stages = sum(len(p.stages) for p in s.pipelines)
        click.echo(
            f"  {s.name}  {s.display_name}"
            f"  ({len(s.pipelines)} pipelines, {total_stages} stages, {status})"
        )


def _format_skillset_show(resp: Any) -> None:
    s = resp.skillset
    status = "implemented" if s.is_implemented else "prospectus"
    click.echo(f"Name:        {s.name}")
    click.echo(f"Display:     {s.display_name}")
    click.echo(f"Description: {s.description}")
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
    for p in s.pipelines:
        click.echo(f"\nPipeline: {p.name} ({p.display_name})")
        click.echo(f"  Slug:   {p.slug_pattern}")
        click.echo(f"  Stages: {len(p.stages)}")
        for st in p.stages:
            click.echo(f"    {st.order}. {st.description} ({st.skill})")


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
# pantheon (cross-skillset luminary aggregation)
# ---------------------------------------------------------------------------


@cli.group()
def pantheon() -> None:
    """Luminary aggregation from knowledge packs."""


def _format_list_pantheon(resp: Any) -> None:
    if not resp.luminaries:
        click.echo("No luminaries found.")
        return
    by_skillset: dict[str, list] = {}
    for lum in resp.luminaries:
        by_skillset.setdefault(lum.skillset, []).append(lum)
    skillsets = sorted(by_skillset)
    click.echo(
        f"Pantheon ({len(resp.luminaries)} luminaries from {len(skillsets)} skillsets):"
    )
    for ss in skillsets:
        click.echo(f"\n  {ss}:")
        for lum in by_skillset[ss]:
            click.echo(f"    {lum.name}")
            click.echo(f"      {lum.summary}")


@pantheon.command("list")
@click.option("--skillsets", required=True, help="Comma-separated skillset names.")
@click.pass_context
def list_pantheon(ctx: click.Context, skillsets: str) -> None:
    """List luminaries from specified skillset pantheons."""
    from practice.exceptions import DomainError

    di = ctx.obj
    names = [s.strip() for s in skillsets.split(",")]
    try:
        resp = di.list_pantheon_usecase.execute(
            ListPantheonRequest(skillset_names=names)
        )
    except DomainError as e:
        raise click.ClickException(str(e))
    _format_list_pantheon(resp)


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
# wip (cross-client work-in-progress)
# ---------------------------------------------------------------------------


def _format_wip(resp: Any) -> None:
    if not resp.engagements:
        click.echo("No work in progress.")
        return
    for eng in resp.engagements:
        click.echo(f"{eng.client}/{eng.engagement_slug} ({eng.status})")
        for p in eng.projects:
            label = f"stage {p.current_stage}/{p.total_stages}"
            click.echo(f"  {p.project_slug} ({p.skillset}): {label}")
            if p.blocked:
                click.echo(f"    BLOCKED: {p.blocked_reason}")
            elif p.next_skill:
                click.echo(f"    next: {p.next_skill}")
    if resp.nudges:
        click.echo()
        for nudge in resp.nudges:
            click.echo(click.style(f"  {nudge}", fg="yellow"))


cli.add_command(
    generate_command(
        name="wip",
        request_model=GetWipRequest,
        usecase_attr="get_wip_status_usecase",
        format_output=_format_wip,
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


# ---------------------------------------------------------------------------
# observation (cross-BC, stays here)
# ---------------------------------------------------------------------------


@cli.group()
def observation() -> None:
    """Observation routing operations."""


def _format_needs_brief(resp: Any) -> None:
    click.echo("## Observation Brief")
    click.echo(f"\nYou are at a **{resp.inflection}** inflection point.\n")

    if not resp.needs:
        click.echo("No observation needs declared for this context.\n")
    else:
        click.echo("### What to watch for\n")
        for i, n in enumerate(resp.needs, 1):
            served = " (already served)" if n.served else ""
            click.echo(f"{i}. **{n.slug}** — {n.need}{served}")
            click.echo(f"   Rationale: {n.rationale}\n")

    click.echo("### How to record observations\n")
    click.echo("Write each observation as a markdown file in:")
    click.echo(f"  {resp.pending_dir}/\n")
    click.echo("Frontmatter template:")
    click.echo("  ---")
    click.echo("  slug: <unique-kebab-case>")
    click.echo(f"  source_inflection: {resp.inflection}")
    click.echo("  need_refs: [need-slug-1, need-slug-2]")
    click.echo("  ---")
    click.echo("  <observation content>\n")

    if resp.destinations:
        click.echo("### Eligible destinations\n")
        for d in resp.destinations:
            click.echo(f"- {d.owner_type}/{d.owner_ref}")
        click.echo()

    click.echo("### When done\n")
    click.echo(
        "Run: practice observation flush --client <client> --engagement <engagement>"
    )

    if resp.nudges:
        click.echo("\n### Nudges\n")
        for nudge in resp.nudges:
            click.echo(f"- {nudge}")


observation.add_command(
    generate_command(
        name="brief",
        request_model=AggregateNeedsBriefRequest,
        usecase_attr="aggregate_needs_brief_usecase",
        format_output=_format_needs_brief,
    )
)


def _format_flush_result(resp: Any) -> None:
    click.echo(f"Flushed: {resp.flushed} routed, {resp.rejected} rejected")


observation.add_command(
    generate_command(
        name="flush",
        request_model=FlushObservationsRequest,
        usecase_attr="flush_observations_usecase",
        format_output=_format_flush_result,
    )
)


if __name__ == "__main__":
    cli()
