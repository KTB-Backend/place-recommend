# Requirements Document

## Intent Analysis

- **User Request**: `where-meeting` 프로젝트를 참고하여 `where` 워크스페이스에 RAG 기반 모임 장소 추천 시스템을 새롭게 설계·구현
- **Request Type**: New Project (아키텍처 재설계)
- **Scope Estimate**: System-wide (전체 시스템 신규 구현)
- **Complexity Estimate**: Moderate-Complex (RAG 파이프라인, 벡터 DB, 한국어 임베딩, REST API, PBT)
- **Reference Source**: `C:\Users\Owner\where-meeting` (참조 구현체 - 그대로 포팅하지 않음)

---

## Functional Requirements

### FR-01: 중간지점 계산 API
- 여러 사용자의 출발 위치(위도/경도)를 입력받아 지리적 중간지점을 계산한다
- `POST /api/v1/midpoint` 엔드포인트로 제공
- 최소 2개 이상의 좌표를 입력받아야 한다
- 중간지점 좌표(위도/경도)를 반환한다

### FR-02: 장소 추천 API
- 중간지점 좌표 + 목적 카테고리(데이트, 회식, 스터디 등)를 입력받아 추천 장소 목록을 반환한다
- `POST /api/v1/recommend` 엔드포인트로 제공
- 중간지점에서 가장 가까운 지하철역을 탐색한다
- 해당 역 근처의 장소를 RAG 벡터 검색으로 추천한다
- 기본 top-k=3, 최대 top-k=10 결과 반환

### FR-03: 역 탐색 (Phase 1)
- 현재 단계에서는 서울 주요 역 목록을 하드코딩 데이터로 관리한다
- 향후 카카오 Maps API 연동이 가능하도록 추상화 레이어를 설계한다 (StationRepository 인터페이스)
- Haversine 공식으로 중간지점과 각 역 간의 거리를 계산한다
- 설정 가능한 반경(기본 5km) 내 역을 필터링한다

### FR-04: 벡터 검색 (RAG)
- 장소 데이터를 `jhgan/ko-sroberta-multitask` 한국어 SBERT 모델로 임베딩한다
- ChromaDB에 임베딩 벡터와 메타데이터를 영구 저장한다
- 쿼리: `"{역이름} 주변 {카테고리}하기 좋은 장소"` 형식으로 코사인 유사도 검색
- 역 이름으로 메타데이터 필터링 후 검색 수행

### FR-05: 장소 데이터 관리
- `where-meeting`의 기존 JSON 데이터를 기반으로 확장/수정한다
- 데이터 수집 스크립트와 ChromaDB 인제스트 스크립트를 분리하여 관리한다
- 장소 스키마: id, name, description, category, subcategory, tags, station, exit_number, distance_from_station_m, address, lat, lng, rating, price_range

### FR-06: 헬스 체크 API
- `GET /health` 엔드포인트로 서비스 상태 반환

---

## Non-Functional Requirements

### NFR-01: 아키텍처 (재설계 핵심)
- **클린 아키텍처 적용**: Domain / Application / Infrastructure / API 레이어 명확히 분리
- **Repository 패턴**: `StationRepository` 인터페이스 → `HardcodedStationRepository` (현재) → `KakaoStationRepository` (미래)
- **의존성 주입**: FastAPI의 `Depends()` 시스템 활용
- **도메인 모델**: Pydantic v2 모델로 도메인 객체 정의

### NFR-02: 성능 (프로토타입 수준)
- 응답 시간: 단일 요청 기준 3초 이내 (임베딩 모델 첫 로드 제외)
- 임베딩 모델: 싱글톤 패턴으로 애플리케이션 시작 시 1회 로드
- ChromaDB: 로컬 영구 저장소 (`./data/chroma_db`)
- 동시 요청: 단일 워커 프로세스 (프로토타입 수준)

### NFR-03: 테스트 (표준 + PBT)
- **단위 테스트**: 각 서비스, 유틸리티 함수 단위 테스트 (pytest)
- **통합 테스트**: FastAPI TestClient로 API 엔드포인트 통합 테스트
- **속성 기반 테스트 (PBT)**: Hypothesis 프레임워크 사용 (전체 규칙 적용)
  - Haversine 거리 계산 (불변식: 거리 >= 0, 대칭성)
  - 중간지점 계산 (불변식: 바운딩 박스 내 위치, 교환법칙)
  - Pydantic 모델 직렬화/역직렬화 (라운드트립)
  - 좌표 정규화 함수

### NFR-04: 확장성 (미래 대비 설계)
- 카카오 Maps API 연동: `StationRepository` 인터페이스 구현체 교체만으로 전환 가능
- LLM 연동: `RecommendationService`에 선택적 `LLMProvider` 의존성 주입 슬롯 예약
- Vector DB 마이그레이션: `VectorRepository` 인터페이스로 ChromaDB/Qdrant 교체 가능

### NFR-05: 개발 환경
- Python 3.11+
- 가상환경 기반 (`requirements.txt`)
- `.env` 파일로 환경 변수 관리
- IDE: IntelliJ IDEA (`.idea` 설정 존재)

### NFR-06: 보안
- 현재 단계에서는 보안 규칙 미적용 (프로토타입)
- 이후 단계에서 API 키 관리, 입력값 검증 등 적용 예정

---

## API Specification

### POST /api/v1/midpoint
```
Request:
{
  "locations": [
    {"lat": 37.5665, "lng": 126.9780},
    {"lat": 37.5171, "lng": 127.0473}
  ]
}

Response:
{
  "midpoint": {"lat": 37.5418, "lng": 127.0127},
  "location_count": 2
}
```

### POST /api/v1/recommend
```
Request:
{
  "midpoint": {"lat": 37.5563, "lng": 126.9236},
  "category": "데이트",
  "radius_km": 5.0,
  "top_k": 3
}

Response:
{
  "midpoint": {"lat": 37.5563, "lng": 126.9236},
  "nearest_station": "홍대입구역 (2호선)",
  "nearest_station_distance_m": 450.5,
  "category": "데이트",
  "results": [...],
  "total_found": 3
}
```

### GET /health
```
Response: {"status": "ok"}
```

---

## Architecture Decision Record

### ADR-01: 아키텍처 재설계 (where-meeting 참조 구현 불채택)
- **결정**: where-meeting 코드를 그대로 포팅하지 않고 클린 아키텍처로 재설계
- **이유**: 더 명확한 관심사 분리, 미래 확장성(카카오 API, LLM, Qdrant) 대비
- **결과**: Domain/Application/Infrastructure/API 4개 레이어 구조

### ADR-02: StationRepository 추상화
- **결정**: 역 탐색 로직을 인터페이스로 추상화
- **이유**: Phase 1(하드코딩) → Phase 2(카카오 API) 전환 시 코드 변경 최소화
- **결과**: `StationRepository` ABC → `HardcodedStationRepository` 구현

### ADR-03: PBT 프레임워크 선택 - Hypothesis
- **결정**: Python PBT 프레임워크로 Hypothesis 채택
- **이유**: 성숙한 생태계, 뛰어난 shrinking, pytest 통합
- **결과**: `hypothesis` 의존성 추가, 도메인 전용 strategy 정의

### ADR-04: 새 API 엔드포인트 추가
- **결정**: `POST /api/v1/midpoint` 추가 (where-meeting에 없는 기능)
- **이유**: 여러 출발지 → 중간지점 계산 기능이 핵심 사용 시나리오
- **결과**: MidpointService 별도 구현, 지리 좌표 가중 평균 계산

---

## 구현 제외 사항 (이후 단계)
- 카카오 Maps API 연동 (역 탐색)
- LLM 연동 (Claude/OpenAI - 추천 설명 생성)
- Redis 캐싱
- Qdrant 벡터 DB 마이그레이션
- Docker 컨테이너화
- 사용자 피드백/평가 API
- 보안 강화 (API 키 인증, rate limiting 등)
