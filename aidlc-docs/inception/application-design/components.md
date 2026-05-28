# Components

## 아키텍처 레이어 구조 (플랫 패키지 레이아웃)

```
where/
├── domain/          # 도메인 모델 + 인터페이스(포트)
├── application/     # 애플리케이션 서비스 (오케스트레이션)
├── infrastructure/  # 인터페이스 구현체 (어댑터)
├── api/             # FastAPI 진입점 + DI 설정
├── core/            # 설정 (Pydantic Settings)
├── data/            # 장소 JSON 데이터
├── scripts/         # 데이터 수집·인제스트 스크립트
└── tests/           # 단위·통합·PBT 테스트
```

---

## 컴포넌트 목록

### [DOMAIN-01] Location
- **레이어**: domain
- **유형**: Value Object (Pydantic BaseModel, frozen)
- **책임**: 위도/경도 좌표 쌍을 불변 값 객체로 표현. 입력 유효성 검증 포함.
- **파일**: `domain/models.py`

---

### [DOMAIN-02] Station
- **레이어**: domain
- **유형**: Entity (Pydantic BaseModel)
- **책임**: 지하철역 정보를 표현. 이름, 호선, 좌표 포함.
- **파일**: `domain/models.py`

---

### [DOMAIN-03] Place
- **레이어**: domain
- **유형**: Entity (Pydantic BaseModel)
- **책임**: 추천 장소 정보 표현. 카테고리, 주소, 평점, 가격대, 역 정보 등 포함.
- **파일**: `domain/models.py`

---

### [DOMAIN-04] Recommendation
- **레이어**: domain
- **유형**: Value Object (Pydantic BaseModel, frozen)
- **책임**: 단일 추천 결과 표현. Place + 코사인 유사도 점수 포함.
- **파일**: `domain/models.py`

---

### [DOMAIN-05] EmbeddingPort
- **레이어**: domain
- **유형**: Abstract Interface (ABC)
- **책임**: 텍스트 임베딩 생성 계약 정의. 미래 임베딩 모델 교체(e.g., OpenAI embeddings)를 위한 추상화.
- **파일**: `domain/interfaces.py`

---

### [DOMAIN-06] StationRepository
- **레이어**: domain
- **유형**: Abstract Interface (ABC)
- **책임**: 역 탐색 계약 정의. 현재(하드코딩) → 미래(카카오 Maps API) 교체 지점.
- **파일**: `domain/interfaces.py`

---

### [DOMAIN-07] VectorRepository
- **레이어**: domain
- **유형**: Abstract Interface (ABC)
- **책임**: 벡터 유사도 검색 계약 정의. 현재(ChromaDB) → 미래(Qdrant) 교체 지점.
- **파일**: `domain/interfaces.py`

---

### [DOMAIN-08] Domain Exceptions
- **레이어**: domain
- **유형**: Exception 클래스들
- **책임**: 비즈니스 실패 시나리오 표현 (`NoNearbyStationError`, `NoRecommendationsError`, `VectorDBError`).
- **파일**: `domain/exceptions.py`

---

### [APP-01] MidpointService
- **레이어**: application
- **유형**: Service
- **책임**: 2개 이상의 Location에서 지리적 중간지점을 계산. 순수 비즈니스 로직 — 외부 의존성 없음.
- **파일**: `application/midpoint_service.py`

---

### [APP-02] RecommendationService
- **레이어**: application
- **유형**: Service
- **책임**: 장소 추천 오케스트레이션. StationRepository로 최근접 역 탐색 → VectorRepository로 RAG 검색 → Recommendation 목록 반환.
- **파일**: `application/recommendation_service.py`
- **의존성**: `StationRepository`, `VectorRepository`

---

### [INFRA-01] SBERTEmbedder
- **레이어**: infrastructure
- **유형**: EmbeddingPort 구현체
- **책임**: `jhgan/ko-sroberta-multitask` 모델로 텍스트 임베딩 생성. 싱글톤 패턴으로 앱 시작 시 1회 로드.
- **파일**: `infrastructure/embedding/sbert_embedder.py`
- **구현 인터페이스**: `EmbeddingPort`

---

### [INFRA-02] HardcodedStationRepository
- **레이어**: infrastructure
- **유형**: StationRepository 구현체
- **책임**: 서울 주요 역(26개) 하드코딩 데이터로 Haversine 거리 기반 최근접 역 탐색 구현.
- **파일**: `infrastructure/station/hardcoded_station_repository.py`
- **구현 인터페이스**: `StationRepository`

---

### [INFRA-03] ChromaVectorRepository
- **레이어**: infrastructure
- **유형**: VectorRepository 구현체
- **책임**: ChromaDB 영구 저장소에서 코사인 유사도 검색 수행. 역 이름으로 메타데이터 필터링.
- **파일**: `infrastructure/vector/chroma_vector_repository.py`
- **구현 인터페이스**: `VectorRepository`
- **의존성**: `EmbeddingPort`

---

### [API-01] FastAPI Application
- **레이어**: api
- **유형**: FastAPI App (진입점)
- **책임**: 앱 인스턴스 생성, 라우터 등록, 전역 exception handler 설정, startup/shutdown 훅.
- **파일**: `api/main.py`

---

### [API-02] DependencyContainer
- **레이어**: api
- **유형**: 의존성 팩토리 모듈
- **책임**: 모든 DI 설정 중앙 관리. `functools.lru_cache`로 싱글톤 보장. 각 라우터 핸들러가 `Depends()`로 참조.
- **파일**: `api/dependencies.py`

---

### [API-03] MidpointRouter
- **레이어**: api
- **유형**: FastAPI APIRouter
- **책임**: `POST /api/v1/midpoint` 요청 처리. 입력 검증 → MidpointService 호출 → 응답 직렬화.
- **파일**: `api/v1/midpoint.py`

---

### [API-04] RecommendRouter
- **레이어**: api
- **유형**: FastAPI APIRouter
- **책임**: `POST /api/v1/recommend` 요청 처리. 입력 검증 → RecommendationService 호출 → 응답 직렬화.
- **파일**: `api/v1/recommend.py`

---

### [CORE-01] Settings
- **레이어**: core
- **유형**: Pydantic BaseSettings
- **책임**: 환경 변수 로드 및 타입 안전 설정 관리 (모델명, ChromaDB 경로, 서버 설정 등).
- **파일**: `core/config.py`
