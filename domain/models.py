from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

# ── 재사용 가능한 타입 별칭 ──────────────────────────────────────────────
Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]
Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]
Rating = Annotated[float, Field(ge=0.0, le=5.0)]
SimilarityScore = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegativeInt = Annotated[int, Field(ge=0)]

PriceRange = Literal["저렴", "중간", "비쌈"]


# ── 도메인 모델 ─────────────────────────────────────────────────────────
class Location(BaseModel, frozen=True):
    lat: Latitude
    lng: Longitude


class Station(BaseModel):
    id: str
    name: str
    line: str
    lat: float
    lng: float


class Place(BaseModel):
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    tags: list[str]
    station: str
    exit_number: int
    distance_from_station_m: NonNegativeInt
    address: str
    lat: float
    lng: float
    rating: Rating
    price_range: PriceRange


class Recommendation(BaseModel, frozen=True):
    place: Place
    # similarity_score = 1.0 - chroma_distance (높을수록 유사, 0~1)
    similarity_score: SimilarityScore
