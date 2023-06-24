import os
import sys
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
        # проверка успешного логина
        (
            {
                "reg_request_body": {"login": "test_log_1", "password": "test"},
                "log_request_body": {"login": "test_log_1", "password": "test"},
            },
            {"number": 0, "status": HTTPStatus.OK, "body": ""},
        ),
        # логин с неправильным паролем
        (
            {
                "reg_request_body": {"login": "test_log_2", "password": "test"},
                "log_request_body": {"login": "test_log_2", "password": "qwerty"},
            },
            {
                "status": HTTPStatus.UNAUTHORIZED,
                "body": {"err_msg": "Password is not valid."},
            },
        ),
        # логин с неправильным логином
        (
            {
                "reg_request_body": {"login": "test_log_3", "password": "test"},
                "log_request_body": {"login": "qwerty", "password": "test"},
            },
            {
                "status": HTTPStatus.UNAUTHORIZED,
                "body": {"err_msg": "Login is not valid."},
            },
        ),
        # отсутствие поля password
        (
            {
                "reg_request_body": {"login": "test_log_4", "password": "test"},
                "log_request_body": {
                    "login": "test_log_4",
                },
            },
            {"status": HTTPStatus.BAD_REQUEST, "body": {"err_msg": "Invalid json"}},
        ),
        # отсутствие поля login
        (
            {
                "reg_request_body": {"login": "test_log_5", "password": "test"},
                "log_request_body": {"password": "test_log_5"},
            },
            {"status": HTTPStatus.BAD_REQUEST, "body": {"err_msg": "Invalid json"}},
        ),
    ],
)
async def test_login(
    redis_client: Redis, make_get_request, query_data: dict, expected_answer: dict
):
    url = test_settings.service_url + "/api/v1/auth/login"
    # регистрация пользователя
    _, reg_status = await make_get_request(
        test_settings.service_url + "/api/v1/auth/register",
        method="POST",
        data=query_data["reg_request_body"],
    )
    assert reg_status == HTTPStatus.OK, "ошибка регистрации"

    body, status = await make_get_request(
        url, method="POST", data=query_data["log_request_body"]
    )

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
