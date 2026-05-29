from __future__ import annotations

from pydantic import BaseModel, Field

from domain.models import Latitude, Longitude


class LocationInput(BaseModel):
    lat: Latitude
    lng: Longitude


class MidpointRequest(BaseModel):
    locations: list[LocationInput] = Field(..., min_length=2, max_length=10)


class RecommendRequest(BaseModel):
    locations: list[LocationInput] = Field(..., min_length=2, max_length=10)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)
