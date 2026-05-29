from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies import get_recommendation_service
from api.v1.schemas import RecommendRequest
from application.recommendation_service import RecommendationService
from domain.models import Location, Recommendation

router = APIRouter()


@router.post("/recommend", response_model=list[Recommendation])
async def recommend(
    body: RecommendRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> list[Recommendation]:
    locations = [Location(lat=loc.lat, lng=loc.lng) for loc in body.locations]
    return service.recommend(locations, body.query, body.top_k)
