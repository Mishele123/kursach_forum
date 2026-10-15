import os
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)


_BASE_KWARGS: dict[str, Any] = {
    "env_file": ENV_PATH,
    "env_file_encoding": "utf-8",
    "extra": "ignore",
}


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(**_BASE_KWARGS, env_prefix="POSTGRES_")
    host: str
    port: int
    user: str
    password: str
    db: str


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(**_BASE_KWARGS, env_prefix="REDIS_")
    host: str
    port: int
    password: str
    key_prefix: str = ""
    session_ttl_seconds: int


class Config:
    def __init__(self) -> None:
        self.postgres = PostgresConfig()
        self.redis = RedisConfig()


class WebConfig(BaseSettings):
    model_config = SettingsConfigDict(**_BASE_KWARGS, env_prefix='WEB_')
    allowed_origins: list[str] = ['http://localhost:5173', 'http://127.0.0.1:5173']
    cookie_secure: bool = False
