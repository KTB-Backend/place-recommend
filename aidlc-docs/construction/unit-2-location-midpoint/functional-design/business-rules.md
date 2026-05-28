# Business Rules — Unit 2: Location & Midpoint

## BR-01: Haversine 거리 계산

```
지구 반지름 R = 6371.0 km

Δlat = lat2 - lat1 (라디안)
Δlng = lng2 - lng1 (라디안)

a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlng/2)
c = 2 × atan2(√a, √(1−a))
distance = R × c
```

**제약**: 입력은 유효한 WGS84 좌표여야 함 (Location 모델이 보장)

---

## BR-02: 최근접 역 탐색

1. 26개 역 전체에 대해 Haversine 거리 계산
2. `radius_km` 이하인 역만 후보로 선정
3. 후보 중 거리 최솟값인 역 반환
4. 후보 없으면 `None` 반환 → 서비스 계층에서 `NoNearbyStationError` 발생

---

## BR-03: 중간지점 계산 (산술 평균)

```
midpoint.lat = Σ(loc.lat) / n
midpoint.lng = Σ(loc.lng) / n
```

**전제**: 서울 내 좌표 (위도 37.4~37.7, 경도 126.8~127.2) 범위에서 구면 오차 무시 가능

**입력 검증**: locations 리스트는 1개 이상이어야 함 (빈 리스트 → `InvalidLocationError`)

---

## BR-04: MidpointService 오케스트레이션

```
find_meeting_station(locations: list[Location]) -> Station:
  1. validate: len(locations) >= 1, else InvalidLocationError
  2. midpoint = calculate_midpoint(locations)
  3. station = repository.find_nearest(midpoint, radius_km)
  4. if station is None: raise NoNearbyStationError
  5. return station
```

---

## PBT 속성 정의

### Haversine 불변식
| ID | 속성 | 검증 방법 |
|---|---|---|
| PBT-H01 | `distance(a, b) >= 0` | 두 임의 좌표에 대해 항상 비음수 |
| PBT-H02 | `distance(a, b) == distance(b, a)` | 대칭성 |
| PBT-H03 | `distance(a, a) == 0` | 동일 좌표 거리 = 0 |
| PBT-H04 | `distance(a, b) <= 20015` | 지구 최대 거리(반둘레 ≈ 20015km) 초과 불가 |

### 중간지점 불변식
| ID | 속성 | 검증 방법 |
|---|---|---|
| PBT-M01 | `midpoint([loc]) == loc` | 단일 좌표의 중간지점 = 본인 |
| PBT-M02 | `midpoint([a,b]) == midpoint([b,a])` | 교환법칙 |
| PBT-M03 | 결과 lat ∈ [-90, 90] | 유효 좌표 범위 유지 |
| PBT-M04 | 결과 lng ∈ [-180, 180] | 유효 좌표 범위 유지 |
