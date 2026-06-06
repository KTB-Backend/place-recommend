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
        Station(id="seoul_station",     name="서울역",         line="1·4호선",      lat=37.5546, lng=126.9706),
        Station(id="namyeong",          name="남영",           line="1호선",        lat=37.5403, lng=126.9706),
        Station(id="yongsan",           name="용산",           line="1호선",        lat=37.5299, lng=126.9649),
        Station(id="nodukhoom",         name="노들",           line="9호선",        lat=37.5145, lng=126.9313),
        Station(id="noryangjin",        name="노량진",         line="1·9호선",      lat=37.5118, lng=126.9433),
        Station(id="daebang",           name="대방",           line="1호선",        lat=37.5143, lng=126.9264),
        Station(id="sindorim",          name="신도림",         line="1·2호선",      lat=37.5082, lng=126.8912),
        Station(id="guro",              name="구로",           line="1호선",        lat=37.5028, lng=126.8818),
        Station(id="sindaebang",        name="신대방",         line="2호선",        lat=37.4876, lng=126.9148),
        Station(id="dongdaemun",        name="동대문",         line="1·4호선",      lat=37.5717, lng=127.0088),
        Station(id="sinseoldong",       name="신설동",         line="1·2호선",      lat=37.5741, lng=127.0198),
        Station(id="cheongnyangni",     name="청량리",         line="1호선",        lat=37.5803, lng=127.0447),
        Station(id="hoegi",             name="회기",           line="1호선",        lat=37.5894, lng=127.0613),
        Station(id="changdong",         name="창동",           line="1·4호선",      lat=37.6530, lng=127.0475),
        Station(id="ssangmun",          name="쌍문",           line="4호선",        lat=37.6485, lng=127.0327),

        # ── 2호선 ──────────────────────────────────────────────────────────
        Station(id="cityhall",          name="시청",           line="1·2호선",      lat=37.5650, lng=126.9774),
        Station(id="euljiro_ib",        name="을지로입구",     line="2호선",        lat=37.5662, lng=126.9826),
        Station(id="euljiro3",          name="을지로3가",      line="2·3호선",      lat=37.5663, lng=126.9916),
        Station(id="euljiro4",          name="을지로4가",      line="2·5호선",      lat=37.5659, lng=127.0005),
        Station(id="ddp",               name="동대문역사문화공원", line="2·4·5호선", lat=37.5653, lng=127.0099),
        Station(id="sindang",           name="신당",           line="2·6호선",      lat=37.5647, lng=127.0188),
        Station(id="sangwangsimni",     name="상왕십리",       line="2호선",        lat=37.5621, lng=127.0296),
        Station(id="wangsimni",         name="왕십리",         line="2·5호선",      lat=37.5616, lng=127.0384),
        Station(id="hanyang_univ",      name="한양대",         line="2호선",        lat=37.5553, lng=127.0445),
        Station(id="ttukseom",          name="뚝섬",           line="2호선",        lat=37.5474, lng=127.0528),
        Station(id="seongsu",           name="성수",           line="2호선",        lat=37.5447, lng=127.0557),
        Station(id="konkuk",            name="건대입구",       line="2·7호선",      lat=37.5403, lng=127.0698),
        Station(id="guui",              name="구의",           line="2호선",        lat=37.5375, lng=127.0872),
        Station(id="gangbyeon",         name="강변",           line="2호선",        lat=37.5340, lng=127.0930),
        Station(id="jamsil_naru",       name="잠실나루",       line="2호선",        lat=37.5136, lng=127.0877),
        Station(id="jamsil",            name="잠실",           line="2·8호선",      lat=37.5133, lng=127.1001),
        Station(id="sincheon",          name="신천",           line="2호선",        lat=37.5108, lng=127.1003),
        Station(id="sports_complex",    name="종합운동장",     line="2·9호선",      lat=37.5107, lng=127.0734),
        Station(id="samsung",           name="삼성",           line="2호선",        lat=37.5088, lng=127.0630),
        Station(id="seolleung",         name="선릉",           line="2·분당선",     lat=37.5048, lng=127.0495),
        Station(id="yeoksam",           name="역삼",           line="2호선",        lat=37.5001, lng=127.0365),
        Station(id="gangnam",           name="강남",           line="2호선",        lat=37.4979, lng=127.0276),
        Station(id="gyodae",            name="교대",           line="2·3호선",      lat=37.4935, lng=127.0138),
        Station(id="seocho",            name="서초",           line="2호선",        lat=37.4915, lng=127.0071),
        Station(id="bangbae",           name="방배",           line="2호선",        lat=37.4808, lng=126.9974),
        Station(id="sadang",            name="사당",           line="2·4호선",      lat=37.4767, lng=126.9815),
        Station(id="nakseongdae",       name="낙성대",         line="2호선",        lat=37.4757, lng=126.9639),
        Station(id="snu",               name="서울대입구",     line="2호선",        lat=37.4813, lng=126.9527),
        Station(id="bongcheon",         name="봉천",           line="2호선",        lat=37.4816, lng=126.9435),
        Station(id="sillim",            name="신림",           line="2호선",        lat=37.4845, lng=126.9293),
        Station(id="guro_digital",      name="구로디지털단지", line="2호선",        lat=37.4857, lng=126.9013),
        Station(id="daelim",            name="대림",           line="2·7호선",      lat=37.4920, lng=126.8965),
        Station(id="mullae",            name="문래",           line="2호선",        lat=37.5178, lng=126.8960),
        Station(id="yeongdeungpo_gu",   name="영등포구청",     line="2·5호선",      lat=37.5255, lng=126.8964),
        Station(id="dangsan",           name="당산",           line="2·9호선",      lat=37.5341, lng=126.9002),
        Station(id="hapjeong",          name="합정",           line="2·6호선",      lat=37.5499, lng=126.9138),
        Station(id="hongdae",           name="홍대입구",       line="2·경의중앙선", lat=37.5574, lng=126.9249),
        Station(id="sinchon",           name="신촌",           line="2호선",        lat=37.5551, lng=126.9368),
        Station(id="ewha",              name="이대",           line="2호선",        lat=37.5565, lng=126.9466),
        Station(id="ahyeon",            name="아현",           line="2호선",        lat=37.5572, lng=126.9571),
        Station(id="chungjeongno",      name="충정로",         line="2·5호선",      lat=37.5600, lng=126.9634),

        # ── 3호선 ──────────────────────────────────────────────────────────
        Station(id="gyeongbokgung",     name="경복궁",         line="3호선",        lat=37.5789, lng=126.9746),
        Station(id="anguk",             name="안국",           line="3호선",        lat=37.5759, lng=126.9851),
        Station(id="chungmuro",         name="충무로",         line="3·4호선",      lat=37.5616, lng=126.9940),
        Station(id="dongdae_ib",        name="동대입구",       line="3호선",        lat=37.5592, lng=127.0053),
        Station(id="yaksu",             name="약수",           line="3·6호선",      lat=37.5519, lng=127.0071),
        Station(id="geumho",            name="금호",           line="3호선",        lat=37.5489, lng=127.0145),
        Station(id="oksu",              name="옥수",           line="3호선",        lat=37.5440, lng=127.0182),
        Station(id="apgujeong",         name="압구정",         line="3호선",        lat=37.5270, lng=127.0282),
        Station(id="sinsa",             name="신사",           line="3호선",        lat=37.5160, lng=127.0209),
        Station(id="jamwon",            name="잠원",           line="3호선",        lat=37.5127, lng=127.0111),
        Station(id="express_terminal",  name="고속터미널",     line="3·7·9호선",    lat=37.5047, lng=127.0047),
        Station(id="nambu_terminal",    name="남부터미널",     line="3호선",        lat=37.4854, lng=127.0191),
        Station(id="yangjae",           name="양재",           line="3·신분당선",   lat=37.4843, lng=127.0345),
        Station(id="maebong",           name="매봉",           line="3호선",        lat=37.4830, lng=127.0479),
        Station(id="dogok",             name="도곡",           line="3·분당선",     lat=37.4907, lng=127.0553),
        Station(id="daechi",            name="대치",           line="3호선",        lat=37.4944, lng=127.0616),
        Station(id="hagnyeoul",         name="학여울",         line="3호선",        lat=37.4959, lng=127.0709),
        Station(id="daecheong",         name="대청",           line="3호선",        lat=37.4936, lng=127.0796),
        Station(id="irwon",             name="일원",           line="3호선",        lat=37.4835, lng=127.0842),
        Station(id="suseo",             name="수서",           line="3·수인분당선", lat=37.4867, lng=127.1025),
        Station(id="garak_market",      name="가락시장",       line="3·8호선",      lat=37.4941, lng=127.1160),
        Station(id="ogeum",             name="오금",           line="3·5호선",      lat=37.5031, lng=127.1275),

        # ── 4호선 ──────────────────────────────────────────────────────────
        Station(id="hyehwa",            name="혜화",           line="4호선",        lat=37.5827, lng=127.0017),
        Station(id="hanseongdae",       name="한성대입구",     line="4호선",        lat=37.5893, lng=127.0060),
        Station(id="sungshin_univ",     name="성신여대입구",   line="4호선",        lat=37.5926, lng=127.0166),
        Station(id="gireum",            name="길음",           line="4호선",        lat=37.6034, lng=127.0267),
        Station(id="mia_sa",            name="미아사거리",     line="4호선",        lat=37.6130, lng=127.0307),
        Station(id="mia",               name="미아",           line="4호선",        lat=37.6265, lng=127.0252),
        Station(id="suyu",              name="수유",           line="4호선",        lat=37.6385, lng=127.0255),
        Station(id="nowon",             name="노원",           line="4·7호선",      lat=37.6541, lng=127.0614),
        Station(id="myeongdong",        name="명동",           line="4호선",        lat=37.5612, lng=126.9826),
        Station(id="hoehyeon",          name="회현",           line="4호선",        lat=37.5575, lng=126.9790),
        Station(id="sukdae_ib",         name="숙대입구",       line="4호선",        lat=37.5449, lng=126.9728),
        Station(id="samgakji",          name="삼각지",         line="4·6호선",      lat=37.5349, lng=126.9733),
        Station(id="ichon",             name="이촌",           line="4호선",        lat=37.5225, lng=126.9750),
        Station(id="dongjak",           name="동작",           line="4·9호선",      lat=37.5027, lng=126.9799),
        Station(id="isu",               name="이수",           line="4·7호선",      lat=37.4850, lng=126.9820),

        # ── 5호선 ──────────────────────────────────────────────────────────
        Station(id="gwanghwamun",       name="광화문",         line="5호선",        lat=37.5716, lng=126.9768),
        Station(id="seodaemun",         name="서대문",         line="5호선",        lat=37.5660, lng=126.9667),
        Station(id="aeogage",           name="애오개",         line="5호선",        lat=37.5495, lng=126.9556),
        Station(id="gongdeok",          name="공덕",           line="5·6호선",      lat=37.5440, lng=126.9524),
        Station(id="mapo",              name="마포",           line="5호선",        lat=37.5376, lng=126.9506),
        Station(id="yeouinaru",         name="여의나루",       line="5호선",        lat=37.5285, lng=126.9326),
        Station(id="yeouido",           name="여의도",         line="5·9호선",      lat=37.5216, lng=126.9244),
        Station(id="yeongdeungpo",      name="영등포시장",     line="5호선",        lat=37.5224, lng=126.9055),
        Station(id="cheongu",           name="청구",           line="5·6호선",      lat=37.5644, lng=127.0136),
        Station(id="haengdang",         name="행당",           line="5호선",        lat=37.5568, lng=127.0316),
        Station(id="gunja",             name="군자",           line="5·7호선",      lat=37.5583, lng=127.0780),
        Station(id="achasan",           name="아차산",         line="5호선",        lat=37.5557, lng=127.0887),
        Station(id="gwangnaru",         name="광나루",         line="5호선",        lat=37.5456, lng=127.1058),
        Station(id="cheonho",           name="천호",           line="5·8호선",      lat=37.5385, lng=127.1232),
        Station(id="gangdong",          name="강동",           line="5호선",        lat=37.5354, lng=127.1335),

        # ── 6호선 ──────────────────────────────────────────────────────────
        Station(id="mangwon",           name="망원",           line="6호선",        lat=37.5552, lng=126.9116),
        Station(id="sangsu",            name="상수",           line="6호선",        lat=37.5480, lng=126.9224),
        Station(id="itaewon",           name="이태원",         line="6호선",        lat=37.5344, lng=126.9942),
        Station(id="hangangjin",        name="한강진",         line="6호선",        lat=37.5396, lng=127.0017),
        Station(id="noksapyeong",       name="녹사평",         line="6호선",        lat=37.5347, lng=126.9867),
        Station(id="bomun",             name="보문",           line="6호선",        lat=37.5887, lng=127.0169),
        Station(id="anam",              name="안암",           line="6호선",        lat=37.5863, lng=127.0257),
        Station(id="korea_univ",        name="고려대",         line="6호선",        lat=37.5880, lng=127.0326),
        Station(id="wolgok",            name="월곡",           line="6호선",        lat=37.6014, lng=127.0413),
        Station(id="taereung",          name="태릉입구",       line="6·7호선",      lat=37.6193, lng=127.0742),

        # ── 7호선 ──────────────────────────────────────────────────────────
        Station(id="ttukseom_resort",   name="뚝섬유원지",     line="7호선",        lat=37.5305, lng=127.0658),
        Station(id="cheongdam",         name="청담",           line="7호선",        lat=37.5198, lng=127.0512),
        Station(id="gangnam_gu",        name="강남구청",       line="7호선",        lat=37.5176, lng=127.0437),
        Station(id="hakdong",           name="학동",           line="7호선",        lat=37.5142, lng=127.0315),
        Station(id="nonhyeon",          name="논현",           line="7호선",        lat=37.5119, lng=127.0244),
        Station(id="banpo",             name="반포",           line="7호선",        lat=37.5082, lng=127.0118),
        Station(id="naebang",           name="내방",           line="7호선",        lat=37.4875, lng=126.9934),
        Station(id="namseong",          name="남성",           line="7호선",        lat=37.4847, lng=126.9711),
        Station(id="sungsil_univ",      name="숭실대입구",     line="7호선",        lat=37.4959, lng=126.9536),
        Station(id="sangdo",            name="상도",           line="7호선",        lat=37.5030, lng=126.9478),
        Station(id="jangseungbaegi",    name="장승배기",       line="7호선",        lat=37.5050, lng=126.9404),
        Station(id="boramae",           name="보라매",         line="7호선",        lat=37.4998, lng=126.9208),
        Station(id="sinpung",           name="신풍",           line="7호선",        lat=37.4967, lng=126.9091),
        Station(id="gasan_digital",     name="가산디지털단지", line="1·7호선",      lat=37.4806, lng=126.8822),

        # ── 9호선 ──────────────────────────────────────────────────────────
        Station(id="heukseok",          name="흑석",           line="9호선",        lat=37.5090, lng=126.9624),
        Station(id="gubanpo",           name="구반포",         line="9호선",        lat=37.5063, lng=126.9981),
        Station(id="sinbanpo",          name="신반포",         line="9호선",        lat=37.5040, lng=127.0068),
        Station(id="sapyeong",          name="사평",           line="9호선",        lat=37.5017, lng=127.0205),
        Station(id="sinnonhyeon",       name="신논현",         line="9호선",        lat=37.5049, lng=127.0251),
        Station(id="eonju",             name="언주",           line="9호선",        lat=37.5107, lng=127.0371),
        Station(id="seonjeongneung",    name="선정릉",         line="9호선",        lat=37.5116, lng=127.0468),
        Station(id="samsung_jungang",   name="삼성중앙",       line="9호선",        lat=37.5089, lng=127.0617),
        Station(id="bongeunsa",         name="봉은사",         line="9호선",        lat=37.5152, lng=127.0706),
        Station(id="hanseongbaekje",    name="한성백제",       line="9호선",        lat=37.5039, lng=127.1254),
        Station(id="olympic_park",      name="올림픽공원",     line="9호선",        lat=37.5162, lng=127.1310),

        # ── 경의중앙선 (서울 구간) ──────────────────────────────────────────
        Station(id="dmc",               name="디지털미디어시티", line="6호선·경의중앙선", lat=37.5773, lng=126.9009),
        Station(id="jongro3ga",         name="종로3가",        line="1·3·5호선",    lat=37.5717, lng=126.9916),
        Station(id="jonggak",           name="종각",           line="1호선",        lat=37.5703, lng=126.9828),
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
