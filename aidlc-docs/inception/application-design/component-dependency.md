# Component Dependency

## 의존성 방향 원칙

```
API → Application → Domain ← Infrastructure
```

- **Domain**: 어디에도 의존하지 않음 (인터페이스 + 모델 + 예외만 정의)
- **Application**: Domain에만 의존 (인프라 구현체 직접 참조 금지)
- **Infrastructure**: Domain 인터페이스 구현 (Application에는 의존하지 않음)
- **API**: Application + Domain 사용, Infrastructure는 `dependencies.py`를 통해서만 간접 참조

---

## 의존성 매트릭스

| 컴포넌트 | domain/models | domain/interfaces | domain/exceptions | application | infrastructure | api/dependencies |
|---|---|---|---|---|---|---|
| **domain/models** | — | — | — | — | — | — |
| **domain/interfaces** | O | — | — | — | — | — |
| **domain/exceptions** | — | — | — | — | — | — |
| **MidpointService** | O | — | O | — | — | — |
| **RecommendationService** | O | O | O | — | — | — |
| **SBERTEmbedder** | — | O (구현) | — | — | — | — |
| **HardcodedStationRepository** | O | O (구현) | — | — | — | — |
| **ChromaVectorRepository** | O | O (구현+의존) | O | — | — | — |
| **api/dependencies** | — | O | — | O | O | — |
| **MidpointRouter** | O | — | — | O | — | O |
| **RecommendRouter** | O | — | — | O | — | O |
| **Settings** | — | — | — | — | — | — |

O = 의존함

---

## 컴포넌트 통신 패턴

```
HTTP Request
     |
     v
[API Router] ──Depends()──> [dependencies.py]
     |                              |
     |                    ┌─────────┴─────────┐
     |                    |                   |
     v                    v                   v
[MidpointService]  [RecommendationService]  [Settings]
     |                    |
     |           ┌────────┴────────┐
     |           |                 |
     v           v                 v
  (계산만)  [StationRepository] [VectorRepository]
                 |                 |
                 v                 v
     [HardcodedStation...]  [ChromaVector...]
                                   |
                                   v
                            [SBERTEmbedder]
                                   |
                                   v
                            [ChromaDB (로컬)]
```

---

## 인터페이스 교체 지점 (확장성)

| 현재 구현체 | 인터페이스 | 미래 교체 대상 | 교체 방법 |
|---|---|---|---|
| `HardcodedStationRepository` | `StationRepository` | `KakaoStationRepository` | `dependencies.py`의 `get_station_repository()` 반환값 변경 |
| `ChromaVectorRepository` | `VectorRepository` | `QdrantVectorRepository` | `dependencies.py`의 `get_vector_repository()` 반환값 변경 |
| `SBERTEmbedder` | `EmbeddingPort` | `OpenAIEmbedder` / `CohereEmbedder` | `dependencies.py`의 `get_embedding_port()` 반환값 변경 |

---

## 데이터 흐름 (POST /api/v1/recommend)

```
1. Client → POST /api/v1/recommend {midpoint, category, radius_km, top_k}
2. RecommendRouter → RecommendRequest 유효성 검증 (Pydantic)
3. RecommendRouter → RecommendationService.recommend(midpoint, category, ...)
4. RecommendationService → StationRepository.find_nearest(midpoint, radius_km)
   └── HardcodedStationRepository: Haversine 계산 → 최근접 Station 반환
5. RecommendationService → 쿼리 생성: "{역이름} 주변 {category}하기 좋은 장소"
6. RecommendationService → VectorRepository.search(query_embedding, station_name, top_k)
   └── ChromaVectorRepository → EmbeddingPort.embed_query(query)
   └── SBERTEmbedder: 768차원 벡터 생성
   └── ChromaDB: 코사인 유사도 검색 (station 필터)
7. RecommendationService → RecommendResult 반환
8. RecommendRouter → RecommendResponse 직렬화
9. Client ← HTTP 200 + JSON 응답
```

---

## 데이터 흐름 (POST /api/v1/midpoint)

```
1. Client → POST /api/v1/midpoint {locations: [{lat, lng}, ...]}
2. MidpointRouter → MidpointRequest 유효성 검증 (최소 2개)
3. MidpointRouter → MidpointService.calculate(locations)
   └── 위도 평균, 경도 평균 계산
4. MidpointRouter → MidpointResponse 직렬화
5. Client ← HTTP 200 + {midpoint: {lat, lng}, location_count: N}
```
