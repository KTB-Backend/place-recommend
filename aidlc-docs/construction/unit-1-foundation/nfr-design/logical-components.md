# Logical Components — Unit 1: Foundation

## 컴포넌트 목록

Unit 1은 런타임 인프라 컴포넌트(캐시, 큐, 서킷 브레이커 등)가 없는 순수 도메인 계층입니다.
논리적 컴포넌트는 **개발·품질 인프라**에 집중합니다.

---

## LC-01: Annotated 타입 별칭 모듈 (`domain/models.py` 상단)

**역할**: 재사용 가능한 제약 타입을 한 곳에 정의  
**소비자**: `Place`, `Location`, `Recommendation` 모델

```
Latitude         = Annotated[float, Field(ge=-90,  le=90)]
Longitude        = Annotated[float, Field(ge=-180, le=180)]
Rating           = Annotated[float, Field(ge=0.0,  le=5.0)]
SimilarityScore  = Annotated[float, Field(ge=0.0,  le=1.0)]
NonNegativeInt   = Annotated[int,   Field(ge=0)]
```

---

## LC-02: Hypothesis 전략 라이브러리 (`tests/unit/properties/strategies.py`)

**역할**: 모든 PBT에서 공유하는 도메인 전략 함수 모음  
**소비자**: `test_location_properties.py`, `test_midpoint_properties.py`, `test_haversine_properties.py`

| 전략 함수 | 생성 대상 | 용도 |
|---|---|---|
| `valid_locations()` | `Location` (유효 범위) | 거리·중간지점 PBT |
| `invalid_locations()` | `dict` (범위 초과) | 검증 실패 PBT |
| `valid_similarity_scores()` | `float` [0.0, 1.0] | Recommendation PBT |
| `two_or_more_locations()` | `list[Location]` (≥2) | MidpointService PBT |

---

## LC-03: Hypothesis 프로파일 설정 (`tests/conftest.py`)

**역할**: 실행 환경에 따른 PBT 설정 자동 전환  
**트리거**: `CI` 환경 변수 존재 여부

```python
# tests/conftest.py
import os
from hypothesis import settings, HealthCheck

settings.register_profile(
    "dev",
    max_examples=50,
    deadline=None,
)
settings.register_profile(
    "ci",
    max_examples=200,
    deadline=500,
    suppress_health_check=[HealthCheck.too_slow],
)
settings.load_profile("ci" if os.getenv("CI") else "dev")
```

---

## LC-04: pyproject.toml 통합 설정 파일

**역할**: mypy, ruff, pytest, coverage 설정 단일 파일 관리

```toml
[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["chromadb.*", "sentence_transformers.*"]
ignore_missing_imports = true

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "ANN"]
ignore = ["ANN101", "ANN102"]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["ANN"]   # 테스트 파일은 어노테이션 생략 허용

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=. --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
omit = ["tests/*", "scripts/*", "*/migrations/*"]

[tool.coverage.report]
exclude_lines = ["if TYPE_CHECKING:", "raise NotImplementedError"]
```

---

## LC-05: .env.example 템플릿

**역할**: 신규 개발자 온보딩 시 필요한 환경 변수 문서화

```dotenv
# 임베딩 모델
EMBEDDING_MODEL=jhgan/ko-sroberta-multitask

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=places

# 서버
APP_HOST=0.0.0.0
APP_PORT=8000

# 추천 기본값
STATION_SEARCH_RADIUS_KM=5.0
DEFAULT_TOP_K=3
```

---

## 컴포넌트 관계

```
LC-04 (pyproject.toml)
  ├── mypy 설정 → LC-01 Annotated 타입 검증
  ├── ruff 설정 → 전체 소스 코드 스타일
  └── pytest 설정 → LC-02, LC-03 PBT 실행

LC-03 (conftest.py)
  └── LC-02 전략 라이브러리 로드 환경 설정
```
