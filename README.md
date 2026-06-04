# mid-meet

여러 사용자의 출발역을 입력받아 중간 지하철역을 계산하고, 그 주변에서 만남 장소를 추천하는 FastAPI 기반 백엔드입니다. 추천 데이터는 Kakao Local API로 수집한 장소 데이터를 기반으로 ChromaDB에 적재하고, SBERT 임베딩 검색으로 질의에 맞는 장소를 찾습니다.

## 주요 기능

- 출발역 이름 기반 중간역 계산
- 좌표 기반 `/midpoint`, `/recommend` 요청도 하위 호환 지원
- 추천 데이터가 있는 중간역이면 바로 장소 추천 반환
- 중간역 주변에 추천 데이터가 없으면 가까운 후보역 3개를 사용자에게 선택지로 반환
- 후보역이 마음에 들지 않을 때 기존 중간역 기준 Kakao Map 검색 링크 제공
- 정적 프론트엔드 제공: `http://localhost:8000/`

## 기술 스택

- Python 3.11+
- FastAPI, Uvicorn
- Pydantic v2, pydantic-settings
- ChromaDB
- sentence-transformers, Torch
- Kakao Local API
- pytest, Hypothesis, pytest-cov
- Ruff, mypy

## 디렉터리 구조

```text
domain/          도메인 모델, 예외, 포트 인터페이스
application/     유스케이스 서비스
infrastructure/  ChromaDB, SBERT, Kakao, 역 저장소 구현체
api/             FastAPI 앱, 라우터, 스키마, 의존성 주입
core/            환경 설정
data/processed/  장소 데이터
docs/            API 문서
frontend/        정적 웹 화면
scripts/         데이터 수집 및 벡터 DB 적재 스크립트
tests/           단위, 통합, property-based 테스트
```

## 로컬 실행

### 1. 의존성 설치

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt
```

### 2. 환경 변수 설정

```bash
copy .env.example .env
```

`.env`에 Kakao REST API 키를 설정합니다.

```env
KAKAO_REST_API_KEY=your_kakao_rest_api_key
KAKAO_SSL_VERIFY=true
```

`.env`와 `data/chroma_db`는 커밋하지 않습니다.

### 3. Kakao 장소 데이터 수집

```bash
python scripts/fetch_kakao_places.py
```

성공하면 `data/processed/places.json`이 갱신됩니다. Kakao API 제한이나 네트워크 오류가 발생하면 기존 `places.json`은 보존하고 `data/processed/places.partial.json`에 부분 결과만 저장합니다.

이미 데이터가 있는 역을 반복 수집하지 않으려면 데이터가 0개인 역만 대상으로 실행합니다.

```bash
python scripts/fetch_kakao_places.py --missing-only
```

기본 실행은 `missing-first` 방식입니다. 현재 `places.json`을 읽어 데이터가 없는 역을 먼저 수집하고, Kakao에서 `API limit has been exceeded`가 반환되면 남은 호출을 즉시 중단합니다.

현재 로컬 데이터 기준:

- 장소 데이터: 2,296개
- 데이터가 없는 역: 49개
- 토큰 쿼터가 리셋된 뒤 `--missing-only`로 재수집

### 4. 벡터 DB 적재

```bash
python scripts/ingest_to_vectordb.py
```

최초 실행 시 SBERT 모델 다운로드가 발생할 수 있습니다.

### 5. 서버 실행

```bash
uvicorn api.main:app --reload --port 8000
```

- 프론트엔드: `http://localhost:8000/`
- Swagger UI: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

## API 예시

자세한 내용은 [docs/API.md](docs/API.md)를 참고합니다.

### 중간역 계산

```http
POST /api/v1/midpoint
```

```json
{
  "stations": ["서울역", "강남역"]
}
```

### 장소 추천

```http
POST /api/v1/recommend
```

```json
{
  "stations": ["서울역", "강남역"],
  "query": "조용한 카페",
  "top_k": 3
}
```

중간역 주변에 추천 데이터가 있으면 `status: "ok"`와 함께 추천 장소를 반환합니다.

```json
{
  "status": "ok",
  "meeting_station": {
    "id": "gangnam",
    "name": "강남역",
    "lat": 37.4979,
    "lng": 127.0276
  },
  "recommendations": []
}
```

중간역 주변에 추천 데이터가 없으면 `status: "station_selection_required"`와 함께 선택 가능한 주변역과 Kakao Map 검색 링크를 반환합니다.

```json
{
  "status": "station_selection_required",
  "meeting_station": {
    "id": "hangangjin",
    "name": "한강진",
    "lat": 37.5397,
    "lng": 127.0019
  },
  "station_options": [],
  "map_search": {
    "provider": "kakao_map",
    "label": "한강진 추천 카페 Kakao Map에서 보기",
    "url": "https://map.kakao.com/?q=..."
  }
}
```

사용자가 후보역을 선택하면 `selected_station_id`를 포함해 다시 요청합니다.

```json
{
  "stations": ["서울역", "강남역"],
  "selected_station_id": "gangnam",
  "query": "조용한 카페",
  "top_k": 3
}
```

## 검증 명령

```bash
pytest
ruff check .
mypy .
```

현재 프로젝트 설정상 `pytest`는 커버리지 80% 이상을 요구합니다. 실제 SBERT 모델 다운로드나 ChromaDB 영속 저장소 접근이 필요한 테스트는 기본 단위 테스트에 넣지 않는 것을 권장합니다.

## 개발 규칙

- `domain/`은 FastAPI, ChromaDB, Kakao 같은 외부 구현에 의존하지 않습니다.
- 외부 연동은 `domain.interfaces`의 포트를 `infrastructure/`에서 구현합니다.
- 비즈니스 로직은 `application/`에 두고 라우터에는 요청 변환과 서비스 호출만 둡니다.
- API 스키마는 `api/v1/schemas.py`에 둡니다.
- 환경 값은 `core.config.Settings`와 `.env.example`로 관리합니다.
- 사용자에게 보이는 API 변경은 README 또는 `docs/API.md`도 함께 갱신합니다.
