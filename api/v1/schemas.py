from __future__ import annotations

from pydantic import BaseModel, Field

from domain.models import Latitude, Longitude, Recommendation, Station


class LocationInput(BaseModel):
    lat: Latitude
    lng: Longitude


class MidpointRequest(BaseModel):
    locations: list[LocationInput] | None = Field(
        default=None,
        min_length=2,
        max_length=10,
    )
    stations: list[str] | None = Field(default=None, min_length=2, max_length=10)


class RecommendRequest(BaseModel):
    locations: list[LocationInput] | None = Field(
        default=None,
        min_length=2,
        max_length=10,
    )
    stations: list[str] | None = Field(default=None, min_length=2, max_length=10)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)
    selected_station_id: str | None = None


class StationRecommendationOption(BaseModel):
    station: Station
    recommendations: list[Recommendation]


class MapSearchLink(BaseModel):
    label: str
    query: str
    url: str


class RecommendOkResponse(BaseModel):
    status: str = "ok"
    origin_locations: list[LocationInput]
    meeting_station: Station
    station: Station
    recommendations: list[Recommendation]


class RecommendSelectionResponse(BaseModel):
    status: str = "station_selection_required"
    origin_locations: list[LocationInput]
    meeting_station: Station
    map_search: MapSearchLink
    options: list[StationRecommendationOption]
