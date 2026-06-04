# API Guide

This document describes the current HTTP API contract for the meeting-place
recommendation service.

Base URL for local development:

```text
http://127.0.0.1:8000
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Midpoint Station

Find the nearest station to the geographic midpoint of 2 to 10 input stations
or coordinates.

```http
POST /api/v1/midpoint
```

Request:

```json
{
  "stations": ["서울역", "강남역"]
}
```

Response:

```json
{
  "id": "hangangjin",
  "name": "한강진",
  "line": "6호선",
  "lat": 37.5299,
  "lng": 126.9973
}
```

## Recommend Places

Recommend places near the midpoint station. If the midpoint station has no
matching places in the local vector DB, the API returns nearby station options
that already have recommendations. The client can then let the user choose one
of those stations.

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

- `stations`: 2 to 10 station names. A trailing `역` suffix is optional.
- `locations`: Optional legacy input, 2 to 10 coordinates.
- `query`: Natural-language place request.
- `top_k`: Maximum recommendations per station, 1 to 20.
- `selected_station_id`: Optional. Use this for the second request after the
  user chooses one of the returned station options.

### Direct Success

Returned when the midpoint station has matching recommendations.

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
  "recommendations": [
    {
      "place": {
        "id": "kakao_123",
        "name": "테스트 카페",
        "description": "조용한 분위기의 카페",
        "category": "카페",
        "subcategory": "디저트카페",
        "tags": ["조용한", "데이트"],
        "station": "강남",
        "exit_number": 1,
        "distance_from_station_m": 200,
        "address": "서울 강남구 테헤란로 1",
        "lat": 37.498,
        "lng": 127.028,
        "rating": 0.0,
        "price_range": "중간"
      },
      "similarity_score": 0.87
    }
  ]
}
```

### Station Selection Required

Returned when the midpoint station has no matching local DB recommendations.
The response contains up to 3 nearby station options, and every option has at
least one recommendation.

```json
{
  "status": "station_selection_required",
  "meeting_station": {
    "id": "hangangjin",
    "name": "한강진",
    "line": "6호선",
    "lat": 37.5299,
    "lng": 126.9973
  },
  "map_search": {
    "label": "카카오맵에서 한강진 조용한 카페 검색",
    "query": "한강진 조용한 카페",
    "url": "https://map.kakao.com/link/search/%ED%95%9C%EA%B0%95%EC%A7%84%20%EC%A1%B0%EC%9A%A9%ED%95%9C%20%EC%B9%B4%ED%8E%98"
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
      "recommendations": [
        {
          "place": {
            "id": "kakao_456",
            "name": "테스트 장소",
            "description": "카카오 지도 데이터 기반 장소",
            "category": "카페",
            "subcategory": "카페",
            "tags": ["카페"],
            "station": "옥수",
            "exit_number": 1,
            "distance_from_station_m": 187,
            "address": "서울 성동구",
            "lat": 37.5442,
            "lng": 127.0161,
            "rating": 0.0,
            "price_range": "중간"
          },
          "similarity_score": 0.45
        }
      ]
    }
  ]
}
```

Client behavior:

1. Show the original `meeting_station`.
2. Show `options` as selectable nearby stations.
3. Also show a button that opens `map_search.url` in Kakao Map.
4. When the user selects an option, send a second `/recommend` request with
   `selected_station_id`.

Second request after user selection:

```json
{
  "stations": ["서울역", "강남역"],
  "query": "조용한 카페",
  "top_k": 3,
  "selected_station_id": "oksu"
}
```

Second response:

```json
{
  "status": "ok",
  "meeting_station": {
    "id": "hangangjin",
    "name": "한강진",
    "line": "6호선",
    "lat": 37.5299,
    "lng": 126.9973
  },
  "station": {
    "id": "oksu",
    "name": "옥수",
    "line": "3호선",
    "lat": 37.544,
    "lng": 127.0182
  },
  "recommendations": [
    {
      "place": {
        "id": "kakao_456",
        "name": "테스트 장소",
        "description": "카카오 지도 데이터 기반 장소",
        "category": "카페",
        "subcategory": "카페",
        "tags": ["카페"],
        "station": "옥수",
        "exit_number": 1,
        "distance_from_station_m": 187,
        "address": "서울 성동구",
        "lat": 37.5442,
        "lng": 127.0161,
        "rating": 0.0,
        "price_range": "중간"
      },
      "similarity_score": 0.45
    }
  ]
}
```

`recommendations` may contain fewer than `top_k` items when the station has
limited data.

## Error Responses

Validation error:

```text
422 Unprocessable Entity
```

No nearby station:

```text
404 Not Found
```

No recommendations found for all candidate stations:

```text
404 Not Found
```

Vector DB error:

```text
503 Service Unavailable
```
