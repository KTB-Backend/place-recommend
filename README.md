# where 📍

> RAG 기반 모임 장소 추천 서비스

여러 사람의 출발 위치를 입력하면 지리적 중간지점을 계산하고, 근처 지하철역 주변의 장소를 AI 임베딩 검색으로 추천합니다.

---

## 주요 기능

- **중간지점 계산** — 2명 이상의 출발 좌표에서 지리적 중간지점 산출
- **RAG 장소 추천** — 중간지점 기준 최근접 역 탐색 → 한국어 벡터 검색으로 목적에 맞는 장소 추천
- **확장 가능한 구조** — 카카오 Maps API, LLM 설명 생성, Qdrant 마이그레이션을 인터페이스 교체만으로 적용 가능

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| API 서버 | FastAPI 0.115+, Uvicorn |
| 임베딩 모델 | `jhgan/ko-sroberta-multitask` (한국어 특화 SBERT) |
| 벡터 DB | ChromaDB (로컬 영구 저장) |
| 데이터 검증 | Pydantic v2 |
| 테스트 | pytest, Hypothesis (PBT) |
| 언어 | Python 3.11+ |

---

## 아키텍처

클린 아키텍처 4레이어로 구성합니다.

```
domain/          ← 도메인 모델 + 인터페이스(포트)
application/     ← 서비스 오케스트레이션
infrastructure/  ← 인터페이스 구현체(어댑터)
api/             ← FastAPI 진입점 + 의존성 주입
```

의존성 방향: `API → Application → Domain ← Infrastructure`

---

## API

### 중간지점 계산

```
POST /api/v1/midpoint
```

```json
// Request
{
  "locations": [
    {"lat": 37.5665, "lng": 126.9780},
    {"lat": 37.5171, "lng": 127.0473}
  ]
}

// Response
{
  "midpoint": {"lat": 37.5418, "lng": 127.0127},
  "location_count": 2
}
```

### 장소 추천

```
POST /api/v1/recommend
```

```json
// Request
{
  "midpoint": {"lat": 37.5563, "lng": 126.9236},
  "category": "데이트",
  "radius_km": 5.0,
  "top_k": 3
}

// Response
{
  "midpoint": {"lat": 37.5563, "lng": 126.9236},
  "nearest_station": "홍대입구역 (2호선)",
  "nearest_station_distance_m": 450.5,
  "category": "데이트",
  "results": [
    {
      "name": "라 파스타 홍대점",
      "category": "레스토랑",
      "subcategory": "이탈리안",
      "address": "서울 마포구 어울마당로 123",
      "station": "홍대입구",
      "distance_from_station_m": 250,
      "rating": 4.5,
      "price_range": "중간",
      "tags": ["데이트", "커플", "와인"],
      "similarity_score": 0.12
    }
  ],
  "total_found": 3
}
```

### 헬스 체크

```
GET /health
→ {"status": "ok"}
```

---

## 로컬 실행

### 1. 환경 설정

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

```bash
cp .env.example .env
# .env 파일에서 필요한 값 설정
```

### 2. 벡터 DB 데이터 인제스트

```bash
python scripts/ingest_to_vectordb.py
```

> 최초 실행 시 임베딩 모델 다운로드 (~400MB)

### 3. 서버 실행

```bash
uvicorn api.main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

---

## 테스트 실행

```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest tests/unit/

# 통합 테스트만
pytest tests/integration/

# PBT (속성 기반 테스트)
pytest tests/unit/properties/ -v
```

---

## 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `EMBEDDING_MODEL` | `jhgan/ko-sroberta-multitask` | 임베딩 모델 이름 |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | ChromaDB 저장 경로 |
| `CHROMA_COLLECTION_NAME` | `places` | ChromaDB 컬렉션 이름 |
| `APP_HOST` | `0.0.0.0` | 서버 호스트 |
| `APP_PORT` | `8000` | 서버 포트 |

---

## 프로젝트 구조

```
where/
├── domain/              # 도메인 모델 + 인터페이스
├── application/         # 비즈니스 서비스
├── infrastructure/      # ChromaDB, SBERT, 역 데이터
│   ├── embedding/
│   ├── station/
│   └── vector/
├── api/                 # FastAPI 앱 + 라우터
│   └── v1/
├── core/                # 설정
├── data/processed/      # 장소 JSON 데이터
├── scripts/             # 데이터 인제스트 스크립트
└── tests/               # 단위 + 통합 + PBT 테스트
```

---

## 로드맵

- [x] Phase 1 — RAG 코어 파이프라인 (현재)
- [ ] Phase 2 — 카카오 Maps API 연동 (실시간 역 탐색)
- [ ] Phase 3 — LLM 연동 (Claude API — 추천 이유 생성)
- [ ] Phase 4 — Qdrant 마이그레이션, Redis 캐싱, Docker 컨테이너화
