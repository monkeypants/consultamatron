"""Tour manifest repository contract tests."""

from __future__ import annotations

from .conftest import make_tour, make_tour_stop

CLIENT = "holloway-group"
ENGAGEMENT = "strat-1"


class TestTourManifestContract:
    def test_get_missing_returns_none(self, tour_repo):
        assert tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor") is None

    def test_save_then_get(self, tour_repo):
        t = make_tour()
        tour_repo.save(t)
        got = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        assert got is not None
        assert got.title == "Investor Tour"
        assert len(got.stops) == 1

    def test_save_replaces(self, tour_repo):
        tour_repo.save(make_tour(stops=[make_tour_stop(order="1")]))
        tour_repo.save(
            make_tour(
                stops=[
                    make_tour_stop(order="1"),
                    make_tour_stop(order="2", title="Risk", atlas_source="atlas/risk/"),
                ]
            )
        )
        got = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        assert len(got.stops) == 2

    def test_different_tours_independent(self, tour_repo):
        tour_repo.save(make_tour(name="investor", title="Investor Tour"))
        tour_repo.save(make_tour(name="technical", title="Technical Tour"))
        inv = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        tech = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "technical")
        assert inv.title == "Investor Tour"
        assert tech.title == "Technical Tour"

    def test_project_isolation(self, tour_repo):
        tour_repo.save(make_tour(project_slug="maps-1"))
        assert tour_repo.get(CLIENT, ENGAGEMENT, "maps-2", "investor") is None

    def test_stops_round_trip(self, tour_repo):
        stops = [
            make_tour_stop(order="1", title="Overview"),
            make_tour_stop(order="2a", title="Risk A"),
            make_tour_stop(order="2b", title="Risk B"),
        ]
        tour_repo.save(make_tour(stops=stops))
        got = tour_repo.get(CLIENT, ENGAGEMENT, "maps-1", "investor")
        assert [s.order for s in got.stops] == ["1", "2a", "2b"]
        assert [s.title for s in got.stops] == ["Overview", "Risk A", "Risk B"]

    def test_list_all_empty(self, tour_repo):
        assert tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-1") == []

    def test_list_all_returns_all_tours(self, tour_repo):
        tour_repo.save(make_tour(name="investor", title="Investor Tour"))
        tour_repo.save(make_tour(name="technical", title="Technical Tour"))
        result = tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-1")
        assert len(result) == 2
        names = {t.name for t in result}
        assert names == {"investor", "technical"}

    def test_list_all_project_isolation(self, tour_repo):
        tour_repo.save(make_tour(project_slug="maps-1"))
        tour_repo.save(make_tour(project_slug="maps-2"))
        assert len(tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-1")) == 1
        assert len(tour_repo.list_all(CLIENT, ENGAGEMENT, "maps-2")) == 1
