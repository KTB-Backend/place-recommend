# Unit 1: Foundation — NFR Design Plan

## 실행 체크리스트

- [x] nfr-design-patterns.md 생성
- [x] logical-components.md 생성

---

## 카테고리별 적용 여부

| 카테고리 | 적용 여부 | 근거 |
|---|---|---|
| Resilience Patterns | N/A | 도메인 레이어는 I/O·네트워크 없음 |
| Scalability Patterns | N/A | 순수 데이터 구조, 컴퓨팅 없음 |
| Performance Patterns | 적용 | Pydantic 검증 스타일 선택 |
| Security Patterns | 적용 | 도메인 경계 입력 검증 |
| Logical Components | 적용 | Hypothesis 전략 설계, pyproject.toml 구조 |

---

## 질문

### Question 1
Pydantic 필드 제약(좌표 범위, 평점 범위 등)을 어떻게 표현할까요?

A) `Annotated` + `Field()` — 타입 레벨에서 제약 선언, 재사용 가능한 타입 별칭 생성

```python
Latitude = Annotated[float, Field(ge=-90.0, le=90.0)]
Longitude = Annotated[float, Field(ge=-180.0, le=180.0)]

class Location(BaseModel, frozen=True):
    lat: Latitude
    lng: Longitude
```

B) `@field_validator` — 메서드 기반 검증, 복잡한 크로스 필드 로직에 유리

```python
class Location(BaseModel, frozen=True):
    lat: float
    lng: float

    @field_validator("lat")
    def validate_lat(cls, v):
        if not -90.0 <= v <= 90.0:
            raise ValueError(...)
        return v
```

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 2
Hypothesis 도메인 전략(strategy)을 어떻게 설계할까요?
(`tests/unit/properties/strategies.py`에 정의될 공용 전략)

A) `st.builds()` 기반 — Pydantic 모델을 직접 빌드하는 전략

```python
# strategies.py
valid_locations = st.builds(
    Location,
    lat=st.floats(min_value=-90.0, max_value=90.0),
    lng=st.floats(min_value=-180.0, max_value=180.0),
)
```

B) `@composite` 기반 — 복잡한 도메인 객체 생성 로직을 함수로 캡슐화

```python
@st.composite
def valid_locations(draw):
    lat = draw(st.floats(min_value=-90.0, max_value=90.0, allow_nan=False))
    lng = draw(st.floats(min_value=-180.0, max_value=180.0, allow_nan=False))
    return Location(lat=lat, lng=lng)
```

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

답변 완료 후 알려주세요.
