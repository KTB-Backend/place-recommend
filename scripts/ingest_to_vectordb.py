from __future__ import annotations

import json
from pathlib import Path

import chromadb

from core.config import get_settings
from domain.models import Place
from infrastructure.embedding.sbert_embedder import SBERTEmbedder
from infrastructure.vector.chroma_vector_repository import _place_to_metadata


def _build_embedding_text(place: Place) -> str:
    tags_str = " ".join(place.tags)
    return f"{place.name} {place.category} {place.subcategory} {tags_str} {place.description}"


def main() -> None:
    settings = get_settings()
    places_path = Path("data/processed/places.json")

    raw: list[dict] = json.loads(places_path.read_text(encoding="utf-8"))
    places = [Place(**p) for p in raw]
    print(f"Loaded {len(places)} places from {places_path}")

    embedder = SBERTEmbedder(settings.embedding_model)
    texts = [_build_embedding_text(p) for p in places]
    embeddings = embedder.embed(texts)
    print(f"Generated {len(embeddings)} embeddings")

    client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    try:
        client.delete_collection(settings.chroma_collection_name)
    except Exception:
        pass
    collection = client.create_collection(
        settings.chroma_collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=[p.id for p in places],
        embeddings=embeddings,
        documents=texts,
        metadatas=[_place_to_metadata(p) for p in places],
    )
    print(f"[OK] Ingested {len(places)} places into ChromaDB collection '{settings.chroma_collection_name}'")


if __name__ == "__main__":
    main()
