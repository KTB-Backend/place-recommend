# Business Rules — Unit 1: Foundation

## 유효성 규칙

### BR-01: Location 좌표 범위
- `lat` 는 `-90.0` 이상 `90.0` 이하여야 한다
- `lng` 는 `-180.0` 이상 `180.0` 이하여야 한다
- 위반 시: Pydantic `ValidationError` (HTTP 422로 변환)

### BR-02: Place 평점 범위
- `rating` 은 `0.0` 이상 `5.0` 이하여야 한다

### BR-03: Place 가격대 허용값
- `price_range` 는 `"저렴"`, `"중간"`, `"비쌈"` 중 하나여야 한다

### BR-04: Place 역 거리 비음수
- `distance_from_station_m` 은 `0` 이상이어야 한다

### BR-05: Recommendation 유사도 범위
- `similarity_score` 는 `0.0` 이상 `1.0` 이하여야 한다
- 계산: `similarity_score = 1.0 - chroma_distance`
- ChromaDB 코사인 거리가 [0, 1] 범위를 벗어나는 경우 `clamp(0.0, 1.0)` 적용

### BR-06: 인터페이스 반환값 계약
- `StationRepository.find_nearest()`: 반경 내 역이 없으면 `None` 반환 (예외 발생 금지)
- `VectorRepository.search()`: 결과 없으면 빈 리스트 `[]` 반환 (예외 발생 금지)
- `EmbeddingPort.embed()`: 입력 리스트와 동일한 길이의 벡터 리스트 반환

### BR-07: Settings 기본값
- `station_search_radius_km`: 기본 `5.0` km (API 요청에서 오버라이드 가능)
- `default_top_k`: 기본 `3` (API 요청에서 오버라이드 가능, 최대 10)

---

## PBT 속성 목록 (PBT-01 준수)

### Location — 테스트 가능 속성

| 속성 | 카테고리 | 설명 |
|---|---|---|
| Pydantic 라운드트립 | Round-trip | `Location.model_validate(loc.model_dump()) == loc` |
| 좌표 범위 불변식 | Invariant | 유효 범위 내 좌표는 항상 생성 성공, 범위 외는 항상 ValidationError |
| 불변성(frozen) | Invariant | 생성 후 `lat`, `lng` 수정 불가 |

### Recommendation — 테스트 가능 속성

| 속성 | 카테고리 | 설명 |
|---|---|---|
| 유사도 범위 불변식 | Invariant | `0.0 <= similarity_score <= 1.0` 항상 성립 |
| 거리→유사도 단조성 | Invariant | distance 증가 → similarity_score 감소 (단조 감소) |

### Place — 테스트 가능 속성

| 속성 | 카테고리 | 설명 |
|---|---|---|
| Pydantic 라운드트립 | Round-trip | `Place.model_validate(place.model_dump()) == place` |
| tags 타입 불변식 | Invariant | `isinstance(place.tags, list)` 항상 True |

### EmbeddingPort (인터페이스 계약) — 구현체에서 검증

| 속성 | 카테고리 | 설명 |
|---|---|---|
| 출력 길이 보존 | Invariant | `len(embed(texts)) == len(texts)` |
| 벡터 차원 일관성 | Invariant | 동일 모델에서 생성한 모든 벡터의 차원은 동일 |

> 인터페이스 자체는 ABC이므로 PBT 없음. 구현체(SBERTEmbedder)에서 Unit 3에 적용.

### Settings — PBT 속성 없음

- 설정 객체는 알고리즘적 로직 없음. PBT 미적용 (N/A).
- **근거**: 환경 변수 로드 및 기본값만 담당, 변환/계산 없음.
