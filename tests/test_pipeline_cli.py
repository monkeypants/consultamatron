"""CLI tests for ``practice pipeline`` commands.

``practice pipeline list`` lists all pipelines for a skillset.
``practice pipeline show`` shows details of one pipeline's stages.

Fixture cosmology: the Holloway Group engagement from test_cli.py.
They have registered a wardley-mapping project. The wardley-mapping
skillset declares pipelines for the multi-pipeline use case.
"""

from __future__ import annotations


CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


def _init(run):
    return run("project", "init", "--client", CLIENT)


def _create_engagement(run, slug=ENGAGEMENT):
    return run("engagement", "create", "--client", CLIENT, "--slug", slug)


def _register(run, slug="maps-1", pipeline="wardley-mapping"):
    _init(run)
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
        "--pipeline",
        pipeline,
        "--scope",
        "Freight operations",
    )


class TestPipelineListCommand:
    """``practice pipeline list`` returns pipelines for a skillset."""

    def test_pipeline_list_exits_zero(self, run):
        """pipeline list exits 0 for a known skillset."""
        result = run("pipeline", "list", "--skillset", "wardley-mapping")
        assert result.exit_code == 0, result.output

    def test_pipeline_list_shows_skillset_pipelines(self, run):
        """pipeline list shows pipeline names for the given skillset."""
        result = run("pipeline", "list", "--skillset", "wardley-mapping")
        assert "wardley-mapping" in result.output

    def test_pipeline_list_unknown_skillset_exits_one(self, run):
        """pipeline list exits 1 for an unknown skillset."""
        result = run("pipeline", "list", "--skillset", "no-such-skillset")
        assert result.exit_code == 1

    def test_pipeline_list_requires_skillset_option(self, run):
        """pipeline list exits non-zero when --skillset is omitted."""
        result = run("pipeline", "list")
        assert result.exit_code != 0


class TestPipelineShowCommand:
    """``practice pipeline show`` shows stages for one pipeline."""

    def test_pipeline_show_exits_zero(self, run):
        """pipeline show exits 0 for a known pipeline."""
        result = run(
            "pipeline",
            "show",
            "--skillset",
            "wardley-mapping",
            "--pipeline",
            "wardley-mapping",
        )
        assert result.exit_code == 0, result.output

    def test_pipeline_show_displays_stages(self, run):
        """pipeline show includes stage information."""
        result = run(
            "pipeline",
            "show",
            "--skillset",
            "wardley-mapping",
            "--pipeline",
            "wardley-mapping",
        )
        assert result.exit_code == 0
        # Should contain at least one stage
        assert result.output.strip() != ""

    def test_pipeline_show_unknown_skillset_exits_one(self, run):
        """pipeline show exits 1 for an unknown skillset."""
        result = run(
            "pipeline",
            "show",
            "--skillset",
            "no-such-skillset",
            "--pipeline",
            "create",
        )
        assert result.exit_code == 1

    def test_pipeline_show_unknown_pipeline_exits_one(self, run):
        """pipeline show exits 1 for an unknown pipeline."""
        result = run(
            "pipeline",
            "show",
            "--skillset",
            "wardley-mapping",
            "--pipeline",
            "no-such-pipeline",
        )
        assert result.exit_code == 1
