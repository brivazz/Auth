import json
from typing import Type
from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity
from pydantic import BaseModel, ValidationError
from flask import jsonify, request


def validator_json_request(validator_class: Type[BaseModel]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                body = json.loads(request.data)
            except json.JSONDecodeError:
                return jsonify({"err_msg": "Invalid json"}), HTTPStatus.BAD_REQUEST

            try:
                body = validator_class(**body)
                res = func(body, *args, **kwargs)
            except (ValidationError, TypeError):
                return jsonify({"err_msg": "Invalid json"}), HTTPStatus.BAD_REQUEST
            return res

        return wrapper

    return decorator


def request_has_user_agent(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.headers.get("User-Agent"):
            return (
                jsonify({"err_msg": "User-Agent is require."}),
                HTTPStatus.BAD_REQUEST,
            )

        res = func(*args, **kwargs)
        return res

    return wrapper


def check_user_has_role(role_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                token_inf = json.loads(get_jwt_identity())
            except json.JSONDecodeError:
                return jsonify({"err_msg": "Invalid jwt token"}), HTTPStatus.BAD_REQUEST

            if role_name not in token_inf["roles"]:
                return jsonify({"err_msg": "Access denied"}), HTTPStatus.FORBIDDEN

            res = func(*args, **kwargs)
            return res

        return wrapper

    return decorator
