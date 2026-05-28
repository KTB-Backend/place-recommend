# Unit of Work Dependency

## 유닛 간 의존성

```
Unit 1: Foundation
    ↓ (모든 유닛의 기반)
Unit 2: Location & Midpoint  ──┐
    ↓                          │ (병렬 가능하나 Unit 3이
Unit 3: RAG Engine         ────┤  Unit 2 완료 후가 검증 쉬움)
    ↓                          │
Unit 4: API & Integration ─────┘
    (Unit 2 + Unit 3 모두 필요)
```

## 의존성 매트릭스

| | Unit 1 | Unit 2 | Unit 3 | Unit 4 |
|---|---|---|---|---|
| **Unit 1** | — | — | — | — |
| **Unit 2** | 필수 | — | — | — |
| **Unit 3** | 필수 | 독립 | — | — |
| **Unit 4** | 필수 | 필수 | 필수 | — |

## 각 유닛이 의존하는 산출물

| 유닛 | 의존 대상 | 의존 이유 |
|---|---|---|
| Unit 2 | Unit 1: `domain/models.py` | `Location`, `Station` 타입 사용 |
| Unit 2 | Unit 1: `domain/interfaces.py` | `StationRepository` ABC 구현 |
| Unit 2 | Unit 1: `domain/exceptions.py` | `NoNearbyStationError` 발생 |
| Unit 3 | Unit 1: `domain/models.py` | `Place`, `Recommendation` 타입 사용 |
| Unit 3 | Unit 1: `domain/interfaces.py` | `EmbeddingPort`, `VectorRepository` ABC 구현 |
| Unit 3 | Unit 1: `domain/exceptions.py` | `VectorDBError`, `NoRecommendationsError` 발생 |
| Unit 4 | Unit 1: `core/config.py` | `Settings` DI 주입 |
| Unit 4 | Unit 2: `HardcodedStationRepository` | DI 팩토리에서 인스턴스화 |
| Unit 4 | Unit 2: `MidpointService` | `/midpoint` 라우터에서 호출 |
| Unit 4 | Unit 3: `SBERTEmbedder` | DI 팩토리에서 인스턴스화 |
| Unit 4 | Unit 3: `ChromaVectorRepository` | DI 팩토리에서 인스턴스화 |
| Unit 4 | Unit 3: `RecommendationService` | `/recommend` 라우터에서 호출 |

## 변경 전파 분석

| 변경 위치 | 영향 범위 |
|---|---|
| `domain/models.py` (Unit 1) | Unit 2, 3, 4 전체 재검토 필요 |
| `domain/interfaces.py` (Unit 1) | 해당 인터페이스 구현체 (Unit 2 또는 3) 수정 필요 |
| `HardcodedStationRepository` (Unit 2) | Unit 4 통합 테스트 재실행 필요 |
| `ChromaVectorRepository` (Unit 3) | Unit 4 통합 테스트 재실행 필요 |
| `api/dependencies.py` (Unit 4) | Unit 4 내부만 영향 |
