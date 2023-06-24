import logging
import os
import sys
import uuid
from http import HTTPStatus

import pytest
from functional.testdata.pg_data import ADMIN_USER

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [
        ({"login": "not_exist"}, {"message": "User not found."}, HTTPStatus.OK),
        ({"login": "super_user"}, {"login": "super_user"}, HTTPStatus.OK),
    ],
)
async def test_user_find(
    make_get_request, admin_tokens, query_data, expected_answer, expected_status
):
    tokens = admin_tokens
    url = test_settings.service_url + f'/api/v1/auth/users/{query_data["login"]}'
    body, status = await make_get_request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )

    if "User not found." != body.get("message"):
        assert expected_answer["login"] in body.get("login")
    else:
        assert body == expected_answer
    assert status == expected_status


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [
        (
            {
                "role_create": {"name": "some_role"},
                "user_id": ADMIN_USER["id"],
                "request": {"role_name": "another_role"},
            },
            {
                "role_assign": {"message": "User or role not found."},
                "check_role": ["admin"],
                "role_revoke": {"message": "User or role not found."},
            },
            HTTPStatus.OK,
        ),
        (
            {
                "role_create": {"name": "test_role"},
                "user_id": ADMIN_USER["id"],
                "request": {"role_name": "test_role"},
            },
            {
                "role_assign": {"message": "Role assigned to user successfully."},
                "check_role": ["admin", "test_role"],
                "role_revoke": {"message": "Role revoked from user successfully."},
            },
            HTTPStatus.OK,
        ),
    ],
)
async def test_assign_revoke_role(
    make_get_request,
    delete_all_pg_data,
    admin_tokens,
    query_data,
    expected_answer,
    expected_status,
):
    url = test_settings.service_url + "/api/v1/auth/roles"

    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="POST",
        data=query_data["role_create"],
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    assert status == HTTPStatus.OK
    logging.info("Role is created")
    # test creating role
    url = (
        test_settings.service_url
        + f'/api/v1/auth/users/{query_data["user_id"]}/assign-role'
    )
    logging.info(query_data["request"])
    body, status = await make_get_request(
        url,
        method="POST",
        data=query_data["request"],
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    assert body == expected_answer["role_assign"]
    assert status == expected_status

    # test check-permission
    url = (
        test_settings.service_url
        + f'/api/v1/auth/users/{query_data["user_id"]}/check-permissions'
    )
    body, status = await make_get_request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    assert expected_answer["check_role"].sort() == body["permissions"].sort()
    assert status == expected_status

    # revoke role
    url = (
        test_settings.service_url
        + f'/api/v1/auth/users/{query_data["user_id"]}/revoke-role'
    )
    logging.info(query_data["request"])
    body, status = await make_get_request(
        url,
        method="POST",
        data=query_data["request"],
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    assert body == expected_answer["role_revoke"]
    assert status == expected_status


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [
        ({"user_id": ADMIN_USER["id"]}, {"message": "User not found."}, HTTPStatus.OK),
        (
            {"user_id": uuid.uuid4()},
            {"message": "User history is not found"},
            HTTPStatus.OK,
        ),
    ],
)
async def test_user_history(
    make_get_request, admin_tokens, query_data, expected_answer, expected_status
):
    tokens = admin_tokens
    url = (
        test_settings.service_url
        + f'/api/v1/auth/users/{query_data["user_id"]}/history'
    )
    body, status = await make_get_request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    assert status == expected_status
    if type(body) == dict:
        assert body == expected_answer
    else:
        for row in body:
            assert row["user_id"] == str(query_data["user_id"])
