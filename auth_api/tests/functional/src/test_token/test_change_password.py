import logging
import os
import sys
from http import HTTPStatus

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        # успешная смена пароля
        (
            {
                "reg_request_body": {"login": "test_ch_p_1", "password": "test"},
                "ch_request_body": {"old_password": "test", "new_password": "new_test"},
            },
            {"status": HTTPStatus.OK, "body": ""},
        ),
        # смена пароля с неправильным паролем
        (
            {
                "reg_request_body": {"login": "test_ch_p_2", "password": "test"},
                "ch_request_body": {
                    "old_password": "qwerty",
                    "new_password": "new_test",
                },
            },
            {
                "status": HTTPStatus.UNAUTHORIZED,
                "body": {"err_msg": "Old password is not valid."},
            },
        ),
        # смена пароля с неправильным access token
        (
            {
                "reg_request_body": {"login": "test_ch_p_3", "password": "test"},
                "headers": {
                    "Authorization": "Bearer eyJGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
                    ".eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4NjE1NjYyMSwianRpIjoiZTE"
                    "xY2RlMTktY2IwZi00NmM2LTg0ZDQtOGZiMGM0ZmI4OTMxIiwidHlwZSI"
                    "6ImFjY2VzcyIsInN1YiI6IntcInJvbGVcIjogXCJjb25zdW1lclwiLCB"
                    "cInVzZXJfaWRcIjogXCIwOGNiNjFkOC1hZTYyLTRkMzAtYTQxZS0xYWE"
                    "yMTM4Y2Y3NTVcIn0iLCJuYmYiOjE2ODYxNTY2MjEsImV4cCI6MTY4NjE"
                    "2MzgyMX0.vTouV4vqvzRSilZMP5Mov7CHUJHiJ8S9k90JwJu72C4"
                },
                "ch_request_body": {
                    "old_password": "qwerty",
                    "new_password": "new_test",
                },
            },
            {
                "status": HTTPStatus.UNPROCESSABLE_ENTITY,
                "body": {"err_msg": "Old password is not valid."},
            },
        ),
        # смена пароля без старого пароля
        (
            {
                "reg_request_body": {"login": "test_ch_p_4", "password": "test"},
                "ch_request_body": {"new_password": "new_test"},
            },
            {"status": HTTPStatus.BAD_REQUEST, "body": {"err_msg": "Invalid json"}},
        ),
        # смена пароля без нового пароля
        (
            {
                "reg_request_body": {"login": "test_ch_p_5", "password": "test"},
                "ch_request_body": {"old_password": "qwerty"},
            },
            {"status": HTTPStatus.BAD_REQUEST, "body": {"err_msg": "Invalid json"}},
        ),
    ],
)
async def test_change_password(
    make_get_request, query_data: dict, expected_answer: dict
):
    url = test_settings.service_url + "/api/v1/auth/change-password"
    # регистрация пользователя
    reg_body, reg_status = await make_get_request(
        test_settings.service_url + "/api/v1/auth/register",
        method="POST",
        data=query_data["reg_request_body"],
    )
    assert reg_status == HTTPStatus.OK, "ошибка регистрации"

    logging.info(f"{reg_body['access_token']}\n\n" * 10)
    if not query_data.get("headers"):
        headers = {"Authorization": f"Bearer {reg_body['access_token']}"}
    else:
        headers = query_data.get("headers")
    body, status = await make_get_request(
        url, method="POST", data=query_data["ch_request_body"], headers=headers
    )

    assert status == expected_answer["status"]

    if status != HTTPStatus.OK:
        if body.get("msg"):
            pass
        else:
            assert body["err_msg"] == expected_answer["body"]["err_msg"]
