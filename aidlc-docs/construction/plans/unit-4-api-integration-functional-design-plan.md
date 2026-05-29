# Unit 4: API & Integration — Functional Design Plan

## 목표
FastAPI 진입점, 의존성 주입 컨테이너, 라우터 2개, 통합 테스트를 설계한다.

## 산출물 목록

- [x] `aidlc-docs/construction/unit-4-api-integration/functional-design/domain-entities.md`
- [x] `aidlc-docs/construction/unit-4-api-integration/functional-design/business-rules.md`
- [x] `aidlc-docs/construction/unit-4-api-integration/functional-design/business-logic-model.md`

## 설계 질문

[Answer Q1]: POST /api/v1/midpoint 응답 형태를 선택해 주세요.
A) Station 도메인 모델 전체 필드 반환 (id, name, line, lat, lng)
B) 간소화 응답 — name + lat + lng만 반환 (별도 Pydantic 응답 모델)

[Answer Q2]: POST /api/v1/recommend 요청에서 query 파라미터 처리를 선택해 주세요.
A) query는 필수 (빈 문자열 허용 안 함)
B) query는 선택(Optional) — 비어있으면 역 이름 기반 텍스트를 자동 생성해 쿼리

[Answer Q3]: 에러 응답 포맷을 선택해 주세요.
A) {"detail": "에러 메시지"} — FastAPI 기본 HTTPException 포맷
B) {"error": "에러 코드", "message": "설명"} — 커스텀 에러 바디

[Answer Q4]: 통합 테스트 의존성 처리를 선택해 주세요.
A) TestClient + 실제 ChromaDB (인메모리 chroma 클라이언트 사용)
B) TestClient + 전체 Mock (SBERTEmbedder, ChromaVectorRepository 모두 mock)

[Answer Q5]: locations 배열 입력 검증 규칙을 선택해 주세요.
A) 최소 2개 ~ 최대 10개 (Pydantic Field 제약)
B) 최소 1개 이상 (단일 위치도 허용, 하한선만 체크)
