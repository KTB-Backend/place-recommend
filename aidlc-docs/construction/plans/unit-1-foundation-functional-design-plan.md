# Unit 1: Foundation — Functional Design Plan

## 실행 체크리스트

- [x] domain-entities.md 생성 (도메인 모델 상세 정의)
- [x] business-rules.md 생성 (유효성 규칙 + PBT 속성 목록)
- [x] business-logic-model.md 생성 (흐름 및 불변식)
- [x] 설계 완전성 검증

---

## 유닛 범위

Unit 1은 순수 도메인 계층입니다. 외부 의존성이 없으며 모든 다른 유닛의 기반이 됩니다.

**포함 컴포넌트**: `Location`, `Station`, `Place`, `Recommendation`, `EmbeddingPort`, `StationRepository`, `VectorRepository`, `DomainError` 계층, `Settings`

---

## 설계 질문

### Question 1
`Place.tags` 필드를 도메인 모델에서 어떻게 표현할까요?
(참조: `where-meeting`의 `places.json`은 `"데이트,커플,와인"` 형태의 콤마 구분 문자열로 저장)

A) `list[str]` — Python 도메인 모델에서는 리스트로 파싱, JSON 직렬화 시 리스트 유지

B) `str` — JSON 원본 그대로 콤마 구분 문자열로 유지, 파싱은 사용 측에서 처리

C) `list[str]` 도메인 모델 + JSON 인제스트 시 파싱 — 도메인은 리스트, `places.json`은 콤마 문자열 그대로 유지 후 인제스트 스크립트에서 변환

X) Other (please describe after [Answer]: tag below)

[Answer]: A

---

### Question 2
`Recommendation.similarity_score` 의미를 어떻게 정의할까요?
(ChromaDB는 코사인 거리를 반환 — 0에 가까울수록 유사함)

A) 거리(distance) 그대로 노출 — 낮을수록 유사 (0.0 ~ 2.0 범위, L2 기준)

B) 유사도(similarity)로 변환 — `1 - distance`로 변환, 높을수록 유사 (0.0 ~ 1.0)

C) 퍼센트 점수로 변환 — `(1 - distance) * 100`, 높을수록 유사 (0 ~ 100)

X) Other (please describe after [Answer]: tag below)

[Answer]: B

---

### Question 3
`Settings`에 포함할 추가 설정값이 있나요?
현재 정의: `embedding_model`, `chroma_persist_dir`, `chroma_collection_name`, `app_host`, `app_port`

A) 없음 — 현재 정의로 충분

B) 추가 필요 — `station_search_radius_km` (기본 역 탐색 반경, 현재 5.0 하드코딩)

C) 추가 필요 — B + `default_top_k` (기본 추천 개수, 현재 3 하드코딩)

X) Other (please describe after [Answer]: tag below)

[Answer]: C

---

답변 완료 후 알려주세요.
