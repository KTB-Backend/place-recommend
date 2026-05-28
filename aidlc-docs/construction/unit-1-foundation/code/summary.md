# Code Summary — Unit 1: Foundation

## 생성된 파일 목록

### 도메인 계층
| 파일 | 설명 |
|---|---|
| `domain/__init__.py` | 패키지 초기화 |
| `domain/models.py` | Location, Station, Place, Recommendation + Annotated 타입 별칭 |
| `domain/interfaces.py` | EmbeddingPort, StationRepository, VectorRepository (ABC) |
| `domain/exceptions.py` | DomainError 계층 (5종) |

### 설정
| 파일 | 설명 |
|---|---|
| `core/__init__.py` | 패키지 초기화 |
| `core/config.py` | Settings (Pydantic BaseSettings) + get_settings() 팩토리 |
| `.env.example` | 환경 변수 템플릿 |

### 프로젝트 설정
| 파일 | 설명 |
|---|---|
| `requirements.txt` | 프로덕션 의존성 |
| `requirements-dev.txt` | 개발·테스트 의존성 |
| `pyproject.toml` | mypy·ruff·pytest·coverage 통합 설정 |

### 테스트
| 파일 | 설명 |
|---|---|
| `tests/conftest.py` | Hypothesis dev/ci 프로파일 자동 설정 |
| `tests/unit/test_domain_models.py` | 도메인 모델 단위 테스트 (25개) |
| `tests/unit/properties/strategies.py` | Hypothesis @composite 전략 6종 |
| `tests/unit/properties/test_location_properties.py` | PBT (라운드트립, 불변식) |

## 완료 검증 명령어

```bash
pytest tests/unit/test_domain_models.py tests/unit/properties/test_location_properties.py -v
```
