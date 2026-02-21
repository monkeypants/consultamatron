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
from practice.entities import SkillManifest
from practice.frontmatter import parse_frontmatter
from bin.cli.dtos import (
    CreateEngagementRequest,
    GetProjectProgressRequest,
    InitializeWorkspaceRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
)
from practice.bc_discovery import _get_pipelines
from practice.discovery import PipelineStage
from practice.entities import CompilationState, Pipeline

from .conftest import (
    make_decision,
    make_engagement_entry,
    make_engagement_dashboard,
    make_item_freshness,
    make_knowledge_pack,
    make_next_action,
    make_observation,
    make_observation_need,
    make_pack_freshness,
    make_pipeline,
    make_pipeline_position,
    make_profile,
    make_project,
    make_prospectus,
    make_research,
    make_routing_allow_list,
    make_routing_destination,
    make_skill_manifest,
    make_skillset,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent
CLIENT = "conformance-corp"


_BC_MODULES = discover_all_bc_modules(_REPO_ROOT)
_ALL_PIPELINES: list[Pipeline] = [p for mod in _BC_MODULES for p in _get_pipelines(mod)]
_IMPLEMENTED = [p for p in _ALL_PIPELINES if p.is_implemented]
_IMPLEMENTED_DICTS = [p.model_dump(mode="json") for p in _IMPLEMENTED]
_IMPLEMENTED_IDS = [p["name"] for p in _IMPLEMENTED_DICTS]

_ALL_DICTS = [p.model_dump(mode="json") for p in _ALL_PIPELINES]
_ALL_IDS = [p["name"] for p in _ALL_DICTS]


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
    """Structural validation of implemented pipeline definitions."""

    @pytest.mark.parametrize("pipeline", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_non_empty(self, pipeline):
        assert len(pipeline["stages"]) >= 1

    @pytest.mark.parametrize("pipeline", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_monotonic_order(self, pipeline):
        orders = [s["order"] for s in pipeline["stages"]]
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Stage order not strictly ascending: {orders}"
            )

    @pytest.mark.parametrize("pipeline", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_gate_chaining(self, pipeline):
        stages = pipeline["stages"]
        for i in range(1, len(stages)):
            assert stages[i]["prerequisite_gate"] == stages[i - 1]["produces_gate"], (
                f"Stage {stages[i]['order']} prerequisite "
                f"({stages[i]['prerequisite_gate']}) != "
                f"stage {stages[i - 1]['order']} produces "
                f"({stages[i - 1]['produces_gate']})"
            )

    @pytest.mark.parametrize("pipeline", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_unique_descriptions(self, pipeline):
        descriptions = [s["description"] for s in pipeline["stages"]]
        assert len(descriptions) == len(set(descriptions)), (
            f"Duplicate descriptions in {pipeline['name']}: {descriptions}"
        )

    @pytest.mark.parametrize("pipeline", _ALL_DICTS, ids=_ALL_IDS)
    def test_slug_pattern_valid(self, pipeline):
        assert "{n}" in pipeline["slug_pattern"], (
            f"slug_pattern missing {{n}} placeholder: {pipeline['slug_pattern']}"
        )

    @pytest.mark.parametrize("pipeline", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_gate_consumes_declared(self, pipeline):
        """Stages with a prerequisite gate must declare what they consume."""
        for stage in pipeline["stages"]:
            if stage["prerequisite_gate"]:
                assert stage.get("consumes"), (
                    f"Stage {stage['order']} ({stage['skill']}) in "
                    f"{pipeline['name']} has prerequisite_gate but no consumes"
                )


# ---------------------------------------------------------------------------
# 2. Decision-title join (implemented skillsets only)
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestDecisionTitleJoin:
    """The string-equality join between DecisionEntry.title and
    PipelineStage.description that drives GetProjectProgressUseCase.
    """

    @pytest.mark.parametrize("pipeline", _IMPLEMENTED_DICTS, ids=_IMPLEMENTED_IDS)
    def test_progress_advances_through_all_stages(self, pipeline, tmp_path):
        di = Container(_tmp_config(tmp_path))

        # Initialize workspace, create engagement, and register project
        di.initialize_workspace_usecase.execute(
            InitializeWorkspaceRequest(client=CLIENT)
        )
        di.create_engagement_usecase.execute(
            CreateEngagementRequest(client=CLIENT, slug="strat-1")
        )
        slug = pipeline["slug_pattern"].replace("{n}", "1")
        di.register_project_usecase.execute(
            RegisterProjectRequest(
                client=CLIENT,
                engagement="strat-1",
                slug=slug,
                skillset=pipeline["name"],
                scope="Conformance test",
            )
        )

        stages = pipeline["stages"]

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
            pytest.param(make_engagement_entry(), id="EngagementEntry"),
            pytest.param(make_research(), id="ResearchTopic"),
            pytest.param(make_pipeline(), id="Pipeline"),
            pytest.param(make_pipeline(stages=[]), id="Pipeline-prospectus"),
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
            pytest.param(make_knowledge_pack(), id="KnowledgePack"),
            pytest.param(
                make_knowledge_pack(compilation_state=CompilationState.DIRTY),
                id="KnowledgePack-dirty",
            ),
            pytest.param(
                make_knowledge_pack(compilation_state=CompilationState.CORRUPT),
                id="KnowledgePack-corrupt",
            ),
            pytest.param(make_skill_manifest(), id="SkillManifest"),
            pytest.param(
                make_skill_manifest(
                    metadata=dict(
                        author="monkeypants",
                        version="0.2",
                        freedom="high",
                        skillset="wardley-mapping",
                        stage="1",
                    ),
                ),
                id="SkillManifest-pipeline",
            ),
            pytest.param(make_item_freshness(), id="ItemFreshness"),
            pytest.param(
                make_item_freshness(state="orphan", is_composite=False),
                id="ItemFreshness-orphan",
            ),
            pytest.param(make_pack_freshness(), id="PackFreshness"),
            pytest.param(
                make_pack_freshness(
                    compilation_state=CompilationState.CORRUPT,
                    items=[make_item_freshness(state="orphan")],
                ),
                id="PackFreshness-corrupt",
            ),
            pytest.param(make_observation_need(), id="ObservationNeed"),
            pytest.param(
                make_observation_need(served=True),
                id="ObservationNeed-served",
            ),
            pytest.param(make_routing_destination(), id="RoutingDestination"),
            pytest.param(make_routing_allow_list(), id="RoutingAllowList"),
            pytest.param(make_observation(), id="Observation"),
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
class TestPipelineDiscipline:
    """Every pipeline (implemented or prospectus) must declare required fields."""

    @pytest.mark.parametrize("pipeline", _ALL_DICTS, ids=_ALL_IDS)
    def test_has_name(self, pipeline):
        assert pipeline["name"], "Pipeline must have a non-empty name"

    @pytest.mark.parametrize("pipeline", _ALL_DICTS, ids=_ALL_IDS)
    def test_has_display_name(self, pipeline):
        assert pipeline["display_name"], "Pipeline must have a non-empty display_name"

    @pytest.mark.parametrize("pipeline", _ALL_DICTS, ids=_ALL_IDS)
    def test_has_description(self, pipeline):
        assert pipeline["description"], "Pipeline must have a non-empty description"

    @pytest.mark.parametrize("pipeline", _ALL_DICTS, ids=_ALL_IDS)
    def test_name_is_kebab_case(self, pipeline):
        import re

        assert re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", pipeline["name"]), (
            f"Pipeline name must be kebab-case: {pipeline['name']}"
        )

    @pytest.mark.parametrize("pipeline", _ALL_DICTS, ids=_ALL_IDS)
    def test_unique_names(self, pipeline):
        """Each pipeline name appears exactly once across all BCs."""
        count = sum(1 for p in _ALL_DICTS if p["name"] == pipeline["name"])
        assert count == 1, f"Pipeline name {pipeline['name']!r} appears {count} times"


@pytest.mark.doctrine
class TestPipelineRegistration:
    """Directory scanning discovers all BC packages."""

    def test_directory_scanning_finds_all_pipelines(self):
        """discover_all_bc_modules finds the same pipelines as direct import."""
        from bin.cli.infrastructure.code_skillset_repository import (
            CodeSkillsetRepository,
        )

        repo = CodeSkillsetRepository(_REPO_ROOT)
        discovered_names = {p.name for p in repo.list_all()}
        expected_names = {p.name for p in _ALL_PIPELINES}
        assert discovered_names == expected_names, (
            f"Discovery mismatch: found {discovered_names}, expected {expected_names}"
        )


@pytest.mark.doctrine
class TestBoundedContextTestOwnership:
    """Implemented BCs must own their test infrastructure."""

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_implemented_bc_has_test_directory(self, mod):
        if not any(p.is_implemented for p in _get_pipelines(mod)):
            pytest.skip("Prospectus-only BC")
        bc_dir = Path(mod.__file__).parent
        assert (bc_dir / "tests" / "__init__.py").is_file()

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_implemented_bc_has_presenter_test(self, mod):
        if not any(p.is_implemented for p in _get_pipelines(mod)):
            pytest.skip("Prospectus-only BC")
        bc_dir = Path(mod.__file__).parent
        assert (bc_dir / "tests" / "test_presenter.py").is_file()

    @pytest.mark.parametrize("mod", _BC_MODULES, ids=[m.__name__ for m in _BC_MODULES])
    def test_implemented_bc_has_presenter_factory(self, mod):
        if not any(p.is_implemented for p in _get_pipelines(mod)):
            pytest.skip("Prospectus-only BC")
        assert hasattr(mod, "PRESENTER_FACTORY")


# ---------------------------------------------------------------------------
# 6. Protocol smoke tests — runtime verification of BC plugin contracts
# ---------------------------------------------------------------------------


_IMPLEMENTED_MODULES = [
    m for m in _BC_MODULES if any(p.is_implemented for p in _get_pipelines(m))
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


def _load_skill_manifest(skill_md_path: Path) -> SkillManifest:
    """Parse and validate a SKILL.md into a SkillManifest entity."""
    fm = parse_frontmatter(skill_md_path)
    return SkillManifest.model_validate(fm)


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
    for pipeline in _IMPLEMENTED:
        for stage in pipeline.stages:
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
        manifest = _load_skill_manifest(path / "SKILL.md")
        assert manifest.name == dir_name, (
            f"Frontmatter name {manifest.name!r} != directory name {dir_name!r}"
        )

    @pytest.mark.parametrize("skill_dir", _SKILL_DIRS, ids=_SKILL_DIR_IDS)
    def test_valid_manifest(self, skill_dir):
        """SKILL.md parses into a valid SkillManifest — name format, description
        length, and freedom level are all enforced by Pydantic validators."""
        _, path = skill_dir
        _load_skill_manifest(path / "SKILL.md")

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
        manifest = _load_skill_manifest(skill_md)
        assert manifest.name == skill_name, (
            f"Frontmatter name {manifest.name!r} != pipeline skill {skill_name!r}"
        )


# ---------------------------------------------------------------------------
# 8. Cross-BC import isolation — dependency rule enforcement
# ---------------------------------------------------------------------------


def _discover_bc_packages():
    """Return set of BC package names from all source containers."""
    packages = set()
    for container in ("commons", "personal", "partnerships"):
        container_dir = _REPO_ROOT / container
        if not container_dir.is_dir():
            continue
        # partnerships has sub-dirs per engagement
        if container == "partnerships":
            for slug_dir in container_dir.iterdir():
                if not slug_dir.is_dir():
                    continue
                for pkg_dir in slug_dir.iterdir():
                    if pkg_dir.is_dir() and (pkg_dir / "__init__.py").is_file():
                        packages.add(pkg_dir.name)
        else:
            for pkg_dir in container_dir.iterdir():
                if pkg_dir.is_dir() and (pkg_dir / "__init__.py").is_file():
                    packages.add(pkg_dir.name)
    return packages


# ---------------------------------------------------------------------------
# 9. Design-time pack freshness — stale bytecode detection
# ---------------------------------------------------------------------------


def _discover_design_time_packs():
    """Find all version-controlled packs via FilesystemKnowledgePackRepository."""
    from bin.cli.infrastructure.filesystem_knowledge_pack_repository import (
        FilesystemKnowledgePackRepository,
    )

    repo = FilesystemKnowledgePackRepository(_REPO_ROOT)
    return [(pack.name, path) for pack, path in repo.packs_with_paths()]


_DESIGN_TIME_PACKS = _discover_design_time_packs()
_DESIGN_TIME_PACK_IDS = [name for name, _ in _DESIGN_TIME_PACKS]


@pytest.mark.doctrine
class TestDesignTimePackFreshness:
    """Version-controlled packs must not have stale or corrupt bytecode.

    ABSENT is tolerated — newly created packs haven't been compiled yet.
    DIRTY means someone edited content without recompiling.
    CORRUPT means orphan mirrors need cleanup.
    """

    @pytest.mark.parametrize(
        "pack_entry", _DESIGN_TIME_PACKS, ids=_DESIGN_TIME_PACK_IDS
    )
    def test_no_dirty_packs(self, pack_entry):
        """Content hash in bytecode frontmatter must match source."""
        from bin.cli.infrastructure.filesystem_freshness_inspector import (
            FilesystemFreshnessInspector,
        )

        name, pack_root = pack_entry
        freshness = FilesystemFreshnessInspector().assess(pack_root)
        assert freshness.deep_state != CompilationState.DIRTY, (
            f"Pack {name!r} at {pack_root} has stale bytecode (DIRTY). "
            "Recompile with the agent or pack-and-wrap."
        )

    @pytest.mark.parametrize(
        "pack_entry", _DESIGN_TIME_PACKS, ids=_DESIGN_TIME_PACK_IDS
    )
    def test_no_corrupt_packs(self, pack_entry):
        """Orphan mirrors (CORRUPT) need cleanup."""
        from bin.cli.infrastructure.filesystem_freshness_inspector import (
            FilesystemFreshnessInspector,
        )

        name, pack_root = pack_entry
        freshness = FilesystemFreshnessInspector().assess(pack_root)
        assert freshness.deep_state != CompilationState.CORRUPT, (
            f"Pack {name!r} at {pack_root} has orphan bytecode mirrors (CORRUPT). "
            "Remove orphans from _bytecode/."
        )


_BC_PACKAGES = _discover_bc_packages()


# ---------------------------------------------------------------------------
# 10. Script REPO_DIR resolution
# ---------------------------------------------------------------------------

_REPO_DIR_RE = re.compile(r"^REPO_DIR=", re.MULTILINE)
_GIT_TOPLEVEL_RE = re.compile(r"git\b.*rev-parse\s+--show-toplevel")


def _discover_all_skill_scripts():
    """Return (relative_path, abs_path) for every .sh under commons/ skills."""
    results = []
    for script in sorted((_REPO_ROOT / "commons").rglob("scripts/*.sh")):
        rel = script.relative_to(_REPO_ROOT)
        results.append((str(rel), script))
    return results


_ALL_SKILL_SCRIPTS = _discover_all_skill_scripts()
_ALL_SKILL_SCRIPT_IDS = [rel for rel, _ in _ALL_SKILL_SCRIPTS]


@pytest.mark.doctrine
class TestScriptRepoRoot:
    """Skill scripts that set REPO_DIR must resolve the repo root reliably.

    The correct pattern is ``git rev-parse --show-toplevel``, not relative
    path traversal (``../..``) which breaks when the directory depth changes.
    """

    @pytest.mark.parametrize(
        "script_entry", _ALL_SKILL_SCRIPTS, ids=_ALL_SKILL_SCRIPT_IDS
    )
    def test_repo_dir_uses_git_rev_parse(self, script_entry):
        _, script_path = script_entry
        source = script_path.read_text()
        if not _REPO_DIR_RE.search(source):
            pytest.skip("Script does not set REPO_DIR")
        assert _GIT_TOPLEVEL_RE.search(source), (
            f"{script_path.relative_to(_REPO_ROOT)} sets REPO_DIR without "
            "git rev-parse --show-toplevel"
        )


# Build (bc_name, py_file) pairs for parametrization
_IMPORT_RE = re.compile(r"^\s*(?:import|from)\s+([\w.]+)", re.MULTILINE)


def _collect_bc_python_files():
    """Return list of (bc_name, py_path) for all Python files in each BC."""
    results = []
    for container in ("commons", "personal", "partnerships"):
        container_dir = _REPO_ROOT / container
        if not container_dir.is_dir():
            continue
        dirs = []
        if container == "partnerships":
            for slug_dir in container_dir.iterdir():
                if slug_dir.is_dir():
                    dirs.extend(
                        d
                        for d in slug_dir.iterdir()
                        if d.is_dir() and (d / "__init__.py").is_file()
                    )
        else:
            dirs = [
                d
                for d in container_dir.iterdir()
                if d.is_dir() and (d / "__init__.py").is_file()
            ]
        for bc_dir in sorted(dirs):
            bc_name = bc_dir.name
            for py_file in sorted(bc_dir.rglob("*.py")):
                # Skip test files — test fixtures legitimately cross BC
                # boundaries for workspace/engagement setup.
                if "tests" in py_file.relative_to(bc_dir).parts:
                    continue
                results.append((bc_name, py_file))
    return results


_BC_PY_FILES = _collect_bc_python_files()
_BC_PY_IDS = [f"{bc}/{py.relative_to(_REPO_ROOT)}" for bc, py in _BC_PY_FILES]


@pytest.mark.doctrine
class TestNoCrossBCImports:
    """No bounded context may import from another bounded context.

    Enforces the dependency rule structurally (Larman Law 4). Allowed
    imports: practice.*, stdlib, third-party, same-BC internals.
    """

    @pytest.mark.parametrize("bc_file", _BC_PY_FILES, ids=_BC_PY_IDS)
    def test_no_cross_bc_import(self, bc_file):
        bc_name, py_path = bc_file
        source = py_path.read_text()
        other_bcs = _BC_PACKAGES - {bc_name}
        violations = []
        for match in _IMPORT_RE.finditer(source):
            top_level = match.group(1).split(".")[0]
            if top_level in other_bcs:
                violations.append(
                    f"  {py_path.relative_to(_REPO_ROOT)}: imports {match.group(1)}"
                )
        assert not violations, f"{bc_name} imports from other BCs:\n" + "\n".join(
            violations
        )
