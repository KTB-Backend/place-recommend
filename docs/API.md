# API Guide

Local base URL:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Midpoint

```http
POST /api/v1/midpoint
```

Station-name request:

```json
{
  "stations": ["서울역", "강남역"]
}
```

Legacy coordinate request:

```json
{
  "locations": [
    {"lat": 37.5665, "lng": 126.978},
    {"lat": 37.4979, "lng": 127.0276}
  ]
}
```

Response:

```json
{
  "id": "hangangjin",
  "name": "한강진",
  "line": "6호선",
  "lat": 37.5397,
  "lng": 127.0019
}
```

## Recommend

```http
POST /api/v1/recommend
```

Request:

```json
{
  "stations": ["서울역", "강남역"],
  "query": "조용한 카페",
  "top_k": 3
}
```

Fields:

- `stations`: 2 to 10 station names. The trailing `역` suffix is optional.
- `locations`: Legacy coordinate input. Use either `stations` or `locations`.
- `query`: Natural-language place request.
- `top_k`: Number of recommendations per station, from 1 to 20.
- `selected_station_id`: Optional. Use it after the user chooses a nearby station option.

### Direct Success

Returned when the midpoint station has local recommendations.

```json
{
  "status": "ok",
  "meeting_station": {
    "id": "gangnam",
    "name": "강남",
    "line": "2호선",
    "lat": 37.4979,
    "lng": 127.0276
  },
  "station": {
    "id": "gangnam",
    "name": "강남",
    "line": "2호선",
    "lat": 37.4979,
    "lng": 127.0276
  },
  "recommendations": []
}
```

### Station Selection Required

Returned when the calculated midpoint station has no matching local DB data.
The API returns:

- the original `meeting_station`
- up to 3 nearby station options that have recommendations
- a Kakao Map search link for the original midpoint station

```json
{
  "status": "station_selection_required",
  "meeting_station": {
    "id": "hangangjin",
    "name": "한강진",
    "line": "6호선",
    "lat": 37.5397,
    "lng": 127.0019
  },
  "map_search": {
    "provider": "kakao_map",
    "label": "한강진 조용한 카페 Kakao Map에서 보기",
    "query": "한강진 조용한 카페",
    "url": "https://map.kakao.com/link/search/..."
  },
  "options": [
    {
      "station": {
        "id": "oksu",
        "name": "옥수",
        "line": "3호선",
        "lat": 37.544,
        "lng": 127.0182
      },
      "recommendations": []
    }
  ]
}
```

Client flow:

1. Show that the current midpoint station has no local DB data.
2. Show nearby selectable station options.
3. Show the Kakao Map link for the original midpoint station.
4. If the user selects an option, call `/api/v1/recommend` again with `selected_station_id`.

Second request:

```json
{
  "stations": ["서울역", "강남역"],
  "query": "조용한 카페",
  "top_k": 3,
  "selected_station_id": "oksu"
}
```

## Kakao Data Collection

Full collection:

```bash
python scripts/fetch_kakao_places.py
```

Collect only stations that currently have no data:

```bash
python scripts/fetch_kakao_places.py --missing-only
```

The script reads `data/processed/places.json`, counts places per station, and
uses that count to avoid wasting quota on already-populated stations.

Default behavior is `missing-first`: stations with zero places are fetched
before stations that already have data.

When Kakao returns `API limit has been exceeded`, the script stops remaining
calls immediately and writes the partial fetch result to:

```text
data/processed/places.partial.json
```

After a successful fetch or merge, re-ingest the vector DB:

```bash
python scripts/ingest_to_vectordb.py
```

Current local dataset status:

- `data/processed/places.json`: 2,296 places
- stations with zero local places: 49
- use `--missing-only` after the Kakao quota resets

Stations currently missing local place data:

```text
대청, 미아, 이촌, 영등포시장, 청구, 행당, 군자, 아차산, 광나루, 천호,
강동, 망원, 상수, 이태원, 한강진, 녹사평, 보문, 안암, 고려대, 월곡,
태릉입구, 뚝섬유원지, 청담, 강남구청, 학동, 논현, 반포, 내방, 남성,
숭실대입구, 상도, 장승배기, 보라매, 신풍, 가산디지털단지, 흑석,
구반포, 신반포, 사평, 신논현, 언주, 선정릉, 삼성중앙, 봉은사,
한성백제, 올림픽공원, 디지털미디어시티, 종로3가, 종각
```

## Error Responses

- `422 Unprocessable Entity`: request validation failed
- `404 Not Found`: no station or recommendations found
- `503 Service Unavailable`: vector DB or embedding backend unavailable
