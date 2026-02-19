"""WIP command tests.

The ``practice wip`` command scans all client workspaces for in-progress
work. It derives pipeline position from gate artifact existence — the
same mechanism as ``engagement status`` — but across all clients and
engagements without requiring the caller to know slugs up front.

Tests exercise the CLI boundary through CliRunner, seeding workspaces
with varying engagement statuses, project completions, and gate states.
"""

from __future__ import annotations

from click.testing import CliRunner

import pytest

from bin.cli.di import Container
from bin.cli.main import cli
from practice.entities import EngagementStatus, ProjectStatus

CLIENT_A = "acme-corp"
CLIENT_B = "globex-inc"
ENGAGEMENT_A = "strat-1"
ENGAGEMENT_B = "strat-2"


@pytest.fixture
def run(tmp_config, monkeypatch):
    """Invoke CLI commands against a temp workspace with skillsets auto-discovered."""
    monkeypatch.setattr(
        "bin.cli.main.Config",
        type(
            "Config",
            (),
            {"from_repo_root": staticmethod(lambda _: tmp_config)},
        ),
    )
    runner = CliRunner()
    return lambda *args: runner.invoke(cli, list(args))


def _init(run, client):
    run("project", "init", "--client", client)


def _create_engagement(run, client, slug):
    run("engagement", "create", "--client", client, "--slug", slug)


def _register_project(run, client, engagement, slug):
    run(
        "project",
        "register",
        "--client",
        client,
        "--engagement",
        engagement,
        "--slug",
        slug,
        "--skillset",
        "wardley-mapping",
        "--scope",
        "Test scope",
    )


def _write_gate(tmp_config, client, engagement, project, gate_path):
    """Create a gate artifact file on disk."""
    gate = (
        tmp_config.workspace_root
        / client
        / "engagements"
        / engagement
        / project
        / gate_path
    )
    gate.parent.mkdir(parents=True, exist_ok=True)
    gate.write_text("agreed\n")


def _get_all_gates(tmp_config):
    """Return the list of gate paths from the wardley-mapping pipeline."""
    from bin.cli.di import Container

    c = Container(tmp_config)
    ss = c.skillsets.get("wardley-mapping")
    return [s.produces_gate for s in sorted(ss.pipeline, key=lambda s: s.order)]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWipShowsIncompleteProjects:
    """A project mid-pipeline appears in WIP output."""

    def test_mid_pipeline_project_appears(self, run, tmp_config):
        _init(run, CLIENT_A)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")

        # Complete first gate only
        gates = _get_all_gates(tmp_config)
        _write_gate(tmp_config, CLIENT_A, ENGAGEMENT_A, "maps-1", gates[0])

        result = run("wip")
        assert result.exit_code == 0
        assert "maps-1" in result.output
        assert "wardley-mapping" in result.output
        assert f"stage 2/{len(gates)}" in result.output


class TestWipExcludesCompleteProjects:
    """A project with all gates present is not WIP."""

    def test_complete_project_omitted(self, run, tmp_config):
        _init(run, CLIENT_A)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")

        # Complete all gates
        for gate in _get_all_gates(tmp_config):
            _write_gate(tmp_config, CLIENT_A, ENGAGEMENT_A, "maps-1", gate)

        result = run("wip")
        assert result.exit_code == 0
        assert "No work in progress" in result.output


class TestWipExcludesClosedEngagements:
    """Closed engagements are excluded from WIP."""

    def test_closed_engagement_omitted(self, run, tmp_config):
        _init(run, CLIENT_A)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")

        # Close the engagement by directly updating the entity
        c = Container(tmp_config)
        eng = c.engagement_entities.get(CLIENT_A, ENGAGEMENT_A)
        c.engagement_entities.save(
            eng.model_copy(update={"status": EngagementStatus.CLOSED})
        )

        result = run("wip")
        assert result.exit_code == 0
        assert "No work in progress" in result.output


class TestWipExcludesClosedProjects:
    """Closed projects are excluded even if engagement is open."""

    def test_closed_project_omitted(self, run, tmp_config):
        _init(run, CLIENT_A)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")

        # Close project by directly updating the entity
        c = Container(tmp_config)
        proj = c.projects.get(CLIENT_A, ENGAGEMENT_A, "maps-1")
        c.projects.save(proj.model_copy(update={"status": ProjectStatus.CLOSED}))

        result = run("wip")
        assert result.exit_code == 0
        assert "No work in progress" in result.output


class TestWipShowsBlockedProjects:
    """A project blocked on a prerequisite gate shows BLOCKED."""

    def test_blocked_project_with_reason(self, run, tmp_config):
        _init(run, CLIENT_A)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")

        # Don't write any gates — stage 1 has a prerequisite (resources/index.md)
        # that doesn't exist, so the project is blocked.
        result = run("wip")
        assert result.exit_code == 0
        assert "maps-1" in result.output
        assert "BLOCKED" in result.output
        assert "prerequisite" in result.output.lower()


class TestWipClientFilter:
    """--client limits output to one client."""

    def test_filter_shows_only_matching_client(self, run, tmp_config):
        _init(run, CLIENT_A)
        _init(run, CLIENT_B)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _create_engagement(run, CLIENT_B, ENGAGEMENT_B)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")
        _register_project(run, CLIENT_B, ENGAGEMENT_B, "maps-2")

        result = run("wip", "--client", CLIENT_A)
        assert result.exit_code == 0
        assert CLIENT_A in result.output
        assert CLIENT_B not in result.output
        assert "maps-1" in result.output
        assert "maps-2" not in result.output


class TestWipEmptyWorkspace:
    """No clients at all shows empty message."""

    def test_no_clients(self, run):
        result = run("wip")
        assert result.exit_code == 0
        assert "No work in progress" in result.output


class TestWipShowsNextSkill:
    """The next skill name appears in output."""

    def test_next_skill_in_output(self, run, tmp_config):
        _init(run, CLIENT_A)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")

        # Write the prerequisite that stage 1 needs so project is unblocked
        c = Container(tmp_config)
        ss = c.skillsets.get("wardley-mapping")
        stage_1 = sorted(ss.pipeline, key=lambda s: s.order)[0]

        if stage_1.prerequisite_gate:
            _write_gate(
                tmp_config,
                CLIENT_A,
                ENGAGEMENT_A,
                "maps-1",
                stage_1.prerequisite_gate,
            )

        result = run("wip")
        assert result.exit_code == 0
        assert f"next: {stage_1.skill}" in result.output


class TestWipMultipleClients:
    """WIP across multiple clients shows all incomplete work."""

    def test_shows_both_clients(self, run, tmp_config):
        _init(run, CLIENT_A)
        _init(run, CLIENT_B)
        _create_engagement(run, CLIENT_A, ENGAGEMENT_A)
        _create_engagement(run, CLIENT_B, ENGAGEMENT_B)
        _register_project(run, CLIENT_A, ENGAGEMENT_A, "maps-1")
        _register_project(run, CLIENT_B, ENGAGEMENT_B, "maps-2")

        result = run("wip")
        assert result.exit_code == 0
        assert CLIENT_A in result.output
        assert CLIENT_B in result.output
        assert "maps-1" in result.output
        assert "maps-2" in result.output
