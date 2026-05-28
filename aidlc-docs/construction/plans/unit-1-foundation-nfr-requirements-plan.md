# Unit 1: Foundation — NFR Requirements Plan

## 실행 체크리스트

- [x] nfr-requirements.md 생성
- [x] tech-stack-decisions.md 생성

---

## 컨텍스트

이미 결정된 기술 스택:
- Python 3.11+, Pydantic v2, FastAPI, ChromaDB, sentence-transformers
- pytest (단위 + 통합), Hypothesis (PBT 전체 적용)

Unit 1 NFR은 **프로젝트 전체에 적용되는 개발 인프라**(코드 품질 도구, 테스트 설정, 타입 검사)에 집중합니다.

---

## 질문

### Question 1
타입 검사 도구를 적용할까요?

A) `mypy` — 엄격 모드(`--strict`), CI에서 강제

B) `pyright` (Pylance 기반) — IntelliJ/VSCode 통합 친화적

C) 적용 안 함 — 타입 힌트는 문서 목적으로만, 런타임 검사 없음

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 2
코드 포매터 / 린터를 적용할까요?

A) `ruff` 단독 — 포매팅 + 린팅 통합 (black + flake8 대체), 빠름

B) `black` + `ruff` — black으로 포매팅, ruff로 린팅

C) 적용 안 함 — 스타일 도구 없이 진행

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 3
pytest 설정 파일 위치를 어디에 둘까요?

A) `pyproject.toml` — 의존성(requirements.txt)과 분리된 표준 Python 설정 파일

B) `pytest.ini` — pytest 전용 설정 파일

C) `requirements.txt`만 사용, 별도 설정 파일 없음 — pytest 기본값으로 실행

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

### Question 4
Hypothesis 설정을 어떻게 할까요?

A) 기본값 — `max_examples=100`, deadline 없음 (개발 환경에 적합)

B) 명시적 설정 — `settings` 프로파일로 CI/개발 환경 분리 (`@settings(max_examples=50)` 등)

C) `hypothesis` 프로파일 최소화 — `suppress_health_check` 적용, 느린 테스트 경고 비활성화

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

답변 완료 후 알려주세요.
