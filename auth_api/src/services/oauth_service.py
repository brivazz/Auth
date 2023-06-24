import uuid
from datetime import datetime, timedelta
import json
import logging
from functools import lru_cache
from http import HTTPStatus

from src.repositories.token_rep import TokenRepository
from src.repositories.oauth_rep import OAuthRepository
from src.utils.extensions import create_hash, create_tokens


class OAuthService:
    def __init__(self, oauth_rep: OAuthRepository, token_rep: TokenRepository):
        self._oauth_repository = oauth_rep
        self._token_repository = token_rep

    def login_or_create_social(self, social_id: str, login: str, user_agent: str):
        """Создание пользователя из социальных сетей."""
        if not self._oauth_repository.social_is_exist(social_id):
            password = str(uuid.uuid4())
            user_id = self._token_repository.save_new_user(login, create_hash(password))
            logging.info(f"User is created {user_id}")
            social_user_id = self._oauth_repository.create_new_social(
                user_id, social_id, login
            )
            logging.info(f"Social user is created {social_user_id}")
        user = self._oauth_repository.user_by_social(social_id)
        role_names = [role.name for role in user.roles]
        access_exp = timedelta(hours=2)
        refresh_exp = timedelta(days=2)
        access_token, refresh_token = create_tokens(
            identity=json.dumps({"roles": role_names, "user_id": str(user.id)}),
            access_expires_delta=access_exp,
            refresh_expires_delta=refresh_exp,
        )
        self._token_repository.save_refresh_token(
            access_token, refresh_token, refresh_exp
        )

        self._token_repository.save_login_history(
            user.id, str(user_agent), datetime.now()
        )
        return HTTPStatus.OK, {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }


@lru_cache()
def get_oauth_service(
    oauth_repository: OAuthRepository, token_repository: TokenRepository
):
    logging.info("init OAuthServices")
    return OAuthService(oauth_repository, token_repository)
