from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from infrastructure.station.hardcoded_station_repository import (  # noqa: E402
    HardcodedStationRepository,
)


def _normalize_station_name(name: str) -> str:
    normalized = "".join(name.replace("역", "").strip().split())
    return normalized


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)) * 1000


def _load_yoon_csv(path: Path) -> dict[str, list[tuple[float, float, str]]]:
    references: dict[str, list[tuple[float, float, str]]] = {}
    with path.open(encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            name = row["name"]
            references.setdefault(_normalize_station_name(name), []).append(
                (float(row["lat"]), float(row["lon"]), name),
            )
    return references


def _load_json5_gist(path: Path) -> dict[str, list[tuple[float, float, str]]]:
    references: dict[str, list[tuple[float, float, str]]] = {}
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"'name':\s*'(?P<name>[^']+)'"
        r"[\s\S]*?'lat':\s*(?P<lat>[0-9.]+),"
        r"[\s\S]*?'lng':\s*(?P<lng>[0-9.]+),",
    )
    for match in pattern.finditer(text):
        name = match.group("name")
        references.setdefault(_normalize_station_name(name), []).append(
            (float(match.group("lat")), float(match.group("lng")), name),
        )
    return references


def _audit(
    references: dict[str, list[tuple[float, float, str]]],
    threshold_m: float,
    station_names: set[str] | None = None,
) -> tuple[list[tuple[float, str, str, float, float, float, float, str]], list[str]]:
    rows: list[tuple[float, str, str, float, float, float, float, str]] = []
    missing: list[str] = []
    for station in HardcodedStationRepository._STATIONS:
        if station_names is not None and station.name not in station_names:
            continue
        candidates = references.get(_normalize_station_name(station.name))
        if not candidates:
            missing.append(station.name)
            continue
        distance_m, ref_lat, ref_lng, ref_name = min(
            (
                _haversine_m(station.lat, station.lng, lat, lng),
                lat,
                lng,
                name,
            )
            for lat, lng, name in candidates
        )
        if distance_m >= threshold_m:
            rows.append(
                (
                    distance_m,
                    station.id,
                    station.name,
                    station.lat,
                    station.lng,
                    ref_lat,
                    ref_lng,
                    ref_name,
                ),
            )
    return sorted(rows, reverse=True), missing


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yoon-csv", type=Path)
    parser.add_argument("--json5-gist", type=Path)
    parser.add_argument("--threshold-m", type=float, default=500.0)
    parser.add_argument(
        "--station-name",
        action="append",
        help="Limit the audit to one or more station names.",
    )
    args = parser.parse_args()

    sources: list[tuple[str, dict[str, list[tuple[float, float, str]]]]] = []
    if args.yoon_csv:
        sources.append(("yoon_csv", _load_yoon_csv(args.yoon_csv)))
    if args.json5_gist:
        sources.append(("json5_gist", _load_json5_gist(args.json5_gist)))

    for source_name, references in sources:
        station_names = set(args.station_name) if args.station_name else None
        rows, missing = _audit(references, args.threshold_m, station_names)
        print(
            f"[{source_name}] mismatches>={args.threshold_m:.0f}m={len(rows)} "
            f"missing={len(missing)}"
        )
        for row in rows[:60]:
            distance_m, station_id, name, lat, lng, ref_lat, ref_lng, ref_name = row
            print(
                f"{name}\t{distance_m:.0f}m\tid={station_id}\t"
                f"local=({lat:.6f},{lng:.6f})\t"
                f"ref=({ref_lat:.6f},{ref_lng:.6f})\tref_name={ref_name}"
            )
        if missing:
            print("missing_names=" + ", ".join(missing[:80]))


if __name__ == "__main__":
    main()
