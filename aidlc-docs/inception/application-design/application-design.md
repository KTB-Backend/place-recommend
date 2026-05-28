# Application Design

## 개요

**where** 는 클린 아키텍처 기반 RAG 장소 추천 FastAPI 서비스입니다.
`where-meeting`을 참조하여 아키텍처를 완전히 재설계했습니다.

---

## 아키텍처 결정 요약

| 항목 | 결정 | 근거 |
|---|---|---|
| 인터페이스 위치 | Domain 레이어 | 포트-어댑터 패턴, 도메인이 인프라에 의존하지 않음 |
| 임베딩 추상화 | `EmbeddingPort` (ABC) | 미래 임베딩 모델 교체 가능성 |
| DI 방식 | `dependencies.py` 중앙 관리 | DI 설정 단일 진입점, 테스트 시 오버라이드 용이 |
| 에러 처리 | 도메인 예외 + FastAPI handler | 도메인 로직과 HTTP 변환 분리 |
| 디렉토리 구조 | 플랫 패키지 (`domain/`, `application/` 등 루트 직접) | 단순성, 소규모 서비스에 적합 |

---

## 프로젝트 디렉토리 구조

```
where/
├── domain/
│   ├── __init__.py
│   ├── models.py            # Location, Station, Place, Recommendation
│   ├── interfaces.py        # EmbeddingPort, StationRepository, VectorRepository (ABC)
│   └── exceptions.py        # DomainError 하위 예외들
│
├── application/
│   ├── __init__.py
│   ├── midpoint_service.py  # MidpointService
│   └── recommendation_service.py  # RecommendationService + RecommendResult
│
├── infrastructure/
│   ├── __init__.py
│   ├── embedding/
│   │   ├── __init__.py
│   │   └── sbert_embedder.py        # SBERTEmbedder(EmbeddingPort)
│   ├── station/
│   │   ├── __init__.py
│   │   └── hardcoded_station_repository.py  # HardcodedStationRepository
│   └── vector/
│       ├── __init__.py
│       └── chroma_vector_repository.py      # ChromaVectorRepository
│
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI 앱 + exception handler 등록
│   ├── dependencies.py      # 전체 DI 팩토리 함수 (@lru_cache 싱글톤)
│   └── v1/
│       ├── __init__.py
│       ├── router.py        # v1 APIRouter 통합
│       ├── midpoint.py      # POST /api/v1/midpoint
│       └── recommend.py     # POST /api/v1/recommend
│
├── core/
│   ├── __init__.py
│   └── config.py            # Settings (Pydantic BaseSettings)
│
├── data/
│   └── processed/
│       └── places.json      # 장소 데이터 (where-meeting 기반 확장)
│
├── scripts/
│   └── ingest_to_vectordb.py  # ChromaDB 데이터 인제스트
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_midpoint_service.py
│   │   ├── test_recommendation_service.py
│   │   ├── test_hardcoded_station_repository.py
│   │   └── properties/
│   │       ├── __init__.py
│   │       ├── strategies.py          # Hypothesis 공용 전략(strategy)
│   │       ├── test_location_properties.py
│   │       ├── test_midpoint_properties.py
│   │       └── test_haversine_properties.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py                # FastAPI TestClient 통합 테스트
│
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 컴포넌트 다이어그램

```
+------------------------------------------------------------------+
|  API LAYER                                                       |
|  +-------------------+  +-------------------+                   |
|  | MidpointRouter    |  | RecommendRouter   |  GET /health      |
|  | POST /midpoint    |  | POST /recommend   |                   |
|  +--------+----------+  +--------+----------+                   |
|           |                      |                              |
|           +----------+-----------+                              |
|                      |                                          |
|              dependencies.py (DI)                               |
+---------------------------+--------------------------------------+
                            |
+---------------------------+--------------------------------------+
|  APPLICATION LAYER        |                                      |
|  +---------------------+  +----------------------------+        |
|  | MidpointService     |  | RecommendationService      |        |
|  | calculate()         |  | recommend()                |        |
|  +---------------------+  +-----+------------------+---+        |
+----------------------------------|------------------|------------+
                                   |                  |
+----------------------------------|------------------|-----------+
|  DOMAIN LAYER (Interfaces)       |                  |           |
|  +----------------------------+  |                  |           |
|  | StationRepository (ABC)    |<-+                  |           |
|  | find_nearest()             |                     |           |
|  +----------------------------+                     |           |
|  +----------------------------+                     |           |
|  | VectorRepository (ABC)     |<--------------------+           |
|  | search()                   |                                 |
|  +----------------------------+                                 |
|  +----------------------------+                                 |
|  | EmbeddingPort (ABC)        |                                 |
|  | embed() / embed_query()    |                                 |
|  +----------------------------+                                 |
+------------------------------------------------------------------+
                            |
+---------------------------+--------------------------------------+
|  INFRASTRUCTURE LAYER     |                                      |
|  +-------------------------+  +----------------------------+    |
|  | HardcodedStation        |  | ChromaVectorRepository     |    |
|  | Repository              |  | (VectorRepository)         |    |
|  | (StationRepository)     |  +--+-----+------------------+    |
|  +-------------------------+     |     |                        |
|                                  |     v                        |
|                         Settings |  SBERTEmbedder               |
|                                  |  (EmbeddingPort)             |
|                                  |     |                        |
|                                  v     v                        |
|                               ChromaDB (로컬)                   |
+------------------------------------------------------------------+
```

---

## 참조 문서

- 컴포넌트 목록 및 책임: `components.md`
- 메서드 시그니처: `component-methods.md`
- 서비스 오케스트레이션: `services.md`
- 의존성 관계: `component-dependency.md`
