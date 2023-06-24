import asyncio

import aiohttp
import pytest
import pytest_asyncio
from redis.asyncio import Redis

from functional.settings import test_settings


pytest_plugins = [
    "functional.fixtures.create_pg_data",
]


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def session_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    client = Redis(host=test_settings.redis_host, port=test_settings.redis_port)
    yield client
    await client.close()


@pytest.fixture(scope="session")
def make_get_request(session_client: aiohttp.ClientSession):
    async def inner(
        url: str,
        params: dict = None,
        method: str = "GET",
        data: dict = None,
        headers: dict = None,
    ):
        if method == "GET":
            async with session_client.get(
                url, params=params, headers=headers
            ) as response:
                body = await response.json()
                status = response.status
                return body, status

        if method == "POST":
            async with session_client.post(url, json=data, headers=headers) as response:
                body = await response.json()
                status = response.status
                return body, status

        if method == "DELETE":
            async with session_client.delete(
                url, json=data, headers=headers
            ) as response:
                body = await response.json()
                status = response.status
                return body, status

        if method == "PUT":
            async with session_client.put(url, json=data, headers=headers) as response:
                body = await response.json()
                status = response.status
                return body, status

    return inner
