from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_midpoint_service
from api.v1.schemas import MidpointRequest
from application.midpoint_service import MidpointService
from domain.models import Location, Station

router = APIRouter()


@router.post("/midpoint", response_model=Station)
async def midpoint(
    body: MidpointRequest,
    service: MidpointService = Depends(get_midpoint_service),
) -> Station:
    locations = [Location(lat=loc.lat, lng=loc.lng) for loc in body.locations]
    return service.find_meeting_station(locations)
