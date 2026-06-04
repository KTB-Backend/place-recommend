import pytest

from domain.models import Location
from infrastructure.station.hardcoded_station_repository import (
    HardcodedStationRepository,
)


@pytest.fixture
def repo() -> HardcodedStationRepository:
    return HardcodedStationRepository()


class TestHardcodedStationRepository:
    def test_find_nearest_known_station(self, repo: HardcodedStationRepository) -> None:
        loc = Location(lat=37.4980, lng=127.0277)
        assert repo.find_nearest(loc).name == "강남"

    def test_find_nearest_always_returns(
        self,
        repo: HardcodedStationRepository,
    ) -> None:
        loc = Location(lat=35.1796, lng=129.0756)  # 부산
        station = repo.find_nearest(loc)
        assert station is not None
        assert station.name != ""

    def test_find_nearest_exact_match(self, repo: HardcodedStationRepository) -> None:
        loc = Location(lat=37.5574, lng=126.9249)  # 홍대입구 좌표
        assert repo.find_nearest(loc).name == "홍대입구"

    def test_all_stations_have_valid_coordinates(self) -> None:
        for s in HardcodedStationRepository._STATIONS:
            assert -90.0 <= s.lat <= 90.0, f"{s.name} lat out of range"
            assert -180.0 <= s.lng <= 180.0, f"{s.name} lng out of range"

    def test_station_count(self) -> None:
        stations = HardcodedStationRepository._STATIONS
        assert len(stations) >= 100
        assert len({s.id for s in stations}) == len(stations)

    def test_find_nearest_candidates_returns_limited_order(
        self,
        repo: HardcodedStationRepository,
    ) -> None:
        loc = Location(lat=37.4979, lng=127.0276)
        stations = repo.find_nearest_candidates(loc, limit=3)

        assert len(stations) == 3
        assert stations[0].name == "강남"

    def test_find_nearest_candidates_zero_limit(
        self,
        repo: HardcodedStationRepository,
    ) -> None:
        loc = Location(lat=37.4979, lng=127.0276)
        assert repo.find_nearest_candidates(loc, limit=0) == []

    def test_find_by_name_accepts_station_suffix(
        self,
        repo: HardcodedStationRepository,
    ) -> None:
        station = repo.find_by_name("강남역")
        assert station is not None
        assert station.id == "gangnam"

    def test_find_by_name_returns_none_for_unknown(
        self,
        repo: HardcodedStationRepository,
    ) -> None:
        assert repo.find_by_name("없는역") is None
