import datetime

from redis import Redis
from uuid import UUID

from src.models.auth_history import AuthHistory
from src.models.role import Role
from src.models.user import User
from flask_sqlalchemy import session

from typing import Union

from src.utils.extensions import parse_devices_type


class TokenRepository:
    def __init__(self, redis_cli: Redis, db_session: session):
        self._redis = redis_cli
        self._postgres_session = db_session

    def _set(
        self,
        key: str,
        expire: Union[int, float, datetime.timedelta],
        value: Union[str, int],
    ):
        self._redis.setex(key, expire, value)

    def _get(self, value):
        return self._redis.get(value)

    def user_is_exist_by_id(self, user_id: UUID):
        existing_user = User.query.filter_by(id=user_id).first()
        if existing_user:
            return True
        return False

    def user_is_exist(self, login: str):
        existing_user = User.query.filter_by(login=login).first()
        if existing_user:
            return True
        return False

    def get_user_by_id(self, user_id: UUID) -> User:
        user = User.query.filter_by(id=user_id).first()
        return user

    def get_user_by_login(self, login: str) -> User:
        user = User.query.filter_by(login=login).first()
        return user

    def get_user_by_refresh(self, refresh_token: str) -> User:
        user_id = self._get(refresh_token)
        return self.get_user_by_id(user_id)

    def save_refresh_token(
        self, access_token: str, refresh_token: str, new_token_exp: datetime.timedelta
    ):
        self._set(refresh_token, new_token_exp, access_token)

    def delete_refresh(self, refresh_for_del: str):
        if self._redis.exists(refresh_for_del):
            self._redis.delete(refresh_for_del)
            return True
        return False

    def rework_refresh(
        self,
        old_refresh: str,
        new_refresh: str,
        new_access: str,
        new_refresh_exp: datetime.timedelta,
    ):
        pipeline = self._redis.pipeline()
        pipeline.setex(new_refresh, new_refresh_exp, str(new_access))
        pipeline.delete(old_refresh)
        pipeline.execute()

    def save_new_user(self, login, pass_hash: bytes) -> UUID:
        consumer_role = Role.query.filter_by(name="consumer").first()
        if not consumer_role:
            consumer_role = Role(name="consumer", created=datetime.datetime.now())
        new_user = User(login=login, password=pass_hash)
        new_user.roles.append(consumer_role)
        self._postgres_session.add(new_user)
        self._postgres_session.commit()
        return new_user.id

    def set_new_password(self, user_id, new_pass_hash: bytes) -> UUID | None:
        user_for_update = User.query.filter_by(id=user_id).first()
        if user_for_update:
            user_for_update.password = new_pass_hash
            self._postgres_session.commit()
            return user_for_update.id
        else:
            return None

    def save_login_history(
        self, user_id: UUID, user_agent: str, auth_date: datetime.datetime
    ):
        device_type = parse_devices_type(user_agent)
        new_login = AuthHistory(
            user_id=user_id,
            user_agent=user_agent,
            auth_date=auth_date,
            user_device_type=device_type,
        )

        self._postgres_session.add(new_login)
        self._postgres_session.commit()

    def get_token_inf(self, token):
        return self._get(token)

    def token_exist(self, token):
        if self._redis.exists(token):
            return True
        return False


token_repository: Union[TokenRepository, None] = None


def get_token_repository():
    return token_repository
