# Requirements Verification Questions

`where-meeting` 프로젝트를 `where` 워크스페이스에 구현하기 위한 요구사항 확인 질문입니다.
각 질문에 `[Answer]:` 태그 다음에 선택한 알파벳을 입력해주세요.

---

## Question 1
구현 범위를 어떻게 설정할까요?

A) `where-meeting`을 그대로 포팅 (완전 동일하게 구현)

B) `where-meeting` 기반으로 개선/확장 (기존 코드 + 새 기능 추가)

C) `where-meeting`을 참고만 하고 새롭게 설계 (아키텍처 재설계)

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question 2
Phase 2 기능 (카카오 Maps API를 활용한 실시간 역 검색)을 이번 구현에 포함할까요?
현재 `where-meeting`은 26개 서울 역이 하드코딩되어 있습니다.

A) 아니요 — Phase 1만 구현 (하드코딩된 26개 역 사용)

B) 예 — 카카오 Maps API 연동으로 실시간 역 검색 구현

C) 선택적 — 설정으로 카카오 API 여부를 전환 가능하게 구현

X) Other (please describe after [Answer]: tag below)

[Answer]: X, 현재 단계에서는 하드 코딩 데이터로 테스트 진행하고 이후 카카오 Maps API 연동 예정

---

## Question 3
LLM 연동 (AI 설명 생성)을 이번 구현에 포함할까요?
현재 `where-meeting`은 단순 벡터 검색만 수행하며 LLM은 계획 단계입니다.

A) 아니요 — 벡터 검색 결과만 반환 (LLM 없음)

B) 예 — Claude API 연동하여 추천 이유 AI 설명 생성

C) 예 — OpenAI API 연동하여 추천 이유 AI 설명 생성

X) Other (please describe after [Answer]: tag below)

[Answer]: A, 이후 개선 예정

---

## Question 4
장소 데이터를 어떻게 관리할까요?
현재 `where-meeting`은 `data/processed/places.json`에 약 100+개 업체 데이터가 있습니다.

A) `where-meeting`의 기존 데이터 그대로 사용

B) 데이터를 확장/수정하여 사용

C) 외부 API (카카오 플레이스 등)로 실시간 데이터 조회

X) Other (please describe after [Answer]: tag below)

[Answer]: B, 이후 개선 예정

---

## Question 5
성능 및 확장성 요구사항은 어느 수준인가요?

A) 개발/프로토타입 수준 — 로컬 ChromaDB, 단일 프로세스

B) 소규모 프로덕션 — ChromaDB 유지, Docker 컨테이너화

C) 중대형 프로덕션 — Qdrant 마이그레이션, Redis 캐싱, 수평 확장 고려

X) Other (please describe after [Answer]: tag below)

[Answer]: A, 이후 개선 예정

---

## Question 6
테스트 커버리지 요구사항은 어느 수준인가요?

A) 기본 — `where-meeting`과 동일한 수준 (retriever 단위 테스트만)

B) 표준 — 단위 테스트 + 통합 테스트 (API 엔드포인트 포함)

C) 포괄적 — 단위 + 통합 + E2E 테스트 + 성능 테스트

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

## Question 7
추가로 구현하고 싶은 API 기능이 있나요?
현재 `where-meeting`은 `/health`, `/api/v1/recommend` 두 개의 엔드포인트가 있습니다.

A) 없음 — 기존 엔드포인트만 구현

B) 예 — 사용자 피드백/평가 API 추가 (Phase 3 계획 기능)

C) 예 — 다중 중간지점 계산 API 추가 (여러 출발지 → 중간지점 계산)

D) 예 — B와 C 모두 추가

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

## Question: Security Extensions
이 프로젝트에 보안 확장 규칙을 적용할까요?

A) 예 — 모든 보안 규칙을 필수 제약으로 적용 (프로덕션 수준 앱에 권장)

B) 아니요 — 보안 규칙 생략 (PoC, 프로토타입, 실험적 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: B, 이후 개선 예정

---

## Question: Property-Based Testing Extension
이 프로젝트에 속성 기반 테스트(PBT) 규칙을 적용할까요?

A) 예 — 모든 PBT 규칙을 필수 제약으로 적용 (비즈니스 로직, 데이터 변환, 직렬화가 있는 프로젝트에 권장)

B) 부분적 — 순수 함수와 직렬화 라운드트립에만 PBT 규칙 적용

C) 아니요 — PBT 규칙 생략 (단순 CRUD, UI 전용, 얇은 통합 레이어에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---
