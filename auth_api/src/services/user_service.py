import logging
from functools import lru_cache
from uuid import UUID

from src.models.user import User
from src.repositories.user_rep import UserRepository


class UserService:
    def __init__(self, user_rep: UserRepository):
        self._repository = user_rep

    def get_all_users(self):
        users = self._repository.get_all_users_with_id()
        return users

    def get_user(self, login: str) -> User:
        role = self._repository.get_user_by_login(login)
        return role

    def assign_role(self, user_id: UUID, role_name: str):
        result = self._repository.assign_role_to_user(user_id, role_name)
        return result

    def revoke_role(self, user_id: UUID, role_name: str):
        role = self._repository.revoke_role_from_user(user_id, role_name)
        return role

    def viewing_role(self, user_id: UUID) -> list[str] | None:
        role = self._repository.get_user_permissions(user_id=user_id)
        return role

    def user_history(
        self, user_id: UUID, page_number: int, page_size: int
    ) -> list[str] | None:
        history = self._repository.get_user_history(
            user_id=user_id, page_number=page_number, page_size=page_size
        )
        return history


@lru_cache()
def get_user_service(user_repository: UserRepository):
    logging.info("init UserServices")
    return UserService(user_repository)
