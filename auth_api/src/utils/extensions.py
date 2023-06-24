import datetime
import logging
from typing import Union

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from ua_parser import user_agent_parser


def create_tokens(
    identity: str,
    access_expires_delta: datetime.timedelta,
    refresh_expires_delta: datetime.timedelta = datetime.timedelta(days=2),
    additional_claims: Union[dict, None] = None,
) -> tuple[str, str]:
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims,
        expires_delta=access_expires_delta,
    )
    refresh_token = create_refresh_token(
        identity=identity, expires_delta=refresh_expires_delta
    )
    return access_token, refresh_token


def create_hash(password: str) -> bytes:
    salt = bcrypt.gensalt()
    password = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password, salt)
    return hashed_password


def check_password(password_to_check: str, hash_pass_with_salt: bytes):
    password_to_check = password_to_check.encode("utf-8")
    logging.info([password_to_check, type(hash_pass_with_salt)])
    logging.info(bcrypt.checkpw(password_to_check, hash_pass_with_salt))
    if bcrypt.checkpw(password_to_check, hash_pass_with_salt):
        return True
    return False


def parse_devices_type(user_agent: str) -> str:
    parsed_user_agent = user_agent_parser.Parse(user_agent)

    api_client_name_list = [
        "api",
        "postmanruntime",
        "curl",
        "python-requests",
        "guzzlehttp",
        "java",
    ]

    if "mobile" in parsed_user_agent["device"]["family"].lower():
        return "mobile"
    elif "smart" in parsed_user_agent["device"]["family"].lower():
        return "smart"
    elif parsed_user_agent["user_agent"]["family"].lower() in api_client_name_list:
        return "api_client"
    else:
        return "web"
