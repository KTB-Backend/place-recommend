# Unit of Work Plan

## 실행 체크리스트

- [x] unit-of-work.md 생성 (유닛 정의 및 책임)
- [x] unit-of-work-dependency.md 생성 (의존성 매트릭스)
- [x] unit-of-work-story-map.md 생성 (기능 → 유닛 매핑)
- [x] 유닛 경계 및 의존성 검증
- [x] 전체 기능 유닛 배정 확인

---

## 시스템 분해 컨텍스트

Application Design에서 확정된 구조:
- 플랫 패키지 레이아웃 (`domain/`, `application/`, `infrastructure/`, `api/`)
- 단일 FastAPI 모놀리식 서비스
- 14개 컴포넌트, 3개 추상 인터페이스, 2개 애플리케이션 서비스

---

## 분해 질문

### Question 1
단일 FastAPI 서비스를 몇 개의 개발 유닛으로 분해할까요?

A) 3개 유닛 — Foundation(도메인+설정+인프라 기반) / Core Services(비즈니스 로직) / API Layer(라우터+테스트)

B) 4개 유닛 — Foundation / Location & Midpoint / RAG Engine / API & Integration

C) 2개 유닛 — Backend Core(도메인+서비스+인프라) / API & Test

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Question 2
각 유닛 완료 후 중간 검증을 어떻게 할까요?

A) 유닛별 단위 테스트 통과 후 다음 유닛으로 진행

B) 모든 유닛 코드 생성 후 통합 테스트 한 번에 실행

C) 각 유닛 완료 시 서버 실행 가능 상태 유지 (점진적 통합)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 3
데이터 인제스트 스크립트(`scripts/ingest_to_vectordb.py`)와 장소 데이터(`data/processed/places.json`)는 어느 유닛에 포함할까요?

A) RAG/벡터 관련 유닛에 포함 (ChromaVectorRepository와 함께)

B) 별도 독립 유닛으로 분리 (데이터 파이프라인 유닛)

C) 마지막 유닛(API/통합)에 포함 (전체 스택이 준비된 후 인제스트 검증)

X) Other (please describe after [Answer]: tag below)

[Answer]: 

---

[Answer]: A

---

답변 완료.
