# Application Design Plan

## 실행 체크리스트

- [x] 컴포넌트 정의 및 책임 문서화 (components.md)
- [x] 컴포넌트 메서드 시그니처 문서화 (component-methods.md)
- [x] 서비스 레이어 설계 문서화 (services.md)
- [x] 컴포넌트 의존성 관계 문서화 (component-dependency.md)
- [x] 통합 설계 문서 (application-design.md)
- [x] 설계 완전성 및 일관성 검증

---

## 설계 컨텍스트 분석

요구사항에서 도출한 주요 컴포넌트 후보:

### 도메인 레이어 (Domain)
- `Location` — 위도/경도 값 객체
- `Station` — 지하철역 엔터티 (이름, 호선, 좌표)
- `Place` — 장소 엔터티 (이름, 카테고리, 주소, 평점 등)
- `Recommendation` — 추천 결과 값 객체 (장소 + 유사도 점수)

### 인터페이스 레이어 (Ports/Interfaces)
- `StationRepository` (ABC) — 역 탐색 추상화 (Phase 2 카카오 API 교체 지점)
- `VectorRepository` (ABC) — 벡터 검색 추상화 (Phase 3 Qdrant 교체 지점)

### 애플리케이션 레이어 (Application Services)
- `MidpointService` — 다중 좌표 → 중간지점 계산
- `RecommendationService` — 역 탐색 + 벡터 검색 오케스트레이션

### 인프라 레이어 (Infrastructure)
- `HardcodedStationRepository` — StationRepository 구현체 (하드코딩 역 데이터)
- `ChromaVectorRepository` — VectorRepository 구현체 (ChromaDB)
- `SBERTEmbedder` — 한국어 임베딩 모델 (jhgan/ko-sroberta-multitask)

### API 레이어
- FastAPI 앱 + v1 라우터
- `POST /api/v1/midpoint` 핸들러
- `POST /api/v1/recommend` 핸들러
- `GET /health` 핸들러

---

## 설계 질문

### Question 1
`StationRepository`와 `VectorRepository` 인터페이스를 어느 레이어에 위치시킬까요?

A) Domain 레이어 — 인터페이스를 도메인 패키지 안에 정의 (포트-어댑터 패턴)

B) 별도 `ports/` 패키지 — domain, application, infrastructure와 분리된 독립 레이어

C) Application 레이어 — 서비스가 선언하는 인터페이스로 application 패키지 안에 위치

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2
`SBERTEmbedder` (임베딩 모델)를 어떻게 설계할까요?

A) 독립 서비스 클래스 — `EmbeddingService`로 분리, `VectorRepository`가 의존

B) `ChromaVectorRepository` 내부에 포함 — 임베더를 레포지토리 생성자에서 주입

C) 별도 인터페이스 (`EmbeddingPort`) 정의 — 미래에 다른 임베딩 모델로 교체 가능

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Question 3
FastAPI 의존성 주입(DI)을 어떻게 구성할까요?

A) `Depends()` + 모듈 수준 팩토리 함수 — 각 라우터 파일에서 의존성 선언

B) `lifespan` 이벤트에서 싱글톤 생성 후 `app.state`에 저장 — 요청마다 `request.app.state`에서 꺼냄

C) 별도 `dependencies.py` 파일 — 모든 DI 설정을 한 곳에서 관리

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

### Question 4
에러 처리 전략을 어떻게 설정할까요?

A) 예외(Exception) 기반 — 도메인 예외 정의, FastAPI `exception_handler`로 HTTP 응답 변환

B) Result 패턴 — 성공/실패를 `Result[T]` 타입으로 반환, 예외 미사용

C) 혼합 — 예외는 진짜 오류(DB 연결 실패 등)에만, 비즈니스 실패(역 없음 등)는 Optional/None 반환

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 5
프로젝트 최상위 디렉토리 구조는 어떻게 할까요?

A) `app/` 단일 패키지 — `app/domain/`, `app/application/`, `app/infrastructure/`, `app/api/`

B) `src/` 레이아웃 — `src/` 아래에 패키지 배치 (Python packaging 표준)

C) 플랫 구조 — `domain/`, `application/`, `infrastructure/`, `api/` 를 루트에 직접 배치

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

답변을 모두 채우신 후 알려주세요.
