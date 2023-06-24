import logging
from functools import lru_cache

from src.repositories.role_rep import RoleRepository
from src.models.role import Role


class RoleService:
    def __init__(self, role_rep: RoleRepository):
        self._repository = role_rep

    def create_role(self, name: str) -> Role:
        role = self._repository.create_role(name)
        return role

    def delete_role(self, name: str) -> dict[str, str]:
        result = self._repository.delete_role(name)
        return result

    def update_role(self, name: str, new_name: str) -> Role:
        role = self._repository.update_role(name=name, new_name=new_name)
        return role

    def viewing_roles(self) -> list[Role] | dict[str, str]:
        role = self._repository.viewing_roles()
        return role


@lru_cache()
def get_role_service(role_repository: RoleRepository) -> RoleService:
    logging.info("init RoleServices")
    return RoleService(role_repository)
