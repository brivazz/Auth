import uuid

from src.models.social import SocialUser
from src.models.user import User
from flask_sqlalchemy import session
from .oauth import oauth


class OAuthRepository:
    def __init__(self, db_session: session):
        self._postgres_session = db_session

    def social_is_exist(self, social_id: str):
        """Проверка наличия роли."""
        existing_social = SocialUser.query.filter_by(social_id=social_id).first()
        if existing_social:
            return True
        return False

    def user_by_social(self, social_id: str):
        """Получение юзера по social_id."""
        user_id = SocialUser.query.filter_by(social_id=social_id).first().user_id
        user = User.query.filter_by(id=user_id).first()
        return user

    def create_new_social(self, user_id: uuid.UUID, social_id: str, login: str):
        """Создание новой социальной сети."""
        new_social = SocialUser(user_id=user_id, social_id=social_id, login=login)
        self._postgres_session.add(new_social)
        self._postgres_session.commit()
        return new_social.id


def create_service(config: dict):
    return oauth.register(**config)


oauth_repository: OAuthRepository | None = None


def get_oauth_repository():
    return oauth_repository
