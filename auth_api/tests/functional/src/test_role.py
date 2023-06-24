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
    "query_data, expected_answer, expected_status",
    [({"name": "test_role"}, "test_role", HTTPStatus.OK)],
)
async def test_role_create(
    admin_tokens, make_get_request, query_data, expected_answer, expected_status
):
    url = test_settings.service_url + "/api/v1/auth/roles"

    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="POST",
        data=query_data,
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    assert body["name"] == expected_answer
    assert status == expected_status


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [
        (
            {"name": "test_role", "new_name": "test_role"},
            {"message": "Role already exists."},
            HTTPStatus.OK,
        )
    ],
)
async def test_role_update_exists(
    admin_tokens, make_get_request, query_data, expected_answer, expected_status
):
    url = test_settings.service_url + "/api/v1/auth/roles/update"

    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="PUT",
        data=query_data,
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )

    assert body == expected_answer
    assert status == expected_status


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [({"name": "test_role"}, {"message": "Role already exists."}, HTTPStatus.OK)],
)
async def test_role_create_replay(
    admin_tokens, make_get_request, query_data, expected_answer, expected_status
):
    url = test_settings.service_url + "/api/v1/auth/roles"

    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="POST",
        data=query_data,
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )

    assert body == expected_answer
    assert status == expected_status


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [({"name": "test_role", "new_name": "like a boss"}, "like a boss", HTTPStatus.OK)],
)
async def test_role_update(
    admin_tokens, make_get_request, query_data, expected_answer, expected_status
):
    url = test_settings.service_url + "/api/v1/auth/roles/update"

    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="PUT",
        data=query_data,
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )

    assert body["name"] == expected_answer
    assert status == expected_status


@pytest.mark.parametrize(
    "expected_answer, expected_status", [([["admin"], ["like a boss"]], HTTPStatus.OK)]
)
async def test_role_viewing(
    admin_tokens, make_get_request, expected_answer, expected_status
):
    url = test_settings.service_url + "/api/v1/auth/roles/view"
    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )
    exists_role_names = list(map(lambda b: list(b.values()), body))
    assert exists_role_names == expected_answer
    assert status == expected_status


@pytest.mark.parametrize(
    "query_data, expected_answer, expected_status",
    [
        (
            {"name": "like a boss"},
            {"message": "Role successfully deleted."},
            HTTPStatus.OK,
        ),
        ({"name": "test_role"}, {"message": "Role does not exists."}, HTTPStatus.OK),
    ],
)
async def test_role_delete(
    admin_tokens, make_get_request, query_data, expected_answer, expected_status
):
    url = test_settings.service_url + "/api/v1/auth/roles/delete"
    tokens = admin_tokens
    body, status = await make_get_request(
        url,
        method="DELETE",
        data=query_data,
        headers={"Authorization": f"Bearer {tokens.get('access_token')}"},
    )

    assert body == expected_answer
    assert status == expected_status
