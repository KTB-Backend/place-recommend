from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    embedding_model: str = "jhgan/ko-sroberta-multitask"
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_collection_name: str = "places"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    station_search_radius_km: float = 5.0
    default_top_k: int = 3
    kakao_rest_api_key: str = ""
    kakao_javascript_key: str = ""
    kakao_ssl_verify: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
