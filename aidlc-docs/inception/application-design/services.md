# Services

## 서비스 레이어 개요

Application 레이어는 두 개의 서비스로 구성됩니다.
각 서비스는 인프라 구현체에 직접 의존하지 않고, Domain 인터페이스(포트)에만 의존합니다.

---

## MidpointService

- **목적**: 여러 사용자의 출발 위치로부터 지리적 중간지점 계산
- **외부 의존성**: 없음 (순수 계산 서비스)
- **오케스트레이션 흐름**:

```
[locations: list[Location]]
        |
        v
  입력 검증 (len >= 2)
        |
        v
  위도 평균, 경도 평균 계산
        |
        v
  [midpoint: Location]
```

- **API 연결**: `POST /api/v1/midpoint` → `MidpointService.calculate()`

---

## RecommendationService

- **목적**: 중간지점 + 카테고리 기반 RAG 장소 추천 오케스트레이션
- **외부 의존성**: `StationRepository` (포트), `VectorRepository` (포트)
- **오케스트레이션 흐름**:

```
[midpoint: Location, category: str, radius_km, top_k]
        |
        v
  StationRepository.find_nearest(midpoint, radius_km)
        |
        +-- None → NoNearbyStationError
        |
        v
  쿼리 구성: "{역이름} 주변 {category}하기 좋은 장소"
        |
        v
  VectorRepository.search(query_embedding, station_name, top_k)
        |
        +-- 빈 결과 → NoRecommendationsError
        |
        v
  [RecommendResult]
```

- **API 연결**: `POST /api/v1/recommend` → `RecommendationService.recommend()`

---

## DI 구성 (api/dependencies.py)

모든 의존성은 `api/dependencies.py`에서 중앙 관리합니다.
`@lru_cache`로 싱글톤을 보장하며, FastAPI `Depends()`로 라우터에 주입합니다.

```
Settings (core/config.py)
    |
    +──> SBERTEmbedder (EmbeddingPort 구현)
    |         |
    |         +──> ChromaVectorRepository (VectorRepository 구현)
    |
    +──> HardcodedStationRepository (StationRepository 구현)

RecommendationService
    ├── StationRepository (Depends)
    └── VectorRepository  (Depends)

MidpointService
    └── (의존성 없음)
```

---

## Exception Handler 등록 (api/main.py)

FastAPI 앱에 전역 exception handler를 등록하여 도메인 예외를 HTTP 응답으로 변환합니다.

| 예외 클래스 | HTTP 상태 코드 | 응답 메시지 |
|---|---|---|
| `NoNearbyStationError` | 404 | "중간지점 반경 내 지하철역을 찾을 수 없습니다." |
| `NoRecommendationsError` | 404 | "해당 조건에 맞는 장소를 찾을 수 없습니다." |
| `VectorDBError` | 503 | "추천 서비스를 일시적으로 사용할 수 없습니다." |
| `InvalidLocationError` | 422 | "유효하지 않은 좌표입니다." |
