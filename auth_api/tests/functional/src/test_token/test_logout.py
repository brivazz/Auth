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
        # проверка успешного логаута
        (
            {
                "reg_request_body": {"login": "test_logout_1", "password": "test"},
            },
            {"number": 0, "status": HTTPStatus.OK, "body": ""},
        ),
        # проверка логаута с неправильным refresh
        (
            {
                "reg_request_body": {"login": "test_logout_2", "password": "test"},
                "logout_request": {"refresh_token": "sesieorjer.serserser.serserser"},
            },
            {
                "number": 0,
                "status": HTTPStatus.BAD_REQUEST,
                "body": {"err_msg": "refresh is not valid"},
            },
        ),
        # проверка логаута без refresh
        (
            {
                "reg_request_body": {"login": "test_logout_9", "password": "test"},
                "logout_request": {},
            },
            {
                "number": 0,
                "status": HTTPStatus.BAD_REQUEST,
                "body": {"err_msg": "Invalid json"},
            },
        ),
    ],
)
async def test_logout(
    redis_client: Redis, make_get_request, query_data: dict, expected_answer: dict
):
    url = test_settings.service_url + "/api/v1/auth/logout"
    # регистрация пользователя
    reg_body, reg_status = await make_get_request(
        test_settings.service_url + "/api/v1/auth/register",
        method="POST",
        data=query_data["reg_request_body"],
    )
    assert reg_status == HTTPStatus.OK, "ошибка регистрации"

    if query_data.get("logout_request") is not None:
        data = query_data.get("logout_request")
    else:
        data = {"refresh_token": reg_body["refresh_token"]}
    logging.error(f'reqest data is: {query_data.get("logout_request")}')
    logging.error(f"reqest data is: {data}")
    body, status = await make_get_request(url, method="POST", data=data)

    assert status == expected_answer["status"]

    if status == HTTPStatus.OK:
        refresh_exist = await redis_client.exists(data["refresh_token"])
        assert not refresh_exist
    else:
        assert body["err_msg"] == expected_answer["body"]["err_msg"]
