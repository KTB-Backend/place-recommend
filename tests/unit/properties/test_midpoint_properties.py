from hypothesis import given

from application.midpoint_service import MidpointService
from infrastructure.station.hardcoded_station_repository import HardcodedStationRepository
from tests.unit.properties.strategies import two_or_more_locations, valid_locations


def _svc() -> MidpointService:
    return MidpointService(repository=HardcodedStationRepository())


class TestMidpointProperties:
    """PBT: MidpointService 불변식."""

    @given(valid_locations())
    def test_single_location_identity(self, loc) -> None:
        """PBT-M01: midpoint([loc]) == loc."""
        assert _svc().calculate_midpoint([loc]) == loc

    @given(valid_locations(), valid_locations())
    def test_commutativity(self, a, b) -> None:
        """PBT-M02: midpoint([a, b]) == midpoint([b, a])."""
        assert _svc().calculate_midpoint([a, b]) == _svc().calculate_midpoint([b, a])

    @given(two_or_more_locations())
    def test_result_lat_in_range(self, locs) -> None:
        """PBT-M03: 결과 lat ∈ [-90, 90]."""
        mid = _svc().calculate_midpoint(locs)
        assert -90.0 <= mid.lat <= 90.0

    @given(two_or_more_locations())
    def test_result_lng_in_range(self, locs) -> None:
        """PBT-M04: 결과 lng ∈ [-180, 180]."""
        mid = _svc().calculate_midpoint(locs)
        assert -180.0 <= mid.lng <= 180.0
