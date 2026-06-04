from __future__ import annotations

from typing import Any

import httpx
import pytest

from domain.models import Station
from infrastructure.kakao.kakao_place_fetcher import (
    KakaoPlaceFetcher,
    _derive_tags,
    _doc_to_place,
)


class FakeClient:
    def __init__(self, responses: list[httpx.Response]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.closed = False

    def get(self, url: str, params: dict[str, object]) -> httpx.Response:
        self.calls.append((url, params))
        response = self.responses.pop(0)
        response.request = httpx.Request("GET", url, params=params)
        return response

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def station() -> Station:
    return Station(id="gangnam", name="강남", line="2호선", lat=37.4979, lng=127.0276)


def _response(payload: dict[str, object], status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code=status_code, json=payload)


def _doc(**overrides: object) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": "1",
        "place_name": "하마커피",
        "category_name": "음식점 > 카페",
        "distance": "123",
        "road_address_name": "서울 강남구 테헤란로 1",
        "address_name": "서울 강남구 역삼동",
        "y": "37.498",
        "x": "127.028",
    }
    data.update(overrides)
    return data


def _fetcher(fake_client: FakeClient) -> KakaoPlaceFetcher:
    fetcher = KakaoPlaceFetcher("test-key", request_interval_s=0)
    fetcher._client = fake_client  # type: ignore[assignment]
    return fetcher


def test_derive_tags_deduplicates_and_adds_fallback() -> None:
    assert _derive_tags("음식점 > 카페 > 카페", "디저트") == [
        "음식점",
        "카페",
        "디저트",
    ]


def test_doc_to_place_maps_kakao_document(station: Station) -> None:
    place = _doc_to_place(_doc(), station.name, "카페")

    assert place is not None
    assert place.id == "kakao_1"
    assert place.name == "하마커피"
    assert place.station == "강남"
    assert place.subcategory == "카페"
    assert place.distance_from_station_m == 123
    assert place.lat == pytest.approx(37.498)
    assert place.lng == pytest.approx(127.028)


def test_doc_to_place_returns_none_for_invalid_document(station: Station) -> None:
    assert _doc_to_place({"id": "broken"}, station.name, "카페") is None


def test_fetch_by_category_uses_station_coordinates(station: Station) -> None:
    fake_client = FakeClient([_response({"documents": [_doc()]})])
    fetcher = _fetcher(fake_client)

    places = fetcher.fetch_by_category(station, "CE7", size=5)

    assert len(places) == 1
    assert places[0].category == "카페"
    _, params = fake_client.calls[0]
    assert params["category_group_code"] == "CE7"
    assert params["x"] == station.lng
    assert params["y"] == station.lat
    assert params["size"] == 5


def test_fetch_by_keyword_overrides_subcategory(station: Station) -> None:
    fake_client = FakeClient(
        [_response({"documents": [_doc(category_name="음식점 > 술집")]})]
    )
    fetcher = _fetcher(fake_client)

    places = fetcher.fetch_by_keyword(station, "술집", category="술집", size=10)

    assert len(places) == 1
    assert places[0].category == "술집"
    assert places[0].subcategory == "술집"
    _, params = fake_client.calls[0]
    assert params["query"] == "술집"


def test_fetch_for_station_deduplicates_places(station: Station) -> None:
    repeated = _doc(id="same")
    fake_client = FakeClient(
        [
            _response({"documents": [repeated]}),
            _response({"documents": [repeated]}),
            _response({"documents": [repeated]}),
        ]
    )
    fetcher = _fetcher(fake_client)

    places = fetcher.fetch_for_station(station)

    assert len(places) == 1
    assert len(fake_client.calls) == 3


def test_fetch_failure_returns_empty_and_tracks_failure(
    station: Station, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_client = FakeClient(
        [
            _response(
                {"errorType": "BadRequest", "message": "API limit has been exceeded."},
                status_code=400,
            )
        ]
    )
    fetcher = _fetcher(fake_client)

    assert fetcher.fetch_by_category(station, "CE7") == []
    assert fetcher.failure_count == 1
    assert "API limit has been exceeded" in capsys.readouterr().err


def test_close_closes_underlying_client() -> None:
    fake_client = FakeClient([])
    fetcher = _fetcher(fake_client)

    fetcher.close()

    assert fake_client.closed is True
