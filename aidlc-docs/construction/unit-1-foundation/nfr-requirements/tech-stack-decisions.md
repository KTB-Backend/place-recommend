# Tech Stack Decisions — Unit 1: Foundation

## 전체 프로젝트 기술 스택

| 분류 | 기술 | 버전 | 선택 이유 |
|---|---|---|---|
| 언어 | Python | 3.11+ | 타입 힌트 완성도, match 문, `tomllib` 내장 |
| API 프레임워크 | FastAPI | 0.115+ | 비동기 지원, Pydantic v2 통합, 자동 OpenAPI |
| ASGI 서버 | Uvicorn | 0.30+ | FastAPI 권장 서버 |
| 데이터 검증 | Pydantic | v2.9+ | 고성능, `model_validate`, `frozen=True` 지원 |
| 벡터 DB | ChromaDB | 0.5+ | 로컬 영구 저장, 코사인 유사도, 메타데이터 필터 |
| 임베딩 모델 | sentence-transformers | 3.1+ | `jhgan/ko-sroberta-multitask` 한국어 특화 |
| ML 백엔드 | PyTorch (CPU) | 2.4+ | sentence-transformers 의존 |
| HTTP 클라이언트 | httpx | 0.27+ | 비동기 지원 (Phase 2 카카오 API 대비) |
| 환경 변수 | python-dotenv | 1.0+ | `.env` 파일 로드 |

## 개발·테스트 도구

| 분류 | 기술 | 버전 | 선택 이유 |
|---|---|---|---|
| 테스트 러너 | pytest | 8.x | 업계 표준, 풍부한 플러그인 생태계 |
| PBT 프레임워크 | hypothesis | 6.x | 성숙한 shrinking, pytest 통합, 도메인 전략 지원 (PBT-09) |
| 커버리지 | pytest-cov | 5.x | pytest 플러그인, HTML 보고서 |
| FastAPI 테스트 | httpx (TestClient) | 0.27+ | 비동기 테스트 지원 |
| 타입 검사 | mypy | 1.x | `--strict` 모드, Pydantic v2 플러그인 |
| 린터·포매터 | ruff | 0.4+ | 단일 도구로 black·flake8·isort 대체, 빠른 속도 |

## pyproject.toml 설정 구조

```toml
[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]   # pycodestyle, pyflakes, isort, pyupgrade, bugbear

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=. --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
omit = ["tests/*", "scripts/*"]
```

## requirements.txt (프로덕션)

```
fastapi>=0.115.0
uvicorn>=0.30.6
pydantic>=2.9.2
pydantic-settings>=2.5.2
chromadb>=0.5.18
sentence-transformers>=3.1.1
torch>=2.4.1
httpx>=0.27.2
python-dotenv>=1.0.1
```

## requirements-dev.txt (개발·테스트)

```
-r requirements.txt
pytest>=8.0.0
hypothesis>=6.100.0
pytest-cov>=5.0.0
mypy>=1.10.0
ruff>=0.4.0
pydantic[mypy]>=2.9.2
```
