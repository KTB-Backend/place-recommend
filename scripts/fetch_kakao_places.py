"""Fetch Kakao Local places around subway stations and update places.json."""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import get_settings
from domain.models import Place, Station
from infrastructure.kakao.kakao_place_fetcher import KakaoPlaceFetcher
from infrastructure.station.hardcoded_station_repository import (
    HardcodedStationRepository,
)

PLACES_PATH = Path("data/processed/places.json")
PARTIAL_PATH = Path("data/processed/places.partial.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch Kakao places and merge them into data/processed/places.json."
        ),
    )
    parser.add_argument(
        "--missing-only",
        action="store_true",
        help="Fetch only stations that currently have no places in places.json.",
    )
    parser.add_argument(
        "--request-interval",
        type=float,
        default=0.2,
        help="Delay between Kakao API requests in seconds.",
    )
    return parser.parse_args()


def load_existing_places(path: Path) -> list[Place]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [Place.model_validate(item) for item in raw]


def station_counts(places: list[Place]) -> Counter[str]:
    return Counter(place.station for place in places)


def select_stations(
    stations: list[Station],
    counts: Counter[str],
    *,
    missing_only: bool,
) -> list[Station]:
    missing = [station for station in stations if counts[station.name] == 0]
    populated = [station for station in stations if counts[station.name] > 0]
    if missing_only:
        return missing
    return [*missing, *populated]


def dedupe_places(places: list[Place]) -> list[Place]:
    by_id: dict[str, Place] = {}
    for place in places:
        by_id.setdefault(place.id, place)
    return list(by_id.values())


def write_places(path: Path, places: list[Place]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            [place.model_dump() for place in places],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    settings = get_settings()

    if not settings.kakao_rest_api_key:
        print("[ERROR] KAKAO_REST_API_KEY is not set.")
        print("  Option 1) Add it to .env: KAKAO_REST_API_KEY=your_key")
        print("  Option 2) Set it in the shell environment.")
        sys.exit(1)

    existing_places = load_existing_places(PLACES_PATH)
    counts = station_counts(existing_places)
    stations = select_stations(
        list(HardcodedStationRepository._STATIONS),
        counts,
        missing_only=args.missing_only,
    )

    if not stations:
        print("[OK] No stations need fetching.")
        return

    fetcher = KakaoPlaceFetcher(
        api_key=settings.kakao_rest_api_key,
        ssl_verify=settings.kakao_ssl_verify,
        request_interval_s=args.request_interval,
    )

    fetched_places: list[Place] = []
    errors: list[str] = []
    missing_count = sum(
        1
        for station in HardcodedStationRepository._STATIONS
        if counts[station.name] == 0
    )

    mode = "missing-only" if args.missing_only else "missing-first"
    print(
        f"Fetching {len(stations)} stations "
        f"(mode={mode}, missing={missing_count}, "
        f"existing_places={len(existing_places)})"
    )
    print("-" * 60)

    try:
        for i, station in enumerate(stations, 1):
            before_failures = fetcher.failure_count
            print(
                f"[{i:3}/{len(stations)}] {station.name:<12} "
                f"existing={counts[station.name]:3}",
                end=" ",
            )
            try:
                places = fetcher.fetch_for_station(station)
                fetched_places.extend(places)
                print(f"fetched={len(places):2}")
                if fetcher.failure_count > before_failures:
                    errors.append(station.name)
                if fetcher.quota_exceeded:
                    print("[STOP] Kakao API quota exceeded. Stopping remaining calls.")
                    break
            except Exception as exc:
                errors.append(station.name)
                print(f"failed ({exc})")
                if fetcher.quota_exceeded:
                    print("[STOP] Kakao API quota exceeded. Stopping remaining calls.")
                    break
            time.sleep(args.request_interval)
    finally:
        fetcher.close()

    merged = dedupe_places([*existing_places, *fetched_places])
    new_count = len(merged) - len(dedupe_places(existing_places))

    print("-" * 60)
    if fetcher.failure_count:
        partial = dedupe_places(fetched_places)
        write_places(PARTIAL_PATH, partial)
        if new_count:
            write_places(PLACES_PATH, merged)
        print(f"[ERROR] Kakao API failures: {fetcher.failure_count}")
        print(f"[WARN] Partial fetched data saved to {PARTIAL_PATH}")
        print(f"[WARN] New places merged into {PLACES_PATH}: {new_count}")
        if errors:
            print(f"[WARN] Stations with failures: {', '.join(dict.fromkeys(errors))}")
        sys.exit(2)

    write_places(PLACES_PATH, merged)
    print(f"[OK] Existing places: {len(existing_places)}")
    print(f"[OK] Fetched places: {len(fetched_places)}")
    print(f"[OK] New places merged: {new_count}")
    print(f"[OK] Total places saved: {len(merged)} -> {PLACES_PATH}")
    print()
    print("Next step: python scripts/ingest_to_vectordb.py")


if __name__ == "__main__":
    main()
