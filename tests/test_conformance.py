"""Conformance tests — bounded-context protocol obligations.

These tests verify that skillsets compose correctly with the engagement
lifecycle layer (the semantic waist). They run under the ``doctrine``
marker, which is the pre-push gate defined in CLAUDE.md.

Four conformance properties:
  1. Pipeline coherence — structural validation of skillset pipelines
  2. Decision-title join — the fragile string join that drives progress
  3. Entity round-trip — JSON serialisation fidelity for all entities
  4. Presenter contract — each presenter produces valid ProjectContribution
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from bin.cli.config import Config
from practice.content import ProjectContribution
from bin.cli.di import Container
from bin.cli.dtos import (
    GetProjectProgressRequest,
    InitializeWorkspaceRequest,
    RecordDecisionRequest,
    RegisterProjectRequest,
)
from practice.discovery import PipelineStage
from practice.entities import Project, ProjectStatus
from bin.cli.infrastructure.bmc_presenter import BmcProjectPresenter
from bin.cli.infrastructure.json_repos import JsonTourManifestRepository
from bin.cli.infrastructure.wardley_presenter import WardleyProjectPresenter

from .conftest import (
    make_decision,
    make_engagement,
    make_project,
    make_research,
    make_skillset,
    make_tour,
    make_tour_stop,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SKILLSETS_INDEX = Path(__file__).resolve().parent.parent / "skillsets" / "index.json"


def _load_skillsets() -> list[dict]:
    """Load skillset definitions from the real index.json."""
    return json.loads(SKILLSETS_INDEX.read_text())


SKILLSETS = _load_skillsets()
SKILLSET_IDS = [s["name"] for s in SKILLSETS]

CLIENT = "conformance-corp"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# 1. Pipeline coherence
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestPipelineCoherence:
    """Structural validation of skillset pipeline definitions."""

    @pytest.mark.parametrize("skillset", SKILLSETS, ids=SKILLSET_IDS)
    def test_non_empty(self, skillset):
        assert len(skillset["pipeline"]) >= 1

    @pytest.mark.parametrize("skillset", SKILLSETS, ids=SKILLSET_IDS)
    def test_monotonic_order(self, skillset):
        orders = [s["order"] for s in skillset["pipeline"]]
        for i in range(1, len(orders)):
            assert orders[i] > orders[i - 1], (
                f"Stage order not strictly ascending: {orders}"
            )

    @pytest.mark.parametrize("skillset", SKILLSETS, ids=SKILLSET_IDS)
    def test_gate_chaining(self, skillset):
        stages = skillset["pipeline"]
        for i in range(1, len(stages)):
            assert stages[i]["prerequisite_gate"] == stages[i - 1]["produces_gate"], (
                f"Stage {stages[i]['order']} prerequisite "
                f"({stages[i]['prerequisite_gate']}) != "
                f"stage {stages[i - 1]['order']} produces "
                f"({stages[i - 1]['produces_gate']})"
            )

    @pytest.mark.parametrize("skillset", SKILLSETS, ids=SKILLSET_IDS)
    def test_unique_descriptions(self, skillset):
        descriptions = [s["description"] for s in skillset["pipeline"]]
        assert len(descriptions) == len(set(descriptions)), (
            f"Duplicate descriptions in {skillset['name']}: {descriptions}"
        )

    @pytest.mark.parametrize("skillset", SKILLSETS, ids=SKILLSET_IDS)
    def test_slug_pattern_valid(self, skillset):
        assert "{n}" in skillset["slug_pattern"], (
            f"slug_pattern missing {{n}} placeholder: {skillset['slug_pattern']}"
        )


# ---------------------------------------------------------------------------
# 2. Decision-title join
# ---------------------------------------------------------------------------


@pytest.mark.doctrine
class TestDecisionTitleJoin:
    """The string-equality join between DecisionEntry.title and
    PipelineStage.description that drives GetProjectProgressUseCase.
    """

    @pytest.mark.parametrize("skillset", SKILLSETS, ids=SKILLSET_IDS)
    def test_progress_advances_through_all_stages(self, skillset, tmp_path):
        # Wire up a container with skillsets seeded from the real index.json
        # (not conftest helpers, which may drift from the source of truth)
        config = Config(
            repo_root=tmp_path,
            workspace_root=tmp_path / "clients",
            skillsets_root=tmp_path / "skillsets",
        )
        config.skillsets_root.mkdir(parents=True, exist_ok=True)
        (config.skillsets_root / "index.json").write_text(SKILLSETS_INDEX.read_text())
        di = Container(config)

        # Initialize workspace and register project
        di.initialize_workspace_usecase.execute(
            InitializeWorkspaceRequest(client=CLIENT)
        )
        slug = skillset["slug_pattern"].replace("{n}", "1")
        di.register_project_usecase.execute(
            RegisterProjectRequest(
                client=CLIENT,
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
                    project_slug=slug,
                    title=stage["description"],
                    fields={},
                )
            )

            resp = di.get_project_progress_usecase.execute(
                GetProjectProgressRequest(client=CLIENT, project_slug=slug)
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
            make_project(),
            make_decision(),
            make_engagement(),
            make_research(),
            make_tour_stop(),
            make_tour(),
            make_skillset(),
            PipelineStage(
                order=1,
                skill="test",
                prerequisite_gate="a",
                produces_gate="b",
                description="Test",
            ),
        ],
        ids=lambda e: type(e).__name__,
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
            skillset=skillset_name,
            status=ProjectStatus.ELABORATION,
            created=date(2025, 6, 1),
        )

        result = presenter.present(project)

        assert isinstance(result, ProjectContribution)
        assert result.slug == slug
        assert result.skillset == skillset_name
        assert isinstance(result.sections, list)
