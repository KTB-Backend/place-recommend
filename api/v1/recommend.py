from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_recommendation_service
from api.v1.schemas import (
    MapSearchLink,
    RecommendOkResponse,
    RecommendRequest,
    RecommendSelectionResponse,
    StationRecommendationOption,
)
from application.recommendation_service import RecommendationService
from domain.models import Location

router = APIRouter()


def _build_kakao_map_search_link(station_name: str, query: str) -> MapSearchLink:
    search_query = f"{station_name} {query}"
    return MapSearchLink(
        label=f"카카오맵에서 {search_query} 검색",
        query=search_query,
        url=f"https://map.kakao.com/link/search/{quote(search_query)}",
    )


@router.post(
    "/recommend",
    response_model=RecommendOkResponse | RecommendSelectionResponse,
)
async def recommend(
    body: RecommendRequest,
    service: RecommendationService = Depends(get_recommendation_service),  # noqa: B008
) -> RecommendOkResponse | RecommendSelectionResponse:
    if body.stations:
        locations = service.locations_from_station_names(body.stations)
    elif body.locations:
        locations = [Location(lat=loc.lat, lng=loc.lng) for loc in body.locations]
    else:
        raise HTTPException(
            status_code=422,
            detail="Either stations or locations must be provided.",
        )
    decision = service.recommend(
        locations,
        body.query,
        body.top_k,
        selected_station_id=body.selected_station_id,
    )
    if decision.status == "ok":
        assert decision.station is not None
        return RecommendOkResponse(
            meeting_station=decision.meeting_station,
            station=decision.station,
            recommendations=decision.recommendations,
        )
    return RecommendSelectionResponse(
        meeting_station=decision.meeting_station,
        map_search=_build_kakao_map_search_link(
            decision.meeting_station.name,
            body.query,
        ),
        options=[
            StationRecommendationOption(
                station=option.station,
                recommendations=option.recommendations,
            )
            for option in decision.options
        ],
    )
