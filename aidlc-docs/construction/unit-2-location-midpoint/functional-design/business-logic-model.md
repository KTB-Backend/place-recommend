# Business Logic Model — Unit 2: Location & Midpoint

## 컴포넌트 흐름

```
[API 계층 - Unit 4]
        │
        │ list[Location]
        ▼
[MidpointService]  ──────────────────────────────────────┐
   application/midpoint_service.py                       │
        │                                                 │
        │ 1. calculate_midpoint()                         │
        │    → Location (산술 평균)                        │
        │                                                 │
        │ 2. repository.find_nearest(midpoint, radius_km) │
        │                                                 │
        ▼                                                 │
[HardcodedStationRepository]                             │
   infrastructure/station/hardcoded_station_repository.py│
        │                                                 │
        │ Haversine 거리 계산 (26개 역 순회)               │
        │                                                 │
        ▼                                                 │
   Station | None ────────────────────────────────────────┘
        │
        │ None → NoNearbyStationError
        │ Station → return
        ▼
   Station (결과)
```

---

## MidpointService 메서드 시그니처

```python
class MidpointService:
    def __init__(self, repository: StationRepository, settings: Settings) -> None: ...

    def calculate_midpoint(self, locations: list[Location]) -> Location:
        """산술 평균으로 중간지점 계산. locations 비어있으면 InvalidLocationError."""

    def find_meeting_station(self, locations: list[Location]) -> Station:
        """중간지점에서 가장 가까운 역 반환. 반경 내 없으면 NoNearbyStationError."""
```

## HardcodedStationRepository 메서드 시그니처

```python
class HardcodedStationRepository(StationRepository):
    _STATIONS: list[Station]  # 26개 역 클래스 변수

    def find_nearest(self, location: Location, radius_km: float) -> Station | None:
        """Haversine 거리 최솟값인 역 반환. radius_km 초과 시 None."""
```

---

## 의존성 방향

```
MidpointService
    └── depends on → StationRepository (ABC, domain layer)
                         ↑ implements
                 HardcodedStationRepository (infrastructure layer)
```

- `MidpointService`는 `StationRepository` ABC에만 의존 (인터페이스 역전 원칙 준수)
- 실제 구현체(`HardcodedStationRepository`)는 Unit 4 DI에서 주입
