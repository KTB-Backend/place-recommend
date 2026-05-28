# Component Methods

상세 비즈니스 로직은 Functional Design(Construction Phase)에서 정의됩니다.
여기서는 메서드 시그니처와 계약(contract)만 정의합니다.

---

## domain/models.py

```python
class Location(BaseModel, frozen=True):
    lat: float   # -90.0 ~ 90.0
    lng: float   # -180.0 ~ 180.0

class Station(BaseModel):
    id: str
    name: str
    line: str
    lat: float
    lng: float

class Place(BaseModel):
    id: str
    name: str
    description: str
    category: str
    subcategory: str
    tags: list[str]
    station: str
    exit_number: int
    distance_from_station_m: int
    address: str
    lat: float
    lng: float
    rating: float
    price_range: str  # "저렴" | "중간" | "비쌈"

class Recommendation(BaseModel, frozen=True):
    place: Place
    similarity_score: float   # 0.0 ~ 1.0 (낮을수록 유사)
```

---

## domain/interfaces.py

```python
class EmbeddingPort(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """텍스트 목록을 벡터 목록으로 변환."""
        ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 텍스트를 벡터로 변환."""
        ...

class StationRepository(ABC):
    @abstractmethod
    def find_nearest(
        self, location: Location, radius_km: float
    ) -> Station | None:
        """location 기준 radius_km 이내 가장 가까운 역 반환. 없으면 None."""
        ...

class VectorRepository(ABC):
    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]:
        """station_name 필터 + 코사인 유사도로 top_k 추천 반환."""
        ...
```

---

## domain/exceptions.py

```python
class DomainError(Exception):
    """도메인 예외 기본 클래스."""

class NoNearbyStationError(DomainError):
    """중간지점 반경 내 지하철역 없음."""

class NoRecommendationsError(DomainError):
    """벡터 검색 결과 없음."""

class VectorDBError(DomainError):
    """벡터 DB 접근/쿼리 오류."""

class InvalidLocationError(DomainError):
    """유효하지 않은 좌표 입력."""
```

---

## application/midpoint_service.py

```python
class MidpointService:
    def calculate(self, locations: list[Location]) -> Location:
        """
        2개 이상 좌표의 지리적 중간지점 계산.
        - 입력: 최소 2개 Location
        - 출력: 중간지점 Location
        - 예외: InvalidLocationError (locations < 2)
        - 알고리즘: 위경도 산술 평균 (소규모 거리 기준 근사치로 충분)
        """
        ...
```

---

## application/recommendation_service.py

```python
@dataclass
class RecommendResult:
    midpoint: Location
    nearest_station: Station
    nearest_station_distance_m: float
    category: str
    recommendations: list[Recommendation]

class RecommendationService:
    def __init__(
        self,
        station_repo: StationRepository,
        vector_repo: VectorRepository,
    ) -> None: ...

    def recommend(
        self,
        midpoint: Location,
        category: str,
        radius_km: float = 5.0,
        top_k: int = 3,
    ) -> RecommendResult:
        """
        1. station_repo.find_nearest()로 최근접 역 탐색
        2. 역 없으면 NoNearbyStationError 발생
        3. 쿼리 구성: "{역이름} 주변 {category}하기 좋은 장소"
        4. vector_repo.search()로 추천 목록 반환
        5. 결과 없으면 NoRecommendationsError 발생
        """
        ...
```

---

## infrastructure/embedding/sbert_embedder.py

```python
class SBERTEmbedder(EmbeddingPort):
    def __init__(self, model_name: str) -> None:
        """SentenceTransformer 모델 로드 (최초 1회)."""
        ...

    def embed(self, texts: list[str]) -> list[list[float]]:
        """배치 임베딩 생성."""
        ...

    def embed_query(self, text: str) -> list[float]:
        """단일 쿼리 임베딩 생성."""
        ...
```

---

## infrastructure/station/hardcoded_station_repository.py

```python
class HardcodedStationRepository(StationRepository):
    def __init__(self) -> None:
        """서울 주요 역 26개 하드코딩 데이터 로드."""
        ...

    def find_nearest(
        self, location: Location, radius_km: float
    ) -> Station | None:
        """Haversine 거리 계산 후 radius_km 이내 최근접 역 반환."""
        ...
```

---

## infrastructure/vector/chroma_vector_repository.py

```python
class ChromaVectorRepository(VectorRepository):
    def __init__(
        self,
        embedder: EmbeddingPort,
        persist_dir: str,
        collection_name: str,
    ) -> None:
        """ChromaDB 클라이언트 초기화, 컬렉션 연결."""
        ...

    def search(
        self,
        query_embedding: list[float],
        station_name: str,
        top_k: int,
    ) -> list[Recommendation]:
        """station_name 메타데이터 필터 + 코사인 유사도 검색."""
        ...
```

---

## api/dependencies.py

```python
@lru_cache
def get_settings() -> Settings: ...

@lru_cache
def get_embedding_port() -> EmbeddingPort:
    """SBERTEmbedder 싱글톤 반환."""
    ...

@lru_cache
def get_station_repository() -> StationRepository:
    """HardcodedStationRepository 싱글톤 반환."""
    ...

@lru_cache
def get_vector_repository() -> VectorRepository:
    """ChromaVectorRepository 싱글톤 반환. EmbeddingPort에 의존."""
    ...

def get_recommendation_service(
    station_repo: StationRepository = Depends(get_station_repository),
    vector_repo: VectorRepository = Depends(get_vector_repository),
) -> RecommendationService: ...

def get_midpoint_service() -> MidpointService: ...
```

---

## api/v1/midpoint.py

```python
class MidpointRequest(BaseModel):
    locations: list[Location]   # 최소 2개

class MidpointResponse(BaseModel):
    midpoint: Location
    location_count: int

@router.post("/midpoint", response_model=MidpointResponse)
async def calculate_midpoint(
    request: MidpointRequest,
    service: MidpointService = Depends(get_midpoint_service),
) -> MidpointResponse: ...
```

---

## api/v1/recommend.py

```python
class RecommendRequest(BaseModel):
    midpoint: Location
    category: str
    radius_km: float = 5.0
    top_k: int = Field(default=3, ge=1, le=10)

class RecommendationItem(BaseModel):
    name: str
    category: str
    subcategory: str
    address: str
    station: str
    distance_from_station_m: int
    rating: float
    price_range: str
    tags: list[str]
    similarity_score: float

class RecommendResponse(BaseModel):
    midpoint: Location
    nearest_station: str
    nearest_station_distance_m: float
    category: str
    results: list[RecommendationItem]
    total_found: int

@router.post("/recommend", response_model=RecommendResponse)
async def recommend_places(
    request: RecommendRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendResponse: ...
```
