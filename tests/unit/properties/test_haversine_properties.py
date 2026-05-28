import pytest
from hypothesis import given

from infrastructure.station.hardcoded_station_repository import _haversine
from tests.unit.properties.strategies import valid_locations


class TestHaversineProperties:
    """PBT: Haversine 거리 불변식."""

    @given(valid_locations(), valid_locations())
    def test_non_negative(self, a, b) -> None:
        """PBT-H01: 거리는 항상 0 이상."""
        assert _haversine(a.lat, a.lng, b.lat, b.lng) >= 0.0

    @given(valid_locations(), valid_locations())
    def test_symmetry(self, a, b) -> None:
        """PBT-H02: distance(a, b) == distance(b, a)."""
        assert _haversine(a.lat, a.lng, b.lat, b.lng) == pytest.approx(
            _haversine(b.lat, b.lng, a.lat, a.lng), rel=1e-9
        )

    @given(valid_locations())
    def test_self_distance_zero(self, a) -> None:
        """PBT-H03: 동일 좌표 거리 == 0."""
        assert _haversine(a.lat, a.lng, a.lat, a.lng) == pytest.approx(0.0, abs=1e-9)

    @given(valid_locations(), valid_locations())
    def test_bounded_by_half_circumference(self, a, b) -> None:
        """PBT-H04: 지구 반둘레(≈20015km) 초과 불가."""
        assert _haversine(a.lat, a.lng, b.lat, b.lng) <= 20016.0
