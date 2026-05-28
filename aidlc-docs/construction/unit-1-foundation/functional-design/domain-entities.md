# Domain Entities — Unit 1: Foundation

## Location

```python
class Location(BaseModel, frozen=True):
    lat: float  # 위도: -90.0 ~ 90.0
    lng: float  # 경도: -180.0 ~ 180.0
```

- **유형**: Value Object (불변)
- **불변식**: `lat ∈ [-90, 90]`, `lng ∈ [-180, 180]`
- **동등성**: 값 기준 (`lat`, `lng` 동일 시 동일 객체)
- **직렬화**: Pydantic 기본 직렬화 (`model_dump()` / `model_validate()`)

---

## Station

```python
class Station(BaseModel):
    id: str         # 고유 식별자 (예: "hongdae")
    name: str       # 역 이름 (예: "홍대입구")
    line: str       # 호선 (예: "2호선")
    lat: float      # 위도
    lng: float      # 경도
```

- **유형**: Entity
- **식별자**: `id` (문자열)
- **불변식**: `name`과 `line`은 비어있을 수 없음

---

## Place

```python
class Place(BaseModel):
    id: str
    name: str
    description: str
    category: str                    # "레스토랑", "카페", "바" 등
    subcategory: str                 # "이탈리안", "디저트" 등
    tags: list[str]                  # ["데이트", "커플", "와인"] — list[str]
    station: str                     # 가장 가까운 역 이름
    exit_number: int                 # 출구 번호
    distance_from_station_m: int     # 역 출구에서 거리 (미터)
    address: str
    lat: float
    lng: float
    rating: float                    # 0.0 ~ 5.0
    price_range: str                 # "저렴" | "중간" | "비쌈"
```

- **유형**: Entity
- **식별자**: `id` (문자열)
- **tags**: `list[str]` — 도메인 모델과 API 응답 모두 리스트. `places.json`의 콤마 문자열은 인제스트 스크립트에서 파싱.
- **불변식**: `rating ∈ [0.0, 5.0]`, `distance_from_station_m ≥ 0`, `price_range ∈ {"저렴", "중간", "비쌈"}`

---

## Recommendation

```python
class Recommendation(BaseModel, frozen=True):
    place: Place
    similarity_score: float    # 0.0 ~ 1.0 (높을수록 유사)
```

- **유형**: Value Object (불변)
- **similarity_score 계산**: `1 - chroma_distance` (ChromaDB 코사인 거리 변환)
  - ChromaDB 코사인 거리 0.0 → similarity_score 1.0 (완전 일치)
  - ChromaDB 코사인 거리 1.0 → similarity_score 0.0 (완전 불일치)
- **불변식**: `similarity_score ∈ [0.0, 1.0]`
- **정렬 기준**: similarity_score 내림차순 (높을수록 상위)

---

## Settings

```python
class Settings(BaseSettings):
    embedding_model: str = "jhgan/ko-sroberta-multitask"
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "places"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    station_search_radius_km: float = 5.0   # 역 탐색 기본 반경
    default_top_k: int = 3                   # 기본 추천 개수

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

---

## 인터페이스 (포트)

```python
class EmbeddingPort(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]: ...

class StationRepository(ABC):
    @abstractmethod
    def find_nearest(self, location: Location, radius_km: float) -> Station | None: ...

class VectorRepository(ABC):
    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]: ...
```

---

## 예외 계층

```
DomainError (base)
├── NoNearbyStationError     — 반경 내 역 없음
├── NoRecommendationsError   — 벡터 검색 결과 없음
├── VectorDBError            — 벡터 DB 접근 오류
└── InvalidLocationError     — 유효하지 않은 좌표
```
