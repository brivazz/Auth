import os
from logging import config as logging_config

from pydantic import BaseSettings, Field

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    project_name: str = Field("movies", env="PROJECT_NAME")
    redis_host: str = Field("localhost", env="ASYNC_REDIS_HOST")
    redis_port: int = Field(6379, env="ASYNC_REDIS_PORT")
    elastic_host: str = Field("localhost", env="ELASTICSEARCH_HOST")
    elastic_port: int = Field(9200, env="ELASTICSEARCH_PORT")
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    auth_server_url = Field("http://api/api/v1/auth", env="AUTH_URL")


settings = Settings()
