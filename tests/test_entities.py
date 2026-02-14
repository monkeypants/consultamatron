"""Entity validation tests.

Pydantic does work for us. Prove it does the right work:
required fields, enum validation, defaults, round-trip fidelity.
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from bin.cli.entities import (
    Confidence,
    DecisionEntry,
    PipelineStage,
    Project,
    ProjectStatus,
)

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
# Required fields
# ---------------------------------------------------------------------------


class TestRequiredFields:
    def test_project_requires_slug(self):
        with pytest.raises(ValidationError):
            make_project(**{"slug": None})  # type: ignore[arg-type]

    def test_project_requires_client(self):
        with pytest.raises(ValidationError):
            Project(
                slug="x",
                client=None,  # type: ignore[arg-type]
                skillset="wm",
                status=ProjectStatus.PLANNED,
                created=date.today(),
            )

    def test_decision_requires_id(self):
        with pytest.raises(ValidationError):
            make_decision(**{"id": None})  # type: ignore[arg-type]

    def test_decision_requires_title(self):
        with pytest.raises(ValidationError):
            make_decision(**{"title": None})  # type: ignore[arg-type]

    def test_engagement_requires_id(self):
        with pytest.raises(ValidationError):
            make_engagement(**{"id": None})  # type: ignore[arg-type]

    def test_tour_manifest_requires_stops(self):
        with pytest.raises(ValidationError):
            make_tour(**{"stops": None})  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Enum validation
# ---------------------------------------------------------------------------


class TestEnumValidation:
    def test_project_status_rejects_invalid(self):
        with pytest.raises(ValidationError):
            make_project(status="bogus")  # type: ignore[arg-type]

    def test_project_status_accepts_valid_string(self):
        p = make_project(status="planned")  # type: ignore[arg-type]
        assert p.status == ProjectStatus.PLANNED

    def test_confidence_rejects_invalid(self):
        with pytest.raises(ValidationError):
            make_research(confidence="Very High")  # type: ignore[arg-type]

    def test_confidence_accepts_valid_values(self):
        for val in ("High", "Medium-High", "Medium", "Low"):
            r = make_research(confidence=val)  # type: ignore[arg-type]
            assert r.confidence == Confidence(val)


# ---------------------------------------------------------------------------
# Default values
# ---------------------------------------------------------------------------


class TestDefaults:
    def test_project_notes_defaults_empty(self):
        p = make_project()
        assert p.notes == ""

    def test_tour_stop_map_file_default(self):
        s = make_tour_stop()
        assert s.map_file == "map.svg"

    def test_tour_stop_analysis_file_default(self):
        s = make_tour_stop()
        assert s.analysis_file == "analysis.md"

    def test_skillset_atlas_skills_defaults_empty(self):
        s = make_skillset()
        assert s.atlas_skills == []

    def test_skillset_tour_skills_defaults_empty(self):
        s = make_skillset()
        assert s.tour_skills == []


# ---------------------------------------------------------------------------
# Round-trip fidelity (model_dump -> model_validate)
# ---------------------------------------------------------------------------


class TestRoundTrip:
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
                skill="wm-research",
                prerequisite_gate="resources/index.md",
                produces_gate="brief.agreed.md",
                description="Kickoff",
            ),
        ],
        ids=lambda e: type(e).__name__,
    )
    def test_json_round_trip(self, entity):
        cls = type(entity)
        dumped = entity.model_dump(mode="json")
        restored = cls.model_validate(dumped)
        assert restored == entity

    def test_date_serialises_as_iso_string(self):
        p = make_project(created=date(2025, 3, 15))
        dumped = p.model_dump(mode="json")
        assert dumped["created"] == "2025-03-15"

    def test_enum_serialises_as_value(self):
        p = make_project(status=ProjectStatus.ACTIVE)
        dumped = p.model_dump(mode="json")
        assert dumped["status"] == "active"

    def test_fields_dict_preserved(self):
        d = make_decision(fields={"Users": "CTO, VP", "Scope": "Narrow"})
        dumped = d.model_dump(mode="json")
        restored = DecisionEntry.model_validate(dumped)
        assert restored.fields == {"Users": "CTO, VP", "Scope": "Narrow"}


# ---------------------------------------------------------------------------
# Entity-specific semantics
# ---------------------------------------------------------------------------


class TestTourStopOrder:
    """TourStop.order is str to support hierarchical numbering."""

    def test_integer_order(self):
        s = make_tour_stop(order="3")
        assert s.order == "3"

    def test_letter_suffix_order(self):
        s = make_tour_stop(order="4a")
        assert s.order == "4a"


class TestProjectStatusValues:
    """All four status values exist and have the expected string form."""

    def test_all_statuses(self):
        assert ProjectStatus.PLANNED.value == "planned"
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.COMPLETE.value == "complete"
        assert ProjectStatus.REVIEWED.value == "reviewed"
