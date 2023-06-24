from functools import wraps
from http import HTTPStatus

from fastapi import Request, HTTPException
import httpx

from core.config import settings


def is_authenticated(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        url = f"{settings.auth_server_url}/is_authenticated"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=request.headers)
            status_code = response.status_code
        if status_code == HTTPStatus.UNAUTHORIZED:
            raise HTTPException(status_code=401, detail="You are not authenticated")
        if status_code != HTTPStatus.OK:
            raise HTTPException(status_code=500, detail="Something was broke")
        return await func(request, *args, **kwargs)

    return wrapper
