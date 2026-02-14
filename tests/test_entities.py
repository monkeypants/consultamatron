"""Entity tests.

Serialisation fidelity, default values, and domain-specific
semantics. Pydantic handles validation — the usecase and repository
tests exercise those paths with better diagnostics than we could
provide here.
"""

from __future__ import annotations

from datetime import date

import pytest

from bin.cli.entities import (
    DecisionEntry,
    PipelineStage,
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
        p = make_project(status=ProjectStatus.ELABORATION)
        dumped = p.model_dump(mode="json")
        assert dumped["status"] == "elaboration"

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
