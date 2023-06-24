from functools import wraps
from http import HTTPStatus
from datetime import datetime

import redis
from flask import jsonify, request

from src.core.config import settings


redis_rate_limit = redis.StrictRedis(
    host=settings.redis.host, port=settings.redis.port, db=1, decode_responses=True
)

if settings.rate_limit_enabled:

    def rate_limit():
        def wrapper(func):
            @wraps(func)
            def inner(*args, **kwargs):
                pipline = redis_rate_limit.pipeline()
                now = datetime.now()
                key = f"{request.remote_addr}:{now.minute}"
                pipline.incr(key, 1)
                pipline.expire(key, 59)
                request_number = pipline.execute()[0]
                if request_number > settings.default_rate_limit:
                    return (
                        jsonify(msg="Too many requests"),
                        HTTPStatus.TOO_MANY_REQUESTS,
                    )
                return func(*args, **kwargs)

            return inner

        return wrapper
