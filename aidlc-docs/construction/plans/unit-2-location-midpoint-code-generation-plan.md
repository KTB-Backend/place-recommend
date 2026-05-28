# Code Generation Plan — Unit 2: Location & Midpoint

## 구현 대상 스토리
- FR-01: 중간지점 계산 API (로직 부분)
- FR-03: 역 탐색 (HardcodedStationRepository)
- NFR-03: 단위 테스트 + PBT (Hypothesis)

## 변경 결정 (사용자 요청)
- `find_nearest`는 항상 `Station`을 반환 (반경 개념 제거)
- `radius_km` 파라미터 제거 — 26개 역 중 절대 최근접 역 반환
- `domain/interfaces.py` 이미 수정 완료

## 생성 파일 목록

| # | 파일 | 유형 |
|---|---|---|
| 1 | `infrastructure/station/hardcoded_station_repository.py` | 인프라 구현체 |
| 2 | `application/midpoint_service.py` | 애플리케이션 서비스 |
| 3 | `tests/unit/test_hardcoded_station_repository.py` | 단위 테스트 |
| 4 | `tests/unit/test_midpoint_service.py` | 단위 테스트 |
| 5 | `tests/unit/properties/strategies.py` | PBT 전략 추가 |
| 6 | `tests/unit/properties/test_haversine_properties.py` | PBT — Haversine 불변식 |
| 7 | `tests/unit/properties/test_midpoint_properties.py` | PBT — 중간지점 불변식 |
| 8 | `aidlc-docs/construction/unit-2-location-midpoint/code/summary.md` | 코드 요약 |

---

## 실행 체크리스트

- [x] Step 1: `infrastructure/station/hardcoded_station_repository.py`
  - [x] 26개 역 데이터 (실좌표) 클래스 변수 정의
  - [x] `_haversine(lat1, lng1, lat2, lng2) -> float` 내부 함수
  - [x] `find_nearest(location) -> Station` 구현 (항상 최근접 역 반환)

- [x] Step 2: `application/midpoint_service.py`
  - [x] `calculate_midpoint(locations: list[Location]) -> Location` 구현
  - [x] `find_meeting_station(locations: list[Location]) -> Station` 구현
  - [x] 빈 리스트 → `InvalidLocationError` 처리

- [x] Step 3: `tests/unit/test_hardcoded_station_repository.py`
  - [x] `test_find_nearest_known_station`: 강남역 근처 → 강남역 반환
  - [x] `test_find_nearest_always_returns`: 서울 외 좌표도 반드시 역 반환
  - [x] `test_find_nearest_exact_match`: 역 위치 정확히 입력 → 해당 역 반환
  - [x] `test_all_stations_have_valid_coordinates`: 26개 역 좌표 유효성 검증

- [x] Step 4: `tests/unit/test_midpoint_service.py`
  - [x] `test_midpoint_of_two_locations`: 두 좌표 중간지점 계산
  - [x] `test_midpoint_of_single_location`: 단일 좌표 → 본인 반환
  - [x] `test_find_meeting_station_returns_station`: 중간지점에서 역 반환
  - [x] `test_find_meeting_station_always_returns`: 어떤 좌표든 항상 역 반환
  - [x] `test_empty_locations_raises`: 빈 리스트 → `InvalidLocationError`

- [x] Step 5: `tests/unit/properties/strategies.py` 업데이트
  - [x] `seoul_locations()` 전략 추가 (서울 범위 좌표)

- [x] Step 6: `tests/unit/properties/test_haversine_properties.py`
  - [x] PBT-H01: `distance(a, b) >= 0`
  - [x] PBT-H02: `distance(a, b) == distance(b, a)` (대칭)
  - [x] PBT-H03: `distance(a, a) == 0` (동일 좌표)
  - [x] PBT-H04: `distance(a, b) <= 20015` (최대 거리 bounded)

- [x] Step 7: `tests/unit/properties/test_midpoint_properties.py`
  - [x] PBT-M01: `midpoint([loc]) == loc`
  - [x] PBT-M02: `midpoint([a,b]) == midpoint([b,a])` (교환법칙)
  - [x] PBT-M03: 결과 lat ∈ [-90, 90]
  - [x] PBT-M04: 결과 lng ∈ [-180, 180]

- [x] Step 8: `aidlc-docs/construction/unit-2-location-midpoint/code/summary.md`

---

## 완료 검증

```bash
pytest tests/unit/test_hardcoded_station_repository.py \
       tests/unit/test_midpoint_service.py \
       tests/unit/properties/test_haversine_properties.py \
       tests/unit/properties/test_midpoint_properties.py -v
```
