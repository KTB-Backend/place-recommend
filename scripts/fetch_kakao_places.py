"""카카오 로컬 API로 전체 역 주변 장소를 수집해 places.json을 갱신한다."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from infrastructure.kakao.kakao_place_fetcher import KakaoPlaceFetcher
from infrastructure.station.hardcoded_station_repository import (
    HardcodedStationRepository,
)


def main() -> None:
    settings = get_settings()

    if not settings.kakao_rest_api_key:
        print("[ERROR] KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        print("  방법 1) .env 파일에 추가:  KAKAO_REST_API_KEY=your_key")
        print("  방법 2) 환경변수 설정:     set KAKAO_REST_API_KEY=your_key")
        sys.exit(1)

    stations = HardcodedStationRepository._STATIONS
    fetcher = KakaoPlaceFetcher(
        api_key=settings.kakao_rest_api_key,
        ssl_verify=settings.kakao_ssl_verify,
    )

    all_places = []
    errors: list[str] = []

    print(f"총 {len(stations)}개 역 수집 시작 (반경 500m, 역당 최대 40개)")
    print("-" * 50)

    for i, station in enumerate(stations, 1):
        print(f"[{i:3}/{len(stations)}] {station.name:<10}", end=" ")
        try:
            places = fetcher.fetch_for_station(station)
            all_places.extend(places)
            print(f"{len(places):2}개")
        except Exception as e:
            errors.append(f"{station.name}: {e}")
            print(f"실패 ({e})")
        time.sleep(0.2)  # 카카오 API rate limit 준수

    fetcher.close()

    # 전역 중복 제거 (복수 역 검색에서 동일 장소 중복 가능)
    seen: set[str] = set()
    unique = []
    for p in all_places:
        if p.id not in seen:
            seen.add(p.id)
            unique.append(p)

    out_path = Path("data/processed/places.json")
    if fetcher.failure_count:
        out_path = Path("data/processed/places.partial.json")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps([p.model_dump() for p in unique], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("-" * 50)
    if fetcher.failure_count:
        print(f"[ERROR] Kakao API 실패 {fetcher.failure_count}건 발생")
        print(f"[WARN] 부분 수집 결과만 저장 → {out_path}")
        print("[WARN] 기존 data/processed/places.json은 덮어쓰지 않았습니다.")
        sys.exit(2)

    print(f"[OK] 총 {len(unique)}개 장소 저장 → {out_path}")
    if errors:
        failed_stations = ", ".join(e.split(":")[0] for e in errors)
        print(f"[WARN] 실패한 역 {len(errors)}개: {failed_stations}")
    print()
    print("다음 단계: python scripts/ingest_to_vectordb.py")


if __name__ == "__main__":
    main()
