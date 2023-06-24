import os
import sys
import logging
from http import HTTPStatus

import pytest

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from settings import test_settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("expected_answer", [{"status": HTTPStatus.OK}])
async def test_hello_world(make_get_request, expected_answer: dict):
    url = test_settings.service_url + "/hello_world"
    body, status = await make_get_request(url)
    logging.info(status)

    assert status == expected_answer["status"]
