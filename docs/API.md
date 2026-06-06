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

- `data/processed/places.json`: 3,916 places
- stations with local places: 146
- stations with zero local places: 0

## Error Responses

- `422 Unprocessable Entity`: request validation failed
- `404 Not Found`: no station or recommendations found
- `503 Service Unavailable`: vector DB or embedding backend unavailable
