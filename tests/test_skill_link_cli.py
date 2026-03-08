"""CLI tests for ``practice skill link`` commands.

``practice skill link sync`` replaces ``bin/maintain-symlinks.sh``.
``practice skill link status`` shows which skills are linked and why.

Fixture cosmology: Amara is a consultant configuring her environment.
She has an ``idea`` skill (generic, should be linked everywhere) and
``wm-research`` (pipeline, must not appear in agent directories).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner


AGENT_DIRS = [".agents/skills", ".claude/skills", ".gemini/skills", ".github/skills"]


def _write_skill(
    root: Path,
    location: str,
    name: str,
    *,
    skillset: str | None = None,
) -> None:
    skill_dir = root / location / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    meta = "  author: amara\n  version: '0.1'\n  freedom: medium"
    if skillset is not None:
        meta += f"\n  skillset: {skillset}"
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: A skill.\nmetadata:\n{meta}\n---\n"
    )


def _setup_agent_dirs(root: Path) -> None:
    for d in AGENT_DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)


@pytest.fixture
def isolated_run(tmp_path, monkeypatch):
    """Invoke CLI commands against an isolated tmp_path repo root.

    Does not require BC packages — skill link commands discover skills
    from the filesystem directly without needing installed BC modules.
    """
    from bin.cli.main import cli
    from bin.cli.config import Config

    config = Config(
        repo_root=tmp_path,
        workspace_root=tmp_path / "clients",
    )
    monkeypatch.setattr(
        "bin.cli.main.Config",
        type(
            "Config",
            (),
            {"from_repo_root": staticmethod(lambda _: config)},
        ),
    )
    runner = CliRunner()
    return lambda *args: runner.invoke(cli, list(args)), tmp_path


class TestSkillLinkSyncCommand:
    """``practice skill link sync`` creates/removes symlinks based on skill type."""

    def test_sync_exits_zero(self, isolated_run):
        """skill link sync exits 0 on a clean run."""
        run, repo_root = isolated_run
        _write_skill(repo_root, "skills", "idea")
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "sync")
        assert result.exit_code == 0, result.output

    def test_sync_reports_linked_generic_skill(self, isolated_run):
        """skill link sync reports a generic skill as linked."""
        run, repo_root = isolated_run
        _write_skill(repo_root, "skills", "idea")
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "sync")
        assert "idea" in result.output
        assert "linked" in result.output.lower()

    def test_sync_dry_run_does_not_create_links(self, isolated_run):
        """skill link sync --dry-run reports without modifying the filesystem."""
        run, repo_root = isolated_run
        _write_skill(repo_root, "skills", "idea")
        _setup_agent_dirs(repo_root)
        run("skill", "link", "sync", "--dry-run")
        link = repo_root / ".agents/skills/idea"
        assert not link.exists(), "Dry run should not create symlinks"

    def test_sync_dry_run_exits_zero(self, isolated_run):
        """skill link sync --dry-run exits 0."""
        run, repo_root = isolated_run
        _write_skill(repo_root, "skills", "idea")
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "sync", "--dry-run")
        assert result.exit_code == 0, result.output

    def test_sync_creates_symlinks_for_generic_skill(self, isolated_run):
        """skill link sync creates actual symlinks for generic skills."""
        run, repo_root = isolated_run
        _write_skill(repo_root, "skills", "idea")
        _setup_agent_dirs(repo_root)
        run("skill", "link", "sync")
        link = repo_root / ".agents/skills/idea"
        assert link.is_symlink(), "Expected symlink in .agents/skills/"

    def test_sync_removes_stale_pipeline_link_and_reports_it(self, isolated_run):
        """skill link sync removes stale links for pipeline skills and reports it."""
        run, repo_root = isolated_run
        skill_dir = repo_root / "commons/mp/wm/skillsets/wm/skills/wm-research"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: wm-research\ndescription: Research.\n"
            "metadata:\n  author: mp\n  version: '0.1'\n  freedom: medium\n"
            "  skillset: wardley-mapping\n---\n"
        )
        _setup_agent_dirs(repo_root)

        # Plant a stale link as if the old bash script ran first
        stale = repo_root / ".agents/skills/wm-research"
        stale.symlink_to(skill_dir)

        result = run("skill", "link", "sync")
        assert result.exit_code == 0, result.output
        assert not stale.exists(), "Stale pipeline link not removed"


class TestSkillLinkStatusCommand:
    """``practice skill link status`` reports current link state."""

    def test_status_exits_zero(self, isolated_run):
        """skill link status exits 0."""
        run, repo_root = isolated_run
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "status")
        assert result.exit_code == 0, result.output

    def test_status_reports_generic_skill_type(self, isolated_run):
        """status output labels generic skills as generic."""
        run, repo_root = isolated_run
        _write_skill(repo_root, "skills", "idea")
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "status")
        assert result.exit_code == 0
        assert "idea" in result.output
        assert "generic" in result.output.lower()

    def test_status_reports_pipeline_skill_type(self, isolated_run):
        """status output labels pipeline skills as pipeline."""
        run, repo_root = isolated_run
        _write_skill(
            repo_root,
            "commons/mp/wm/skillsets/wm/skills",
            "wm-research",
            skillset="wardley-mapping",
        )
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "status")
        assert result.exit_code == 0
        assert "wm-research" in result.output
        assert "pipeline" in result.output.lower()

    def test_status_no_skills_reports_empty(self, isolated_run):
        """status with no skills exits cleanly."""
        run, repo_root = isolated_run
        _setup_agent_dirs(repo_root)
        result = run("skill", "link", "status")
        assert result.exit_code == 0
