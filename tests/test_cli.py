"""CLI boundary tests.

Invokes every command through Click's CliRunner, asserting on exit
codes, output text, and error messages. This is the outermost test
boundary — if a test here fails, either argument parsing, output
formatting, or error handling is broken.

Business rule validation (duplicate slugs, unknown skillsets, invalid
transitions) lives in test_usecases.py. One representative error test
here verifies that DomainError surfaces as exit code 1 + message.

The sample data continues the Holloway Group engagement from
test_usecases.py: a freight logistics company commissioning a
Wardley Map of their operations.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

import pytest

from bin.cli.main import cli

CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


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


def _init(run):
    """Initialize Holloway Group workspace via CLI."""
    return run("project", "init", "--client", CLIENT)


def _create_engagement(run, slug=ENGAGEMENT):
    """Create an engagement via CLI."""
    return run("engagement", "create", "--client", CLIENT, "--slug", slug)


def _register(run, slug="maps-1"):
    """Register a wardley-mapping project via CLI. Creates engagement if needed."""
    _create_engagement(run)
    return run(
        "project",
        "register",
        "--client",
        CLIENT,
        "--engagement",
        ENGAGEMENT,
        "--slug",
        slug,
        "--skillset",
        "wardley-mapping",
        "--scope",
        "Freight operations and digital platform",
    )


# ---------------------------------------------------------------------------
# project init
# ---------------------------------------------------------------------------


class TestProjectInit:
    """Initialize a client workspace from the command line."""

    def test_success_message(self, run):
        result = _init(run)
        assert result.exit_code == 0
        assert "Initialized workspace for 'holloway-group'" in result.output

    def test_duplicate_reports_error(self, run):
        _init(run)
        result = _init(run)
        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_missing_client_rejected(self, run):
        result = run("project", "init")
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()


# ---------------------------------------------------------------------------
# project register
# ---------------------------------------------------------------------------


class TestProjectRegister:
    """Register consulting projects from the command line."""

    def test_success_message(self, run):
        _init(run)
        result = _register(run)
        assert result.exit_code == 0
        assert "maps-1" in result.output
        assert "wardley-mapping" in result.output
        assert "holloway-group" in result.output

    def test_missing_required_option_rejected(self, run):
        _init(run)
        result = run(
            "project",
            "register",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--slug",
            "maps-1",
            # Missing --skillset and --scope
        )
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_notes_defaults_to_empty(self, run):
        _init(run)
        _register(run)  # --notes not provided
        result = run(
            "project",
            "get",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--slug",
            "maps-1",
        )
        assert result.exit_code == 0
        assert "Notes:" not in result.output

    def test_explicit_notes_preserved(self, run):
        _init(run)
        _create_engagement(run)
        result = run(
            "project",
            "register",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--slug",
            "maps-1",
            "--skillset",
            "wardley-mapping",
            "--scope",
            "Test scope",
            "--notes",
            "Important note",
        )
        assert result.exit_code == 0
        result = run(
            "project",
            "get",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--slug",
            "maps-1",
        )
        assert "Notes:    Important note" in result.output


# ---------------------------------------------------------------------------
# project update-status
# ---------------------------------------------------------------------------


class TestProjectUpdateStatus:
    """Transition project status from the command line."""

    def test_planned_to_active(self, run):
        _init(run)
        _register(run)
        result = run(
            "project",
            "update-status",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--status",
            "elaboration",
        )
        assert result.exit_code == 0
        assert "elaboration" in result.output

    def test_invalid_status_value_rejected_by_click(self, run):
        result = run(
            "project",
            "update-status",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--status",
            "mythical",
        )
        assert result.exit_code != 0
        assert (
            "Invalid value" in result.output
            or "invalid choice" in result.output.lower()
        )


# ---------------------------------------------------------------------------
# project list
# ---------------------------------------------------------------------------


class TestProjectList:
    """List projects from the command line."""

    def test_empty_registry(self, run):
        _init(run)
        result = run("project", "list", "--client", CLIENT, "--engagement", ENGAGEMENT)
        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_project_appears_in_list(self, run):
        _init(run)
        _register(run)
        result = run("project", "list", "--client", CLIENT, "--engagement", ENGAGEMENT)
        assert result.exit_code == 0
        assert "maps-1" in result.output
        assert "wardley-mapping" in result.output
        assert "planning" in result.output

    def test_invalid_status_rejected_by_click(self, run):
        _init(run)
        result = run(
            "project",
            "list",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--status",
            "mythical",
        )
        assert result.exit_code != 0
        assert (
            "Invalid value" in result.output
            or "invalid choice" in result.output.lower()
        )

    def test_filter_by_status(self, run):
        _init(run)
        _register(run)
        result = run(
            "project",
            "list",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--status",
            "planning",
        )
        assert result.exit_code == 0
        assert "maps-1" in result.output

    def test_filter_by_status_no_match(self, run):
        _init(run)
        _register(run)
        result = run(
            "project",
            "list",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--status",
            "elaboration",
        )
        assert result.exit_code == 0
        assert "No projects found" in result.output


# ---------------------------------------------------------------------------
# project get
# ---------------------------------------------------------------------------


class TestProjectGet:
    """Retrieve a single project from the command line."""

    def test_found_shows_details(self, run):
        _init(run)
        _register(run)
        result = run(
            "project",
            "get",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--slug",
            "maps-1",
        )
        assert result.exit_code == 0
        assert "Slug:     maps-1" in result.output
        assert "Skillset: wardley-mapping" in result.output
        assert "Status:   planning" in result.output

    def test_not_found_reports_error(self, run):
        _init(run)
        result = run(
            "project",
            "get",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--slug",
            "nonexistent",
        )
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_missing_slug_rejected(self, run):
        result = run("project", "get", "--client", CLIENT, "--engagement", ENGAGEMENT)
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# project progress
# ---------------------------------------------------------------------------


class TestProjectProgress:
    """Show pipeline progress from the command line."""

    def test_all_stages_pending(self, run):
        _init(run)
        _register(run)
        result = run(
            "project",
            "progress",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
        )
        assert result.exit_code == 0
        assert "[ ] 1." in result.output
        assert "(wm-research)" in result.output
        assert "Current: wm-research" in result.output

    def test_not_found_project_error(self, run):
        _init(run)
        result = run(
            "project",
            "progress",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "nonexistent",
        )
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_missing_project_rejected(self, run):
        result = run(
            "project", "progress", "--client", CLIENT, "--engagement", ENGAGEMENT
        )
        assert result.exit_code != 0

    def test_completed_stage_shows_checkmark(self, run):
        _init(run)
        _register(run)
        run(
            "decision",
            "record",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--title",
            "Stage 1: Project brief agreed",
        )
        result = run(
            "project",
            "progress",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
        )
        assert "[x] 1." in result.output
        assert "[ ] 2." in result.output
        assert "Current: wm-needs" in result.output


# ---------------------------------------------------------------------------
# decision record
# ---------------------------------------------------------------------------


class TestDecisionRecord:
    """Record decisions from the command line."""

    def test_success_with_fields(self, run):
        _init(run)
        _register(run)
        result = run(
            "decision",
            "record",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--title",
            "Stage 2: User needs agreed",
            "--field",
            "Users=Freight customers, Fleet operators",
            "--field",
            "Scope=Freight division",
        )
        assert result.exit_code == 0
        assert "Stage 2: User needs agreed" in result.output
        assert "holloway-group/maps-1" in result.output

    def test_fields_default_to_empty(self, run):
        _init(run)
        _register(run)
        result = run(
            "decision",
            "record",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--title",
            "No fields provided",
        )
        assert result.exit_code == 0
        assert "No fields provided" in result.output

    def test_missing_title_rejected(self, run):
        _init(run)
        _register(run)
        result = run(
            "decision",
            "record",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
        )
        assert result.exit_code != 0

    def test_not_found_project_error(self, run):
        _init(run)
        result = run(
            "decision",
            "record",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "nonexistent",
            "--title",
            "Test",
        )
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


# ---------------------------------------------------------------------------
# decision list
# ---------------------------------------------------------------------------


class TestDecisionList:
    """List decisions from the command line."""

    def test_shows_seeded_decision(self, run):
        _init(run)
        _register(run)
        result = run(
            "decision",
            "list",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
        )
        assert result.exit_code == 0
        assert "Project created" in result.output

    def test_missing_project_rejected(self, run):
        result = run("decision", "list", "--client", CLIENT, "--engagement", ENGAGEMENT)
        assert result.exit_code != 0

    def test_empty_decision_log(self, run):
        """A project with no decisions shows the seeded 'Project created' entry."""
        _init(run)
        _register(run)
        result = run(
            "decision",
            "list",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
        )
        # RegisterProject seeds one decision automatically
        assert result.exit_code == 0
        assert "Project created" in result.output


# ---------------------------------------------------------------------------
# engagement add
# ---------------------------------------------------------------------------


class TestEngagementAdd:
    """Add engagement entries from the command line."""

    def test_success_message(self, run):
        _init(run)
        result = run(
            "engagement",
            "add",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--title",
            "Strategy workshop scheduled",
            "--field",
            "Attendees=COO, CTO, VP Engineering",
        )
        assert result.exit_code == 0
        assert "Strategy workshop scheduled" in result.output

    def test_fields_default_to_empty(self, run):
        _init(run)
        result = run(
            "engagement",
            "add",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--title",
            "Quick note",
        )
        assert result.exit_code == 0
        assert "Quick note" in result.output

    def test_not_found_client_error(self, run):
        result = run(
            "engagement",
            "add",
            "--client",
            "nonexistent",
            "--engagement",
            ENGAGEMENT,
            "--title",
            "Test",
        )
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_missing_title_rejected(self, run):
        result = run(
            "engagement", "add", "--client", CLIENT, "--engagement", ENGAGEMENT
        )
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# research add / list
# ---------------------------------------------------------------------------


class TestResearchAdd:
    """Register research topics from the command line."""

    def test_success_message(self, run):
        _init(run)
        result = run(
            "research",
            "add",
            "--client",
            CLIENT,
            "--topic",
            "Technology stack and build-vs-buy decisions",
            "--filename",
            "technology-landscape.md",
            "--confidence",
            "Medium",
        )
        assert result.exit_code == 0
        assert "technology-landscape.md" in result.output

    def test_invalid_confidence_rejected_by_click(self, run):
        result = run(
            "research",
            "add",
            "--client",
            CLIENT,
            "--topic",
            "test",
            "--filename",
            "test.md",
            "--confidence",
            "Legendary",
        )
        assert result.exit_code != 0
        assert "Legendary" in result.output
        assert "Invalid value" in result.output


class TestResearchList:
    """List research topics from the command line."""

    def test_empty_manifest(self, run):
        _init(run)
        result = run("research", "list", "--client", CLIENT)
        assert result.exit_code == 0
        assert "No research topics found" in result.output

    def test_topic_appears_after_add(self, run):
        _init(run)
        run(
            "research",
            "add",
            "--client",
            CLIENT,
            "--topic",
            "Fleet logistics tech",
            "--filename",
            "fleet-tech.md",
            "--confidence",
            "Medium",
        )
        result = run("research", "list", "--client", CLIENT)
        assert result.exit_code == 0
        assert "fleet-tech.md" in result.output
        assert "Fleet logistics tech" in result.output


# ---------------------------------------------------------------------------
# site render
# ---------------------------------------------------------------------------


class TestSiteRender:
    """Render a client site from the command line."""

    def test_nonexistent_client_error(self, run):
        result = run("site", "render", "--client", "nonexistent")
        assert result.exit_code == 1
        assert "Client not found" in result.output

    def test_uses_option_not_argument(self, run):
        """--client is an option, not a positional argument."""
        result = run("site", "render", CLIENT)
        assert result.exit_code != 0

    def test_missing_client_rejected(self, run):
        result = run("site", "render")
        assert result.exit_code != 0


# ---------------------------------------------------------------------------
# tour register
# ---------------------------------------------------------------------------


class TestTourRegister:
    """Register presentation tours from the command line."""

    def test_success_with_json_stops(self, run):
        _init(run)
        _register(run)
        stops = json.dumps(
            [
                {
                    "order": "1",
                    "title": "Strategic Overview",
                    "atlas_source": "atlas/overview/",
                },
                {
                    "order": "2",
                    "title": "Competitive Moats",
                    "atlas_source": "atlas/bottlenecks/",
                },
            ]
        )
        result = run(
            "tour",
            "register",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--name",
            "investor",
            "--title",
            "Investor Briefing: Strategic Position and Defensibility",
            "--stops",
            stops,
        )
        assert result.exit_code == 0
        assert "investor" in result.output
        assert "2 stops" in result.output

    def test_invalid_json_rejected(self, run):
        _init(run)
        _register(run)
        result = run(
            "tour",
            "register",
            "--client",
            CLIENT,
            "--engagement",
            ENGAGEMENT,
            "--project",
            "maps-1",
            "--name",
            "investor",
            "--title",
            "Test",
            "--stops",
            "not valid json",
        )
        assert result.exit_code != 0
        assert "Invalid" in result.output
        assert "JSON" in result.output
