# AGENTS.md

이 파일은 이 저장소에서 작업하는 AI 에이전트와 개발자를 위한 프로젝트 가이드입니다. 루트 디렉터리 전체에 적용됩니다.

## 프로젝트 개요

`mid-meet`는 여러 출발 위치의 중간 지점을 기준으로 만남 장소를 추천하는 Python 백엔드입니다. FastAPI API, 도메인/애플리케이션/인프라 계층, ChromaDB 기반 벡터 검색, SBERT 임베딩을 사용합니다.

주요 엔드포인트:

- `POST /api/v1/midpoint`: 입력 좌표들의 산술 평균 중간 지점에 가장 가까운 지하철역 반환
- `POST /api/v1/recommend`: 입력 좌표들의 만남 역을 찾고, 질의 임베딩과 벡터 DB 검색으로 장소 추천 반환

## 기술 스택

- Python 3.11+
- FastAPI, Uvicorn
- Pydantic v2, pydantic-settings
- ChromaDB
- sentence-transformers / Torch
- pytest, Hypothesis, pytest-cov
- Ruff, mypy strict

## 디렉터리 구조

- `domain/`: 도메인 모델, 예외, 포트 인터페이스
- `application/`: 비즈니스 유스케이스 서비스
- `infrastructure/`: 포트 구현체. ChromaDB, SBERT, 역 저장소, Kakao 연동 코드
- `api/`: FastAPI 앱, 라우터, 요청 스키마, 의존성 주입
- `core/`: 환경 설정
- `data/processed/`: 장소 원천/가공 데이터
- `scripts/`: 데이터 수집 및 벡터 DB 적재 스크립트
- `tests/`: 단위, 통합, property-based 테스트
- `aidlc-docs/`: 설계/프로세스 산출물

## 아키텍처 규칙

- 의존성 방향은 `api -> application -> domain`을 기본으로 유지합니다.
- `domain/`은 프레임워크와 인프라 구현체에 의존하지 않습니다.
- 외부 시스템 연동, 저장소, 임베딩 모델 호출은 `domain.interfaces`의 포트를 구현하는 `infrastructure/` 구현체에 둡니다.
- FastAPI `Depends`와 캐시된 팩토리는 `api/dependencies.py`에 둡니다.
- API 요청 전용 스키마는 `api/v1/schemas.py`에 두고, 응답/비즈니스 객체는 가능한 한 `domain.models`를 사용합니다.
- 서비스 로직은 `application/`에 두며 라우터에는 변환과 호출만 남깁니다.
- 새 예외가 API 응답으로 노출되어야 하면 `domain/exceptions.py`에 정의하고 `api/main.py`에 예외 핸들러를 추가합니다.

## 로컬 실행

가상환경 생성 및 의존성 설치:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

환경 파일:

```bash
copy .env.example .env
```

벡터 DB 적재:

```bash
python scripts/ingest_to_vectordb.py
```

API 서버:

```bash
uvicorn api.main:app --reload --port 8000
```

문서 UI는 `http://localhost:8000/docs`에서 확인합니다.

## 검증 명령

전체 테스트:

```bash
pytest
```

단위 테스트:

```bash
pytest tests/unit/
```

통합 테스트:

```bash
pytest tests/integration/
```

Property-based 테스트:

```bash
pytest tests/unit/properties/ -v
```

정적 검사:

```bash
ruff check .
mypy .
```

`pyproject.toml` 기준으로 pytest는 커버리지 80% 이상을 요구합니다. `scripts/`와 `tests/`는 커버리지 산정에서 제외됩니다.

## 테스트 작성 지침

- 비즈니스 로직은 `tests/unit/`에 서비스/도메인 단위로 검증합니다.
- API 테스트는 `fastapi.testclient.TestClient`와 `app.dependency_overrides`로 외부 의존성을 대체합니다.
- 실제 SBERT 모델 다운로드나 ChromaDB 영속 저장소 접근이 필요한 테스트는 기본 단위 테스트에 넣지 않습니다.
- 좌표 범위, 거리 계산, 중간 지점 불변성처럼 입력 공간이 넓은 규칙은 Hypothesis 기반 테스트를 선호합니다.
- 기존 테스트는 `pytest.approx`를 사용해 부동소수점 결과를 비교합니다.

## 데이터와 인코딩 주의사항

- 기존 일부 한국어 문자열과 문서가 깨진 인코딩으로 보입니다. 요청과 직접 관련 없는 문자열은 수정하지 마십시오.
- 새 파일은 UTF-8로 작성합니다.
- `data/processed/places.json`은 추천 데이터의 기반입니다. 스키마 변경 시 `domain.models.Place`, 적재 스크립트, 벡터 저장소 변환 로직, 관련 테스트를 함께 확인합니다.
- `.env`와 로컬 ChromaDB 데이터(`data/chroma_db`)는 커밋하지 않습니다.

## 구현 시 체크리스트

- 계층 경계를 넘는 직접 import를 만들지 않았는지 확인합니다.
- Pydantic 제약(`Latitude`, `Longitude`, `Rating`, `SimilarityScore`)을 재사용합니다.
- `top_k`, 좌표 개수, 문자열 길이 같은 입력 제약은 API 스키마에 명시합니다.
- 외부 API 키나 모델 경로는 `core.config.Settings`와 `.env.example`을 통해 관리합니다.
- 예외가 빈 리스트로 삼켜지는 코드와 HTTP 에러로 노출되는 코드를 구분해서 테스트합니다.
- 사용자에게 보이는 API 변경은 README 또는 관련 문서도 갱신합니다.

## 코딩 스타일

- `from __future__ import annotations` 패턴을 유지합니다.
- 타입 힌트를 작성하고 mypy strict 기준을 고려합니다.
- Ruff 설정은 line length 88, Python 3.11, import 정렬을 포함합니다.
- 테스트 파일은 annotation 관련 Ruff 규칙이 완화되어 있지만, 제품 코드는 명시적 타입을 유지합니다.
- 불필요한 리팩터링이나 대규모 포맷 변경은 피하고 요청 범위에 맞춘 변경만 수행합니다.
