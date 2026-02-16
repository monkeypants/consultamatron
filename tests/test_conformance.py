"""Conformance tests — bounded-context protocol obligations.

These tests verify that skillsets compose correctly with the engagement
lifecycle layer (the semantic waist). They run under the ``doctrine``
marker, which is the pre-push gate defined in CLAUDE.md.

Five conformance properties:
  1. Pipeline coherence — structural validation of implemented skillset pipelines
  2. Decision-title join — the fragile string join that drives progress
  3. Entity round-trip — JSON serialisation fidelity for all entities
  4. Presenter contract — each presenter produces valid ProjectContribution
  5. Skillset discipline — field-level validation for all skillsets
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

import business_model_canvas
import wardley_mapping
from bin.cli.config import Config
from bin.cli.di import Container
from bin.cli.infrastructure.code_skillset_repository import _read_pyproject_packages
from business_model_canvas.presenter import BmcProjectPresenter
from bin.cli.infrastructure.json_repos import JsonTourManifestRepository
from consulting.dtos import (
    CreateEngagementRequest,
    GetProjectProgressRequest,
    InitializeWorkspaceRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
)
from practice.content import ProjectContribution
from practice.discovery import PipelineStage
from practice.entities import Project, ProjectStatus, Skillset
from wardley_mapping.presenter import WardleyProjectPresenter

from .conftest import (
    make_decision,
    make_engagement,
    make_project,
    make_prospectus,
    make_research,
    make_skillset,
    make_tour,
    make_tour_stop,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALL_SKILLSETS: list[Skillset] = (
    wardley_mapping.SKILLSETS + business_model_canvas.SKILLSETS
)
_IMPLEMENTED = [s for s in _ALL_SKILLSETS if s.is_implemented]
_IMPLEMENTED_DICTS = [s.model_dump(mode="json") for s in _IMPLEMENTED]
_IMPLEMENTED_IDS = [s["name"] for s in _IMPLEMENTED_DICTS]

_ALL_DICTS = [s.model_dump(mode="json") for s in _ALL_SKILLSETS]
_ALL_IDS = [s["name"] for s in _ALL_DICTS]

CLIENT = "conformance-corp"

_REPO_ROOT = Path(__file__).resolve().parent.parent


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


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
            pytest.param(make_tour_stop(), id="TourStop"),
            pytest.param(make_tour(), id="TourManifest"),
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
# 4. Presenter contract
# ---------------------------------------------------------------------------


def _noop_script(tmp_path: Path) -> Path:
    """Create a no-op ensure-owm.sh for tests."""
    script = tmp_path / "noop-owm.sh"
    script.write_text("#!/bin/sh\ntrue\n")
    script.chmod(0o755)
    return script


def _build_presenters(ws_root: Path) -> dict:
    """Build {skillset_name: presenter} for all registered presenters."""
    script = _noop_script(ws_root)
    return {
        "wardley-mapping": WardleyProjectPresenter(
            workspace_root=ws_root,
            ensure_owm_script=script,
            tours=JsonTourManifestRepository(ws_root),
        ),
        "business-model-canvas": BmcProjectPresenter(
            workspace_root=ws_root,
        ),
    }


_PRESENTER_NAMES = ["wardley-mapping", "business-model-canvas"]


@pytest.mark.doctrine
class TestPresenterContract:
    """Each registered presenter produces a valid ProjectContribution
    from a minimal workspace.
    """

    @pytest.mark.parametrize("skillset_name", _PRESENTER_NAMES)
    def test_produces_project_contribution(self, skillset_name, tmp_path):
        client = "presenter-test"
        slug = "test-1"

        # Create minimal project directory with a brief
        proj_dir = tmp_path / client / "projects" / slug
        _write(proj_dir / "brief.agreed.md", "# Brief\n\nMinimal conformance test.")

        presenters = _build_presenters(tmp_path)
        presenter = presenters[skillset_name]

        project = Project(
            slug=slug,
            client=client,
            engagement="strat-1",
            skillset=skillset_name,
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )

        result = presenter.present(project)

        assert isinstance(result, ProjectContribution)
        assert result.slug == slug
        assert result.skillset == skillset_name
        assert isinstance(result.sections, list)


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
        bc_packages = {"wardley_mapping", "business_model_canvas"}
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
