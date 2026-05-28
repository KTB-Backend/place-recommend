# Code Generation Plan — Unit 3: RAG Engine

## 구현 대상 스토리
- FR-02: 장소 추천 API (로직 부분)
- FR-04: 벡터 검색 (SBERTEmbedder, ChromaVectorRepository)
- FR-05: 장소 데이터 관리 (places.json, ingest 스크립트)
- NFR-03: 단위 테스트 (mock 기반)

## 생성 파일 목록

| # | 파일 | 유형 |
|---|---|---|
| 1 | `data/processed/places.json` | 샘플 데이터 (10개) |
| 2 | `infrastructure/embedding/sbert_embedder.py` | 인프라 구현체 |
| 3 | `infrastructure/vector/chroma_vector_repository.py` | 인프라 구현체 |
| 4 | `application/recommendation_service.py` | 애플리케이션 서비스 |
| 5 | `scripts/ingest_to_vectordb.py` | 데이터 인제스트 |
| 6 | `tests/unit/test_recommendation_service.py` | 단위 테스트 (mock) |
| 7 | `aidlc-docs/construction/unit-3-rag-engine/code/summary.md` | 코드 요약 |

---

## 실행 체크리스트

- [x] Step 1: `data/processed/places.json`
  - [x] 10개 샘플 장소 (강남·홍대·합정·이태원·잠실·신촌·건대·여의도 역)
  - [x] 카테고리 다양화 (카페·레스토랑·바·술집)
  - [x] Place 모델 스키마 준수

- [ ] Step 2: `infrastructure/embedding/sbert_embedder.py`
  - [x] `SBERTEmbedder(EmbeddingPort)` 구현
  - [x] `embed(texts)`: 배치 임베딩 → `list[list[float]]`
  - [x] `embed_query(text)`: 단일 임베딩 → `list[float]`

- [ ] Step 3: `infrastructure/vector/chroma_vector_repository.py`
  - [x] `ChromaVectorRepository(VectorRepository)` 구현
  - [x] `_place_to_metadata(place)`: Place → ChromaDB 메타데이터
  - [x] `_metadata_to_place(meta)`: ChromaDB 메타데이터 → Place
  - [x] `search(query_embedding, station_name, top_k)`: 메타데이터 필터 + 코사인 유사도
  - [x] `similarity_score = max(0.0, 1.0 - distance)`

- [ ] Step 4: `application/recommendation_service.py`
  - [x] `RecommendationService` 구현
  - [x] `recommend(locations, query, top_k)` 오케스트레이션
  - [x] 결과 없으면 `NoRecommendationsError`

- [ ] Step 5: `scripts/ingest_to_vectordb.py`
  - [x] `places.json` 로드 → Place 파싱
  - [x] `_build_embedding_text(place)` 구성
  - [x] 배치 임베딩 → ChromaDB 저장 (멱등성: 기존 컬렉션 삭제 후 재생성)

- [ ] Step 6: `tests/unit/test_recommendation_service.py`
  - [x] `test_recommend_returns_list`: 결과 리스트 반환
  - [x] `test_recommend_result_type`: Recommendation 타입 확인
  - [x] `test_recommend_no_results_raises`: 빈 결과 → NoRecommendationsError
  - [x] `test_recommend_calls_correct_station`: 올바른 역명으로 검색 호출
  - [x] `test_empty_locations_raises`: 빈 좌표 → InvalidLocationError

- [ ] Step 7: `aidlc-docs/construction/unit-3-rag-engine/code/summary.md`

---

## 완료 검증

```bash
pytest tests/unit/test_recommendation_service.py -v
```
