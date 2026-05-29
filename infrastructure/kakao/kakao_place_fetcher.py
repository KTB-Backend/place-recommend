from __future__ import annotations

import time

import httpx

from domain.models import Place, Station


_CATEGORY_MAP: dict[str, str] = {
    "FD6": "레스토랑",
    "CE7": "카페",
}


def _derive_tags(category_name: str, fallback: str) -> list[str]:
    parts = [p.strip() for p in category_name.split(">") if p.strip()]
    seen: set[str] = set()
    tags: list[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            tags.append(p)
    if fallback not in seen:
        tags.append(fallback)
    return tags[:6]


def _build_description(place_name: str, category_name: str) -> str:
    parts = [p.strip() for p in category_name.split(">") if p.strip()]
    detail = " > ".join(parts[1:]) if len(parts) > 1 else parts[0] if parts else ""
    return f"{place_name}. {detail} 업소. (카카오 지도 데이터)"


def _doc_to_place(doc: dict, station_name: str, category: str) -> Place | None:
    try:
        cat_name: str = doc.get("category_name", "")
        parts = [p.strip() for p in cat_name.split(">") if p.strip()]
        subcategory = parts[-1] if len(parts) > 1 else category

        return Place(
            id=f"kakao_{doc['id']}",
            name=doc["place_name"],
            description=_build_description(doc["place_name"], cat_name),
            category=category,
            subcategory=subcategory,
            tags=_derive_tags(cat_name, subcategory),
            station=station_name,
            exit_number=1,
            distance_from_station_m=max(0, int(doc.get("distance") or 0)),
            address=doc.get("road_address_name") or doc.get("address_name", ""),
            lat=float(doc["y"]),
            lng=float(doc["x"]),
            rating=0.0,
            price_range="중간",
        )
    except (KeyError, ValueError, TypeError):
        return None


class KakaoPlaceFetcher:
    """카카오 로컬 API로 역 주변 장소를 수집하는 어댑터."""

    _BASE = "https://dapi.kakao.com/v2/local/search"

    def __init__(self, api_key: str, ssl_verify: bool = True) -> None:
        self._client = httpx.Client(
            headers={"Authorization": f"KakaoAK {api_key}"},
            verify=ssl_verify,
            timeout=10.0,
        )

    def close(self) -> None:
        self._client.close()

    def _get(self, endpoint: str, params: dict) -> dict:
        resp = self._client.get(f"{self._BASE}/{endpoint}.json", params=params)
        resp.raise_for_status()
        return resp.json()

    def fetch_by_category(
        self,
        station: Station,
        code: str,
        size: int = 15,
    ) -> list[Place]:
        category = _CATEGORY_MAP.get(code, "레스토랑")
        try:
            data = self._get("category", {
                "category_group_code": code,
                "x": station.lng,
                "y": station.lat,
                "radius": 500,
                "size": size,
                "sort": "distance",
            })
        except Exception:
            return []

        results: list[Place] = []
        for doc in data.get("documents", []):
            place = _doc_to_place(doc, station.name, category)
            if place:
                results.append(place)
        return results

    def fetch_by_keyword(
        self,
        station: Station,
        keyword: str,
        category: str = "술집",
        size: int = 10,
    ) -> list[Place]:
        try:
            data = self._get("keyword", {
                "query": keyword,
                "x": station.lng,
                "y": station.lat,
                "radius": 500,
                "size": size,
                "sort": "distance",
            })
        except Exception:
            return []

        results: list[Place] = []
        for doc in data.get("documents", []):
            cat_name: str = doc.get("category_name", "")
            parts = [p.strip() for p in cat_name.split(">") if p.strip()]
            subcategory = parts[-1] if len(parts) > 1 else keyword
            place = _doc_to_place(doc, station.name, category)
            if place:
                # subcategory를 키워드 기반으로 오버라이드
                place = Place(**{**place.model_dump(), "subcategory": subcategory})
                results.append(place)
        return results

    def fetch_for_station(self, station: Station) -> list[Place]:
        """역 주변 음식점·카페·술집을 수집하고 중복 제거 후 반환."""
        seen: set[str] = set()
        result: list[Place] = []

        candidates = [
            *self.fetch_by_category(station, "FD6", size=15),  # 음식점
            *self.fetch_by_category(station, "CE7", size=15),  # 카페
            *self.fetch_by_keyword(station, "술집", size=10),
        ]

        for place in candidates:
            if place.id not in seen:
                seen.add(place.id)
                result.append(place)

        return result
