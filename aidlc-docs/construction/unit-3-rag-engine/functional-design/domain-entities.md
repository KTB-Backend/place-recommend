# Domain Entities — Unit 3: RAG Engine

## 핵심 컴포넌트

### SBERTEmbedder (EmbeddingPort 구현체)

```python
class SBERTEmbedder(EmbeddingPort):
    model_name: str  # "jhgan/ko-sroberta-multitask"

    def embed(self, texts: list[str]) -> list[list[float]]
    def embed_query(self, text: str) -> list[float]
```

### ChromaVectorRepository (VectorRepository 구현체)

```python
class ChromaVectorRepository(VectorRepository):
    collection: chromadb.Collection

    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]
```

### RecommendationService

```python
class RecommendationService:
    def __init__(
        self,
        midpoint_service: MidpointService,
        embedding_port: EmbeddingPort,
        vector_repository: VectorRepository,
    ) -> None: ...

    def recommend(
        self,
        locations: list[Location],
        query: str,
        top_k: int,
    ) -> list[Recommendation]
```

---

## places.json 스키마

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "category": "레스토랑 | 카페 | 바 | 술집",
  "subcategory": "string",
  "tags": ["string"],
  "station": "string",
  "exit_number": "int (1~15)",
  "distance_from_station_m": "int (>=0)",
  "address": "string",
  "lat": "float (37.4~37.7)",
  "lng": "float (126.8~127.2)",
  "rating": "float (0.0~5.0)",
  "price_range": "저렴 | 중간 | 비쌈"
}
```

---

## 임베딩 텍스트 구성 (Q1 결정: A)

```python
def _build_embedding_text(place: Place) -> str:
    tags_str = " ".join(place.tags)
    return f"{place.name} {place.category} {place.subcategory} {tags_str} {place.description}"
```

**예시**:
- 입력: `name="카페 드 파리"`, `category="카페"`, `subcategory="디저트카페"`, `tags=["조용한","데이트"]`, `description="파리풍 분위기"`
- 결과: `"카페 드 파리 카페 디저트카페 조용한 데이트 파리풍 분위기"`

---

## 쿼리 입력 형태 (Q2 결정: B — 자유 텍스트)

- API 입력: `query: str` (예: `"조용한 분위기 카페"`, `"삼겹살 먹고 싶어"`)
- `embed_query(query)` → 벡터 → ChromaDB 코사인 유사도 검색
