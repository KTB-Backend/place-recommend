# Unit Test Execution

## 테스트 구조

```
tests/unit/
├── test_domain_models.py           # Unit 1: 도메인 모델 유효성
├── test_hardcoded_station_repository.py  # Unit 2: 역 탐색 로직
├── test_midpoint_service.py        # Unit 2: 중간지점 계산
├── test_recommendation_service.py  # Unit 3: 추천 오케스트레이션 (mock)
└── properties/
    ├── test_location_properties.py # PBT: Location 불변식
    ├── test_haversine_properties.py # PBT: Haversine 대칭성·삼각부등식
    └── test_midpoint_properties.py # PBT: 중간지점 기하 속성
```

## 단위 테스트 실행

### 1. 전체 단위 테스트 실행 (커버리지 포함)

```bash
pytest tests/unit/ -v
```

### 2. 커버리지 리포트 포함 실행

```bash
pytest tests/unit/ -v --cov=. --cov-report=term-missing
```

### 3. PBT 전용 실행

```bash
# 개발 프로파일 (빠른 실행)
pytest tests/unit/properties/ -v

# CI 프로파일 (더 많은 예제)
CI=true pytest tests/unit/properties/ -v --hypothesis-seed=0
```

### 4. 특정 테스트 파일 실행

```bash
pytest tests/unit/test_domain_models.py -v
pytest tests/unit/test_midpoint_service.py -v
pytest tests/unit/test_recommendation_service.py -v
```

## 예상 결과

- **전체 단위 테스트**: 전체 PASS (모델 로드 없이 실행)
- **커버리지 목표**: `domain/`, `application/` 90%+
- **PBT 실행 속도**: dev 프로파일 기준 30초 내

## 테스트 격리

단위 테스트는 **ML 모델 로드 없이** 동작:
- `test_recommendation_service.py` — `MidpointService`, `EmbeddingPort`, `VectorRepository` 전부 Mock
- `tests/unit/properties/` — 순수 Python 계산만 검증

## 실패 시 대응

1. 실패한 테스트 케이스와 트레이스백 확인
2. PBT 실패 시 출력된 `Falsifying example` 저장 → 회귀 테스트로 추가
3. `pytest -x` 옵션으로 첫 실패에서 중단하여 디버깅 집중
