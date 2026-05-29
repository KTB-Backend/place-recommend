from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.dependencies import get_embedder, get_station_repo, get_vector_repo
from api.main import app
from domain.exceptions import NoNearbyStationError, NoRecommendationsError, VectorDBError
from domain.interfaces import EmbeddingPort, StationRepository, VectorRepository
from domain.models import Location, Place, Recommendation, Station

# ── 픽스처 데이터 ────────────────────────────────────────────────────────
SAMPLE_STATION = Station(id="gangnam", name="강남", line="2호선", lat=37.4979, lng=127.0276)
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


# ── Mock 구현체 ──────────────────────────────────────────────────────────
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
        if self._mode == "error":
            raise VectorDBError("DB 오류")
        return [SAMPLE_RECOMMENDATION]


# ── 픽스처 ───────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_station():
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo(raise_error=True)
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_no_recommendations():
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo(mode="empty")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_vector_db_error():
    app.dependency_overrides[get_embedder] = lambda: MockEmbedder()
    app.dependency_overrides[get_station_repo] = lambda: MockStationRepo()
    app.dependency_overrides[get_vector_repo] = lambda: MockVectorRepo(mode="error")
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── /midpoint 테스트 ─────────────────────────────────────────────────────
def test_midpoint_happy_path(client: TestClient) -> None:
    resp = client.post("/api/v1/midpoint", json={"locations": LOCATIONS_PAYLOAD})
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == SAMPLE_STATION.id
    assert data["name"] == SAMPLE_STATION.name
    assert data["line"] == SAMPLE_STATION.line
    assert "lat" in data and "lng" in data


def test_midpoint_no_station(client_no_station: TestClient) -> None:
    resp = client_no_station.post("/api/v1/midpoint", json={"locations": LOCATIONS_PAYLOAD})
    assert resp.status_code == 404
    assert "역을 찾을 수 없습니다" in resp.json()["detail"]


def test_midpoint_validation_one_location(client: TestClient) -> None:
    resp = client.post("/api/v1/midpoint", json={"locations": [{"lat": 37.5, "lng": 127.0}]})
    assert resp.status_code == 422


# ── /recommend 테스트 ────────────────────────────────────────────────────
def test_recommend_happy_path(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/recommend",
        json={"locations": LOCATIONS_PAYLOAD, "query": "조용한 카페", "top_k": 1},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["similarity_score"] == pytest.approx(0.87)
    assert data[0]["place"]["name"] == SAMPLE_PLACE.name


def test_recommend_no_recommendations(client_no_recommendations: TestClient) -> None:
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
