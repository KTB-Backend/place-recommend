from __future__ import annotations

from domain.exceptions import NoRecommendationsError
from domain.interfaces import EmbeddingPort, VectorRepository
from domain.models import Location, Recommendation
from application.midpoint_service import MidpointService


class RecommendationService:
    def __init__(
        self,
        midpoint_service: MidpointService,
        embedding_port: EmbeddingPort,
        vector_repository: VectorRepository,
    ) -> None:
        self._midpoint_service = midpoint_service
        self._embedding_port = embedding_port
        self._vector_repository = vector_repository

    def recommend(
        self,
        locations: list[Location],
        query: str,
        top_k: int,
    ) -> list[Recommendation]:
        station = self._midpoint_service.find_meeting_station(locations)
        query_vector = self._embedding_port.embed_query(query)
        results = self._vector_repository.search(query_vector, station.name, top_k)
        if not results:
            raise NoRecommendationsError(
                f"역 '{station.name}' 주변에 '{query}'에 해당하는 추천 장소가 없습니다."
            )
        return results
