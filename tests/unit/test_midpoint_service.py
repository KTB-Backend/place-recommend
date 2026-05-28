import pytest

from domain.exceptions import InvalidLocationError
from domain.models import Location, Station
from application.midpoint_service import MidpointService
from infrastructure.station.hardcoded_station_repository import HardcodedStationRepository


@pytest.fixture
def service() -> MidpointService:
    return MidpointService(repository=HardcodedStationRepository())


class TestCalculateMidpoint:
    def test_midpoint_of_two_locations(self, service: MidpointService) -> None:
        a = Location(lat=37.5, lng=127.0)
        b = Location(lat=37.6, lng=127.1)
        mid = service.calculate_midpoint([a, b])
        assert mid.lat == pytest.approx(37.55)
        assert mid.lng == pytest.approx(127.05)

    def test_midpoint_of_single_location(self, service: MidpointService) -> None:
        loc = Location(lat=37.5665, lng=126.9780)
        assert service.calculate_midpoint([loc]) == loc

    def test_empty_locations_raises(self, service: MidpointService) -> None:
        with pytest.raises(InvalidLocationError):
            service.calculate_midpoint([])


class TestFindMeetingStation:
    def test_find_meeting_station_returns_station(self, service: MidpointService) -> None:
        locs = [Location(lat=37.5, lng=127.0), Location(lat=37.6, lng=127.1)]
        result = service.find_meeting_station(locs)
        assert isinstance(result, Station)

    def test_find_meeting_station_always_returns(self, service: MidpointService) -> None:
        loc = Location(lat=35.1796, lng=129.0756)  # 부산 — 반경 무관하게 반환
        result = service.find_meeting_station([loc])
        assert result is not None

    def test_empty_locations_raises(self, service: MidpointService) -> None:
        with pytest.raises(InvalidLocationError):
            service.find_meeting_station([])
