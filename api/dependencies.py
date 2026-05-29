from __future__ import annotations

from functools import lru_cache

import chromadb
from fastapi import Depends

from application.midpoint_service import MidpointService
from application.recommendation_service import RecommendationService
from core.config import get_settings
from domain.interfaces import EmbeddingPort, StationRepository, VectorRepository
from infrastructure.embedding.sbert_embedder import SBERTEmbedder
from infrastructure.station.hardcoded_station_repository import HardcodedStationRepository
from infrastructure.vector.chroma_vector_repository import ChromaVectorRepository


@lru_cache
def get_embedder() -> EmbeddingPort:
    settings = get_settings()
    return SBERTEmbedder(settings.embedding_model)


@lru_cache
def get_station_repo() -> StationRepository:
    return HardcodedStationRepository()


@lru_cache
def get_vector_repo() -> VectorRepository:
    settings = get_settings()
    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = client.get_or_create_collection(
        name=settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )
    return ChromaVectorRepository(collection)


def get_midpoint_service(
    station_repo: StationRepository = Depends(get_station_repo),
) -> MidpointService:
    return MidpointService(station_repo)


def get_recommendation_service(
    midpoint_svc: MidpointService = Depends(get_midpoint_service),
    embedder: EmbeddingPort = Depends(get_embedder),
    vector_repo: VectorRepository = Depends(get_vector_repo),
) -> RecommendationService:
    return RecommendationService(midpoint_svc, embedder, vector_repo)
