# Build and Test Summary

## 빌드 정보

| 항목 | 값 |
|---|---|
| 빌드 도구 | pip + venv |
| Python 버전 | 3.11+ |
| 프로덕션 의존성 | `requirements.txt` (9개 패키지) |
| 개발 의존성 | `requirements-dev.txt` (ruff, mypy, pytest, hypothesis, pytest-cov) |
| 빌드 산출물 | `data/chroma_db/` (벡터 저장소), FastAPI ASGI 앱 |

## 테스트 범위

### 단위 테스트 (Unit Tests)

| 파일 | 테스트 수 | 대상 |
|---|---|---|
| `test_domain_models.py` | 5 | Location, Station, Place, Recommendation 유효성 |
| `test_hardcoded_station_repository.py` | 4 | HardcodedStationRepository find_nearest |
| `test_midpoint_service.py` | 5 | MidpointService 계산 로직 |
| `test_recommendation_service.py` | 5 | RecommendationService 오케스트레이션 (mock) |
| `properties/test_location_properties.py` | PBT | Location 불변식 |
| `properties/test_haversine_properties.py` | PBT | Haversine 대칭성·비음수·삼각부등식 |
| `properties/test_midpoint_properties.py` | PBT | 중간지점 기하 속성 |

### 통합 테스트 (Integration Tests)

| 파일 | 테스트 수 | 대상 |
|---|---|---|
| `tests/integration/test_api.py` | 7 | FastAPI 엔드포인트 전체 흐름 (Mock 기반) |

### 성능 테스트

프로토타입 단계 — 수동 응답 시간 확인 수준 (공식 NFR 없음)

## 전체 테스트 실행 명령

```bash
# 전체 실행 (단위 + 통합 + 커버리지)
pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=80

# CI 환경 (PBT 시드 고정)
CI=true pytest tests/ -v --hypothesis-seed=0 --cov=. --cov-report=term-missing --cov-fail-under=80
```

## 코드 품질 검사

```bash
# 린팅 (ruff)
ruff check .

# 포매팅 검사 (ruff)
ruff format --check .

# 타입 검사 (mypy strict)
mypy .
```

## Overall Status

| 항목 | 상태 |
|---|---|
| 빌드 | Ready (pip install) |
| 단위 테스트 | 생성 완료 — 실행 필요 |
| 통합 테스트 | 생성 완료 — 실행 필요 |
| 성능 테스트 | 프로토타입 — 수동 확인 |
| 커버리지 목표 | 80% (pytest-cov --cov-fail-under=80) |
| Operations 준비 | 테스트 통과 후 Yes |

## 다음 단계

1. `pytest tests/ -v` 실행하여 전체 테스트 통과 확인
2. `ruff check .` + `mypy .` 통과 확인
3. `python scripts/ingest_to_vectordb.py` 실행 후 서버 구동 검증
4. `http://localhost:8000/docs` 에서 Swagger UI로 엔드포인트 직접 테스트
