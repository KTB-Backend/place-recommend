from __future__ import annotations

from hypothesis import strategies as st

from domain.models import Location, Place, Recommendation


@st.composite
def valid_locations(draw: st.DrawFn) -> Location:
    lat = draw(st.floats(min_value=-90.0, max_value=90.0,
                         allow_nan=False, allow_infinity=False))
    lng = draw(st.floats(min_value=-180.0, max_value=180.0,
                         allow_nan=False, allow_infinity=False))
    return Location(lat=lat, lng=lng)


@st.composite
def invalid_location_dicts(draw: st.DrawFn) -> dict[str, float]:
    """유효 범위를 벗어난 좌표 딕셔너리. ValidationError 발생 검증용."""
    case = draw(st.sampled_from(["lat_high", "lat_low", "lng_high", "lng_low"]))
    match case:
        case "lat_high":
            return {"lat": draw(st.floats(min_value=90.001, max_value=1000.0,
                                          allow_nan=False)), "lng": 0.0}
        case "lat_low":
            return {"lat": draw(st.floats(min_value=-1000.0, max_value=-90.001,
                                          allow_nan=False)), "lng": 0.0}
        case "lng_high":
            return {"lat": 0.0, "lng": draw(st.floats(min_value=180.001, max_value=1000.0,
                                                        allow_nan=False))}
        case _:
            return {"lat": 0.0, "lng": draw(st.floats(min_value=-1000.0, max_value=-180.001,
                                                        allow_nan=False))}


@st.composite
def valid_similarity_scores(draw: st.DrawFn) -> float:
    return draw(st.floats(min_value=0.0, max_value=1.0,
                          allow_nan=False, allow_infinity=False))


@st.composite
def two_or_more_locations(draw: st.DrawFn) -> list[Location]:
    """최소 2개 이상의 유효 Location 리스트. MidpointService PBT용."""
    n = draw(st.integers(min_value=2, max_value=10))
    return [draw(valid_locations()) for _ in range(n)]


@st.composite
def seoul_locations(draw: st.DrawFn) -> Location:
    """서울 범위 내 유효 Location. Haversine/Midpoint PBT용."""
    lat = draw(st.floats(min_value=37.4, max_value=37.7,
                         allow_nan=False, allow_infinity=False))
    lng = draw(st.floats(min_value=126.8, max_value=127.2,
                         allow_nan=False, allow_infinity=False))
    return Location(lat=lat, lng=lng)


@st.composite
def valid_places(draw: st.DrawFn) -> Place:
    return Place(
        id=draw(st.text(min_size=1, max_size=20)),
        name=draw(st.text(min_size=1, max_size=50)),
        description=draw(st.text(max_size=200)),
        category=draw(st.sampled_from(["레스토랑", "카페", "바", "술집"])),
        subcategory=draw(st.text(min_size=1, max_size=30)),
        tags=draw(st.lists(st.text(min_size=1, max_size=10), max_size=10)),
        station=draw(st.text(min_size=1, max_size=20)),
        exit_number=draw(st.integers(min_value=1, max_value=15)),
        distance_from_station_m=draw(st.integers(min_value=0, max_value=2000)),
        address=draw(st.text(min_size=1, max_size=100)),
        lat=draw(st.floats(min_value=37.4, max_value=37.7,
                           allow_nan=False, allow_infinity=False)),
        lng=draw(st.floats(min_value=126.8, max_value=127.2,
                           allow_nan=False, allow_infinity=False)),
        rating=draw(st.floats(min_value=0.0, max_value=5.0,
                              allow_nan=False, allow_infinity=False)),
        price_range=draw(st.sampled_from(["저렴", "중간", "비쌈"])),
    )
