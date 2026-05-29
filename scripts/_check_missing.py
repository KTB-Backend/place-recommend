"""데이터 없는 역 목록 출력 + 여러 역 직접 API 테스트."""
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from core.config import get_settings
from infrastructure.station.hardcoded_station_repository import HardcodedStationRepository

settings = get_settings()
existing = json.loads(Path("data/processed/places.json").read_text(encoding="utf-8"))
counts: dict[str, int] = defaultdict(int)
for p in existing:
    counts[p["station"]] += 1

all_stations = HardcodedStationRepository._STATIONS
missing = [s for s in all_stations if counts[s.name] == 0]
print(f"데이터 없는 역: {len(missing)}개\n")

# 여러 역 테스트
test_stations = missing[:5]
for s in test_stations:
    print(f"[{s.name}] lat={s.lat}, lng={s.lng}")
    try:
        r = httpx.get(
            "https://dapi.kakao.com/v2/local/search/category.json",
            headers={"Authorization": f"KakaoAK {settings.kakao_rest_api_key}"},
            params={
                "category_group_code": "CE7",
                "x": str(s.lng),
                "y": str(s.lat),
                "radius": "500",
                "size": "5",
            },
            verify=False, timeout=10,
        )
        print(f"  HTTP {r.status_code}")
        if r.status_code != 200:
            print(f"  에러: {r.text[:200]}")
        else:
            docs = r.json().get("documents", [])
            print(f"  결과: {len(docs)}개" + (f" | 첫 번째: {docs[0]['place_name']}" if docs else ""))
    except Exception as e:
        print(f"  예외: {type(e).__name__}: {e}")
    print()
