from __future__ import annotations


class DomainError(Exception):
    """도메인 예외 기본 클래스."""


class NoNearbyStationError(DomainError):
    """중간지점 반경 내 지하철역 없음."""


class NoRecommendationsError(DomainError):
    """벡터 검색 결과 없음."""


class VectorDBError(DomainError):
    """벡터 DB 접근·쿼리 오류."""


class InvalidLocationError(DomainError):
    """유효하지 않은 좌표 입력."""
