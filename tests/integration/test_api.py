from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_embedder, get_station_repo, get_vector_repo
from api.main import app
from domain.exceptions import (
    NoNearbyStationError,
    NoRecommendationsError,
    VectorDBError,
)
from domain.interfaces import EmbeddingPort, StationRepository, VectorRepository
from domain.models import Location, Place, Recommendation, Station

SAMPLE_STATION = Station(
    id="gangnam",
    name="강남",
    line="2호선",
    lat=37.4979,
    lng=127.0276,
)
SAMPLE_OPTION_STATION = Station(
    id="oksu",
    name="옥수",
    line="3호선",
    lat=37.5440,
    lng=127.0182,
)
SAMPLE_PLACE = Place(
    id="cafe_1",
    name="테스트 카페",
    description="조용한 분위기의 카페",
    category="카페",
    subcategory="디저트카페",
    tags=["조용한", "데이트", "커플"],
    station="강남",
    exit_number=1,
    distance_from_station_m=200,
    address="서울 강남구 테헤란로 1",
    lat=37.498,
    lng=127.028,
    rating=4.5,
    price_range="중간",
)
SAMPLE_RECOMMENDATION = Recommendation(place=SAMPLE_PLACE, similarity_score=0.87)

LOCATIONS_PAYLOAD = [
    {"lat": 37.5, "lng": 127.0},
    {"lat": 37.6, "lng": 127.1},
]


class MockEmbedder(EmbeddingPort):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 10 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1] * 10


class MockStationRepo(StationRepository):
    def __init__(self, raise_error: bool = False) -> None:
        self._raise_error = raise_error

    def find_nearest(self, location: Location) -> Station:
        if self._raise_error:
            raise NoNearbyStationError("역 없음")
        return SAMPLE_STATION

    def find_nearest_candidates(
        self,
        location: Location,
        limit: int,
    ) -> list[Station]:
        if self._raise_error:
            raise NoNearbyStationError("역 없음")
        return [SAMPLE_STATION, SAMPLE_OPTION_STATION][:limit]

    def find_by_name(self, name: str) -> Station | None:
        if self._raise_error:
            raise NoNearbyStationError("역 없음")
        stations = {SAMPLE_STATION.name: SAMPLE_STATION, "강남역": SAMPLE_STATION}
        return stations.get(name)


class MockVectorRepo(VectorRepository):
    def __init__(self, mode: str = "ok") -> None:
        self._mode = mode

    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]:
        if self._mode == "empty":
            raise NoRecommendationsError("추천 없음")
        if self._mode == "selection":
            if station_name == SAMPLE_STATION.name:
                return []
            return [SAMPLE_RECOMMENDATION]
        if self._mode == "error":
            raise VectorDBError("DB 오류")
        return [SAMPLE_RECOMMENDATION]


@pytest.fixture
def client() -> TestClient:
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_station() -> TestClient:
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo(
        raise_error=True
    )
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_recommendations() -> TestClient:
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo(mode="empty")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_vector_db_error() -> TestClient:
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo(mode="error")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_selection_required() -> TestClient:
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo(mode="selection")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_midpoint_happy_path(client: TestClient) -> None:
    resp = client.post("/api/v1/midpoint", json={"locations": LOCATIONS_PAYLOAD})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == SAMPLE_STATION.id
    assert data["name"] == SAMPLE_STATION.name
    assert data["line"] == SAMPLE_STATION.line
    assert "lat" in data and "lng" in data


def test_midpoint_no_station(client_no_station: TestClient) -> None:
    resp = client_no_station.post(
        "/api/v1/midpoint",
        json={"locations": LOCATIONS_PAYLOAD},
    )
    assert resp.status_code == 404
    assert "역을 찾을 수 없습니다" in resp.json()["detail"]


def test_midpoint_validation_one_location(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/midpoint",
        json={"locations": [{"lat": 37.5, "lng": 127.0}]},
    )
    assert resp.status_code == 422


def test_midpoint_accepts_station_names(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/midpoint",
        json={"stations": ["강남역", "강남"]},
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == SAMPLE_STATION.id


def test_recommend_happy_path(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/recommend",
        json={"locations": LOCATIONS_PAYLOAD, "query": "조용한 카페", "top_k": 1},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["origin_locations"] == LOCATIONS_PAYLOAD
    assert data["station"]["id"] == SAMPLE_STATION.id
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["similarity_score"] == pytest.approx(0.87)
    assert data["recommendations"][0]["place"]["name"] == SAMPLE_PLACE.name


def test_recommend_accepts_station_names(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/recommend",
        json={"stations": ["강남역", "강남"], "query": "조용한 카페", "top_k": 1},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_recommend_returns_station_options_when_primary_empty(
    client_selection_required: TestClient,
) -> None:
    resp = client_selection_required.post(
        "/api/v1/recommend",
        json={"locations": LOCATIONS_PAYLOAD, "query": "조용한 카페", "top_k": 1},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "station_selection_required"
    assert data["origin_locations"] == LOCATIONS_PAYLOAD
    assert data["meeting_station"]["id"] == SAMPLE_STATION.id
    assert data["map_search"]["query"] == "강남 조용한 카페"
    assert data["map_search"]["url"].startswith("https://map.kakao.com/link/search/")
    assert data["options"][0]["station"]["id"] == SAMPLE_OPTION_STATION.id
    assert data["options"][0]["recommendations"]


def test_recommend_selected_station(client_selection_required: TestClient) -> None:
    resp = client_selection_required.post(
        "/api/v1/recommend",
        json={
            "locations": LOCATIONS_PAYLOAD,
            "query": "조용한 카페",
            "top_k": 1,
            "selected_station_id": SAMPLE_OPTION_STATION.id,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["station"]["id"] == SAMPLE_OPTION_STATION.id
    assert len(data["recommendations"]) == 1


def test_recommend_no_recommendations(
    client_no_recommendations: TestClient,
) -> None:
    resp = client_no_recommendations.post(
        "/api/v1/recommend",
        json={"locations": LOCATIONS_PAYLOAD, "query": "조용한 카페"},
    )
    assert resp.status_code == 404
    assert "추천 장소를 찾을 수 없습니다" in resp.json()["detail"]


def test_recommend_vector_db_error(client_vector_db_error: TestClient) -> None:
    resp = client_vector_db_error.post(
        "/api/v1/recommend",
        json={"locations": LOCATIONS_PAYLOAD, "query": "조용한 카페"},
    )
    assert resp.status_code == 503
    assert "벡터 데이터베이스" in resp.json()["detail"]


def test_recommend_empty_query(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/recommend",
        json={"locations": LOCATIONS_PAYLOAD, "query": ""},
    )
    assert resp.status_code == 422
