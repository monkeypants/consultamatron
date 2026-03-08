"""Skill link manager tests.

The skill link manager enforces the generic/pipeline skill type
distinction as a protocol: generic skills (no skillset in metadata)
get symlinks in all agent directories; pipeline skills (skillset set)
do not.

Fixture cosmology: a consultant workspace with two skillsets and a
handful of skills. ``idea`` and ``review`` are generic control
surface skills — always in context. ``wm-research`` and ``wm-evolve``
belong to the wardley-mapping skillset — pipeline skills accessed
only through the CLI narrow waist.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AGENT_DIRS = [".agents/skills", ".claude/skills", ".gemini/skills", ".github/skills"]


def _write_skill(
    tmp_path: Path,
    location: str,
    name: str,
    *,
    skillset: str | None = None,
    description: str = "A skill.",
) -> Path:
    """Write a minimal valid SKILL.md at the given location within tmp_path."""
    skill_dir = tmp_path / location / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    meta = "  author: test\n  version: '0.1'\n  freedom: medium"
    if skillset is not None:
        meta += f"\n  skillset: {skillset}"
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\nmetadata:\n{meta}\n---\n"
    )
    return skill_dir


def _skill_link(tmp_path: Path, agent_dir: str, skill_name: str) -> Path:
    return tmp_path / agent_dir / skill_name


def _all_agent_dirs(tmp_path: Path) -> list[Path]:
    dirs = [tmp_path / d for d in AGENT_DIRS]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    return dirs


# ---------------------------------------------------------------------------
# SkillLinkManager protocol — structural contract
# ---------------------------------------------------------------------------


class TestSkillLinkManagerProtocol:
    """FilesystemSkillLinkManager satisfies the SkillLinkManager protocol."""

    def test_implements_protocol(self, tmp_path):
        """FilesystemSkillLinkManager is structurally compatible with SkillLinkManager."""
        from bin.cli.infrastructure.filesystem_skill_link_manager import (
            FilesystemSkillLinkManager,
        )
        from practice.repositories import SkillLinkManager

        _all_agent_dirs(tmp_path)
        mgr = FilesystemSkillLinkManager(tmp_path)
        assert isinstance(mgr, SkillLinkManager)

    def test_sync_returns_sync_result(self, tmp_path):
        """sync() returns a SyncResult with changed and unchanged counts."""
        from bin.cli.infrastructure.filesystem_skill_link_manager import (
            FilesystemSkillLinkManager,
        )

        _all_agent_dirs(tmp_path)
        mgr = FilesystemSkillLinkManager(tmp_path)
        result = mgr.sync()
        assert hasattr(result, "linked")
        assert hasattr(result, "unlinked")
        assert hasattr(result, "removed")
        assert hasattr(result, "ok")

    def test_status_returns_list_of_skill_link_status(self, tmp_path):
        """status() returns a list of SkillLinkStatus objects."""
        from bin.cli.infrastructure.filesystem_skill_link_manager import (
            FilesystemSkillLinkManager,
        )

        _all_agent_dirs(tmp_path)
        mgr = FilesystemSkillLinkManager(tmp_path)
        statuses = mgr.status()
        assert isinstance(statuses, list)


# ---------------------------------------------------------------------------
# SyncSkillLinksUseCase — generic skills get links
# ---------------------------------------------------------------------------


class TestSyncSkillLinksUseCaseLinksGeneric:
    """SyncSkillLinksUseCase creates symlinks for generic skills in all agent dirs.

    Rosalind is a consultant who has added an ``idea`` skill to her personal
    workspace. It has no skillset metadata — it is a generic control surface
    command she wants available in every agent context.
    """

    def test_creates_symlinks_for_generic_skill_in_all_agent_dirs(self, tmp_path):
        """A generic skill gets a symlink in each agent directory."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())

        for agent_dir in AGENT_DIRS:
            link = _skill_link(tmp_path, agent_dir, "idea")
            assert link.is_symlink(), f"Expected symlink at {link}"
            assert link.resolve().exists(), f"Symlink at {link} is broken"

    def test_generic_skill_link_points_to_skill_dir(self, tmp_path):
        """The symlink points to the directory containing SKILL.md, not the file."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        skill_dir = _write_skill(tmp_path, "skills", "review")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())

        link = _skill_link(tmp_path, ".agents/skills", "review")
        assert link.resolve() == skill_dir.resolve()

    def test_is_idempotent(self, tmp_path):
        """Running sync twice produces the same result — no duplicate or broken links."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())
        uc.execute(SyncSkillLinksRequest())

        link = _skill_link(tmp_path, ".agents/skills", "idea")
        assert link.is_symlink()
        assert link.resolve().exists()


# ---------------------------------------------------------------------------
# SyncSkillLinksUseCase — pipeline skills are unlinked
# ---------------------------------------------------------------------------


class TestSyncSkillLinksUseCaseUnlinksPipeline:
    """SyncSkillLinksUseCase removes symlinks for pipeline skills.

    The wardley-mapping skillset contains ``wm-research`` and ``wm-evolve``.
    These are pipeline skills — they belong to a bounded context and must
    only be accessed through the CLI narrow waist. Any stale symlinks for
    them must be removed from agent directories.
    """

    def test_does_not_create_symlinks_for_pipeline_skill(self, tmp_path):
        """A pipeline skill gets no symlink in any agent directory."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(
            tmp_path,
            "commons/monkeypants/wm/skillsets/wardley_mapping/skills",
            "wm-research",
            skillset="wardley-mapping",
        )
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())

        for agent_dir in AGENT_DIRS:
            link = _skill_link(tmp_path, agent_dir, "wm-research")
            assert not link.exists(), f"Unexpected link at {link}"

    def test_removes_stale_pipeline_symlinks(self, tmp_path):
        """Existing stale symlinks for pipeline skills are removed."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        skill_dir = _write_skill(
            tmp_path,
            "commons/monkeypants/wm/skillsets/wardley_mapping/skills",
            "wm-evolve",
            skillset="wardley-mapping",
        )
        _all_agent_dirs(tmp_path)

        # Manually create a stale symlink (as if the old bash script ran first)
        stale_link = tmp_path / ".agents/skills/wm-evolve"
        stale_link.symlink_to(skill_dir)
        assert stale_link.exists()

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())

        assert not stale_link.exists(), "Stale pipeline symlink was not removed"

    def test_removes_broken_symlinks(self, tmp_path):
        """Broken symlinks (pointing to nonexistent targets) are removed."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _all_agent_dirs(tmp_path)

        # Create a broken symlink in .agents/skills
        broken_link = tmp_path / ".agents/skills/ghost-skill"
        broken_link.symlink_to(tmp_path / "skills/ghost-skill")
        assert not broken_link.resolve().exists()

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())

        assert not broken_link.exists(), "Broken symlink was not removed"


# ---------------------------------------------------------------------------
# SyncSkillLinksUseCase — dry run
# ---------------------------------------------------------------------------


class TestSyncSkillLinksUseCaseDryRun:
    """Dry-run mode reports changes without modifying the filesystem."""

    def test_dry_run_reports_generic_skill_as_linked(self, tmp_path):
        """Dry run reports a generic skill would be linked."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        result = uc.execute(SyncSkillLinksRequest(dry_run=True))

        assert len(result.linked) > 0

    def test_dry_run_does_not_modify_filesystem(self, tmp_path):
        """Dry run leaves no symlinks on disk."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest(dry_run=True))

        link = _skill_link(tmp_path, ".agents/skills", "idea")
        assert not link.exists(), "Dry run should not create symlinks"


# ---------------------------------------------------------------------------
# SyncSkillLinksUseCase — SyncResult structure
# ---------------------------------------------------------------------------


class TestSyncResult:
    """SyncResult captures what changed."""

    def test_linked_entry_reports_generic_skill(self, tmp_path):
        """linked contains skill names that received new symlinks."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        result = uc.execute(SyncSkillLinksRequest())

        names = {e.skill for e in result.linked}
        assert "idea" in names

    def test_ok_entry_reports_already_linked_skill(self, tmp_path):
        """ok contains skill names whose links were already correct."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())  # first run links
        result = uc.execute(SyncSkillLinksRequest())  # second run: already ok

        names = {e.skill for e in result.ok}
        assert "idea" in names

    def test_unlinked_entry_reports_pipeline_skill_with_stale_link(self, tmp_path):
        """unlinked contains pipeline skill names whose stale links were removed."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        skill_dir = _write_skill(
            tmp_path,
            "commons/monkeypants/wm/skillsets/wardley_mapping/skills",
            "wm-research",
            skillset="wardley-mapping",
        )
        agent_dirs = _all_agent_dirs(tmp_path)

        # Plant a stale link
        stale = agent_dirs[0] / "wm-research"
        stale.symlink_to(skill_dir)

        uc = SyncSkillLinksUseCase(tmp_path)
        result = uc.execute(SyncSkillLinksRequest())

        names = {e.skill for e in result.unlinked}
        assert "wm-research" in names


# ---------------------------------------------------------------------------
# GetSkillLinkStatusUseCase — reporting
# ---------------------------------------------------------------------------


class TestGetSkillLinkStatusUseCase:
    """GetSkillLinkStatusUseCase reports the current link state for all skills.

    Tomas is debugging which skills are in which agent directories.
    He runs ``practice skill link status`` to see a per-skill report
    without modifying anything.
    """

    def test_reports_generic_skill_as_linked_when_links_exist(self, tmp_path):
        """A generic skill with correct symlinks is reported as linked."""
        from bin.cli.usecases import (
            GetSkillLinkStatusUseCase,
            SkillLinkStatusRequest,
            SyncSkillLinksUseCase,
            SyncSkillLinksRequest,
        )

        _write_skill(tmp_path, "skills", "idea")
        _all_agent_dirs(tmp_path)

        # Sync first to create links
        SyncSkillLinksUseCase(tmp_path).execute(SyncSkillLinksRequest())

        uc = GetSkillLinkStatusUseCase(tmp_path)
        resp = uc.execute(SkillLinkStatusRequest())

        idea_status = next((s for s in resp.statuses if s.skill == "idea"), None)
        assert idea_status is not None
        assert idea_status.skill_type == "generic"
        assert idea_status.linked is True

    def test_reports_pipeline_skill_as_not_linked(self, tmp_path):
        """A pipeline skill is reported as not linked (correct state)."""
        from bin.cli.usecases import (
            GetSkillLinkStatusUseCase,
            SkillLinkStatusRequest,
        )

        _write_skill(
            tmp_path,
            "commons/monkeypants/wm/skillsets/wardley_mapping/skills",
            "wm-research",
            skillset="wardley-mapping",
        )
        _all_agent_dirs(tmp_path)

        uc = GetSkillLinkStatusUseCase(tmp_path)
        resp = uc.execute(SkillLinkStatusRequest())

        wm_status = next((s for s in resp.statuses if s.skill == "wm-research"), None)
        assert wm_status is not None
        assert wm_status.skill_type == "pipeline"
        assert wm_status.linked is False

    def test_reports_generic_skill_as_not_linked_when_links_absent(self, tmp_path):
        """A generic skill with no links is reported as linked=False (incorrect state)."""
        from bin.cli.usecases import (
            GetSkillLinkStatusUseCase,
            SkillLinkStatusRequest,
        )

        _write_skill(tmp_path, "skills", "review")
        _all_agent_dirs(tmp_path)

        uc = GetSkillLinkStatusUseCase(tmp_path)
        resp = uc.execute(SkillLinkStatusRequest())

        review_status = next((s for s in resp.statuses if s.skill == "review"), None)
        assert review_status is not None
        assert review_status.skill_type == "generic"
        assert review_status.linked is False


# ---------------------------------------------------------------------------
# Doctrine: generic skills have links, pipeline skills do not
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestSkillLinkDoctrine:
    """Structural invariants for the generic/pipeline skill distinction.

    These tests verify the protocol obligation: every generic skill
    must be linked; no pipeline skill may be linked.
    """

    def test_all_agent_dirs_contain_only_generic_skills(self, tmp_path):
        """After sync, agent dirs contain exactly the generic skills — no pipeline skills."""
        from bin.cli.usecases import SyncSkillLinksUseCase, SyncSkillLinksRequest

        _write_skill(tmp_path, "skills", "idea")
        _write_skill(tmp_path, "skills", "review")
        _write_skill(
            tmp_path,
            "commons/monkeypants/wm/skillsets/wardley_mapping/skills",
            "wm-research",
            skillset="wardley-mapping",
        )
        _all_agent_dirs(tmp_path)

        uc = SyncSkillLinksUseCase(tmp_path)
        uc.execute(SyncSkillLinksRequest())

        for agent_dir in AGENT_DIRS:
            dir_path = tmp_path / agent_dir
            linked_names = {p.name for p in dir_path.iterdir() if p.is_symlink()}
            assert "idea" in linked_names
            assert "review" in linked_names
            assert "wm-research" not in linked_names

    def test_sync_then_status_shows_consistent_state(self, tmp_path):
        """After sync, status reports correct linked/unlinked state for all skills."""
        from bin.cli.usecases import (
            GetSkillLinkStatusUseCase,
            SkillLinkStatusRequest,
            SyncSkillLinksUseCase,
            SyncSkillLinksRequest,
        )

        _write_skill(tmp_path, "skills", "idea")
        _write_skill(
            tmp_path,
            "commons/monkeypants/wm/skillsets/wardley_mapping/skills",
            "wm-research",
            skillset="wardley-mapping",
        )
        _all_agent_dirs(tmp_path)

        SyncSkillLinksUseCase(tmp_path).execute(SyncSkillLinksRequest())
        resp = GetSkillLinkStatusUseCase(tmp_path).execute(SkillLinkStatusRequest())

        statuses = {s.skill: s for s in resp.statuses}
        assert statuses["idea"].linked is True
        assert statuses["wm-research"].linked is False
