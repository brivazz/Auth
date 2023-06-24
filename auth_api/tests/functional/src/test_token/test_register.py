import os
import sys
import logging
from http import HTTPStatus

from redis.asyncio import Redis
import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        # проверка нормальной регистрации
        (
            {
                "request_body": {"login": "test", "password": "test"},
            },
            {"number": 0, "status": HTTPStatus.OK, "body": ""},
        ),
        # регистрация пользователя с существующим login
        (
            {
                "request_body": {"login": "test", "password": "test"},
            },
            {
                "status": HTTPStatus.CONFLICT,
                "body": {"err_msg": "User with this login already exists."},
            },
        ),
        # отсутствие поля password
        (
            {
                "request_body": {
                    "login": "test",
                },
            },
            {"status": HTTPStatus.BAD_REQUEST, "body": {"err_msg": "Invalid json"}},
        ),
        # отсутствие поля login
        (
            {
                "request_body": {"password": "test"},
            },
            {"status": HTTPStatus.BAD_REQUEST, "body": {"err_msg": "Invalid json"}},
        ),
    ],
)
async def test_register(
    redis_client: Redis, make_get_request, query_data: dict, expected_answer: dict
):
    url = test_settings.service_url + "/api/v1/auth/register"
    body, status = await make_get_request(
        url, method="POST", data=query_data["request_body"]
    )
    logging.info([body, status])
    assert status == expected_answer["status"]

    if status == HTTPStatus.OK:
        assert "access_token" in body
        assert "refresh_token" in body
        if "refresh_token" in body:
            access_token_in_redis: bytes = await redis_client.get(body["refresh_token"])
            assert access_token_in_redis is not None
            assert access_token_in_redis.decode("utf-8") == body["access_token"]

    else:
        assert body["err_msg"] == expected_answer["body"]["err_msg"]
