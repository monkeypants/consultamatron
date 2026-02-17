"""Conformance tests — bounded-context protocol obligations.

These tests verify that skillsets compose correctly with the engagement
lifecycle layer (the semantic waist). They run under the ``doctrine``
marker, which is the pre-push gate defined in CLAUDE.md.

Conformance properties:
  1. Pipeline coherence — structural validation of implemented skillset pipelines
  2. Decision-title join — the fragile string join that drives progress
  3. Entity round-trip — JSON serialisation fidelity for all entities
  4. Skillset discipline — field-level validation for all skillsets
  5. BC test ownership — implemented BCs own their test infrastructure
  6. Protocol smoke tests — runtime verification of BC plugin contracts
  7. Skill file conformance — SKILL.md files match agentskills.io spec
"""

from __future__ import annotations

import importlib
import os
import re
from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from practice.bc_discovery import discover_all_bc_modules
from consulting.dtos import (
    CreateEngagementRequest,
    GetProjectProgressRequest,
    InitializeWorkspaceRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
)
from practice.discovery import PipelineStage
from practice.entities import Skillset

from .conftest import (
    make_decision,
    make_engagement,
    make_engagement_dashboard,
    make_next_action,
    make_pipeline_position,
    make_profile,
    make_project,
    make_prospectus,
    make_research,
    make_skillset,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT = "conformance-corp"


_BC_MODULES = discover_all_bc_modules(_REPO_ROOT)
_ALL_SKILLSETS: list[Skillset] = [s for mod in _BC_MODULES for s in mod.SKILLSETS]
_IMPLEMENTED = [s for s in _ALL_SKILLSETS if s.is_implemented]
_IMPLEMENTED_DICTS = [s.model_dump(mode="json") for s in _IMPLEMENTED]
_IMPLEMENTED_IDS = [s["name"] for s in _IMPLEMENTED_DICTS]

_ALL_DICTS = [s.model_dump(mode="json") for s in _ALL_SKILLSETS]
_ALL_IDS = [s["name"] for s in _ALL_DICTS]


def _tmp_config(tmp_path: Path) -> Config:
    """Config with real repo_root for BC discovery, temp workspace for isolation."""
    return Config(
        repo_root=_REPO_ROOT,
        workspace_root=tmp_path / "clients",
        skillsets_root=tmp_path / "skillsets",
    )


# ---------------------------------------------------------------------------
# 1. Pipeline coherence (implemented skillsets only)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPipelineCoherence:
    """Structural validation of implemented skillset pipeline definitions."""

    @pytest.mark.parametrize("skillset", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_non_empty(self, skillset):
        assert len(skillset["pipeline"]) >= 1

    @pytest.mark.parametrize("skillset", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_monotonic_order(self, skillset):
        orders = [s["order"] for s in skillset["pipeline"]]
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Stage order not strictly ascending: {orders}"
            )

    @pytest.mark.parametrize("skillset", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_gate_chaining(self, skillset):
        stages = skillset["pipeline"]
        for i in range(1, len(stages)):
            assert stages[i]["prerequisite_gate"] == stages[i - 1]["produces_gate"], (
                f"Stage {stages[i]['order']} prerequisite "
                f"({stages[i]['prerequisite_gate']}) != "
                f"stage {stages[i - 1]['order']} produces "
                f"({stages[i - 1]['produces_gate']})"
            )

    @pytest.mark.parametrize("skillset", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_unique_descriptions(self, skillset):
        descriptions = [s["description"] for s in skillset["pipeline"]]
        assert len(descriptions) == len(set(descriptions)), (
            f"Duplicate descriptions in {skillset['name']}: {descriptions}"
        )

    @pytest.mark.parametrize("skillset", _ALL_DICTS, ids=_ALL_IDS)
    def test_slug_pattern_valid(self, skillset):
        assert "{n}" in skillset["slug_pattern"], (
            f"slug_pattern missing {{n}} placeholder: {skillset['slug_pattern']}"
        )

    @pytest.mark.parametrize("skillset", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_gate_consumes_declared(self, skillset):
        """Stages with a prerequisite gate must declare what they consume."""
        for stage in skillset["pipeline"]:
            if stage["prerequisite_gate"]:
                assert stage.get("consumes"), (
                    f"Stage {stage['order']} ({stage['skill']}) in "
                    f"{skillset['name']} has prerequisite_gate but no consumes"
                )


# ---------------------------------------------------------------------------
# 2. Decision-title join (implemented skillsets only)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestDecisionTitleJoin:
    """The string-equality join between DecisionEntry.title and
    PipelineStage.description that drives GetProjectProgressUseCase.
    """

    @pytest.mark.parametrize("skillset", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_progress_advances_through_all_stages(self, skillset, tmp_path):
        di = Container(_tmp_config(tmp_path))

        # Initialize workspace, create engagement, and register project
        di.initialize_workspace_usecase.execute(
            InitializeWorkspaceRequest(client=CLIENT)
        )
        di.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-1")
        )
        slug = skillset["slug_pattern"].replace("{n}", "1")
        di.register_project_usecase.execute(
            RegisterProjectRequest(
                client=CLIENT,
                engagement="strat-1",
                slug=slug,
                skillset=skillset["name"],
                scope="Conformance test",
            )
        )

        stages = skillset["pipeline"]

        # Walk through each stage, recording a decision with the matching title
        for i, stage in enumerate(stages):
            di.record_decision_usecase.execute(
                RecordDecisionRequest(
                    client=CLIENT,
                    engagement="strat-1",
                    project_slug=slug,
                    title=stage["description"],
                    fields={},
                )
            )

            resp = di.get_project_progress_usecase.execute(
                GetProjectProgressRequest(
                    client=CLIENT, engagement="strat-1", project_slug=slug
                )
            )

            completed = [s for s in resp.stages if s.completed]
            assert len(completed) == i + 1, (
                f"After recording '{stage['description']}', "
                f"expected {i + 1} completed stages, got {len(completed)}"
            )

            # After the last stage, current_stage should be None (all done)
            if i == len(stages) - 1:
                assert resp.current_stage is None
            else:
                assert resp.current_stage == stages[i + 1]["skill"]


# ---------------------------------------------------------------------------
# 3. Entity round-trip
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestEntityRoundTrip:
    """JSON round-trip fidelity for all entity types."""

    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(make_project(), id="Project"),
            pytest.param(make_decision(), id="DecisionEntry"),
            pytest.param(make_engagement(), id="EngagementEntry"),
            pytest.param(make_research(), id="ResearchTopic"),
            pytest.param(make_skillset(), id="Skillset"),
            pytest.param(make_prospectus(), id="Skillset-prospectus"),
            pytest.param(make_profile(), id="Profile"),
            pytest.param(make_pipeline_position(), id="ProjectPipelinePosition"),
            pytest.param(make_engagement_dashboard(), id="EngagementDashboard"),
            pytest.param(make_next_action(), id="NextAction"),
            pytest.param(
                PipelineStage(
                    order=1,
                    skill="test",
                    prerequisite_gate="a",
                    produces_gate="b",
                    description="Test",
                ),
                id="PipelineStage",
            ),
        ],
    )
    def test_json_round_trip(self, entity):
        dumped = entity.model_dump(mode="json")
        restored = type(entity).model_validate(dumped)
        assert restored == entity


# ---------------------------------------------------------------------------
# 5. Skillset discipline — field-level validation for all skillsets
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestSkillsetDiscipline:
    """Every skillset (implemented or prospectus) must declare required fields."""

    @pytest.mark.parametrize("skillset", _ALL_DICTS, ids=_ALL_IDS)
    def test_has_name(self, skillset):
        assert skillset["name"], "Skillset must have a non-empty name"

    @pytest.mark.parametrize("skillset", _ALL_DICTS, ids=_ALL_IDS)
    def test_has_display_name(self, skillset):
        assert skillset["display_name"], "Skillset must have a non-empty display_name"

    @pytest.mark.parametrize("skillset", _ALL_DICTS, ids=_ALL_IDS)
    def test_has_description(self, skillset):
        assert skillset["description"], "Skillset must have a non-empty description"

    @pytest.mark.parametrize("skillset", _ALL_DICTS, ids=_ALL_IDS)
    def test_name_is_kebab_case(self, skillset):
        import re

        assert re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", skillset["name"]), (
            f"Skillset name must be kebab-case: {skillset['name']}"
        )

    @pytest.mark.parametrize("skillset", _ALL_DICTS, ids=_ALL_IDS)
    def test_unique_names(self, skillset):
        """Each skillset name appears exactly once across all BCs."""
        count = sum(1 for s in _ALL_DICTS if s["name"] == skillset["name"])
        assert count == 1, f"Skillset name {skillset['name']!r} appears {count} times"


@pytest.mark.doctrine
class TestSkillsetRegistration:
    """Directory scanning discovers all BC packages."""

    def test_directory_scanning_finds_all_skillsets(self):
        """discover_all_bc_modules finds the same skillsets as direct import."""
        from bin.cli.infrastructure.code_skillset_repository import (
            CodeSkillsetRepository,
        )

        repo = CodeSkillsetRepository(_REPO_ROOT)
        discovered_names = {s.name for s in repo.list_all()}
        expected_names = {s.name for s in _ALL_SKILLSETS}
        assert discovered_names == expected_names, (
            f"Discovery mismatch: found {discovered_names}, expected {expected_names}"
        )


@pytest.mark.doctrine
class TestBoundedContextTestOwnership:
    """Implemented BCs must own their test infrastructure."""

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_implemented_bc_has_test_directory(self, mod):
        if not any(s.is_implemented for s in mod.SKILLSETS):
            pytest.skip("Prospectus-only BC")
        bc_dir = Path(mod.__file__).parent
        assert (bc_dir / "tests" / "__init__.py").is_file()

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_implemented_bc_has_presenter_test(self, mod):
        if not any(s.is_implemented for s in mod.SKILLSETS):
            pytest.skip("Prospectus-only BC")
        bc_dir = Path(mod.__file__).parent
        assert (bc_dir / "tests" / "test_presenter.py").is_file()

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_implemented_bc_has_presenter_factory(self, mod):
        if not any(s.is_implemented for s in mod.SKILLSETS):
            pytest.skip("Prospectus-only BC")
        assert hasattr(mod, "PRESENTER_FACTORY")


# ---------------------------------------------------------------------------
# 6. Protocol smoke tests — runtime verification of BC plugin contracts
# ---------------------------------------------------------------------------


_IMPLEMENTED_MODULES = [
    m for m in _BC_MODULES if any(s.is_implemented for s in m.SKILLSETS)
]


@pytest.mark.doctrine
class TestPresenterProtocol:
    """PRESENTER_FACTORY produces a working ProjectPresenter."""

    @pytest.mark.parametrize(
        "mod", _IMPLEMENTED_MODULES, ids=[m.__name__ for m in _IMPLEMENTED_MODULES]
    )
    def test_presenter_returns_project_contribution(self, mod, tmp_path):
        from datetime import date

        from practice.content import ProjectContribution
        from practice.entities import Project, ProjectStatus

        factory = mod.PRESENTER_FACTORY
        entries = factory if isinstance(factory, list) else [factory]
        for skillset_name, create_fn in entries:
            presenter = create_fn(tmp_path, _REPO_ROOT)

            project = Project(
                slug="smoke-1",
                client="smoke-corp",
                engagement="strat-1",
                skillset=skillset_name,
                status=ProjectStatus.ELABORATION,
                created=date(2025, 6, 1),
            )
            result = presenter.present(project)
            assert isinstance(result, ProjectContribution)
            assert result.skillset == skillset_name


@pytest.mark.doctrine
class TestServiceRegistrationProtocol:
    """register_services() hooks run without error."""

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_register_services_callable(self, mod, tmp_path):
        register = getattr(mod, "register_services", None)
        if register is None:
            pytest.skip("No register_services hook")
        container = Container(_tmp_config(tmp_path))
        # Should not raise
        register(container)


@pytest.mark.doctrine
class TestCliRegistrationProtocol:
    """BC CLI modules register commands without error."""

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_cli_register_commands(self, mod):
        import click

        try:
            cli_mod = importlib.import_module(f"{mod.__name__}.cli")
        except (ImportError, ModuleNotFoundError):
            pytest.skip("No CLI module")
        group = click.Group("test")
        cli_mod.register_commands(group)
        assert len(group.commands) > 0, (
            f"{mod.__name__}.cli.register_commands added no commands"
        )


# ---------------------------------------------------------------------------
# 7. Skill file conformance — agentskills.io spec
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z][a-z0-9]*)*$")


def _parse_skill_frontmatter(skill_md_path: Path) -> dict:
    """Parse YAML frontmatter from a SKILL.md file.

    Minimal parser — handles flat ``key: value`` pairs and the YAML
    ``>`` folded-scalar continuation used for descriptions.  No
    external YAML dependency required.
    """
    text = skill_md_path.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    result = {}
    current_key = None
    folding = False
    fold_lines: list[str] = []

    for line in parts[1].splitlines():
        stripped = line.strip()
        if not stripped:
            if folding:
                fold_lines.append("")
            continue

        # Indented continuation of a folded scalar
        if folding and line[0] in (" ", "\t"):
            fold_lines.append(stripped)
            continue

        # Flush any accumulated folded text
        if folding:
            result[current_key] = " ".join(ln for ln in fold_lines if ln)
            folding = False
            fold_lines = []

        if ":" not in stripped:
            continue

        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()

        if value == ">":
            current_key = key
            folding = True
            fold_lines = []
        elif value:
            result[key] = value
        else:
            result[key] = ""

    # Flush trailing folded scalar
    if folding:
        result[current_key] = " ".join(ln for ln in fold_lines if ln)

    return result


def _discover_skill_dirs():
    """Return list of (name, resolved_path) for all skill directories."""
    skills_dir = _REPO_ROOT / ".claude" / "skills"
    results = []
    if not skills_dir.is_dir():
        return results
    for entry in sorted(skills_dir.iterdir()):
        skill_md = entry / "SKILL.md"
        if skill_md.is_file():
            results.append((entry.name, entry.resolve()))
    return results


def _discover_pipeline_skills():
    """Return sorted list of skill names referenced by implemented pipelines."""
    names = set()
    for skillset in _IMPLEMENTED:
        for stage in skillset.pipeline:
            names.add(stage.skill)
    return sorted(names)


def _discover_bash_scripts():
    """Return list of (skill_name, script_path) for all scripts/ entries."""
    results = []
    for name, skill_dir in _discover_skill_dirs():
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.is_dir():
            continue
        for script in sorted(scripts_dir.iterdir()):
            if script.suffix == ".sh" and script.is_file():
                results.append((name, script))
    return results


_SKILL_DIRS = _discover_skill_dirs()
_SKILL_DIR_IDS = [name for name, _ in _SKILL_DIRS]
_PIPELINE_SKILLS = _discover_pipeline_skills()
_BASH_SCRIPTS = _discover_bash_scripts()
_BASH_SCRIPT_IDS = [f"{name}/{p.name}" for name, p in _BASH_SCRIPTS]


@pytest.mark.doctrine
class TestSkillFileConformance:
    """Skill files conform to agentskills.io specification."""

    # --- SKILL.md existence and structure ---

    @pytest.mark.parametrize("skill_name", _PIPELINE_SKILLS)
    def test_pipeline_skill_has_skill_file(self, skill_name):
        """Every pipeline stage has a discoverable SKILL.md."""
        skills_dir = _REPO_ROOT / ".claude" / "skills"
        if not skills_dir.is_dir() or not any(skills_dir.iterdir()):
            pytest.skip(
                "No .claude/skills/ symlinks (regenerate with maintain-symlinks.sh)"
            )
        skill_dir = skills_dir / skill_name
        assert skill_dir.exists(), f"No .claude/skills/{skill_name} directory/symlink"
        assert (skill_dir / "SKILL.md").is_file(), (
            f".claude/skills/{skill_name}/SKILL.md missing"
        )

    @pytest.mark.parametrize("skill_dir", _SKILL_DIRS, ids=_SKILL_DIR_IDS)
    def test_name_matches_directory(self, skill_dir):
        """SKILL.md name field matches parent directory name."""
        dir_name, path = skill_dir
        fm = _parse_skill_frontmatter(path / "SKILL.md")
        assert "name" in fm, f"No name in frontmatter: {path / 'SKILL.md'}"
        assert fm["name"] == dir_name, (
            f"Frontmatter name {fm['name']!r} != directory name {dir_name!r}"
        )

    @pytest.mark.parametrize("skill_dir", _SKILL_DIRS, ids=_SKILL_DIR_IDS)
    def test_name_format(self, skill_dir):
        """name is <=64 chars, lowercase/hyphens, no leading/trailing/consecutive hyphens."""
        _, path = skill_dir
        fm = _parse_skill_frontmatter(path / "SKILL.md")
        name = fm.get("name", "")
        assert name, f"Empty name in {path / 'SKILL.md'}"
        assert len(name) <= 64, f"Name {name!r} exceeds 64 chars ({len(name)})"
        assert _NAME_RE.match(name), (
            f"Name {name!r} does not match pattern ^[a-z][a-z0-9]*(-[a-z][a-z0-9]*)*$"
        )

    @pytest.mark.parametrize("skill_dir", _SKILL_DIRS, ids=_SKILL_DIR_IDS)
    def test_description_length(self, skill_dir):
        """description is <=1024 characters and non-empty."""
        _, path = skill_dir
        fm = _parse_skill_frontmatter(path / "SKILL.md")
        desc = fm.get("description", "")
        assert desc, f"Empty description in {path / 'SKILL.md'}"
        assert len(desc) <= 1024, (
            f"Description exceeds 1024 chars ({len(desc)}): {path / 'SKILL.md'}"
        )

    @pytest.mark.parametrize("skill_dir", _SKILL_DIRS, ids=_SKILL_DIR_IDS)
    def test_line_count(self, skill_dir):
        """SKILL.md is under 500 lines."""
        _, path = skill_dir
        skill_md = path / "SKILL.md"
        line_count = len(skill_md.read_text().splitlines())
        assert line_count < 500, f"{skill_md} has {line_count} lines (limit 500)"

    # --- Bash wrappers ---

    @pytest.mark.parametrize("script_entry", _BASH_SCRIPTS, ids=_BASH_SCRIPT_IDS)
    def test_bash_scripts_executable(self, script_entry):
        """Recording scripts are executable."""
        _, script_path = script_entry
        mode = os.stat(script_path).st_mode
        assert mode & 0o111, f"{script_path} is not executable"

    # --- Pipeline-specific checks ---

    @pytest.mark.parametrize("skill_name", _PIPELINE_SKILLS)
    def test_frontmatter_name_matches_pipeline_skill(self, skill_name):
        """SKILL.md name field matches the pipeline stage skill field."""
        skill_md = _REPO_ROOT / ".claude" / "skills" / skill_name / "SKILL.md"
        if not skill_md.is_file():
            pytest.skip(f"No SKILL.md for {skill_name}")
        fm = _parse_skill_frontmatter(skill_md)
        assert fm.get("name") == skill_name, (
            f"Frontmatter name {fm.get('name')!r} != pipeline skill {skill_name!r}"
        )
