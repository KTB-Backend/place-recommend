# Code Summary — Unit 2: Location & Midpoint

## 생성된 파일 목록

### 인프라 계층
| 파일 | 설명 |
|---|---|
| `infrastructure/station/hardcoded_station_repository.py` | 서울 26개 역 실좌표 + Haversine 거리 계산 + `find_nearest` 구현 |

### 애플리케이션 계층
| 파일 | 설명 |
|---|---|
| `application/midpoint_service.py` | 산술 평균 중간지점 계산 + 최근접 역 탐색 오케스트레이션 |

### 도메인 계층 수정
| 파일 | 변경 내용 |
|---|---|
| `domain/interfaces.py` | `find_nearest` 반환 타입 `Station \| None` → `Station` |

### 테스트
| 파일 | 설명 |
|---|---|
| `tests/unit/test_hardcoded_station_repository.py` | 단위 테스트 5개 (좌표 검증, 항상 반환, 정확도) |
| `tests/unit/test_midpoint_service.py` | 단위 테스트 6개 (중간지점, 빈 리스트, 항상 반환) |
| `tests/unit/properties/strategies.py` | `seoul_locations()` 전략 추가 |
| `tests/unit/properties/test_haversine_properties.py` | PBT H01~H04 (비음수, 대칭, 자기거리, 상한) |
| `tests/unit/properties/test_midpoint_properties.py` | PBT M01~M04 (단일항등원, 교환법칙, 범위) |

## 완료 검증 명령어

```bash
pytest tests/unit/test_hardcoded_station_repository.py \
       tests/unit/test_midpoint_service.py \
       tests/unit/properties/test_haversine_properties.py \
       tests/unit/properties/test_midpoint_properties.py -v
```
