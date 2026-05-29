# Performance Test Instructions

## 현재 범위

**프로토타입 단계** — 공식 성능 목표(NFR)가 정의되지 않았습니다.  
현재 단계에서는 기본 응답 시간 확인 수준의 수동 테스트만 권장합니다.

## 기본 응답 시간 확인

### 1. 서버 실행 및 데이터 인제스트

```bash
python scripts/ingest_to_vectordb.py
uvicorn api.main:app --reload
```

### 2. 수동 응답 시간 측정

```bash
# /midpoint 응답 시간
curl -s -w "\n응답 시간: %{time_total}s\n" \
  -X POST http://localhost:8000/api/v1/midpoint \
  -H "Content-Type: application/json" \
  -d '{"locations": [{"lat": 37.5, "lng": 127.0}, {"lat": 37.6, "lng": 127.1}]}'

# /recommend 응답 시간
curl -s -w "\n응답 시간: %{time_total}s\n" \
  -X POST http://localhost:8000/api/v1/recommend \
  -H "Content-Type: application/json" \
  -d '{"locations": [{"lat": 37.5, "lng": 127.0}, {"lat": 37.6, "lng": 127.1}], "query": "조용한 카페"}'
```

### 3. 예상 응답 시간 (참고)

| 엔드포인트 | 예상 시간 | 병목 |
|---|---|---|
| `POST /midpoint` | < 50ms | Haversine 계산 (무시할 수준) |
| `POST /recommend` (최초) | 1~3초 | SBERT 임베딩 생성 |
| `POST /recommend` (반복) | 200~500ms | ChromaDB 쿼리 |

> **참고**: SBERT 임베딩은 CPU 기준입니다. GPU 사용 시 대폭 개선.

## 향후 성능 테스트 (프로토타입 이후)

프로덕션 전환 시 아래 도구 및 목표 검토 권장:

```bash
# locust를 이용한 부하 테스트
pip install locust
locust -f locustfile.py --headless -u 10 -r 1 --run-time 60s
```

| 지표 | 권장 목표 (프로덕션) |
|---|---|
| 응답 시간 P95 | < 500ms |
| 처리량 | 10 req/s |
| 오류율 | < 1% |
