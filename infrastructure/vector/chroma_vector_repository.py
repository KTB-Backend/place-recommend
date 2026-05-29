from __future__ import annotations

import json

import chromadb

from domain.interfaces import VectorRepository
from domain.models import Place, Recommendation


def _place_to_metadata(place: Place) -> dict:
    return {
        "place_id": place.id,
        "name": place.name,
        "description": place.description,
        "category": place.category,
        "subcategory": place.subcategory,
        "tags": json.dumps(place.tags, ensure_ascii=False),
        "station": place.station,
        "exit_number": place.exit_number,
        "distance_from_station_m": place.distance_from_station_m,
        "address": place.address,
        "lat": place.lat,
        "lng": place.lng,
        "rating": place.rating,
        "price_range": place.price_range,
    }


def _metadata_to_place(meta: dict) -> Place:
    return Place(
        id=meta["place_id"],
        name=meta["name"],
        description=meta["description"],
        category=meta["category"],
        subcategory=meta["subcategory"],
        tags=json.loads(meta["tags"]),
        station=meta["station"],
        exit_number=int(meta["exit_number"]),
        distance_from_station_m=int(meta["distance_from_station_m"]),
        address=meta["address"],
        lat=float(meta["lat"]),
        lng=float(meta["lng"]),
        rating=float(meta["rating"]),
        price_range=meta["price_range"],
    )


class ChromaVectorRepository(VectorRepository):
    def __init__(self, collection: chromadb.Collection) -> None:
        self._collection = collection

    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]:
        # n_results가 실제 매칭 문서 수를 초과하면 ChromaDB가 오류를 발생시키므로 clamp
        try:
            count = self._collection.count()
            n = max(1, min(top_k, count))
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n,
                where={"station": station_name},
                include=["metadatas", "distances"],
            )
        except Exception:
            return []

        metadatas: list[dict] = results["metadatas"][0]  # type: ignore[index]
        distances: list[float] = results["distances"][0]  # type: ignore[index]

        recommendations = []
        for meta, dist in zip(metadatas, distances):
            place = _metadata_to_place(meta)
            score = max(0.0, 1.0 - dist)
            recommendations.append(Recommendation(place=place, similarity_score=score))

        return recommendations
