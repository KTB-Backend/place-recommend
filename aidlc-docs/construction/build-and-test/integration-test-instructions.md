# Integration Test Instructions

## 목적

Unit 4 API 계층과 Unit 1~3 애플리케이션/인프라 계층이 올바르게 연동되는지 검증.  
TestClient + `app.dependency_overrides` Mock 방식으로 외부 의존성(SBERT, ChromaDB) 없이 실행.

## 통합 테스트 위치

```
tests/integration/
└── test_api.py    # FastAPI TestClient 기반 통합 테스트 7개
```

## 통합 테스트 시나리오

| # | 테스트명 | 시나리오 | 검증 항목 |
|---|---|---|---|
| 1 | `test_midpoint_happy_path` | 정상 locations 2개 → 역 반환 | 200, Station 전체 필드 |
| 2 | `test_midpoint_no_station` | StationRepo가 NoNearbyStationError 발생 | 404, detail 메시지 |
| 3 | `test_midpoint_validation_one_location` | locations 1개 전송 | 422 |
| 4 | `test_recommend_happy_path` | 정상 query 요청 → 추천 목록 | 200, similarity_score 검증 |
| 5 | `test_recommend_no_recommendations` | VectorRepo가 NoRecommendationsError 발생 | 404, detail 메시지 |
| 6 | `test_recommend_vector_db_error` | VectorRepo가 VectorDBError 발생 | 503, detail 메시지 |
| 7 | `test_recommend_empty_query` | query="" 전송 | 422 |

## 실행 방법

### 1. 통합 테스트만 실행

```bash
pytest tests/integration/ -v
```

### 2. 단위 + 통합 전체 실행

```bash
pytest tests/ -v
```

### 3. 커버리지 포함 전체 실행

```bash
pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=80
```

## 예상 결과

- 7개 통합 테스트 전체 PASS
- ML 모델 로드 없이 실행 (Mock 사용)
- 실행 시간: 10초 내

## 의존성 연동 검증 포인트

| 검증 포인트 | 방식 |
|---|---|
| MidpointRequest → MidpointService 연결 | `get_station_repo` override로 확인 |
| 전역 예외 핸들러 동작 | NoNearbyStationError → 404 검증 |
| 응답 직렬화 (Station, Recommendation) | response_model 필드 검증 |
| Pydantic 입력 검증 (422) | 잘못된 요청 전송으로 확인 |

## 실패 시 대응

1. `pytest tests/integration/test_api.py -v -s` — stdout 출력 켜기
2. 특정 테스트 단독 실행: `pytest tests/integration/test_api.py::test_midpoint_happy_path -v`
3. `app.dependency_overrides`가 `clear()` 되었는지 확인 (fixture 정리)
