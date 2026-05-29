# Domain Entities — Unit 4: API & Integration

## API 요청 스키마

### LocationInput

```python
class LocationInput(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0)
    lng: float = Field(..., ge=-180.0, le=180.0)
```

- **유형**: API 입력 Value Object
- **변환**: `LocationInput → domain.Location` (라우터 핸들러 내부)
- **불변식**: `lat ∈ [-90, 90]`, `lng ∈ [-180, 180]`

---

### MidpointRequest

```python
class MidpointRequest(BaseModel):
    locations: list[LocationInput] = Field(..., min_length=2, max_length=10)
```

- **유형**: `POST /api/v1/midpoint` 요청 바디
- **불변식**: `2 ≤ len(locations) ≤ 10`

---

### RecommendRequest

```python
class RecommendRequest(BaseModel):
    locations: list[LocationInput] = Field(..., min_length=2, max_length=10)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)
```

- **유형**: `POST /api/v1/recommend` 요청 바디
- **불변식**: `query`는 빈 문자열 불가, `top_k ∈ [1, 20]`

---

## API 응답 스키마

### MidpointResponse (= domain.Station 재사용)

Q1=A 결정: 도메인 Station 모델 전체 필드를 그대로 응답으로 사용.

```python
# 응답 타입: Station (domain/models.py)
# {
#   "id": "gangnam",
#   "name": "강남",
#   "line": "2호선",
#   "lat": 37.4979,
#   "lng": 127.0276
# }
```

- **response_model**: `Station`

---

### RecommendResponse

```python
# 응답 타입: list[Recommendation] (domain/models.py)
# [
#   {
#     "place": { ...Place fields... },
#     "similarity_score": 0.87
#   },
#   ...
# ]
```

- **response_model**: `list[Recommendation]`

---

## 의존성 컨테이너 (api/dependencies.py)

```python
@lru_cache
def get_settings() -> Settings

@lru_cache
def get_embedder() -> EmbeddingPort          # SBERTEmbedder 반환

@lru_cache
def get_station_repo() -> StationRepository  # HardcodedStationRepository 반환

@lru_cache
def get_vector_repo() -> VectorRepository    # ChromaVectorRepository 반환

def get_midpoint_service(
    station_repo: StationRepository = Depends(get_station_repo)
) -> MidpointService

def get_recommendation_service(
    midpoint_svc: MidpointService = Depends(get_midpoint_service),
    embedder: EmbeddingPort = Depends(get_embedder),
    vector_repo: VectorRepository = Depends(get_vector_repo),
) -> RecommendationService
```

- **싱글톤 보장**: `@lru_cache`가 적용된 팩토리는 앱 수명 동안 1회만 인스턴스 생성
- **테스트 교체**: `app.dependency_overrides[get_embedder] = lambda: MockEmbedder()`
