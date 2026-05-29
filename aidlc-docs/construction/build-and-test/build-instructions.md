# Build Instructions

## Prerequisites

- **언어**: Python 3.11+
- **빌드 도구**: pip (패키지 설치)
- **ASGI 서버**: Uvicorn 0.30+
- **환경 변수**: `.env` 파일 (선택 — 기본값으로 동작)
- **시스템 요구사항**: RAM 4GB+ (SBERT 모델 로드 시), SSD 권장

## 환경 변수 (.env)

| 변수 | 기본값 | 설명 |
|---|---|---|
| `EMBEDDING_MODEL` | `jhgan/ko-sroberta-multitask` | SBERT 모델명 |
| `CHROMA_PERSIST_DIR` | `./data/chroma_db` | ChromaDB 저장 경로 |
| `CHROMA_COLLECTION_NAME` | `places` | 컬렉션명 |
| `APP_HOST` | `0.0.0.0` | 서버 호스트 |
| `APP_PORT` | `8000` | 서버 포트 |
| `DEFAULT_TOP_K` | `3` | 기본 추천 개수 |

## Build Steps

### 1. 가상 환경 생성 및 활성화

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 2. 프로덕션 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 개발/테스트 의존성 설치

```bash
pip install -r requirements-dev.txt
```

### 4. 환경 변수 설정 (선택)

```bash
# .env 파일 생성 (기본값 사용 시 불필요)
cp .env.example .env  # 예시 파일이 있는 경우
```

### 5. 벡터 DB 초기화 (추천 API 실행 전 필수)

```bash
python scripts/ingest_to_vectordb.py
```

> **주의**: SBERT 모델(`jhgan/ko-sroberta-multitask`)이 최초 실행 시 HuggingFace에서 자동 다운로드됩니다 (~500MB).

### 6. 서버 실행

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. 빌드 성공 확인

- 서버 시작 후 `http://localhost:8000/docs` 접속 → Swagger UI 확인
- 자동 생성 엔드포인트: `POST /api/v1/midpoint`, `POST /api/v1/recommend`

## 빌드 산출물

| 산출물 | 위치 | 설명 |
|---|---|---|
| ChromaDB 벡터 저장소 | `data/chroma_db/` | ingest 후 생성 |
| FastAPI OpenAPI 스펙 | `http://localhost:8000/openapi.json` | 런타임 생성 |

## 트러블슈팅

### 모듈 임포트 오류 (`ModuleNotFoundError`)
- **원인**: 가상 환경이 활성화되지 않았거나 의존성 미설치
- **해결**: `.venv` 활성화 후 `pip install -r requirements-dev.txt` 재실행

### ChromaDB 오류 (`Collection not found`)
- **원인**: `ingest_to_vectordb.py` 미실행
- **해결**: `python scripts/ingest_to_vectordb.py` 실행

### SBERT 모델 다운로드 실패
- **원인**: 인터넷 연결 없음 또는 HuggingFace 접근 차단
- **해결**: 네트워크 확인 또는 프록시 설정 (`HF_ENDPOINT` 환경 변수)
