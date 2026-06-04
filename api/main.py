from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from api.v1 import midpoint, recommend
from domain.exceptions import (
    NoNearbyStationError,
    NoRecommendationsError,
    VectorDBError,
)

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="Where 장소 추천 API", version="1.0.0")


@app.exception_handler(NoNearbyStationError)
async def no_nearby_station_handler(
    request: Request,
    exc: NoNearbyStationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "주어진 위치 근처에 역을 찾을 수 없습니다."},
    )


@app.exception_handler(NoRecommendationsError)
async def no_recommendations_handler(
    request: Request,
    exc: NoRecommendationsError,
) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": "해당 역 주변 추천 장소를 찾을 수 없습니다."},
    )


@app.exception_handler(VectorDBError)
async def vector_db_error_handler(
    request: Request,
    exc: VectorDBError,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"detail": "벡터 데이터베이스 오류가 발생했습니다."},
    )


app.include_router(midpoint.router, prefix="/api/v1", tags=["midpoint"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommend"])

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
async def frontend() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")
