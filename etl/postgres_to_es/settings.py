import logging

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

load_dotenv()


class PostgresDSN(BaseSettings):
    dbname: str = Field(env="ASYNC_POSTGRES_DB")
    user: str = Field(env="ASYNC_POSTGRES_USER")
    password: str = Field(env="ASYNC_POSTGRES_PASSWORD")
    host: str = Field(env="ASYNC_POSTGRES_HOST")
    port: int = Field(env="ASYNC_POSTGRES_PORT")
    options: str = Field(env="ASYNC_POSTGRES_OPTIONS")


class ElasticConfig(BaseSettings):
    host: str = Field(env="ELASTICSEARCH_HOST")
    port: int = Field(env="ELASTICSEARCH_PORT")
    scheme: str = "http"


class RedisConfig(BaseSettings):
    host: str = Field(env="ASYNC_REDIS_HOST")
    port: int = Field(env="ASYNC_REDIS_PORT")


class AppConfig(BaseSettings):
    batch_size: int = Field(env="BATCH_SIZE")
    frequency: int = Field(env="FREQUENCY")
    movies_index: str = Field(env="MOVIES_INDEX")
    persons_index: str = Field(env="PERSONS_INDEX")
    genres_index: str = Field(env="GENRES_INDEX")


postgres_dsn = PostgresDSN()
elastic_config = ElasticConfig()
redis_config = RedisConfig()
app_config = AppConfig()

logger_settings = {
    "format": "%(asctime)s - %(name)s.%(funcName)s:%(lineno)d - %(levelname)s - %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "level": logging.INFO,
    "handlers": [logging.StreamHandler()],
}
