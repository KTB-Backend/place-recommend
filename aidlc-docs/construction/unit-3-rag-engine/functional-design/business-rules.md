# Business Rules — Unit 3: RAG Engine

## BR-01: 임베딩 생성

- 인제스트 시: 모든 장소에 대해 `_build_embedding_text(place)` → 배치 임베딩
- 쿼리 시: 사용자 자유 텍스트 → `embed_query(text)` → 단일 벡터
- 모델: `jhgan/ko-sroberta-multitask` (한국어 특화 Sentence-BERT)

## BR-02: ChromaDB 저장 구조

- **document**: `_build_embedding_text(place)` (임베딩 원본 텍스트)
- **embedding**: 위 텍스트의 벡터
- **metadata**: `{"station": place.station, "place_id": place.id}`
- **id**: `place.id`

## BR-03: 벡터 검색

1. `station_name` 메타데이터 필터: `{"station": station_name}`
2. 코사인 유사도 기준 top_k 반환
3. 거리 → 유사도 변환: `similarity_score = 1.0 - chroma_distance`
4. 결과를 `Recommendation(place=place, similarity_score=score)` 리스트로 반환
5. 해당 역 장소 없으면 빈 리스트 반환 → `NoRecommendationsError`

## BR-04: RecommendationService 오케스트레이션

```
recommend(locations, query, top_k):
  1. station = midpoint_service.find_meeting_station(locations)
  2. query_vector = embedding_port.embed_query(query)
  3. results = vector_repository.search(query_vector, station.name, top_k)
  4. if not results: raise NoRecommendationsError
  5. return results  # list[Recommendation], 유사도 내림차순
```

## BR-05: 데이터 인제스트 규칙

- `places.json` 로드 → `Place` 모델 파싱 (유효성 자동 검증)
- 기존 컬렉션 있으면 초기화 후 재적재 (멱등성)
- 배치 임베딩으로 처리 (전체를 한 번에)
