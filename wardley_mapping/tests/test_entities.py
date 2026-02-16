"""Wardley Mapping entity tests.

TourStop and TourManifest defaults, ordering, and round-trip fidelity.
"""

from __future__ import annotations

import pytest

from .conftest import make_tour, make_tour_stop


class TestTourStopDefaults:
    def test_map_file_default(self):
        s = make_tour_stop()
        assert s.map_file == "map.svg"

    def test_analysis_file_default(self):
        s = make_tour_stop()
        assert s.analysis_file == "analysis.md"


class TestTourStopOrder:
    """TourStop.order is str to support hierarchical numbering."""

    def test_integer_order(self):
        s = make_tour_stop(order="3")
        assert s.order == "3"

    def test_letter_suffix_order(self):
        s = make_tour_stop(order="4a")
        assert s.order == "4a"


class TestRoundTrip:
    @pytest.mark.parametrize(
        "entity",
        [
            pytest.param(make_tour_stop(), id="TourStop"),
            pytest.param(make_tour(), id="TourManifest"),
        ],
    )
    def test_json_round_trip(self, entity):
        cls = type(entity)
        dumped = entity.model_dump(mode="json")
        restored = cls.model_validate(dumped)
        assert restored == entity
