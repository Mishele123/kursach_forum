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

    def get_db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.db}"
        )


class Config:
    def __init__(self) -> None:
        self.postgres = PostgresConfig()


config = Config()
print(config.postgres.get_db_url())
