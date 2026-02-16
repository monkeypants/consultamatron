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
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.infrastructure.code_skillset_repository import _read_pyproject_packages
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


def _discover_bc_modules():
    """Discover BC modules by scanning repo root for SKILLSETS exports."""
    for path in sorted(_REPO_ROOT.iterdir()):
        if not path.is_dir() or not (path / "__init__.py").is_file():
            continue
        try:
            mod = importlib.import_module(path.name)
            if hasattr(mod, "SKILLSETS"):
                yield mod
        except ImportError:
            continue


_BC_MODULES = list(_discover_bc_modules())
_ALL_SKILLSETS: list[Skillset] = [s for mod in _BC_MODULES for s in mod.SKILLSETS]
_IMPLEMENTED = [s for s in _ALL_SKILLSETS if s.is_implemented]
_IMPLEMENTED_DICTS = [s.model_dump(mode="json") for s in _IMPLEMENTED]
_IMPLEMENTED_IDS = [s["name"] for s in _IMPLEMENTED_DICTS]

_ALL_DICTS = [s.model_dump(mode="json") for s in _ALL_SKILLSETS]
_ALL_IDS = [s["name"] for s in _ALL_DICTS]


def _write_pyproject(tmp_path: Path) -> None:
    """Copy the real pyproject.toml into a tmp directory for Container."""
    import shutil

    shutil.copy(_REPO_ROOT / "pyproject.toml", tmp_path / "pyproject.toml")


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
        # Copy pyproject.toml so CodeSkillsetRepository can discover packages
        _write_pyproject(tmp_path)

        config = Config(
            repo_root=tmp_path,
            workspace_root=tmp_path / "clients",
            skillsets_root=tmp_path / "skillsets",
        )
        di = Container(config)

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
    """Every BC package with SKILLSETS is listed in pyproject.toml."""

    def test_all_bc_packages_in_pyproject(self):
        """Packages exporting SKILLSETS must appear in pyproject.toml packages."""
        pyproject_path = _REPO_ROOT / "pyproject.toml"
        registered = _read_pyproject_packages(pyproject_path)
        bc_packages = {mod.__name__ for mod in _BC_MODULES}
        for pkg in bc_packages:
            assert pkg in registered, (
                f"BC package {pkg!r} not in pyproject.toml packages list"
            )

    def test_dynamic_discovery_finds_all_skillsets(self):
        """CodeSkillsetRepository discovers the same skillsets as direct import."""
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
        _write_pyproject(tmp_path)
        config = Config(
            repo_root=tmp_path,
            workspace_root=tmp_path / "clients",
            skillsets_root=tmp_path / "skillsets",
        )
        container = Container(config)
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
