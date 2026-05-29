# Business Logic Model — Unit 4: API & Integration

## HTTP 요청 흐름

### POST /api/v1/midpoint

```
[HTTP Client]
  POST /api/v1/midpoint
  {"locations": [{"lat": 37.5, "lng": 127.0}, {"lat": 37.6, "lng": 127.1}]}
        │
        ▼
[FastAPI — MidpointRouter]
  1. Pydantic 자동 검증 (MidpointRequest)
     ├─ locations 길이: 2 ≤ n ≤ 10  → 실패 시 422
     └─ lat/lng 범위 검증           → 실패 시 422
        │
        ▼
  2. LocationInput → domain.Location 변환
        │
        ▼
  3. MidpointService.find_meeting_station(locations)
        │
        ├─ NoNearbyStationError → raise HTTPException(404)
        └─ OK
           │
           ▼
  4. Station 반환 (전체 필드)
     {"id": "...", "name": "...", "line": "...", "lat": ..., "lng": ...}
```

---

### POST /api/v1/recommend

```
[HTTP Client]
  POST /api/v1/recommend
  {"locations": [...], "query": "조용한 카페", "top_k": 3}
        │
        ▼
[FastAPI — RecommendRouter]
  1. Pydantic 자동 검증 (RecommendRequest)
     ├─ locations 길이: 2 ≤ n ≤ 10   → 실패 시 422
     ├─ query: len ≥ 1               → 실패 시 422
     └─ top_k: 1 ≤ n ≤ 20           → 실패 시 422
        │
        ▼
  2. LocationInput → domain.Location 변환
        │
        ▼
  3. RecommendationService.recommend(locations, query, top_k)
        │
        ├─ NoNearbyStationError    → raise HTTPException(404)
        ├─ NoRecommendationsError  → raise HTTPException(404)
        ├─ VectorDBError           → raise HTTPException(503)
        └─ OK
           │
           ▼
  4. list[Recommendation] 반환
     [{"place": {...}, "similarity_score": 0.87}, ...]
```

---

## 의존성 주입 구조

```
FastAPI App (api/main.py)
    │
    ├─ lifespan: 앱 시작/종료 훅 (필요시)
    ├─ include_router(midpoint_router, prefix="/api/v1")
    ├─ include_router(recommend_router, prefix="/api/v1")
    └─ exception_handler 등록 (도메인 예외 → HTTPException 변환)

api/dependencies.py
    ├─ get_settings()         @lru_cache → Settings (singleton)
    ├─ get_embedder()         @lru_cache → SBERTEmbedder (singleton)
    ├─ get_station_repo()     @lru_cache → HardcodedStationRepository (singleton)
    ├─ get_vector_repo()      @lru_cache → ChromaVectorRepository (singleton)
    ├─ get_midpoint_service() → MidpointService (per-request)
    └─ get_recommendation_service() → RecommendationService (per-request)

api/v1/midpoint.py
    └─ router = APIRouter()
       └─ POST /midpoint
          └─ Depends(get_midpoint_service)

api/v1/recommend.py
    └─ router = APIRouter()
       └─ POST /recommend
          └─ Depends(get_recommendation_service)
```

---

## 통합 테스트 구조 (Mock 기반)

```
tests/integration/test_api.py
    │
    ├─ conftest.py
    │   ├─ MockEmbedder   (EmbeddingPort 구현 — 고정 벡터 반환)
    │   ├─ MockVectorRepo (VectorRepository 구현 — 고정 Recommendation 반환)
    │   └─ MockStationRepo (StationRepository 구현 — 고정 Station 반환)
    │
    ├─ @pytest.fixture client
    │   └─ app.dependency_overrides 설정 → TestClient 생성 → yield → clear()
    │
    ├─ test_midpoint_happy_path          POST /midpoint → 200 Station
    ├─ test_midpoint_no_station          Mock raises NoNearbyStationError → 404
    ├─ test_midpoint_validation_one_loc  locations=[1개] → 422
    ├─ test_recommend_happy_path         POST /recommend → 200 list[Recommendation]
    ├─ test_recommend_no_recommendations Mock raises NoRecommendationsError → 404
    ├─ test_recommend_vector_db_error    Mock raises VectorDBError → 503
    └─ test_recommend_empty_query        query="" → 422
```

---

## 예외 핸들러 등록 방식

```python
# api/main.py
@app.exception_handler(NoNearbyStationError)
async def no_station_handler(request, exc):
    raise HTTPException(status_code=404, detail="주어진 위치 근처에 역을 찾을 수 없습니다.")

@app.exception_handler(NoRecommendationsError)
async def no_recs_handler(request, exc):
    raise HTTPException(status_code=404, detail="해당 역 주변 추천 장소를 찾을 수 없습니다.")

@app.exception_handler(VectorDBError)
async def vector_db_handler(request, exc):
    raise HTTPException(status_code=503, detail="벡터 데이터베이스 오류가 발생했습니다.")
```
