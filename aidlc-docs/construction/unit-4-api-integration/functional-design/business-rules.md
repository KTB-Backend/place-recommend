# Business Rules — Unit 4: API & Integration

## 입력 검증 규칙

| 필드 | 규칙 | HTTP 오류 |
|---|---|---|
| `locations` 길이 | `2 ≤ len ≤ 10` | 422 Unprocessable Entity |
| `LocationInput.lat` | `-90.0 ≤ lat ≤ 90.0` | 422 Unprocessable Entity |
| `LocationInput.lng` | `-180.0 ≤ lng ≤ 180.0` | 422 Unprocessable Entity |
| `query` | `len ≥ 1` (빈 문자열 불가) | 422 Unprocessable Entity |
| `top_k` | `1 ≤ top_k ≤ 20` | 422 Unprocessable Entity |

- 검증 실패 시 FastAPI/Pydantic이 자동으로 422 응답 생성 (별도 핸들러 불필요)

---

## 도메인 예외 → HTTP 상태 코드 매핑

| 도메인 예외 | HTTP 상태 | `detail` 메시지 |
|---|---|---|
| `NoNearbyStationError` | 404 Not Found | "주어진 위치 근처에 역을 찾을 수 없습니다." |
| `NoRecommendationsError` | 404 Not Found | "해당 역 주변 추천 장소를 찾을 수 없습니다." |
| `VectorDBError` | 503 Service Unavailable | "벡터 데이터베이스 오류가 발생했습니다." |
| `InvalidLocationError` | 422 Unprocessable Entity | "유효하지 않은 좌표입니다." |

- 에러 응답 포맷 (Q3=A): `{"detail": "<메시지>"}` — FastAPI 기본 HTTPException 포맷

---

## 라우터별 비즈니스 규칙

### POST /api/v1/midpoint

1. `locations`를 domain `Location` 리스트로 변환
2. `MidpointService.find_meeting_station(locations)` 호출
3. 결과 `Station` 반환 (전체 필드, Q1=A)
4. `NoNearbyStationError` → 404

### POST /api/v1/recommend

1. `locations`를 domain `Location` 리스트로 변환
2. `RecommendationService.recommend(locations, query, top_k)` 호출
3. 결과 `list[Recommendation]` 반환
4. `NoNearbyStationError` → 404
5. `NoRecommendationsError` → 404
6. `VectorDBError` → 503

---

## DI 규칙

- `@lru_cache` 팩토리: 앱 프로세스 수명 동안 인스턴스 1회 생성
- 테스트 시 `app.dependency_overrides`로 교체 — 테스트 종료 후 반드시 `app.dependency_overrides.clear()`
- `get_recommendation_service`는 `@lru_cache` 미적용 — 매 요청마다 새 서비스 인스턴스 생성 (의존성 그래프 유지)

---

## 통합 테스트 규칙 (Q4=B — 전체 Mock)

- `TestClient` + `app.dependency_overrides`로 Mock 주입
- Mock 대상: `get_embedder`, `get_vector_repo`, `get_station_repo`
- 실제 네트워크·파일 I/O 없음 (SBERT 모델 로드, ChromaDB 파일 불필요)
- 테스트 케이스 범위:
  - 정상 경로: `/midpoint`, `/recommend`
  - 오류 경로: `NoNearbyStationError` → 404, `NoRecommendationsError` → 404, `VectorDBError` → 503
  - 검증 오류: locations 1개, query 빈 문자열 → 422
