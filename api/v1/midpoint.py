from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_midpoint_service
from api.v1.schemas import MidpointRequest
from application.midpoint_service import MidpointService
from domain.models import Location, Station

router = APIRouter()


@router.post("/midpoint", response_model=Station)
async def midpoint(
    body: MidpointRequest,
    service: MidpointService = Depends(get_midpoint_service),  # noqa: B008
) -> Station:
    if body.stations:
        locations = service.locations_from_station_names(body.stations)
    elif body.locations:
        locations = [Location(lat=loc.lat, lng=loc.lng) for loc in body.locations]
    else:
        raise HTTPException(
            status_code=422,
            detail="Either stations or locations must be provided.",
        )
    return service.find_meeting_station(locations)
