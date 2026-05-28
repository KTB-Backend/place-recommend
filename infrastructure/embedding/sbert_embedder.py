from __future__ import annotations

from sentence_transformers import SentenceTransformer

from domain.interfaces import EmbeddingPort


class SBERTEmbedder(EmbeddingPort):
    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, convert_to_numpy=True).tolist()  # type: ignore[return-value]

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode(text, convert_to_numpy=True).tolist()  # type: ignore[return-value]
