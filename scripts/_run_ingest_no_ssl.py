"""SSL 검증 우회 후 ingest_to_vectordb 실행 (회사 프록시 환경용 임시 스크립트)."""
import ssl
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# httpx SSL 검증 비활성화
import httpx
_orig_client_init = httpx.Client.__init__
_orig_async_client_init = httpx.AsyncClient.__init__

def _patched_client_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _orig_client_init(self, *args, **kwargs)

def _patched_async_client_init(self, *args, **kwargs):
    kwargs["verify"] = False
    _orig_async_client_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init

# Python 기본 SSL 컨텍스트도 우회
ssl._create_default_https_context = ssl._create_unverified_context

# urllib3 경고 억제
import urllib3
urllib3.disable_warnings()

# 이제 실제 ingest 실행
import runpy
runpy.run_path(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "ingest_to_vectordb.py"),
    run_name="__main__",
)
