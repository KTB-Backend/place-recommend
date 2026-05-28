# NFR Requirements — Unit 1: Foundation

## 코드 품질

### NFR-Q1: 타입 안전성
- **도구**: `mypy` (`--strict` 모드)
- **적용 범위**: `domain/`, `application/`, `infrastructure/`, `api/`, `core/` 전체
- **CI 강제**: mypy 통과 실패 시 빌드 실패
- **설정 위치**: `pyproject.toml` `[tool.mypy]` 섹션

### NFR-Q2: 코드 스타일
- **도구**: `ruff` 단독 (포매팅 + 린팅 통합)
  - 포매팅: `ruff format` (black 호환)
  - 린팅: `ruff check` (flake8, isort, pyupgrade 등 통합)
- **라인 길이**: 88자
- **설정 위치**: `pyproject.toml` `[tool.ruff]` 섹션

---

## 테스트

### NFR-T1: pytest 설정
- **설정 파일**: `pyproject.toml` `[tool.pytest.ini_options]` 섹션
- **테스트 경로**: `tests/`
- **커버리지**: `pytest-cov` 플러그인
- **최소 커버리지**: 80% (Unit 4 완료 기준)

### NFR-T2: Hypothesis 설정 (PBT-09 준수)
- **프레임워크**: `hypothesis` (Python PBT 표준)
- **프로파일 전략**: 개발(dev)·CI 환경 분리

  ```python
  # tests/unit/properties/conftest.py
  from hypothesis import settings, HealthCheck

  settings.register_profile("dev", max_examples=50, deadline=None)
  settings.register_profile(
      "ci",
      max_examples=200,
      deadline=500,          # 500ms 제한
      suppress_health_check=[HealthCheck.too_slow],
  )
  settings.load_profile("ci" if os.getenv("CI") else "dev")
  ```

- **시드 로깅**: CI에서 `--hypothesis-seed=0` 고정 또는 실패 시 seed 출력 (PBT-08 준수)
- **shrinking**: 기본값 유지 (비활성화 금지, PBT-08 준수)

---

## 의존성 관리

### NFR-D1: 의존성 파일
- **`requirements.txt`**: 프로덕션 의존성 (버전 고정)
- **`requirements-dev.txt`**: 개발·테스트 전용 의존성 (`mypy`, `ruff`, `hypothesis`, `pytest-cov`)
- **`pyproject.toml`**: 도구 설정 통합 파일 (코드 없음)

### NFR-D2: Python 버전
- **최소 버전**: Python 3.11
- **pyproject.toml**에 `requires-python = ">=3.11"` 명시
