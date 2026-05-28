from __future__ import annotations

import math

from domain.interfaces import StationRepository
from domain.models import Location, Station


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class HardcodedStationRepository(StationRepository):
    _STATIONS: list[Station] = [
        Station(id="gangnam",           name="강남",           line="2호선",       lat=37.4979, lng=127.0276),
        Station(id="hongdae",           name="홍대입구",       line="2·경의중앙선", lat=37.5574, lng=126.9249),
        Station(id="sinchon",           name="신촌",           line="2호선",       lat=37.5551, lng=126.9368),
        Station(id="konkuk",            name="건대입구",       line="2·7호선",     lat=37.5403, lng=127.0698),
        Station(id="jamsil",            name="잠실",           line="2·8호선",     lat=37.5133, lng=127.1001),
        Station(id="seongsu",           name="성수",           line="2호선",       lat=37.5447, lng=127.0557),
        Station(id="hapjeong",          name="합정",           line="2·6호선",     lat=37.5499, lng=126.9138),
        Station(id="cityhall",          name="시청",           line="1·2호선",     lat=37.5650, lng=126.9774),
        Station(id="jongro3ga",         name="종로3가",        line="1·3·5호선",   lat=37.5717, lng=126.9916),
        Station(id="itaewon",           name="이태원",         line="6호선",       lat=37.5344, lng=126.9942),
        Station(id="apgujeong",         name="압구정",         line="3호선",       lat=37.5270, lng=127.0282),
        Station(id="gyodae",            name="교대",           line="2·3호선",     lat=37.4935, lng=127.0138),
        Station(id="express_terminal",  name="고속터미널",     line="3·7·9호선",   lat=37.5047, lng=127.0047),
        Station(id="yeouido",           name="여의도",         line="5·9호선",     lat=37.5216, lng=126.9244),
        Station(id="gwanghwamun",       name="광화문",         line="5호선",       lat=37.5716, lng=126.9768),
        Station(id="snu",               name="서울대입구",     line="2호선",       lat=37.4813, lng=126.9527),
        Station(id="wangsimni",         name="왕십리",         line="2·5호선",     lat=37.5616, lng=127.0384),
        Station(id="sillim",            name="신림",           line="2호선",       lat=37.4845, lng=126.9293),
        Station(id="suyu",              name="수유",           line="4호선",       lat=37.6385, lng=127.0255),
        Station(id="nowon",             name="노원",           line="4·7호선",     lat=37.6541, lng=127.0614),
        Station(id="dangsan",           name="당산",           line="2·9호선",     lat=37.5341, lng=126.9002),
        Station(id="isu",               name="이수",           line="4·7호선",     lat=37.4850, lng=126.9820),
        Station(id="seolleung",         name="선릉",           line="2·분당선",    lat=37.5048, lng=127.0495),
        Station(id="ddp",               name="동대문역사문화공원", line="2·4·5호선", lat=37.5653, lng=127.0099),
        Station(id="sinsa",             name="신사",           line="3호선",       lat=37.5160, lng=127.0209),
        Station(id="jonggak",           name="종각",           line="1호선",       lat=37.5703, lng=126.9828),
    ]

    def find_nearest(self, location: Location) -> Station:
        return min(
            self._STATIONS,
            key=lambda s: _haversine(location.lat, location.lng, s.lat, s.lng),
        )
