# Code Summary — Unit 3: RAG Engine

## 생성된 파일 목록

### 데이터
| 파일 | 설명 |
|---|---|
| `data/processed/places.json` | 샘플 장소 10개 (강남·홍대·합정·이태원·잠실·신촌·건대·여의도) |

### 인프라 계층
| 파일 | 설명 |
|---|---|
| `infrastructure/embedding/sbert_embedder.py` | `jhgan/ko-sroberta-multitask` 배치/단일 임베딩 |
| `infrastructure/vector/chroma_vector_repository.py` | ChromaDB 메타데이터 필터 + 코사인 유사도 검색 |

### 애플리케이션 계층
| 파일 | 설명 |
|---|---|
| `application/recommendation_service.py` | 중간지점 → 임베딩 → 벡터 검색 오케스트레이션 |

### 스크립트
| 파일 | 설명 |
|---|---|
| `scripts/ingest_to_vectordb.py` | places.json → SBERT 임베딩 → ChromaDB 저장 (멱등성) |

### 테스트
| 파일 | 설명 |
|---|---|
| `tests/unit/test_recommendation_service.py` | 단위 테스트 5개 (mock 기반, ML 의존성 없음) |

## 완료 검증 명령어

```bash
# 단위 테스트 (mock — ML 모델 불필요)
pytest tests/unit/test_recommendation_service.py -v

# 데이터 인제스트 (실제 SBERT 모델 필요)
python scripts/ingest_to_vectordb.py
```
