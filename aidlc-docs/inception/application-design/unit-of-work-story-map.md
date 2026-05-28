# Unit of Work Story Map

## 기능 → 유닛 매핑

| 기능 (FR/NFR) | 유닛 | 주요 산출물 |
|---|---|---|
| FR-01: 중간지점 계산 API | Unit 2 (로직) + Unit 4 (API) | MidpointService, MidpointRouter |
| FR-02: 장소 추천 API | Unit 3 (로직) + Unit 4 (API) | RecommendationService, RecommendRouter |
| FR-03: 역 탐색 (하드코딩) | Unit 2 | HardcodedStationRepository |
| FR-04: 벡터 검색 (RAG) | Unit 3 | SBERTEmbedder, ChromaVectorRepository |
| FR-05: 장소 데이터 관리 | Unit 3 | `places.json`, `ingest_to_vectordb.py` |
| FR-06: 헬스 체크 API | Unit 4 | `GET /health` in `api/main.py` |
| NFR-01: 클린 아키텍처 | Unit 1 | `domain/`, 인터페이스 ABC |
| NFR-03: 단위 테스트 | Unit 2·3 | `tests/unit/` |
| NFR-03: 통합 테스트 | Unit 4 | `tests/integration/` |
| NFR-03: PBT (Hypothesis) | Unit 2·3 | `tests/unit/properties/` |
| NFR-04: 인터페이스 추상화 | Unit 1 | `StationRepository`, `VectorRepository`, `EmbeddingPort` |
| NFR-05: 환경 변수 관리 | Unit 1 | `core/config.py`, `.env.example` |

---

## 유닛별 파일 전체 목록

### Unit 1: Foundation
```
domain/__init__.py
domain/models.py
domain/interfaces.py
domain/exceptions.py
core/__init__.py
core/config.py
requirements.txt
.env.example
tests/__init__.py
tests/unit/__init__.py
tests/unit/test_domain_models.py
```

### Unit 2: Location & Midpoint
```
infrastructure/__init__.py
infrastructure/station/__init__.py
infrastructure/station/hardcoded_station_repository.py
application/__init__.py
application/midpoint_service.py
tests/unit/test_midpoint_service.py
tests/unit/test_hardcoded_station_repository.py
tests/unit/properties/__init__.py
tests/unit/properties/strategies.py
tests/unit/properties/test_haversine_properties.py
tests/unit/properties/test_midpoint_properties.py
```

### Unit 3: RAG Engine
```
infrastructure/embedding/__init__.py
infrastructure/embedding/sbert_embedder.py
infrastructure/vector/__init__.py
infrastructure/vector/chroma_vector_repository.py
application/recommendation_service.py
data/processed/places.json
scripts/__init__.py
scripts/ingest_to_vectordb.py
tests/unit/test_recommendation_service.py
tests/unit/properties/test_location_properties.py
```

### Unit 4: API & Integration
```
api/__init__.py
api/main.py
api/dependencies.py
api/v1/__init__.py
api/v1/router.py
api/v1/midpoint.py
api/v1/recommend.py
tests/integration/__init__.py
tests/integration/test_api.py
```

---

## 각 유닛 완료 검증 명령어

```bash
# Unit 1 완료 검증
pytest tests/unit/test_domain_models.py -v

# Unit 2 완료 검증
pytest tests/unit/test_midpoint_service.py \
       tests/unit/test_hardcoded_station_repository.py \
       tests/unit/properties/ -v

# Unit 3 완료 검증
python scripts/ingest_to_vectordb.py
pytest tests/unit/test_recommendation_service.py \
       tests/unit/properties/test_location_properties.py -v

# Unit 4 완료 검증
pytest tests/integration/test_api.py -v
uvicorn api.main:app --port 8000  # 수동 확인
```
