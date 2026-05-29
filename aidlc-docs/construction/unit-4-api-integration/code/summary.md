# Code Summary — Unit 4: API & Integration

## 생성된 파일 목록

### API 계층

| 파일 | 설명 |
|---|---|
| `api/v1/schemas.py` | `LocationInput`, `MidpointRequest`, `RecommendRequest` Pydantic 스키마 |
| `api/dependencies.py` | `@lru_cache` DI 팩토리 — embedder, station_repo, vector_repo, midpoint_service, recommendation_service |
| `api/v1/midpoint.py` | `POST /api/v1/midpoint` 라우터 → `Station` 응답 |
| `api/v1/recommend.py` | `POST /api/v1/recommend` 라우터 → `list[Recommendation]` 응답 |
| `api/main.py` | FastAPI 앱 + 도메인 예외 핸들러 3개 + 라우터 등록 |

### 테스트

| 파일 | 설명 |
|---|---|
| `tests/integration/test_api.py` | Mock 기반 통합 테스트 7개 |

## 테스트 케이스

| 테스트 | 시나리오 | 예상 결과 |
|---|---|---|
| `test_midpoint_happy_path` | 정상 요청 | 200 Station 전체 필드 |
| `test_midpoint_no_station` | `NoNearbyStationError` | 404 |
| `test_midpoint_validation_one_location` | locations 1개 | 422 |
| `test_recommend_happy_path` | 정상 요청 | 200 list[Recommendation] |
| `test_recommend_no_recommendations` | `NoRecommendationsError` | 404 |
| `test_recommend_vector_db_error` | `VectorDBError` | 503 |
| `test_recommend_empty_query` | query="" | 422 |

## 완료 검증 명령어

```bash
# 통합 테스트 (mock — ML 모델 불필요)
pytest tests/integration/test_api.py -v

# 서버 실행
uvicorn api.main:app --reload
```
