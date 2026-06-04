from __future__ import annotations

from abc import ABC, abstractmethod

from domain.models import Location, Recommendation, Station


class EmbeddingPort(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """텍스트 목록 → 벡터 목록. len(output) == len(texts)."""
        ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 텍스트 → 벡터."""
        ...


class StationRepository(ABC):
    @abstractmethod
    def find_nearest(self, location: Location) -> Station:
        """location 기준 가장 가까운 역 반환. 항상 Station을 반환."""
        ...


    @abstractmethod
    def find_nearest_candidates(
        self,
        location: Location,
        limit: int,
    ) -> list[Station]:
        """Return nearest station candidates ordered by distance."""
        ...

    @abstractmethod
    def find_by_name(self, name: str) -> Station | None:
        """Return a station by user-facing name, or None when not found."""
        ...


class VectorRepository(ABC):
    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]:
        """station_name 필터 + 코사인 유사도로 top_k 추천 반환. 결과 없으면 []."""
        ...
