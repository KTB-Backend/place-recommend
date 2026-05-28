# Business Logic Model — Unit 3: RAG Engine

## RAG 파이프라인 흐름

```
[API 계층 - Unit 4]
   locations: list[Location]
   query: str
   top_k: int
        │
        ▼
[RecommendationService]
   application/recommendation_service.py
        │
        ├─ 1. MidpointService.find_meeting_station(locations)
        │       └─ HardcodedStationRepository.find_nearest()
        │               └─ Station (예: 강남)
        │
        ├─ 2. EmbeddingPort.embed_query(query)
        │       └─ SBERTEmbedder
        │               └─ list[float] (벡터)
        │
        └─ 3. VectorRepository.search(vector, "강남", top_k)
                └─ ChromaVectorRepository
                        ├─ metadata filter: {"station": "강남"}
                        ├─ cosine similarity
                        └─ list[Recommendation]
```

---

## 인제스트 흐름

```
places.json
    │
    ▼
[ingest_to_vectordb.py]
    ├─ Place 모델 파싱 (Pydantic 유효성 검증)
    ├─ _build_embedding_text() × N
    ├─ SBERTEmbedder.embed(texts) → 배치 벡터
    └─ ChromaDB.add(ids, embeddings, documents, metadatas)
```

---

## 컴포넌트 의존성

```
RecommendationService
    ├── MidpointService (Unit 2)
    ├── EmbeddingPort (ABC) ← SBERTEmbedder (impl)
    └── VectorRepository (ABC) ← ChromaVectorRepository (impl)
```

---

## similarity_score 변환

| ChromaDB distance | similarity_score | 의미 |
|---|---|---|
| 0.0 | 1.0 | 완전 일치 |
| 0.5 | 0.5 | 보통 유사 |
| 1.0 | 0.0 | 전혀 무관 |

`similarity_score = max(0.0, 1.0 - distance)` (음수 방지)
