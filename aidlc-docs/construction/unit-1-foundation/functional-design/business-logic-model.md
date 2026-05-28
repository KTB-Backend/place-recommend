# Business Logic Model — Unit 1: Foundation

## 개요

Unit 1은 순수 도메인 계층입니다. 외부 I/O, 알고리즘, 오케스트레이션이 없으며
모든 다른 유닛이 이 유닛에 의존합니다.

---

## similarity_score 변환 로직

ChromaDB는 코사인 거리(distance)를 반환합니다.
도메인 계층은 이를 직관적인 유사도(similarity)로 노출합니다.

```
chroma_distance ∈ [0.0, 1.0] (코사인 거리)
       ↓
similarity_score = max(0.0, min(1.0, 1.0 - chroma_distance))
       ↓
similarity_score ∈ [0.0, 1.0] (높을수록 유사)
```

- distance = 0.0 → similarity = 1.0 (완전 일치)
- distance = 0.5 → similarity = 0.5
- distance = 1.0 → similarity = 0.0 (완전 불일치)
- clamp 처리로 부동소수점 오차 방어

이 변환은 `ChromaVectorRepository` (Unit 3)에서 수행하고, `Recommendation` 생성 시 적용됩니다.
도메인 모델(`Recommendation`)은 이미 변환된 값만 수신합니다.

---

## tags 처리 흐름

```
places.json (원본):
  "tags": "데이트,커플,와인,파스타,로맨틱"   ← 콤마 구분 문자열

ingest_to_vectordb.py (Unit 3):
  tags_list = tags_str.split(",")          ← 파싱

ChromaDB 메타데이터:
  {"tags": "데이트,커플,와인,..."}           ← 문자열 그대로 저장 (ChromaDB 제약)

ChromaVectorRepository (Unit 3):
  place.tags = metadata["tags"].split(",") ← 도메인 모델로 변환 시 파싱

Place.tags (도메인):
  ["데이트", "커플", "와인", "파스타", "로맨틱"]  ← list[str]
```

---

## 인터페이스 계약 (불변식)

### StationRepository

```
입력: location: Location, radius_km: float (> 0)
출력:
  - 반경 내 역 존재 → Station (가장 가까운 역)
  - 반경 내 역 없음 → None
예외: 구현체 내부 오류 시에만 발생 (비즈니스 실패는 None으로 표현)
```

### VectorRepository

```
입력: query_embedding: list[float], station_name: str, top_k: int (≥ 1)
출력:
  - 결과 있음 → list[Recommendation] (len ≤ top_k, similarity_score 내림차순)
  - 결과 없음 → []
예외: DB 접근 오류 시 VectorDBError 발생
```

### EmbeddingPort

```
입력: texts: list[str] (비어있지 않음)
출력: list[list[float]] (len == len(texts), 각 벡터 차원 동일)
보장: 동일 텍스트 → 동일 벡터 (결정론적)
```

---

## 예외 처리 정책

| 상황 | 예외 | 처리 레이어 |
|---|---|---|
| 잘못된 좌표 입력 | `InvalidLocationError` / Pydantic `ValidationError` | API 레이어 (HTTP 422) |
| 반경 내 역 없음 | `NoNearbyStationError` | Application → API (HTTP 404) |
| 벡터 검색 결과 없음 | `NoRecommendationsError` | Application → API (HTTP 404) |
| ChromaDB 접근 실패 | `VectorDBError` | Infrastructure → API (HTTP 503) |

---

## 코드 조직 전략 (Greenfield)

Unit 1 완료 시 생성되는 파일 구조:

```
domain/
├── __init__.py          (빈 파일)
├── models.py            (Location, Station, Place, Recommendation)
├── interfaces.py        (EmbeddingPort, StationRepository, VectorRepository)
└── exceptions.py        (DomainError 계층)

core/
├── __init__.py
└── config.py            (Settings)

requirements.txt         (전체 의존성)
.env.example             (환경 변수 템플릿)

tests/
├── __init__.py
└── unit/
    ├── __init__.py
    └── test_domain_models.py    (Pydantic 모델 단위 테스트)
```
