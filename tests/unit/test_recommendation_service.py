import pytest
from unittest.mock import MagicMock

from domain.exceptions import InvalidLocationError, NoRecommendationsError
from domain.models import Location, Place, Recommendation, Station
from application.midpoint_service import MidpointService
from application.recommendation_service import RecommendationService


@pytest.fixture
def sample_place() -> Place:
    return Place(
        id="p001", name="테스트 카페", description="조용한 카페",
        category="카페", subcategory="스페셜티",
        tags=["조용한", "작업"], station="강남", exit_number=3,
        distance_from_station_m=350,
        address="서울 강남구", lat=37.4965, lng=127.0289,
        rating=4.5, price_range="중간",
    )


@pytest.fixture
def sample_station() -> Station:
    return Station(id="gangnam", name="강남", line="2호선", lat=37.4979, lng=127.0276)


@pytest.fixture
def service(sample_station: Station, sample_place: Place) -> RecommendationService:
    mock_station_repo = MagicMock()
    mock_station_repo.find_nearest.return_value = sample_station

    mock_embedder = MagicMock()
    mock_embedder.embed_query.return_value = [0.1] * 768

    mock_vector_repo = MagicMock()
    mock_vector_repo.search.return_value = [
        Recommendation(place=sample_place, similarity_score=0.85)
    ]

    return RecommendationService(
        midpoint_service=MidpointService(repository=mock_station_repo),
        embedding_port=mock_embedder,
        vector_repository=mock_vector_repo,
    )


class TestRecommendationService:
    def test_recommend_returns_list(self, service: RecommendationService) -> None:
        results = service.recommend([Location(lat=37.5, lng=127.0)], "조용한 카페", top_k=3)
        assert isinstance(results, list)
        assert len(results) > 0

    def test_recommend_result_is_recommendation(self, service: RecommendationService) -> None:
        results = service.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)
        assert isinstance(results[0], Recommendation)

    def test_recommend_no_results_raises(self, sample_station: Station) -> None:
        mock_station_repo = MagicMock()
        mock_station_repo.find_nearest.return_value = sample_station
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 768
        mock_vector_repo = MagicMock()
        mock_vector_repo.search.return_value = []

        svc = RecommendationService(
            midpoint_service=MidpointService(repository=mock_station_repo),
            embedding_port=mock_embedder,
            vector_repository=mock_vector_repo,
        )
        with pytest.raises(NoRecommendationsError):
            svc.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)

    def test_recommend_calls_correct_station(
        self, service: RecommendationService, sample_station: Station
    ) -> None:
        service.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)
        call_args = service._vector_repository.search.call_args
        assert call_args[0][1] == sample_station.name

    def test_empty_locations_raises(self, service: RecommendationService) -> None:
        with pytest.raises(InvalidLocationError):
            service.recommend([], "카페", top_k=3)
