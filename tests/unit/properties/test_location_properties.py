import pytest
from hypothesis import given
from pydantic import ValidationError

from domain.models import Location, Place, Recommendation
from tests.unit.properties.strategies import (
    invalid_location_dicts,
    valid_locations,
    valid_places,
    valid_similarity_scores,
)


class TestLocationRoundTrip:
    """PBT-02: Location Pydantic 직렬화 라운드트립 속성."""

    @given(valid_locations())
    def test_serialize_deserialize_identity(self, loc: Location) -> None:
        assert Location.model_validate(loc.model_dump()) == loc

    @given(valid_locations())
    def test_json_round_trip(self, loc: Location) -> None:
        assert Location.model_validate_json(loc.model_dump_json()) == loc


class TestLocationInvariants:
    """PBT-03: Location 좌표 범위 불변식."""

    @given(valid_locations())
    def test_valid_location_always_in_range(self, loc: Location) -> None:
        assert -90.0 <= loc.lat <= 90.0
        assert -180.0 <= loc.lng <= 180.0

    @given(invalid_location_dicts())
    def test_invalid_location_always_raises(self, data: dict[str, float]) -> None:
        with pytest.raises(ValidationError):
            Location(**data)


class TestRecommendationInvariants:
    """PBT-03: Recommendation similarity_score 범위 불변식."""

    @given(valid_places(), valid_similarity_scores())
    def test_similarity_score_always_in_range(
        self, place: Place, score: float
    ) -> None:
        rec = Recommendation(place=place, similarity_score=score)
        assert 0.0 <= rec.similarity_score <= 1.0

    @given(valid_places(), valid_similarity_scores())
    def test_higher_score_means_more_similar(
        self, place: Place, score: float
    ) -> None:
        # 유사도가 높을수록 더 유사한 결과임을 불변식으로 표현
        rec = Recommendation(place=place, similarity_score=score)
        assert rec.similarity_score >= 0.0


class TestPlaceRoundTrip:
    """PBT-02: Place Pydantic 직렬화 라운드트립 속성."""

    @given(valid_places())
    def test_serialize_deserialize_identity(self, place: Place) -> None:
        assert Place.model_validate(place.model_dump()) == place

    @given(valid_places())
    def test_tags_always_list(self, place: Place) -> None:
        """PBT-03: tags는 항상 list[str]."""
        assert isinstance(place.tags, list)
        assert all(isinstance(t, str) for t in place.tags)
