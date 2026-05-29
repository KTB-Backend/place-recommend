import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from core.config import get_settings

s = get_settings()
print(f"API 키 길이: {len(s.kakao_rest_api_key)}")
print(f"SSL verify: {s.kakao_ssl_verify}")

try:
    resp = httpx.get(
        "https://dapi.kakao.com/v2/local/search/category.json",
        headers={"Authorization": f"KakaoAK {s.kakao_rest_api_key}"},
        params={"category_group_code": "CE7", "x": 127.0276, "y": 37.4979, "radius": 500, "size": 5},
        verify=s.kakao_ssl_verify,
        timeout=10.0,
    )
    print(f"HTTP {resp.status_code}")
    print(resp.text[:800])
except Exception as e:
    print(f"예외: {type(e).__name__}: {e}")
