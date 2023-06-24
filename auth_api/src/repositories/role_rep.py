from src.models.role import Role
from flask_sqlalchemy import session


class RoleRepository:
    def __init__(self, db_session: session):
        self._postgres_session = db_session

    def create_role(self, name: str) -> Role:
        """Создать роль."""
        role = Role.query.filter_by(name=name).first()
        if role:
            return {"message": "Role already exists."}

        new_role = Role(name=name)
        self._postgres_session.add(new_role)
        self._postgres_session.commit()
        return {"role_id": new_role.id, "name": new_role.name}

    def delete_role(self, name: str) -> dict[str]:
        """Удалить роль."""
        if Role.query.filter_by(name=name).delete():
            self._postgres_session.commit()
            return {"message": "Role successfully deleted."}

        return {"message": "Role does not exists."}

    def update_role(self, name: str, new_name: str) -> Role:
        """Обновление роли."""
        update_role = Role.query.filter_by(name=name).first()
        if update_role:
            new_name_role = Role.query.filter_by(name=new_name).first()

            if new_name_role:
                return {"message": "Role already exists."}

            update_role.name = new_name
            self._postgres_session.commit()
            return {"role_id": update_role.id, "name": update_role.name}

        return {"message": "No role was found."}

    def viewing_roles(self) -> list[Role]:
        """Просмотр всех ролей."""
        roles = Role.query.all()
        if not roles:
            return {"message": "No roles was found."}

        if len(roles) == 1:
            return {"role_id": roles[0].id, "name": roles[0].name}

        return [{str(role.id): role.name} for role in roles]


role_repository: RoleRepository | None = None


def get_role_repository():
    return role_repository
