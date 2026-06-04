from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from application.midpoint_service import MidpointService
from domain.exceptions import NoRecommendationsError
from domain.interfaces import EmbeddingPort, VectorRepository
from domain.models import Location, Recommendation, Station

DEFAULT_STATION_CANDIDATE_LIMIT = 8
DEFAULT_STATION_OPTION_LIMIT = 3


@dataclass(frozen=True)
class StationRecommendationOption:
    station: Station
    recommendations: list[Recommendation]


@dataclass(frozen=True)
class RecommendationDecision:
    status: Literal["ok", "station_selection_required"]
    meeting_station: Station
    station: Station | None
    recommendations: list[Recommendation]
    options: list[StationRecommendationOption]


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
        selected_station_id: str | None = None,
    ) -> RecommendationDecision:
        stations = self._midpoint_service.find_meeting_station_candidates(
            locations,
            limit=DEFAULT_STATION_CANDIDATE_LIMIT,
        )
        query_vector = self._embedding_port.embed_query(query)
        meeting_station = stations[0]

        if selected_station_id:
            station = self._find_station_by_id(stations, selected_station_id)
            results = self._vector_repository.search(
                query_vector,
                station.name,
                top_k,
            )
            if not results:
                raise NoRecommendationsError(
                    f"No recommendations found near selected station "
                    f"'{station.name}' for query '{query}'."
                )
            return RecommendationDecision(
                status="ok",
                meeting_station=meeting_station,
                station=station,
                recommendations=results,
                options=[],
            )

        primary_results = self._vector_repository.search(
            query_vector,
            meeting_station.name,
            top_k,
        )
        if primary_results:
            return RecommendationDecision(
                status="ok",
                meeting_station=meeting_station,
                station=meeting_station,
                recommendations=primary_results,
                options=[],
            )

        options = self._find_recommendable_options(
            stations[1:],
            query_vector,
            top_k,
        )
        if options:
            return RecommendationDecision(
                status="station_selection_required",
                meeting_station=meeting_station,
                station=None,
                recommendations=[],
                options=options,
            )

        station_text = ", ".join(station.name for station in stations) or "unknown"
        raise NoRecommendationsError(
            f"No recommendations found near candidate stations "
            f"({station_text}) for query '{query}'."
        )

    def _find_recommendable_options(
        self,
        stations: list[Station],
        query_vector: list[float],
        top_k: int,
    ) -> list[StationRecommendationOption]:
        options: list[StationRecommendationOption] = []
        for station in stations:
            results = self._vector_repository.search(query_vector, station.name, top_k)
            if results:
                options.append(
                    StationRecommendationOption(
                        station=station,
                        recommendations=results,
                    )
                )
            if len(options) == DEFAULT_STATION_OPTION_LIMIT:
                break
        return options

    def _find_station_by_id(
        self,
        stations: list[Station],
        station_id: str,
    ) -> Station:
        for station in stations:
            if station.id == station_id:
                return station
        raise NoRecommendationsError(
            f"Selected station '{station_id}' is not a nearby candidate."
        )

    def locations_from_station_names(self, station_names: list[str]) -> list[Location]:
        return self._midpoint_service.locations_from_station_names(station_names)
