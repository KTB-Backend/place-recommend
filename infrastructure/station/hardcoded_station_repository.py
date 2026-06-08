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
        # ── 1호선 ──────────────────────────────────────────────────────────
        Station(id="seoul_station",     name="서울역",         line="1·4호선",      lat=37.553150, lng=126.972533),
        Station(id="namyeong",          name="남영",           line="1호선",        lat=37.540567, lng=126.971331),
        Station(id="yongsan",           name="용산",           line="1호선",        lat=37.529774, lng=126.964630),
        Station(id="nodukhoom",         name="노들",           line="9호선",        lat=37.512672, lng=126.953096),
        Station(id="noryangjin",        name="노량진",         line="1·9호선",      lat=37.514055, lng=126.942110),
        Station(id="daebang",           name="대방",           line="1호선",        lat=37.513354, lng=126.926494),
        Station(id="sindorim",          name="신도림",         line="1·2호선",      lat=37.508815, lng=126.891222),
        Station(id="guro",              name="구로",           line="1호선",        lat=37.503342, lng=126.882308),
        Station(id="sindaebang",        name="신대방",         line="2호선",        lat=37.487534, lng=126.913279),
        Station(id="dongdaemun",        name="동대문",         line="1·4호선",      lat=37.570840, lng=127.009403),
        Station(id="sinseoldong",       name="신설동",         line="1·2호선",      lat=37.574653, lng=127.025158),
        Station(id="cheongnyangni",     name="청량리",         line="1호선",        lat=37.580148, lng=127.045063),
        Station(id="hoegi",             name="회기",           line="1호선",        lat=37.589796, lng=127.058048),
        Station(id="changdong",         name="창동",           line="1·4호선",      lat=37.652993, lng=127.046746),
        Station(id="ssangmun",          name="쌍문",           line="4호선",        lat=37.648274, lng=127.034381),

        # ── 2호선 ──────────────────────────────────────────────────────────
        Station(id="cityhall",          name="시청",           line="1·2호선",      lat=37.563590, lng=126.975407),
        Station(id="euljiro_ib",        name="을지로입구",     line="2호선",        lat=37.565998, lng=126.982569),
        Station(id="euljiro3",          name="을지로3가",      line="2·3호선",      lat=37.566292, lng=126.991773),
        Station(id="euljiro4",          name="을지로4가",      line="2·5호선",      lat=37.566580, lng=126.998127),
        Station(id="ddp",               name="동대문역사문화공원", line="2·4·5호선", lat=37.565597, lng=127.009113),
        Station(id="sindang",           name="신당",           line="2·6호선",      lat=37.565681, lng=127.019488),
        Station(id="sangwangsimni",     name="상왕십리",       line="2호선",        lat=37.564504, lng=127.028872),
        Station(id="wangsimni",         name="왕십리",         line="2·5호선",      lat=37.561970, lng=127.037264),
        Station(id="hanyang_univ",      name="한양대",         line="2호선",        lat=37.556580, lng=127.043504),
        Station(id="ttukseom",          name="뚝섬",           line="2호선",        lat=37.547180, lng=127.047413),
        Station(id="seongsu",           name="성수",           line="2호선",        lat=37.544628, lng=127.055983),
        Station(id="konkuk",            name="건대입구",       line="2·7호선",      lat=37.540408, lng=127.069231),
        Station(id="guui",              name="구의",           line="2호선",        lat=37.536857, lng=127.085024),
        Station(id="gangbyeon",         name="강변",           line="2호선",        lat=37.535161, lng=127.094684),
        Station(id="jamsil_naru",       name="잠실나루",       line="2호선",        lat=37.520688, lng=127.103836),
        Station(id="jamsil",            name="잠실",           line="2·8호선",      lat=37.513305, lng=127.100129),
        Station(id="sincheon",          name="신천",           line="2호선",        lat=37.513311, lng=127.100231),
        Station(id="sports_complex",    name="종합운동장",     line="2·9호선",      lat=37.511008, lng=127.073641),
        Station(id="samsung",           name="삼성",           line="2호선",        lat=37.508827, lng=127.063203),
        Station(id="seolleung",         name="선릉",           line="2·분당선",     lat=37.504257, lng=127.048174),
        Station(id="yeoksam",           name="역삼",           line="2호선",        lat=37.500658, lng=127.036430),
        Station(id="gangnam",           name="강남",           line="2호선",        lat=37.497958, lng=127.027539),
        Station(id="gyodae",            name="교대",           line="2·3호선",      lat=37.493060, lng=127.013796),
        Station(id="seocho",            name="서초",           line="2호선",        lat=37.491910, lng=127.007945),
        Station(id="bangbae",           name="방배",           line="2호선",        lat=37.481469, lng=126.997627),
        Station(id="sadang",            name="사당",           line="2·4호선",      lat=37.476536, lng=126.981631),
        Station(id="nakseongdae",       name="낙성대",         line="2호선",        lat=37.476930, lng=126.963783),
        Station(id="snu",               name="서울대입구",     line="2호선",        lat=37.481233, lng=126.952745),
        Station(id="bongcheon",         name="봉천",           line="2호선",        lat=37.482416, lng=126.941896),
        Station(id="sillim",            name="신림",           line="2호선",        lat=37.484216, lng=126.929573),
        Station(id="guro_digital",      name="구로디지털단지", line="2호선",        lat=37.485005, lng=126.902626),
        Station(id="daelim",            name="대림",           line="2·7호선",      lat=37.492426, lng=126.895293),
        Station(id="mullae",            name="문래",           line="2호선",        lat=37.517993, lng=126.894766),
        Station(id="yeongdeungpo_gu",   name="영등포구청",     line="2·5호선",      lat=37.525766, lng=126.896627),
        Station(id="dangsan",           name="당산",           line="2·9호선",      lat=37.533877, lng=126.902011),
        Station(id="hapjeong",          name="합정",           line="2·6호선",      lat=37.550025, lng=126.914557),
        Station(id="hongdae",           name="홍대입구",       line="2·경의중앙선", lat=37.556748, lng=126.923643),
        Station(id="sinchon",           name="신촌",           line="2호선",        lat=37.555153, lng=126.936890),
        Station(id="ewha",              name="이대",           line="2호선",        lat=37.556734, lng=126.945897),
        Station(id="ahyeon",            name="아현",           line="2호선",        lat=37.557407, lng=126.956079),
        Station(id="chungjeongno",      name="충정로",         line="2·5호선",      lat=37.560061, lng=126.962783),

        # ── 3호선 ──────────────────────────────────────────────────────────
        Station(id="gyeongbokgung",     name="경복궁",         line="3호선",        lat=37.575844, lng=126.973576),
        Station(id="anguk",             name="안국",           line="3호선",        lat=37.576562, lng=126.985470),
        Station(id="chungmuro",         name="충무로",         line="3·4호선",      lat=37.561302, lng=126.995473),
        Station(id="dongdae_ib",        name="동대입구",       line="3호선",        lat=37.558160, lng=127.005273),
        Station(id="yaksu",             name="약수",           line="3·6호선",      lat=37.554087, lng=127.010237),
        Station(id="geumho",            name="금호",           line="3호선",        lat=37.548269, lng=127.015785),
        Station(id="oksu",              name="옥수",           line="3호선",        lat=37.541653, lng=127.017303),
        Station(id="apgujeong",         name="압구정",         line="3호선",        lat=37.526169, lng=127.028502),
        Station(id="sinsa",             name="신사",           line="3호선",        lat=37.516438, lng=127.020247),
        Station(id="jamwon",            name="잠원",           line="3호선",        lat=37.512989, lng=127.011613),
        Station(id="express_terminal",  name="고속터미널",     line="3·7·9호선",    lat=37.504953, lng=127.004916),
        Station(id="nambu_terminal",    name="남부터미널",     line="3호선",        lat=37.484940, lng=127.016289),
        Station(id="yangjae",           name="양재",           line="3·신분당선",   lat=37.484660, lng=127.035130),
        Station(id="maebong",           name="매봉",           line="3호선",        lat=37.487114, lng=127.046907),
        Station(id="dogok",             name="도곡",           line="3·분당선",     lat=37.491129, lng=127.055694),
        Station(id="daechi",            name="대치",           line="3호선",        lat=37.494601, lng=127.063449),
        Station(id="hagnyeoul",         name="학여울",         line="3호선",        lat=37.496757, lng=127.070541),
        Station(id="daecheong",         name="대청",           line="3호선",        lat=37.493607, lng=127.079526),
        Station(id="irwon",             name="일원",           line="3호선",        lat=37.483890, lng=127.084160),
        Station(id="suseo",             name="수서",           line="3·수인분당선", lat=37.487507, lng=127.101324),
        Station(id="garak_market",      name="가락시장",       line="3·8호선",      lat=37.493004, lng=127.118279),
        Station(id="ogeum",             name="오금",           line="3·5호선",      lat=37.502228, lng=127.127701),

        # ── 4호선 ──────────────────────────────────────────────────────────
        Station(id="hyehwa",            name="혜화",           line="4호선",        lat=37.582116, lng=127.001759),
        Station(id="hanseongdae",       name="한성대입구",     line="4호선",        lat=37.588380, lng=127.006751),
        Station(id="sungshin_univ",     name="성신여대입구",   line="4호선",        lat=37.592782, lng=127.017338),
        Station(id="gireum",            name="길음",           line="4호선",        lat=37.604087, lng=127.025353),
        Station(id="mia_sa",            name="미아사거리",     line="4호선",        lat=37.613276, lng=127.030083),
        Station(id="mia",               name="미아",           line="4호선",        lat=37.626435, lng=127.026151),
        Station(id="suyu",              name="수유",           line="4호선",        lat=37.637127, lng=127.024731),
        Station(id="nowon",             name="노원",           line="4·7호선",      lat=37.654478, lng=127.060555),
        Station(id="myeongdong",        name="명동",           line="4호선",        lat=37.561055, lng=126.988271),
        Station(id="hoehyeon",          name="회현",           line="4호선",        lat=37.559698, lng=126.979565),
        Station(id="sukdae_ib",         name="숙대입구",       line="4호선",        lat=37.545124, lng=126.971952),
        Station(id="samgakji",          name="삼각지",         line="4·6호선",      lat=37.535057, lng=126.973354),
        Station(id="ichon",             name="이촌",           line="4호선",        lat=37.522525, lng=126.973350),
        Station(id="dongjak",           name="동작",           line="4·9호선",      lat=37.503567, lng=126.980171),
        Station(id="isu",               name="이수",           line="4·7호선",      lat=37.485258, lng=126.981766),

        # ── 5호선 ──────────────────────────────────────────────────────────
        Station(id="gwanghwamun",       name="광화문",         line="5호선",        lat=37.570545, lng=126.976568),
        Station(id="seodaemun",         name="서대문",         line="5호선",        lat=37.565812, lng=126.966639),
        Station(id="aeogage",           name="애오개",         line="5호선",        lat=37.553592, lng=126.956733),
        Station(id="gongdeok",          name="공덕",           line="5·6호선",      lat=37.543592, lng=126.951664),
        Station(id="mapo",              name="마포",           line="5호선",        lat=37.539718, lng=126.946043),
        Station(id="yeouinaru",         name="여의나루",       line="5호선",        lat=37.527145, lng=126.932807),
        Station(id="yeouido",           name="여의도",         line="5·9호선",      lat=37.521578, lng=126.924318),
        Station(id="yeongdeungpo",      name="영등포시장",     line="5호선",        lat=37.522760, lng=126.905143),
        Station(id="cheongu",           name="청구",           line="5·6호선",      lat=37.560237, lng=127.013790),
        Station(id="haengdang",         name="행당",           line="5호선",        lat=37.557297, lng=127.029482),
        Station(id="gunja",             name="군자",           line="5·7호선",      lat=37.557151, lng=127.079484),
        Station(id="achasan",           name="아차산",         line="5호선",        lat=37.552005, lng=127.089609),
        Station(id="gwangnaru",         name="광나루",         line="5호선",        lat=37.545301, lng=127.103478),
        Station(id="cheonho",           name="천호",           line="5·8호선",      lat=37.538566, lng=127.123539),
        Station(id="gangdong",          name="강동",           line="5호선",        lat=37.535810, lng=127.132490),

        # ── 6호선 ──────────────────────────────────────────────────────────
        Station(id="mangwon",           name="망원",           line="6호선",        lat=37.556031, lng=126.910129),
        Station(id="sangsu",            name="상수",           line="6호선",        lat=37.547704, lng=126.922920),
        Station(id="itaewon",           name="이태원",         line="6호선",        lat=37.534485, lng=126.994369),
        Station(id="hangangjin",        name="한강진",         line="6호선",        lat=37.539560, lng=127.001729),
        Station(id="noksapyeong",       name="녹사평",         line="6호선",        lat=37.534690, lng=126.986650),
        Station(id="bomun",             name="보문",           line="6호선",        lat=37.585293, lng=127.019377),
        Station(id="anam",              name="안암",           line="6호선",        lat=37.586261, lng=127.029030),
        Station(id="korea_univ",        name="고려대",         line="6호선",        lat=37.590340, lng=127.036260),
        Station(id="wolgok",            name="월곡",           line="6호선",        lat=37.601920, lng=127.041492),
        Station(id="taereung",          name="태릉입구",       line="6·7호선",      lat=37.617319, lng=127.074741),

        # ── 7호선 ──────────────────────────────────────────────────────────
        Station(id="ttukseom_resort",   name="뚝섬유원지",     line="7호선",        lat=37.531558, lng=127.066714),
        Station(id="cheongdam",         name="청담",           line="7호선",        lat=37.519097, lng=127.051851),
        Station(id="gangnam_gu",        name="강남구청",       line="7호선",        lat=37.517185, lng=127.041220),
        Station(id="hakdong",           name="학동",           line="7호선",        lat=37.514262, lng=127.031738),
        Station(id="nonhyeon",          name="논현",           line="7호선",        lat=37.511108, lng=127.021385),
        Station(id="banpo",             name="반포",           line="7호선",        lat=37.508171, lng=127.011717),
        Station(id="naebang",           name="내방",           line="7호선",        lat=37.487640, lng=126.993541),
        Station(id="namseong",          name="남성",           line="7호선",        lat=37.484688, lng=126.971108),
        Station(id="sungsil_univ",      name="숭실대입구",     line="7호선",        lat=37.496258, lng=126.953649),
        Station(id="sangdo",            name="상도",           line="7호선",        lat=37.502790, lng=126.947949),
        Station(id="jangseungbaegi",    name="장승배기",       line="7호선",        lat=37.504845, lng=126.939025),
        Station(id="boramae",           name="보라매",         line="7호선",        lat=37.499916, lng=126.920112),
        Station(id="sinpung",           name="신풍",           line="7호선",        lat=37.500107, lng=126.909806),
        Station(id="gasan_digital",     name="가산디지털단지", line="1·7호선",      lat=37.480376, lng=126.882704),

        # ── 9호선 ──────────────────────────────────────────────────────────
        Station(id="heukseok",          name="흑석",           line="9호선",        lat=37.5090, lng=126.9624),
        Station(id="gubanpo",           name="구반포",         line="9호선",        lat=37.5063, lng=126.9981),
        Station(id="sinbanpo",          name="신반포",         line="9호선",        lat=37.5040, lng=127.0068),
        Station(id="sapyeong",          name="사평",           line="9호선",        lat=37.5017, lng=127.0205),
        Station(id="sinnonhyeon",       name="신논현",         line="9호선",        lat=37.5049, lng=127.0251),
        Station(id="eonju",             name="언주",           line="9호선",        lat=37.507324, lng=127.033905),
        Station(id="seonjeongneung",    name="선정릉",         line="9호선",        lat=37.510278, lng=127.043902),
        Station(id="samsung_jungang",   name="삼성중앙",       line="9호선",        lat=37.513060, lng=127.053334),
        Station(id="bongeunsa",         name="봉은사",         line="9호선",        lat=37.514258, lng=127.060257),
        Station(id="hanseongbaekje",    name="한성백제",       line="9호선",        lat=37.516311, lng=127.116168),
        Station(id="olympic_park",      name="올림픽공원",     line="9호선",        lat=37.516217, lng=127.130957),

        # ── 경의중앙선 (서울 구간) ──────────────────────────────────────────
        Station(id="dmc",               name="디지털미디어시티", line="6호선·경의중앙선", lat=37.577005, lng=126.898643),
        Station(id="jongro3ga",         name="종로3가",        line="1·3·5호선",    lat=37.570455, lng=126.992134),
        Station(id="jonggak",           name="종각",           line="1호선",        lat=37.570203, lng=126.983116),
    ]

    def find_nearest(self, location: Location) -> Station:
        return self.find_nearest_candidates(location, limit=1)[0]

    def find_nearest_candidates(
        self,
        location: Location,
        limit: int,
    ) -> list[Station]:
        if limit <= 0:
            return []
        return sorted(
            self._STATIONS,
            key=lambda s: _haversine(location.lat, location.lng, s.lat, s.lng),
        )[:limit]

    def find_by_name(self, name: str) -> Station | None:
        target = _normalize_station_name(name)
        for station in self._STATIONS:
            if _normalize_station_name(station.name) == target:
                return station
        return None


def _normalize_station_name(name: str) -> str:
    normalized = "".join(name.strip().split())
    if normalized.endswith("역"):
        normalized = normalized[:-1]
    return normalized
