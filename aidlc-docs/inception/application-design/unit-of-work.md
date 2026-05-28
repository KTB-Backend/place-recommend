# Unit of Work

## 분해 전략

- **유닛 수**: 4개
- **검증 방식**: 유닛별 단위 테스트 통과 후 다음 유닛 진행
- **배포 모델**: 단일 FastAPI 모놀리식 서비스 (패키지 레이아웃은 클린 아키텍처)
- **개발 순서**: Unit 1 → Unit 2 → Unit 3 → Unit 4 (직렬)

---

## Unit 1: Foundation

**목적**: 프로젝트 뼈대 — 도메인 모델, 인터페이스, 예외, 설정

### 포함 컴포넌트
| 컴포넌트 | 파일 |
|---|---|
| Location, Station, Place, Recommendation | `domain/models.py` |
| EmbeddingPort, StationRepository, VectorRepository | `domain/interfaces.py` |
| DomainError 및 하위 예외 4종 | `domain/exceptions.py` |
| Settings (Pydantic BaseSettings) | `core/config.py` |
| 프로젝트 스캐폴딩 | `requirements.txt`, `.env.example`, `__init__.py` 전체 |

### 책임
- 나머지 모든 유닛이 의존하는 도메인 계층 확립
- 인터페이스 계약 정의 (구현체는 Unit 2·3에서 작성)
- 환경 변수 스키마 확정

### 완료 기준
- `pytest tests/unit/test_domain_models.py` 통과
- Pydantic 모델 유효성 검증 (좌표 범위, 필수 필드)
- 인터페이스 ABC 정의 확인

---

## Unit 2: Location & Midpoint

**목적**: 위치 계산 로직 — Haversine 거리, 역 탐색, 중간지점 서비스

### 포함 컴포넌트
| 컴포넌트 | 파일 |
|---|---|
| HardcodedStationRepository | `infrastructure/station/hardcoded_station_repository.py` |
| MidpointService | `application/midpoint_service.py` |
| 단위 테스트 (예시 기반) | `tests/unit/test_midpoint_service.py` |
| 단위 테스트 (예시 기반) | `tests/unit/test_hardcoded_station_repository.py` |
| PBT 전략 정의 | `tests/unit/properties/strategies.py` |
| PBT — 거리/중간지점 | `tests/unit/properties/test_haversine_properties.py` |
| PBT — 중간지점 | `tests/unit/properties/test_midpoint_properties.py` |

### 책임
- Haversine 공식으로 두 좌표 간 거리 계산
- 반경 내 최근접 역 탐색 (서울 26개 역 데이터)
- 다중 좌표 → 지리적 중간지점 계산
- PBT: 거리 불변식(≥0, 대칭), 중간지점 교환법칙 검증

### 완료 기준
- `pytest tests/unit/test_midpoint_service.py tests/unit/test_hardcoded_station_repository.py` 통과
- `pytest tests/unit/properties/` 통과 (Hypothesis PBT)

---

## Unit 3: RAG Engine

**목적**: 임베딩 + 벡터 검색 + 추천 오케스트레이션 + 데이터 인제스트

### 포함 컴포넌트
| 컴포넌트 | 파일 |
|---|---|
| SBERTEmbedder | `infrastructure/embedding/sbert_embedder.py` |
| ChromaVectorRepository | `infrastructure/vector/chroma_vector_repository.py` |
| RecommendationService | `application/recommendation_service.py` |
| 데이터 인제스트 스크립트 | `scripts/ingest_to_vectordb.py` |
| 장소 데이터 | `data/processed/places.json` |
| 단위 테스트 | `tests/unit/test_recommendation_service.py` |
| PBT — Pydantic 라운드트립 | `tests/unit/properties/test_location_properties.py` |

### 책임
- `jhgan/ko-sroberta-multitask` 모델 로드 및 임베딩 생성
- ChromaDB 연결, 컬렉션 관리, 코사인 유사도 검색
- 역 탐색 + 쿼리 생성 + 벡터 검색 오케스트레이션
- 장소 JSON 데이터 → ChromaDB 인제스트

### 완료 기준
- `python scripts/ingest_to_vectordb.py` 성공
- `pytest tests/unit/test_recommendation_service.py` 통과 (ChromaDB mock)
- `pytest tests/unit/properties/test_location_properties.py` 통과

---

## Unit 4: API & Integration

**목적**: FastAPI 앱, DI 설정, 라우터, 통합 테스트

### 포함 컴포넌트
| 컴포넌트 | 파일 |
|---|---|
| FastAPI 앱 + exception handler | `api/main.py` |
| DI 팩토리 함수 (전체) | `api/dependencies.py` |
| v1 라우터 통합 | `api/v1/router.py` |
| MidpointRouter | `api/v1/midpoint.py` |
| RecommendRouter | `api/v1/recommend.py` |
| 통합 테스트 | `tests/integration/test_api.py` |

### 책임
- FastAPI 앱 인스턴스 생성 및 라우터 등록
- 도메인 예외 → HTTP 응답 변환 (`exception_handler`)
- `@lru_cache` 싱글톤 DI 팩토리 구성
- 전체 API E2E 통합 테스트 (`TestClient`)

### 완료 기준
- `uvicorn api.main:app --port 8000` 실행 성공
- `pytest tests/integration/test_api.py` 통과
- `/docs` Swagger UI 접근 가능

---

## 개발 순서 요약

```
Unit 1: Foundation
  ↓ (도메인 모델·인터페이스 완성)
Unit 2: Location & Midpoint
  ↓ (위치 계산 로직·PBT 완성)
Unit 3: RAG Engine
  ↓ (임베딩·벡터검색·인제스트 완성)
Unit 4: API & Integration
  ↓ (전체 스택 통합·E2E 완성)
```
