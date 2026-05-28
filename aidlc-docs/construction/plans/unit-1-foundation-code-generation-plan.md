# Unit 1: Foundation — Code Generation Plan

## 유닛 컨텍스트

- **유닛**: Unit 1 — Foundation
- **구현 기능**: NFR-01(클린 아키텍처), NFR-03(테스트 인프라), NFR-05(환경 변수 관리)
- **코드 위치**: `C:\Users\Owner\where\` (루트 직접 배치, 플랫 패키지)
- **의존 유닛**: 없음 (모든 유닛의 기반)

---

## 생성 단계

### Step 1: 프로젝트 구조 초기화
- [ ] `domain/__init__.py` 생성
- [ ] `application/__init__.py` 생성
- [ ] `infrastructure/__init__.py` 생성
- [ ] `api/__init__.py` 생성
- [ ] `core/__init__.py` 생성
- [ ] `tests/__init__.py` 생성
- [ ] `tests/unit/__init__.py` 생성
- [ ] `tests/unit/properties/__init__.py` 생성
- [ ] `tests/integration/__init__.py` 생성
- [ ] `scripts/__init__.py` 생성
- [ ] `data/processed/` 디렉토리 확인

### Step 2: 도메인 모델 생성 (`domain/models.py`)
- [ ] `Annotated` 타입 별칭 정의 (`Latitude`, `Longitude`, `Rating`, `SimilarityScore`, `NonNegativeInt`)
- [ ] `Location` (frozen Value Object)
- [ ] `Station` (Entity)
- [ ] `Place` (Entity, `price_range` Literal 제약)
- [ ] `Recommendation` (frozen Value Object, `similarity_score` 변환 주석)

### Step 3: 도메인 인터페이스 생성 (`domain/interfaces.py`)
- [ ] `EmbeddingPort` (ABC)
- [ ] `StationRepository` (ABC)
- [ ] `VectorRepository` (ABC)

### Step 4: 도메인 예외 생성 (`domain/exceptions.py`)
- [ ] `DomainError` (base)
- [ ] `NoNearbyStationError`
- [ ] `NoRecommendationsError`
- [ ] `VectorDBError`
- [ ] `InvalidLocationError`

### Step 5: 설정 생성 (`core/config.py`)
- [ ] `Settings` (Pydantic `BaseSettings`)
- [ ] `station_search_radius_km`, `default_top_k` 포함
- [ ] `get_settings()` 캐시 팩토리 함수

### Step 6: 프로젝트 설정 파일
- [ ] `requirements.txt` 생성 (프로덕션 의존성)
- [ ] `requirements-dev.txt` 생성 (개발·테스트 의존성)
- [ ] `pyproject.toml` 생성 (mypy, ruff, pytest, coverage 통합 설정)
- [ ] `.env.example` 생성

### Step 7: 단위 테스트 생성 (`tests/unit/test_domain_models.py`)
- [ ] `Location` 유효성 검증 테스트 (유효 범위, 범위 초과)
- [ ] `Location` frozen 불변성 테스트
- [ ] `Place` 유효성 검증 테스트 (`price_range` Literal)
- [ ] `Recommendation` `similarity_score` 범위 테스트
- [ ] Pydantic 직렬화 라운드트립 예시 테스트

### Step 8: Hypothesis 전략 생성 (`tests/unit/properties/strategies.py`)
- [ ] `valid_locations()` `@composite` 전략
- [ ] `invalid_locations()` `@composite` 전략
- [ ] `valid_similarity_scores()` `@composite` 전략
- [ ] `two_or_more_locations()` `@composite` 전략

### Step 9: PBT 테스트 생성 (`tests/unit/properties/test_location_properties.py`)
- [ ] Location Pydantic 라운드트립 속성 테스트 (PBT-02)
- [ ] Location 좌표 범위 불변식 테스트 (PBT-03)
- [ ] Recommendation 유사도 범위 불변식 테스트 (PBT-03)
- [ ] Place 라운드트립 속성 테스트 (PBT-02)

### Step 10: Hypothesis 프로파일 설정 (`tests/conftest.py`)
- [ ] dev/ci 프로파일 등록 및 자동 로드 설정

### Step 11: 코드 요약 문서 생성
- [ ] `aidlc-docs/construction/unit-1-foundation/code/summary.md` 생성

---

## 스토리 트레이서빌리티

| Step | 구현 기능 |
|---|---|
| Step 1-5 | NFR-01 클린 아키텍처 도메인 계층 |
| Step 6 | NFR-05 환경 변수 관리 |
| Step 7-10 | NFR-03 단위 테스트 + PBT |
