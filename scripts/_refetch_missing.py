"""places.json에 데이터가 없는 역만 재수집해 기존 데이터에 병합한다."""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from infrastructure.kakao.kakao_place_fetcher import KakaoPlaceFetcher
from infrastructure.station.hardcoded_station_repository import HardcodedStationRepository


def main() -> None:
    settings = get_settings()
    out_path = Path("data/processed/places.json")

    # 기존 데이터 로드
    existing: list[dict] = json.loads(out_path.read_text(encoding="utf-8"))
    existing_ids: set[str] = {p["id"] for p in existing}

    # 역별 장소 수 집계
    station_counts: dict[str, int] = defaultdict(int)
    for p in existing:
        station_counts[p["station"]] += 1

    # 데이터 없는 역 추출
    all_stations = HardcodedStationRepository._STATIONS
    missing = [s for s in all_stations if station_counts[s.name] == 0]

    print(f"전체 역: {len(all_stations)}개  |  데이터 없는 역: {len(missing)}개")
    print(f"기존 장소: {len(existing)}개")
    print("-" * 50)

    if not missing:
        print("[OK] 모든 역에 데이터가 있습니다.")
        return

    fetcher = KakaoPlaceFetcher(
        api_key=settings.kakao_rest_api_key,
        ssl_verify=settings.kakao_ssl_verify,
    )

    new_places: list[dict] = []
    for i, station in enumerate(missing, 1):
        print(f"[{i:3}/{len(missing)}] {station.name:<12}", end=" ")
        try:
            places = fetcher.fetch_for_station(station)
            added = 0
            for p in places:
                if p.id not in existing_ids:
                    existing_ids.add(p.id)
                    new_places.append(p.model_dump())
                    added += 1
            print(f"{added}개")
        except Exception as e:
            print(f"실패 ({e})")
        time.sleep(0.25)

    fetcher.close()

    merged = existing + new_places
    out_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("-" * 50)
    print(f"[OK] 신규 {len(new_places)}개 추가  →  총 {len(merged)}개 저장")
    print("다음 단계: python scripts/ingest_to_vectordb.py")


if __name__ == "__main__":
    main()
