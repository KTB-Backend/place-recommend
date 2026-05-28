# NFR Design Patterns — Unit 1: Foundation

## 패턴 1: Annotated 타입 별칭 (검증 패턴)

**적용 목적**: 도메인 경계에서 잘못된 좌표·범위값이 내부로 진입하는 것을 차단.  
Pydantic이 인스턴스 생성 시점에 자동으로 검증하므로 별도 guard 코드 불필요.

```python
# domain/models.py

from typing import Annotated
from pydantic import BaseModel, Field

# ── 재사용 가능한 타입 별칭 ──────────────────────────────────
Latitude    = Annotated[float, Field(ge=-90.0,  le=90.0)]
Longitude   = Annotated[float, Field(ge=-180.0, le=180.0)]
Rating      = Annotated[float, Field(ge=0.0,    le=5.0)]
SimilarityScore = Annotated[float, Field(ge=0.0, le=1.0)]
NonNegativeInt  = Annotated[int,   Field(ge=0)]

# ── 도메인 모델 ──────────────────────────────────────────────
class Location(BaseModel, frozen=True):
    lat: Latitude
    lng: Longitude

class Place(BaseModel):
    ...
    distance_from_station_m: NonNegativeInt
    rating: Rating
    price_range: Literal["저렴", "중간", "비쌈"]
    tags: list[str]

class Recommendation(BaseModel, frozen=True):
    place: Place
    similarity_score: SimilarityScore
```

**장점**:
- 타입 별칭을 여러 모델에서 재사용 → 제약 조건 단일 정의
- mypy + Pydantic 플러그인이 타입 수준에서 정적 검증
- `ValidationError` 자동 발생 → API 레이어에서 HTTP 422 변환

---

## 패턴 2: 도메인 경계 입력 검증 (보안 패턴)

**적용 목적**: 외부 입력(HTTP 요청)은 API 레이어에서 Pydantic 모델로 역직렬화될 때 자동 검증. 도메인 모델 자체가 방어선이 됨.

```
외부 입력 (JSON)
      ↓
API 레이어 Request 모델 (Pydantic) ── 1차 검증 (형식, 범위)
      ↓
Application Service ── 도메인 모델 생성
      ↓
Domain 모델 (Annotated 타입) ── 2차 검증 (불변식 보장)
      ↓
Infrastructure (ChromaDB, SBERT) ── 신뢰할 수 있는 입력만 도달
```

**구현 원칙**:
- `Location`, `Place` 등 도메인 모델은 생성 자체가 검증 통과를 의미
- 인프라 레이어는 도메인 모델을 받아 추가 검증 없이 사용
- 예외는 도메인 계층에서 정의, HTTP 변환은 API 레이어 책임

---

## 패턴 3: PBT @composite 전략 패턴

**적용 목적**: 도메인 객체 생성 로직을 캡슐화하여 모든 PBT에서 일관된 도메인 전략 재사용 (PBT-07 준수).

```python
# tests/unit/properties/strategies.py

from hypothesis import strategies as st
from hypothesis.strategies import SearchStrategy

@st.composite
def valid_locations(draw) -> Location:
    """유효 범위 내 Location 생성. NaN·Inf 제외."""
    lat = draw(st.floats(min_value=-90.0, max_value=90.0,
                         allow_nan=False, allow_infinity=False))
    lng = draw(st.floats(min_value=-180.0, max_value=180.0,
                         allow_nan=False, allow_infinity=False))
    return Location(lat=lat, lng=lng)

@st.composite
def invalid_locations(draw) -> dict:
    """유효 범위를 벗어난 좌표 딕셔너리. ValidationError 발생 검증용."""
    strategy = draw(st.sampled_from(["lat_high", "lat_low", "lng_high", "lng_low"]))
    match strategy:
        case "lat_high": return {"lat": draw(st.floats(min_value=90.001)), "lng": 0.0}
        case "lat_low":  return {"lat": draw(st.floats(max_value=-90.001)), "lng": 0.0}
        case "lng_high": return {"lat": 0.0, "lng": draw(st.floats(min_value=180.001))}
        case "lng_low":  return {"lat": 0.0, "lng": draw(st.floats(max_value=-180.001))}

@st.composite
def valid_similarity_scores(draw) -> float:
    return draw(st.floats(min_value=0.0, max_value=1.0,
                          allow_nan=False, allow_infinity=False))

@st.composite
def two_or_more_locations(draw) -> list[Location]:
    """최소 2개 이상 Location 리스트. MidpointService 테스트용."""
    n = draw(st.integers(min_value=2, max_value=10))
    return [draw(valid_locations()) for _ in range(n)]
```

**설계 원칙**:
- `allow_nan=False`, `allow_infinity=False` 필수 — Pydantic은 허용하지만 도메인에서 무의미
- 유효·무효 전략 쌍으로 제공 — 경계값 테스트 포함
- 전략 함수는 모든 PBT 파일에서 import하여 재사용 (PBT-07: 중앙화)
