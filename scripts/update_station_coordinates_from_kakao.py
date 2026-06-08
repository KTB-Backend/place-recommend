from __future__ import annotations

import argparse
import csv
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from infrastructure.station.hardcoded_station_repository import (  # noqa: E402
    HardcodedStationRepository,
)

KAKAO_KEYWORD_URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
STATION_FILE = ROOT_DIR / "infrastructure/station/hardcoded_station_repository.py"
REPORT_FILE = ROOT_DIR / "station_coordinate_kakao_report.csv"


@dataclass(frozen=True)
class Candidate:
    station_id: str
    station_name: str
    station_line: str
    query: str
    place_name: str
    category_name: str
    address_name: str
    lat: float
    lng: float
    distance_m: int | None
    score: int


class KakaoApiLimitError(RuntimeError):
    pass


def _load_env_value(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value.strip()
    env_path = ROOT_DIR / ".env"
    if not env_path.exists():
        return ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.lstrip().startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        if key.strip() == name:
            return raw_value.strip().strip('"').strip("'")
    return ""


def _line_tokens(line: str) -> list[str]:
    compact = line.replace(" ", "")
    if re.fullmatch(r"(?:\d+·)+\d+호선", compact):
        prefix = compact.removesuffix("호선")
        return [f"{part}호선" for part in prefix.split("·")]

    tokens = re.split(r"[·/,\s]+", compact)
    normalized: list[str] = []
    for token in tokens:
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            token = f"{token}호선"
        if token == "분당선":
            token = "수인분당선"
        normalized.append(token)
    return normalized or [line]


def _normalize_name(name: str) -> str:
    return "".join(name.replace("역", "").strip().split())


def _queries(station_name: str, line: str) -> list[str]:
    station_keyword = (
        station_name if station_name.endswith("역") else f"{station_name}역"
    )
    queries = [f"{station_keyword} {token}" for token in _line_tokens(line)]
    queries.append(station_keyword)
    return list(dict.fromkeys(queries))


def _score_doc(
    doc: dict[str, Any],
    station_name: str,
    line: str,
    distance_m: int | None,
) -> int:
    place_name = str(doc.get("place_name") or "")
    category_name = str(doc.get("category_name") or "")
    searchable = f"{place_name} {category_name}"
    score = 0

    if "지하철" in category_name or "전철" in category_name:
        score += 120
    if "교통" in category_name:
        score += 30
    if _normalize_name(station_name) in _normalize_name(place_name):
        score += 80

    for token in _line_tokens(line):
        if token and token in searchable:
            score += 60

    if place_name.endswith("역"):
        score += 10
    if distance_m is not None:
        score -= min(distance_m // 100, 50)
    return score


def _candidate_from_doc(
    doc: dict[str, Any],
    station_id: str,
    station_name: str,
    station_line: str,
    query: str,
) -> Candidate:
    distance_raw = str(doc.get("distance") or "")
    distance_m = int(distance_raw) if distance_raw.isdigit() else None
    return Candidate(
        station_id=station_id,
        station_name=station_name,
        station_line=station_line,
        query=query,
        place_name=str(doc.get("place_name") or ""),
        category_name=str(doc.get("category_name") or ""),
        address_name=str(doc.get("address_name") or ""),
        lat=float(doc["y"]),
        lng=float(doc["x"]),
        distance_m=distance_m,
        score=_score_doc(doc, station_name, station_line, distance_m),
    )


def _search_candidates(
    client: httpx.Client,
    api_key: str,
    station_id: str,
    station_name: str,
    station_line: str,
    lat: float,
    lng: float,
    radius_m: int,
) -> list[Candidate]:
    headers = {"Authorization": f"KakaoAK {api_key}"}
    candidates: list[Candidate] = []
    for query in _queries(station_name, station_line):
        response = client.get(
            KAKAO_KEYWORD_URL,
            headers=headers,
            params={
                "query": query,
                "x": lng,
                "y": lat,
                "radius": radius_m,
                "size": 10,
            },
        )
        if response.status_code == 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            if payload.get("code") == -10:
                raise KakaoApiLimitError("Kakao Local API limit has been exceeded.")
        response.raise_for_status()
        for doc in response.json().get("documents", []):
            try:
                candidates.append(
                    _candidate_from_doc(
                        doc,
                        station_id,
                        station_name,
                        station_line,
                        query,
                    ),
                )
            except (KeyError, TypeError, ValueError):
                continue
        time.sleep(0.08)
    return candidates


def _best_candidate(candidates: list[Candidate]) -> Candidate | None:
    subway_candidates = [
        candidate
        for candidate in candidates
        if "지하철" in candidate.category_name or "전철" in candidate.category_name
    ]
    pool = subway_candidates or candidates
    if not pool:
        return None
    return max(pool, key=lambda candidate: candidate.score)


def _replace_station_coordinates(
    source: str,
    updates: dict[str, tuple[float, float]],
) -> str:
    for station_id, (lat, lng) in updates.items():
        pattern = re.compile(
            rf'(Station\(id="{re.escape(station_id)}".*?lat=)'
            rf"-?\d+\.\d+"
            rf"(,\s*lng=)"
            rf"-?\d+\.\d+",
        )
        source, count = pattern.subn(
            rf"\g<1>{lat:.4f}\g<2>{lng:.4f}",
            source,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"Failed to update station id={station_id}")
    return source


def _write_report(rows: list[dict[str, str]]) -> None:
    fieldnames = [
        "status",
        "id",
        "name",
        "line",
        "old_lat",
        "old_lng",
        "new_lat",
        "new_lng",
        "delta_m",
        "score",
        "query",
        "place_name",
        "category_name",
        "address_name",
    ]
    with REPORT_FILE.open("w", encoding="utf-8-sig", newline="") as report:
        writer = csv.DictWriter(report, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--min-score", type=int, default=140)
    parser.add_argument("--min-delta-m", type=int, default=20)
    parser.add_argument("--radius-m", type=int, default=5000)
    parser.add_argument("--start-after-id")
    parser.add_argument("--max-stations", type=int)
    args = parser.parse_args()

    api_key = _load_env_value("KAKAO_REST_API_KEY")
    if not api_key:
        raise SystemExit("KAKAO_REST_API_KEY is missing.")

    rows: list[dict[str, str]] = []
    updates: dict[str, tuple[float, float]] = {}
    processed = 0
    should_skip = bool(args.start_after_id)
    with httpx.Client(timeout=15.0) as client:
        for station in HardcodedStationRepository._STATIONS:
            if should_skip:
                if station.id == args.start_after_id:
                    should_skip = False
                continue
            if args.max_stations is not None and processed >= args.max_stations:
                break
            try:
                candidates = _search_candidates(
                    client,
                    api_key,
                    station.id,
                    station.name,
                    station.line,
                    station.lat,
                    station.lng,
                    args.radius_m,
                )
            except KakaoApiLimitError:
                _write_report(rows)
                raise
            processed += 1
            best = _best_candidate(candidates)
            if best is None:
                rows.append(
                    {
                        "status": "missing",
                        "id": station.id,
                        "name": station.name,
                        "line": station.line,
                        "old_lat": f"{station.lat:.6f}",
                        "old_lng": f"{station.lng:.6f}",
                    },
                )
                continue

            delta_m = int(best.distance_m or 0)
            should_update = best.score >= args.min_score and delta_m >= args.min_delta_m
            if should_update:
                updates[station.id] = (best.lat, best.lng)

            rows.append(
                {
                    "status": "update" if should_update else "keep",
                    "id": station.id,
                    "name": station.name,
                    "line": station.line,
                    "old_lat": f"{station.lat:.6f}",
                    "old_lng": f"{station.lng:.6f}",
                    "new_lat": f"{best.lat:.6f}",
                    "new_lng": f"{best.lng:.6f}",
                    "delta_m": str(delta_m),
                    "score": str(best.score),
                    "query": best.query,
                    "place_name": best.place_name,
                    "category_name": best.category_name,
                    "address_name": best.address_name,
                },
            )

    _write_report(rows)

    if args.apply and updates:
        source = STATION_FILE.read_text(encoding="utf-8")
        STATION_FILE.write_text(
            _replace_station_coordinates(source, updates),
            encoding="utf-8",
        )

    print(f"report={REPORT_FILE}")
    print(f"updates={len(updates)}")
    if not args.apply:
        print("dry_run=true")


if __name__ == "__main__":
    main()
