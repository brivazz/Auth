import datetime
from datetime import timedelta
import json
import logging
from functools import lru_cache
from http import HTTPStatus
from typing import Tuple

from flask_jwt_extended import decode_token

from src.repositories.token_rep import TokenRepository
from src.utils.extensions import create_hash, create_tokens, check_password


class TokenServices:
    def __init__(self, token_rep: TokenRepository):
        self._repository = token_rep

    def change_password(self, token_inf: dict, old_password, new_password):
        user_id = token_inf["user_id"]

        if not self._repository.user_is_exist_by_id(user_id):
            return HTTPStatus.CONFLICT, {"err_msg": "Access token is not valid."}

        user = self._repository.get_user_by_id(user_id)
        if not check_password(old_password, user.password):
            return HTTPStatus.UNAUTHORIZED, {"err_msg": "Old password is not valid."}

        pass_hash = create_hash(new_password)
        if self._repository.set_new_password(user_id, pass_hash):
            return HTTPStatus.OK, "new pass saved"
        return HTTPStatus.NOT_FOUND, "please try again"

    def login(self, login: str, response_password: str, user_agent: str):
        if not self._repository.user_is_exist(login):
            return HTTPStatus.UNAUTHORIZED, {"err_msg": "Login is not valid."}

        user = self._repository.get_user_by_login(login)
        if not check_password(response_password, user.password):
            return HTTPStatus.UNAUTHORIZED, {"err_msg": "Password is not valid."}

        access_exp = timedelta(hours=2)
        refresh_exp = timedelta(days=2)
        role_names = [role.name for role in user.roles]
        access_token, refresh_token = create_tokens(
            identity=json.dumps({"roles": role_names, "user_id": str(user.id)}),
            access_expires_delta=access_exp,
            refresh_expires_delta=refresh_exp,
        )
        self._repository.save_refresh_token(access_token, refresh_token, refresh_exp)

        self._repository.save_login_history(
            user.id, str(user_agent), datetime.datetime.now()
        )
        return HTTPStatus.OK, {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def logout(self, refresh_token):
        if self._repository.delete_refresh(refresh_token):
            return HTTPStatus.OK, "you are logout"
        return HTTPStatus.BAD_REQUEST, {"err_msg": "refresh is not valid"}

    def refresh_tokens(self, old_refresh_token: str):
        if self._repository.token_exist(old_refresh_token):
            token_inf = decode_token(old_refresh_token)
            if token_inf["type"] == "refresh":
                token_sub_inf: dict = json.loads(token_inf["sub"])
                user_id = token_sub_inf["user_id"]
                user = self._repository.get_user_by_id(user_id)

                role_names = [role.name for role in user.roles]
                access_exp = timedelta(hours=2)
                refresh_exp = timedelta(days=2)
                new_access_token, new_refresh_token = create_tokens(
                    identity=json.dumps({"roles": role_names, "user_id": str(user_id)}),
                    access_expires_delta=access_exp,
                    refresh_expires_delta=refresh_exp,
                )
                self._repository.rework_refresh(
                    old_refresh_token, new_refresh_token, new_access_token, refresh_exp
                )
                return HTTPStatus.OK, {
                    "access_token": new_access_token,
                    "refresh_token": new_refresh_token,
                }

            return HTTPStatus.BAD_REQUEST, "refresh token is not valid"

        return HTTPStatus.BAD_REQUEST, {"err_msg": "refresh token is not exist"}

    def register(self, login: str, password: str, user_agent: str) -> Tuple[int, any]:
        if self._repository.user_is_exist(login):
            return HTTPStatus.CONFLICT, {
                "err_msg": "User with this login already exists."
            }
        pass_hash = create_hash(password)
        user_id = self._repository.save_new_user(login, pass_hash)
        user = self._repository.get_user_by_id(user_id)
        logging.info(user_agent)

        access_exp = timedelta(hours=2)
        refresh_exp = timedelta(days=2)
        role_names = [role.name for role in user.roles]
        access_token, refresh_token = create_tokens(
            identity=json.dumps({"roles": role_names, "user_id": str(user.id)}),
            access_expires_delta=access_exp,
            refresh_expires_delta=refresh_exp,
        )
        self._repository.save_refresh_token(access_token, refresh_token, refresh_exp)

        self._repository.save_login_history(
            user_id, str(user_agent), datetime.datetime.now()
        )
        return HTTPStatus.OK, {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


@lru_cache()
def get_token_service(token_repository: TokenRepository):
    logging.info("init TokenServices")
    return TokenServices(token_repository)
