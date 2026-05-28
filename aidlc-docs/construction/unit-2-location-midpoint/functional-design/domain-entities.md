# Domain Entities — Unit 2: Location & Midpoint

## 핵심 엔티티

### Station (도메인 모델, Unit 1에서 정의)

```python
class Station(BaseModel):
    id: str        # 고유 식별자 (예: "gangnam")
    name: str      # 역 이름 (예: "강남")
    line: str      # 노선 (예: "2호선")
    lat: float     # 위도
    lng: float     # 경도
```

### Location (도메인 모델, Unit 1에서 정의)

```python
class Location(BaseModel, frozen=True):
    lat: Latitude  # -90.0 ~ 90.0
    lng: Longitude  # -180.0 ~ 180.0
```

---

## 서울 주요 지하철역 데이터 (26개)

선정 기준: 2·3·4·5·6·7·9호선 주요 환승역 및 대표 번화가 역

| id | name | line | lat | lng |
|---|---|---|---|---|
| gangnam | 강남 | 2호선 | 37.4979 | 127.0276 |
| hongdae | 홍대입구 | 2·경의중앙선 | 37.5574 | 126.9249 |
| sinchon | 신촌 | 2호선 | 37.5551 | 126.9368 |
| konkuk | 건대입구 | 2·7호선 | 37.5403 | 127.0698 |
| jamsil | 잠실 | 2·8호선 | 37.5133 | 127.1001 |
| seongsu | 성수 | 2호선 | 37.5447 | 127.0557 |
| hapjeong | 합정 | 2·6호선 | 37.5499 | 126.9138 |
| cityhall | 시청 | 1·2호선 | 37.5650 | 126.9774 |
| jongro3ga | 종로3가 | 1·3·5호선 | 37.5717 | 126.9916 |
| itaewon | 이태원 | 6호선 | 37.5344 | 126.9942 |
| apgujeong | 압구정 | 3호선 | 37.5270 | 127.0282 |
| gyodae | 교대 | 2·3호선 | 37.4935 | 127.0138 |
| express_terminal | 고속터미널 | 3·7·9호선 | 37.5047 | 127.0047 |
| yeouido | 여의도 | 5·9호선 | 37.5216 | 126.9244 |
| gwanghwamun | 광화문 | 5호선 | 37.5716 | 126.9768 |
| snu | 서울대입구 | 2호선 | 37.4813 | 126.9527 |
| wangsimni | 왕십리 | 2·5호선 | 37.5616 | 127.0384 |
| sillim | 신림 | 2호선 | 37.4845 | 126.9293 |
| suyu | 수유 | 4호선 | 37.6385 | 127.0255 |
| nowon | 노원 | 4·7호선 | 37.6541 | 127.0614 |
| dangsan | 당산 | 2·9호선 | 37.5341 | 126.9002 |
| isu | 이수 | 4·7호선 | 37.4850 | 126.9820 |
| seolleung | 선릉 | 2·분당선 | 37.5048 | 127.0495 |
| ddp | 동대문역사문화공원 | 2·4·5호선 | 37.5653 | 127.0099 |
| sinsa | 신사 | 3호선 | 37.5160 | 127.0209 |
| jonggak | 종각 | 1호선 | 37.5703 | 126.9828 |

---

## 컴포넌트 책임

### HardcodedStationRepository
- `StationRepository` ABC 구현체
- 26개 역 데이터를 메모리 내 리스트로 보유
- `find_nearest(location, radius_km)`: Haversine 거리로 최근접 역 탐색

### MidpointService
- 순수 도메인 서비스 (외부 의존성 없음)
- `calculate_midpoint(locations)`: 산술 평균으로 중간지점 계산
- `find_meeting_station(locations)`: 중간지점 → 역 탐색 오케스트레이션
