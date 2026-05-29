# Code Generation Plan — Unit 4: API & Integration

## 구현 대상 스토리
- FR-01: 중간지점 계산 API (`POST /api/v1/midpoint`)
- FR-02: 장소 추천 API (`POST /api/v1/recommend`)
- FR-03: 다중 중간지점 계산 API (locations 2~10개 지원)
- NFR-03: 단위/통합 테스트

## 의존성
- Unit 1: `domain/models.py`, `domain/exceptions.py`, `domain/interfaces.py`, `core/config.py`
- Unit 2: `application/midpoint_service.py`, `infrastructure/station/hardcoded_station_repository.py`
- Unit 3: `application/recommendation_service.py`, `infrastructure/embedding/sbert_embedder.py`, `infrastructure/vector/chroma_vector_repository.py`

## 생성 파일 목록

| # | 파일 | 유형 |
|---|---|---|
| 1 | `api/v1/schemas.py` | API 요청/응답 스키마 |
| 2 | `api/dependencies.py` | DI 컨테이너 |
| 3 | `api/v1/midpoint.py` | Midpoint 라우터 |
| 4 | `api/v1/recommend.py` | Recommend 라우터 |
| 5 | `api/main.py` | FastAPI 앱 진입점 |
| 6 | `tests/integration/test_api.py` | 통합 테스트 (전체 Mock) |
| 7 | `aidlc-docs/construction/unit-4-api-integration/code/summary.md` | 코드 요약 |

---

## 실행 체크리스트

- [x] Step 1: `api/v1/schemas.py`
  - [x] `LocationInput(BaseModel)` — lat/lng, Field 범위 검증
  - [x] `MidpointRequest(BaseModel)` — `locations: list[LocationInput]`, min_length=2, max_length=10
  - [x] `RecommendRequest(BaseModel)` — locations, `query: str` (필수, min_length=1), `top_k: int` (기본 3, 1~20)

- [x] Step 2: `api/dependencies.py`
  - [x] `get_settings()` — `@lru_cache`, Settings 반환
  - [x] `get_embedder()` — `@lru_cache`, SBERTEmbedder 반환
  - [x] `get_station_repo()` — `@lru_cache`, HardcodedStationRepository 반환
  - [x] `get_vector_repo()` — `@lru_cache`, ChromaVectorRepository 반환
  - [x] `get_midpoint_service()` — `Depends(get_station_repo)`, MidpointService 반환
  - [x] `get_recommendation_service()` — midpoint_svc + embedder + vector_repo, RecommendationService 반환

- [x] Step 3: `api/v1/midpoint.py`
  - [x] `router = APIRouter()`
  - [x] `POST /midpoint` — `MidpointRequest` 입력, `Station` 응답
  - [x] LocationInput → domain Location 변환
  - [x] 예외는 main.py 전역 핸들러에서 처리

- [x] Step 4: `api/v1/recommend.py`
  - [x] `router = APIRouter()`
  - [x] `POST /recommend` — `RecommendRequest` 입력, `list[Recommendation]` 응답
  - [x] LocationInput → domain Location 변환
  - [x] 예외는 main.py 전역 핸들러에서 처리

- [x] Step 5: `api/main.py`
  - [x] `FastAPI()` 앱 생성 (title, version)
  - [x] 도메인 예외 핸들러 3개 등록 (`NoNearbyStationError`, `NoRecommendationsError`, `VectorDBError`)
  - [x] 라우터 등록 (`prefix="/api/v1"`)

- [x] Step 6: `tests/integration/test_api.py`
  - [x] `MockEmbedder` — 고정 벡터 반환
  - [x] `MockVectorRepo` — 고정 `Recommendation` 1개 반환 / `NoRecommendationsError` 발생 variant
  - [x] `MockStationRepo` — 고정 `Station` 반환 / `NoNearbyStationError` 발생 variant
  - [x] `client` fixture — `app.dependency_overrides` 주입 → `TestClient` → clear
  - [x] `test_midpoint_happy_path` — 200, Station 필드 검증
  - [x] `test_midpoint_no_station` — `NoNearbyStationError` → 404
  - [x] `test_midpoint_validation_one_location` — locations 1개 → 422
  - [x] `test_recommend_happy_path` — 200, list[Recommendation] 검증
  - [x] `test_recommend_no_recommendations` — `NoRecommendationsError` → 404
  - [x] `test_recommend_vector_db_error` — `VectorDBError` → 503
  - [x] `test_recommend_empty_query` — query="" → 422

- [x] Step 7: `aidlc-docs/construction/unit-4-api-integration/code/summary.md`

---

## 완료 검증

```bash
# 통합 테스트 (mock — ML 모델 불필요)
pytest tests/integration/test_api.py -v

# 서버 실행 (선택)
uvicorn api.main:app --reload
```
