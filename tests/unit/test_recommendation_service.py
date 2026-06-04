from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from application.midpoint_service import MidpointService
from application.recommendation_service import RecommendationService
from domain.exceptions import InvalidLocationError, NoRecommendationsError
from domain.models import Location, Place, Recommendation, Station


@pytest.fixture
def sample_place() -> Place:
    return Place(
        id="p001",
        name="테스트 카페",
        description="조용한 카페",
        category="카페",
        subcategory="디저트",
        tags=["조용한", "작업"],
        station="강남",
        exit_number=3,
        distance_from_station_m=350,
        address="서울 강남구",
        lat=37.4965,
        lng=127.0289,
        rating=4.5,
        price_range="중간",
    )


@pytest.fixture
def sample_station() -> Station:
    return Station(id="gangnam", name="강남", line="2호선", lat=37.4979, lng=127.0276)


def _recommendation(place: Place) -> Recommendation:
    return Recommendation(place=place, similarity_score=0.85)


@pytest.fixture
def service(sample_station: Station, sample_place: Place) -> RecommendationService:
    mock_station_repo = MagicMock()
    mock_station_repo.find_nearest_candidates.return_value = [sample_station]

    mock_embedder = MagicMock()
    mock_embedder.embed_query.return_value = [0.1] * 768

    mock_vector_repo = MagicMock()
    mock_vector_repo.search.return_value = [_recommendation(sample_place)]

    return RecommendationService(
        midpoint_service=MidpointService(repository=mock_station_repo),
        embedding_port=mock_embedder,
        vector_repository=mock_vector_repo,
    )


class TestRecommendationService:
    def test_recommend_returns_ok_decision(
        self,
        service: RecommendationService,
        sample_station: Station,
    ) -> None:
        decision = service.recommend(
            [Location(lat=37.5, lng=127.0)],
            "조용한 카페",
            top_k=3,
        )

        assert decision.status == "ok"
        assert decision.station == sample_station
        assert len(decision.recommendations) == 1
        assert decision.options == []

    def test_recommend_result_is_recommendation(
        self,
        service: RecommendationService,
    ) -> None:
        decision = service.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)
        assert isinstance(decision.recommendations[0], Recommendation)

    def test_recommend_no_results_raises(self, sample_station: Station) -> None:
        mock_station_repo = MagicMock()
        mock_station_repo.find_nearest_candidates.return_value = [sample_station]
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

    def test_recommend_calls_primary_station(
        self,
        service: RecommendationService,
        sample_station: Station,
    ) -> None:
        service.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)
        call_args = service._vector_repository.search.call_args
        assert call_args[0][1] == sample_station.name

    def test_recommend_returns_three_selectable_station_options(
        self,
        sample_place: Place,
    ) -> None:
        stations = [
            Station(id="primary", name="중간역", line="1호선", lat=37.50, lng=127.00),
            Station(id="s1", name="후보1", line="1호선", lat=37.51, lng=127.01),
            Station(id="s2", name="후보2", line="2호선", lat=37.52, lng=127.02),
            Station(id="s3", name="후보3", line="3호선", lat=37.53, lng=127.03),
            Station(id="s4", name="후보4", line="4호선", lat=37.54, lng=127.04),
        ]
        mock_station_repo = MagicMock()
        mock_station_repo.find_nearest_candidates.return_value = stations
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 768
        mock_vector_repo = MagicMock()
        mock_vector_repo.search.side_effect = [
            [],
            [_recommendation(sample_place)],
            [_recommendation(sample_place)],
            [_recommendation(sample_place)],
            [_recommendation(sample_place)],
        ]

        svc = RecommendationService(
            midpoint_service=MidpointService(repository=mock_station_repo),
            embedding_port=mock_embedder,
            vector_repository=mock_vector_repo,
        )

        decision = svc.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)

        assert decision.status == "station_selection_required"
        assert decision.meeting_station == stations[0]
        assert [option.station.id for option in decision.options] == ["s1", "s2", "s3"]
        assert all(option.recommendations for option in decision.options)

    def test_recommend_skips_option_without_results(self, sample_place: Place) -> None:
        stations = [
            Station(id="primary", name="중간역", line="1호선", lat=37.50, lng=127.00),
            Station(id="empty", name="빈역", line="1호선", lat=37.51, lng=127.01),
            Station(id="filled", name="추천역", line="2호선", lat=37.52, lng=127.02),
        ]
        mock_station_repo = MagicMock()
        mock_station_repo.find_nearest_candidates.return_value = stations
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 768
        mock_vector_repo = MagicMock()
        mock_vector_repo.search.side_effect = [
            [],
            [],
            [_recommendation(sample_place)],
        ]

        svc = RecommendationService(
            midpoint_service=MidpointService(repository=mock_station_repo),
            embedding_port=mock_embedder,
            vector_repository=mock_vector_repo,
        )

        decision = svc.recommend([Location(lat=37.5, lng=127.0)], "카페", top_k=3)

        assert decision.status == "station_selection_required"
        assert [option.station.id for option in decision.options] == ["filled"]

    def test_recommend_selected_station_returns_ok(self, sample_place: Place) -> None:
        stations = [
            Station(id="primary", name="중간역", line="1호선", lat=37.50, lng=127.00),
            Station(id="s1", name="후보1", line="1호선", lat=37.51, lng=127.01),
        ]
        mock_station_repo = MagicMock()
        mock_station_repo.find_nearest_candidates.return_value = stations
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 768
        mock_vector_repo = MagicMock()
        mock_vector_repo.search.return_value = [_recommendation(sample_place)]

        svc = RecommendationService(
            midpoint_service=MidpointService(repository=mock_station_repo),
            embedding_port=mock_embedder,
            vector_repository=mock_vector_repo,
        )

        decision = svc.recommend(
            [Location(lat=37.5, lng=127.0)],
            "카페",
            top_k=3,
            selected_station_id="s1",
        )

        assert decision.status == "ok"
        assert decision.station == stations[1]
        assert len(decision.recommendations) == 1
        assert mock_vector_repo.search.call_args.args[1] == "후보1"

    def test_unknown_selected_station_raises(self, sample_place: Place) -> None:
        mock_station_repo = MagicMock()
        mock_station_repo.find_nearest_candidates.return_value = [
            Station(id="primary", name="중간역", line="1호선", lat=37.50, lng=127.00)
        ]
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 768
        mock_vector_repo = MagicMock()

        svc = RecommendationService(
            midpoint_service=MidpointService(repository=mock_station_repo),
            embedding_port=mock_embedder,
            vector_repository=mock_vector_repo,
        )

        with pytest.raises(NoRecommendationsError):
            svc.recommend(
                [Location(lat=37.5, lng=127.0)],
                "카페",
                top_k=3,
                selected_station_id="missing",
            )

    def test_empty_locations_raises(self, service: RecommendationService) -> None:
        with pytest.raises(InvalidLocationError):
            service.recommend([], "카페", top_k=3)
