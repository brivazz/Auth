from logging import config as logging_config

from pydantic import BaseSettings, Field

from src.core.logger import LOGGING
from dotenv import load_dotenv


load_dotenv()
logging_config.dictConfig(LOGGING)


class PostgresSettings(BaseSettings):
    dbname: str = Field(..., env="POSTGRES_DB")
    user: str = Field(..., env="POSTGRES_USER")
    password: str = Field(..., env="POSTGRES_PASSWORD")
    host: str = Field("localhost", env="POSTGRES_HOST")
    port: int = Field(5432, env="POSTGRES_PORT")


class RedisSettings(BaseSettings):
    host: str = Field("localhost", env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")


class YandexOAuthSettings(BaseSettings):
    name: str = "yandex"
    client_id: str = Field(..., env="YANDEX_ID")
    client_secret: str = Field(..., env="YANDEX_SECRET")
    authorize_url: str = Field(..., env="YANDEX_AUTHORIZE_URL")
    access_token_url: str = Field(..., env="YANDEX_ACCESS_TOKEN")
    get_info_url: str = Field(..., env="YANDEX_INFO_URL")
    response_type: str = "code"
    display: str = "popup"
    scope: str = "login:info"


class OAuthSettings(BaseSettings):
    yandex: YandexOAuthSettings = YandexOAuthSettings()


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    debug: bool = Field(..., env="DEBUG")
    postgres: PostgresSettings = PostgresSettings()
    redis: RedisSettings = RedisSettings()
    oauth = OAuthSettings = OAuthSettings()

    default_rate_limit: int = Field(10, env="DEFAULT_RATE_LIMIT")
    rate_limit_enabled: bool = Field(True, env="RATE_LIMIT_ENABLED")

    tracer_enabled: bool = Field(True, env="TRACER_ENABLED")
    tracer_host: str = Field("localhost", env="TRACER_HOST")
    tracer_port: int = Field(6831, env="TRACER_UDP_PORT")


settings = Settings()
