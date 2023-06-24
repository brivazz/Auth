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
        # проверка успешного обновления токенов
        (
            {
                "reg_request_body": {"login": "test_ref_1", "password": "test"},
            },
            {
                "number": 0,
                "status": HTTPStatus.OK,
            },
        ),
        # проверка логаута с неправильным refresh
        (
            {
                "reg_request_body": {"login": "test_ref_2", "password": "test"},
                "ref_request": {"refresh_token": "sesieorjer.serserser.serserser"},
            },
            {
                "number": 0,
                "status": HTTPStatus.BAD_REQUEST,
                "body": {"err_msg": "refresh token is not exist"},
            },
        ),
        # проверка логаута без refresh
        (
            {
                "reg_request_body": {"login": "test_ref_3", "password": "test"},
                "ref_request": {},
            },
            {
                "number": 0,
                "status": HTTPStatus.BAD_REQUEST,
                "body": {"err_msg": "Invalid json"},
            },
        ),
    ],
)
async def test_refresh_tokens(
    redis_client: Redis, make_get_request, query_data: dict, expected_answer: dict
):
    url = test_settings.service_url + "/api/v1/auth/refresh-tokens"
    # регистрация пользователя
    reg_body, reg_status = await make_get_request(
        test_settings.service_url + "/api/v1/auth/register",
        method="POST",
        data=query_data["reg_request_body"],
    )
    assert reg_status == HTTPStatus.OK, "ошибка регистрации"

    if query_data.get("ref_request") is not None:
        data = query_data.get("ref_request")
    else:
        data = {"refresh_token": reg_body["refresh_token"]}
    logging.error(f'reqest data is: {query_data.get("logout_request")}')
    logging.error(f"reqest data is: {data}")
    body, status = await make_get_request(url, method="POST", data=data)

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
