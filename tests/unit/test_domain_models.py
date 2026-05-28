import pytest
from pydantic import ValidationError

from domain.models import Location, Place, Recommendation


class TestLocation:
    def test_valid_location(self) -> None:
        loc = Location(lat=37.5665, lng=126.9780)
        assert loc.lat == 37.5665
        assert loc.lng == 126.9780

    def test_boundary_values(self) -> None:
        assert Location(lat=-90.0, lng=-180.0)
        assert Location(lat=90.0, lng=180.0)
        assert Location(lat=0.0, lng=0.0)

    def test_lat_too_high(self) -> None:
        with pytest.raises(ValidationError):
            Location(lat=90.001, lng=0.0)

    def test_lat_too_low(self) -> None:
        with pytest.raises(ValidationError):
            Location(lat=-90.001, lng=0.0)

    def test_lng_too_high(self) -> None:
        with pytest.raises(ValidationError):
            Location(lat=0.0, lng=180.001)

    def test_lng_too_low(self) -> None:
        with pytest.raises(ValidationError):
            Location(lat=0.0, lng=-180.001)

    def test_frozen_immutable(self) -> None:
        loc = Location(lat=37.0, lng=127.0)
        with pytest.raises(ValidationError):
            loc.lat = 38.0  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        assert Location(lat=37.0, lng=127.0) == Location(lat=37.0, lng=127.0)

    def test_round_trip_serialization(self) -> None:
        loc = Location(lat=37.5665, lng=126.9780)
        assert Location.model_validate(loc.model_dump()) == loc


class TestPlace:
    def _make_place(self, **overrides: object) -> Place:
        defaults = dict(
            id="p001", name="테스트 카페", description="설명",
            category="카페", subcategory="디저트",
            tags=["데이트", "커플"],
            station="홍대입구", exit_number=9,
            distance_from_station_m=200,
            address="서울 마포구", lat=37.55, lng=126.92,
            rating=4.5, price_range="중간",
        )
        defaults.update(overrides)
        return Place(**defaults)  # type: ignore[arg-type]

    def test_valid_place(self) -> None:
        place = self._make_place()
        assert place.tags == ["데이트", "커플"]

    def test_invalid_price_range(self) -> None:
        with pytest.raises(ValidationError):
            self._make_place(price_range="아주비쌈")

    def test_negative_distance_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._make_place(distance_from_station_m=-1)

    def test_rating_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            self._make_place(rating=5.1)

    def test_round_trip_serialization(self) -> None:
        place = self._make_place()
        assert Place.model_validate(place.model_dump()) == place


class TestRecommendation:
    def _make_recommendation(self, score: float) -> Recommendation:
        place = Place(
            id="p001", name="테스트", description="설명",
            category="카페", subcategory="디저트",
            tags=[], station="강남", exit_number=1,
            distance_from_station_m=100,
            address="서울 강남구", lat=37.49, lng=127.02,
            rating=4.0, price_range="저렴",
        )
        return Recommendation(place=place, similarity_score=score)

    def test_valid_similarity_score(self) -> None:
        rec = self._make_recommendation(0.87)
        assert rec.similarity_score == 0.87

    def test_similarity_score_zero(self) -> None:
        assert self._make_recommendation(0.0)

    def test_similarity_score_one(self) -> None:
        assert self._make_recommendation(1.0)

    def test_similarity_score_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._make_recommendation(-0.01)

    def test_similarity_score_over_one_rejected(self) -> None:
        with pytest.raises(ValidationError):
            self._make_recommendation(1.01)
